from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.models import CustomAdmin


class CustomAdminAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")

        if user_id is None:
            return None

        try:
            return CustomAdmin.objects.get(id=user_id)
        except CustomAdmin.DoesNotExist:
            return None