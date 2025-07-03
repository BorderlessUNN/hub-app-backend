from django.contrib.auth.hashers import check_password
from rest_framework import serializers

from accounts.models import CustomAdmin, CustomUser
from accounts.tokens import get_auth_tokens_for_admin, get_access_token_from_refresh_token
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
    

class AccessTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')
        return {
            'access_token': get_access_token_from_refresh_token(refresh_token)
        }



class CustomMemberCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[]
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'user_name',
            'email',
            'department',
            'whatsapp_number',
            'date_of_birth',
            'tech_stack',
        ]
        extra_kwargs = {
            'user_name': {'required': True},
            'email': {'required': True},
            'department': {'required': True},
            'whatsapp_number': {'required': True},
            'date_of_birth': {'required': True},
            'tech_stack': {'required': True},
        }

    def validate_email(self, value):
        # Only raise error if a *member* with the email exists
        if CustomUser.objects.filter(email__iexact=value, is_member=True).exists():
            raise CustomValidationException("A member with this email already exists.")
        return value

    def validate(self, attrs):
        attrs['email'] = attrs['email'].lower()
        attrs['user_name'] = attrs['user_name'].title()
        return attrs

    def create(self, validated_data):
        """
        Create a new member.
        
        If a user with the email exists, update their data and mark as member.
        If not, create a new member.
        """
        email = validated_data['email']
        user, created = CustomUser.objects.get_or_create(email=email, defaults={
            'user_name': validated_data['user_name'],
            'department': validated_data['department'],
            'whatsapp_number': validated_data['whatsapp_number'],
            'date_of_birth': validated_data['date_of_birth'],
            'tech_stack': validated_data['tech_stack'],
            'is_member': True
        })

        if not created:
            # Update existing user fields
            user.user_name = validated_data['user_name']
            user.department = validated_data['department']
            user.whatsapp_number = validated_data['whatsapp_number']
            user.date_of_birth = validated_data['date_of_birth']
            user.tech_stack = validated_data['tech_stack']
            user.is_member = True
            user.save()

        return user
    

class CaptureNonMemberDataSerializer(CustomMemberCreateSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'user_name',
            'email',
            'department',
            'whatsapp_number',
            'date_of_birth',
            'tech_stack',
        ]
    
    def create(self, validated_data):
        """
        Capture non member data for reference
        
        If a user with the email exists, update their data.
        If not, create a new non member.
        """
        email = validated_data['email']
        user, created = CustomUser.objects.get_or_create(email=email, defaults={
            'user_name': validated_data['user_name'],
            'department': validated_data['department'],
            'whatsapp_number': validated_data['whatsapp_number'],
            'date_of_birth': validated_data['date_of_birth'],
            'tech_stack': validated_data['tech_stack'],
            'is_member': False
        })

        if not created:
            # Update existing user fields
            user.user_name = validated_data['user_name']
            user.department = validated_data['department']
            user.whatsapp_number = validated_data['whatsapp_number']
            user.date_of_birth = validated_data['date_of_birth']
            user.tech_stack = validated_data['tech_stack']
            user.is_member = False
            user.save()

        return user


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