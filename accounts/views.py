from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.hashers import check_password
from accounts.models import CustomAdmin

from helpers.responses import CustomResponse



class AdminLoginView(APIView):
    """
    API view for CustomAdmin login
    """
    def post(self, request):
        return CustomResponse(valid=True, msg="Login successful", status=status.HTTP_200_OK)
        # email = request.data.get('email', '').lower()
        # password = request.data.get('password', '')

        # if not email or not password:
        #     return CustomResponse({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     admin = CustomAdmin.objects.get(email=email)
        #     if check_password(password, admin.password):
        #         # Example: return session data or a message
        #         request.session['admin_id'] = admin.id
        #         return CustomResponse({"detail": "Login successful", "admin_id": admin.id}, status=status.HTTP_200_OK)
        #     else:
        #         return CustomResponse({"detail": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)
        # except CustomAdmin.DoesNotExist:
        #     return CustomResponse({"detail": "Admin with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

