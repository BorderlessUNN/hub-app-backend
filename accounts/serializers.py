from django.contrib.auth.hashers import check_password
from rest_framework import serializers

from accounts.models import CustomAdmin
from helpers.exceptions import CustomValidationException


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
        
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate user using email and password
        try:
            admin = CustomAdmin.objects.get(email=email)
            if not check_password(password, admin.password):
                raise CustomValidationException(
                    msg="Invalid credentials provided.",
                    code=401
                )
        except CustomAdmin.DoesNotExist:
            raise CustomValidationException(
                msg="Admin not found.",
                code=404
            )
        
        admin.update_last_login()
        return {
            'name': admin.admin_name,
            'email': admin.email,
            'id': admin.id,
        }
