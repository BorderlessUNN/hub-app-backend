from django.contrib.auth.hashers import check_password
from rest_framework import serializers

from accounts.models import CustomAdmin, CustomMember
from accounts.utils import get_auth_tokens_for_admin
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
            'tokens': get_auth_tokens_for_admin(admin)
        }


class CustomMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomMember
        fields = [
            'user_name',
            'email',
            'department',
            'whatsapp_number',
            'date_of_birth',
            'tech_stack',
        ]

    def validate_email(self, value):
        if CustomMember.objects.filter(email__iexact=value).exists():
            raise CustomValidationException("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Ensure name is capitalized and email is lowercase
        validated_data['user_name'] = validated_data.get('user_name', '').title()
        validated_data['email'] = validated_data.get('email', '').lower()
        return super().create(validated_data)

