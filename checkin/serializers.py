from rest_framework import serializers
from accounts.models import CustomUser
from helpers.exceptions import CustomValidationException
from django.utils import timezone

class MemberCheckInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        email = email.lower()
        try:
            self.member = CustomUser.objects.get(email=email, is_member=True)
        except CustomUser.DoesNotExist:
            raise CustomValidationException(
                    msg="No member found with this email",
                    code=404
                )
        # Check if the user already checked in today
        last_checkin = self.member.last_checkin
        today = timezone.now().date()

        if last_checkin and last_checkin == today:
            raise CustomValidationException(
                msg=f"{self.member.email} has already checked in today.",
                code=400
            )
        # Update the last_checkin field
        self.member.last_checkin = timezone.now()
        self.member.save(update_fields=["last_checkin"])

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

        return self.instance

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "name": instance.user_name,
            "email": instance.email,
            "last_checkin": instance.last_checkin
        }