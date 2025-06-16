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

    