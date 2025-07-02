from rest_framework import serializers
from accounts.models import CustomUser
from helpers.exceptions import CustomValidationException
from django.utils import timezone

class UserExistsSerializer(serializers.Serializer):
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

        self.member = member
        return attrs

    def to_representation(self):
        return {
            "id": str(self.member.id),
            "name": self.member.user_name,
            "email": self.member.email,
            "is_member": self.member.is_member,
        }
