import csv
import io

from django.db import transaction
from rest_framework import serializers

from accounts.models import CustomUser
from accounts.utils import normalize_phone_number
from helpers.exceptions import CustomValidationException

CSV_COLUMNS = ['user_name', 'email', 'phone_number', 'department', 'tech_stack', 'date_of_birth']


def _clean_row(raw_row, index):
    """
    Normalize and validate a single CSV row into either a valid member
    payload or a structured error. `index` is the 1-based data row number
    (excluding the header) for reporting.
    """
    row = {col: (raw_row.get(col) or '').strip() for col in CSV_COLUMNS}
    errors = []

    for required in ['user_name', 'email', 'phone_number']:
        if not row[required]:
            errors.append(f"Missing {required}")

    normalized_phone = None
    if row['phone_number']:
        try:
            normalized_phone = normalize_phone_number(row['phone_number'])
            row['phone_number'] = normalized_phone
        except CustomValidationException:
            errors.append("Invalid phone number")

    if row['email']:
        row['email'] = row['email'].lower()

    return {
        "row_number": index,
        "data": row,
        "errors": errors,
        "normalized_phone": normalized_phone,
    }


def parse_and_classify_csv(file_obj):
    """
    Parse an uploaded CSV file and classify every data row as valid,
    duplicate (phone already exists on a member), or invalid. Nothing is
    written to the database.
    """
    try:
        decoded = file_obj.read().decode('utf-8-sig')
    except (UnicodeDecodeError, AttributeError):
        raise CustomValidationException(msg="Could not read file - please upload a UTF-8 CSV", code=400)

    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames:
        raise CustomValidationException(msg="CSV file is empty", code=400)

    missing_cols = [c for c in ['user_name', 'email', 'phone_number'] if c not in reader.fieldnames]
    if missing_cols:
        raise CustomValidationException(
            msg=f"CSV is missing required column(s): {', '.join(missing_cols)}",
            code=400,
        )

    valid_rows = []
    duplicate_rows = []
    invalid_rows = []

    # Existing member phone numbers, for duplicate detection.
    existing_member_phones = set(
        CustomUser.objects.filter(is_member=True, phone_number__isnull=False)
        .values_list('phone_number', flat=True)
    )
    # Track phones seen within this same file to catch intra-file dupes.
    seen_phones = set()

    for i, raw_row in enumerate(reader, start=1):
        cleaned = _clean_row(raw_row, i)
        if cleaned['errors']:
            invalid_rows.append(cleaned)
            continue

        phone = cleaned['normalized_phone']
        if phone in existing_member_phones:
            cleaned['reason'] = "A member with this phone number already exists"
            duplicate_rows.append(cleaned)
        elif phone in seen_phones:
            cleaned['reason'] = "Duplicate phone number within this file"
            duplicate_rows.append(cleaned)
        else:
            seen_phones.add(phone)
            valid_rows.append(cleaned)

    return {
        "valid_rows": valid_rows,
        "duplicate_rows": duplicate_rows,
        "invalid_rows": invalid_rows,
        "summary": {
            "valid": len(valid_rows),
            "duplicate": len(duplicate_rows),
            "invalid": len(invalid_rows),
        },
    }


class MemberImportPreviewSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        name = getattr(value, 'name', '') or ''
        if not name.lower().endswith('.csv'):
            raise serializers.ValidationError("Please upload a .csv file")
        return value


class ImportRowSerializer(serializers.Serializer):
    """ A single row echoed back from the preview with the admin's decision. """
    user_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    department = serializers.CharField(required=False, allow_blank=True, default='')
    tech_stack = serializers.CharField(required=False, allow_blank=True, default='')
    date_of_birth = serializers.CharField(required=False, allow_blank=True, default='')
    action = serializers.ChoiceField(choices=['create', 'update', 'skip'], default='create')


class MemberImportConfirmSerializer(serializers.Serializer):
    rows = ImportRowSerializer(many=True)

    def save(self):
        rows = self.validated_data['rows']
        created, updated, skipped = 0, 0, 0
        errors = []

        with transaction.atomic():
            for row in rows:
                action = row.get('action', 'create')
                if action == 'skip':
                    skipped += 1
                    continue

                try:
                    phone = normalize_phone_number(row['phone_number'])
                except CustomValidationException:
                    errors.append({"email": row.get('email'), "error": "Invalid phone number"})
                    continue

                dob = row.get('date_of_birth') or None
                defaults = {
                    'user_name': row['user_name'],
                    'phone_number': phone,
                    'department': row.get('department') or None,
                    'tech_stack': row.get('tech_stack') or None,
                    'date_of_birth': dob,
                    'is_member': True,
                }

                existing = CustomUser.objects.filter(email__iexact=row['email']).first()
                if existing:
                    if action == 'update':
                        for field, val in defaults.items():
                            setattr(existing, field, val)
                        if not existing.has_usable_password():
                            existing.set_unusable_password()
                        existing.save()
                        updated += 1
                    else:
                        skipped += 1
                    continue

                user = CustomUser(email=row['email'].lower(), **defaults)
                user.set_unusable_password()
                user.save()
                created += 1

        return {"created": created, "updated": updated, "skipped": skipped, "errors": errors}
