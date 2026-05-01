from rest_framework_simplejwt.authentication import JWTAuthentication, api_settings
from rest_framework_simplejwt.exceptions import TokenError
from accounts.models import CustomUser
from helpers.exceptions import CustomValidationException


class CustomUserAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                raise CustomValidationException(msg="Invalid or expired token")
        raise CustomValidationException(msg="Invalid or expired token")
            
    
    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")

        if user_id is None:
            return None

        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None