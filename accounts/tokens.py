from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from helpers.exceptions import CustomValidationException


def get_auth_tokens_for_admin(admin):
    refresh = RefreshToken.for_user(admin)
    return {
        'refresh_token': str(refresh),
        'access_token': str(refresh.access_token),
    }

def get_access_token_from_refresh_token(refresh_token):
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)

        return access_token
    except TokenError as e:
        raise CustomValidationException(msg="Invalid or expired refresh token")