from rest_framework import serializers
from accounts.models import CustomUser
from helpers.exceptions import CustomValidationException
from django.utils import timezone
from checkin.models import CheckIn

class MemberCheckInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        try:
            member = CustomUser.objects.get(email=email, is_member=True)
        except CustomUser.DoesNotExist:
            raise CustomValidationException(
                msg="No member found with this email",
                code=404
            )

        today = timezone.now().date()
        if member.last_checkin and member.last_checkin.date() == today:
            raise CustomValidationException(
                msg=f"{member.email} has already checked in today.",
                code=400
            )

        self.member = member
        return attrs

    def save(self):
        now = timezone.now()

        self.member.last_checkin = now
        self.member.save(update_fields=["last_checkin"])

        # Log Check-in
        CheckIn.objects.create(user=self.member, timestamp=now)

        return self.member

    def to_representation(self):
        return {
            "id": str(self.member.id),
            "name": self.member.user_name,
            "email": self.member.email,
            "last_checkin": self.member.last_checkin
        }


class GuestCheckInSerializer(serializers.Serializer):
    user_name = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=True)
    department = serializers.CharField(required=False, max_length=200, allow_blank=True)
    whatsapp_number = serializers.CharField(required=False, max_length=15, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        attrs['email'] = email

        if CustomUser.objects.filter(email=email, is_member=True).exists():
            raise CustomValidationException(
                msg="This email is already registered as a member. Use the member check-in instead.",
                code=400
            )
        
        self.attrs = attrs
        return attrs

    def save(self):
        email = self.attrs.get('email')

        try:
            # Try to get existing guest user
            guest = CustomUser.objects.get(email=email, is_member=False)
            guest.last_checkin = timezone.now()
            guest.save(update_fields=["last_checkin"])
            self.instance = guest

        except CustomUser.DoesNotExist:
            # Create new guest user
            guest = CustomUser.objects.create(
                user_name=self.attrs.get('user_name'),
                email=self.attrs.get('email'),
                department=self.attrs.get('department', ''),
                whatsapp_number=self.attrs.get('whatsapp_number', ''),
                date_of_birth=self.attrs.get('date_of_birth', None),
                last_checkin=timezone.now(),
                is_member=False
            )
            self.instance = guest

        CheckIn.objects.create(user=self.instance)

        return self.instance

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "name": instance.user_name,
            "email": instance.email,
            "last_checkin": instance.last_checkin
        }