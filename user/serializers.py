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

        return {
            "id": str(member.id),
            "name": member.user_name,
            "email": member.email,
            "is_member": member.is_member,
        }

