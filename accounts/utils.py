from rest_framework_simplejwt.tokens import RefreshToken


def get_auth_tokens_for_admin(admin, access_only=False):
    refresh = RefreshToken.for_user(admin)
    return {
        'access_token': str(refresh.access_token)
    } if access_only else {
        'refresh_token': str(refresh),
        'access_token': str(refresh.access_token),
    }