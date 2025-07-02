from rest_framework import serializers
from accounts.models import CustomUser
from helpers.exceptions import CustomValidationException
from django.utils import timezone

class MemberCheckInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        try:
            member = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise CustomValidationException(
                msg="No user found with this email",
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

        return self.member

    def to_representation(self):
        return {
            "id": str(self.member.id),
            "name": self.member.user_name,
            "email": self.member.email,
            "is_member": self.member.is_member,
            "last_checkin": self.member.last_checkin
        }
