from rest_framework.views import APIView
from rest_framework import status
from accounts.models import CustomUser
from helpers.responses import CustomResponse, custom_post_schema 
from accounts.permissions import IsAdminUser
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.serializers import (
    AdminLoginSerializer,
    AdminLoginResponseSerializer,
    CustomMemberCreateSerializer,
    AccessTokenSerializer,
    AccessTokenResponseSerializer,
    CaptureNonMemberDataSerializer,
    UserExistsSerializer,
    UserExistsResponseSerializer,
    SetPasswordSerializer,
    SetPasswordResponseSerializer,
    CustomMemberCreateResponseSerializer,
    CheckIfUserHasPasswordSerializer,
    CheckIfUserHasPasswordResponseSerializer,
    MemberLoginSerializer,
    MemberLoginResponseSerializer,
    CustomUserSerializer,
    MeSerializer,
    LogoutSerializer,
    LogoutResponseSerializer,
)


class AdminLoginView(APIView):
    """
    API view for CustomAdmin login
    """
    serializer_class = AdminLoginSerializer

    @custom_post_schema(AdminLoginSerializer, AdminLoginResponseSerializer, status_code=status.HTTP_200_OK)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return CustomResponse(
            valid=True,
            status=status.HTTP_200_OK,
            msg='Login successful',
            data=serializer.validated_data
        )
    

class AccessTokenView(APIView):
    """
    Get the access token for a user from the refresh token
    """
    serializer_class = AccessTokenSerializer

    @custom_post_schema(AccessTokenSerializer, AccessTokenResponseSerializer, status_code=status.HTTP_200_OK)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return CustomResponse(
            valid=True,
            msg="Access token generated successfully",
            data=serializer.validated_data
        )


class CaptureDataHelperView(APIView):
    permission_classes = [IsAdminUser]
    msg = "Data captured successfully"
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return CustomResponse(
                valid=True,
                msg=self.msg,
                status=status.HTTP_201_CREATED,
                data=self.serializer_class(user).data
            )
        return CustomResponse(
            valid=False,
            msg=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class CreateMemberView(CaptureDataHelperView):
    """
    API View for creating a new member.
    """
    permission_classes = [AllowAny]
    serializer_class = CustomMemberCreateSerializer
    # msg = 'User created successfully'
    @custom_post_schema(CustomMemberCreateSerializer, CustomMemberCreateResponseSerializer, status_code=status.HTTP_201_CREATED)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_unusable_password()
        user.save()
        return CustomResponse(
            valid=True,
            msg='User created successfully',
            status=status.HTTP_201_CREATED,
            data=self.serializer_class(user).data)

class CaptureNonMemberDataView(CaptureDataHelperView):
    """
    API View for capturing non member data
    """
    serializer_class = CaptureNonMemberDataSerializer
    msg = 'Non member data captured successfully'


class UserExistsView(APIView):
    """
    API to check if a hub user exists by email.
    """

    
    permission_classes = [IsAdminUser]

    @custom_post_schema(UserExistsSerializer, UserExistsResponseSerializer, status_code=status.HTTP_200_OK)
    def post(self, request):
        serializer = UserExistsSerializer(data=request.data)
        if serializer.is_valid():
            return CustomResponse(
            valid=True,
            status=status.HTTP_200_OK,
            msg="Hub user exists",
            data=serializer.validated_data
        )
        return CustomResponse(
            valid=False,
            msg=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

# class CustomUserView(APIView):
#     """ Get all users """
#     serializer_class = CustomUserSerializer
#     def get(self, request):
#         users = CustomUser.objects.all()
#         return CustomResponse(
#             valid=True,
#             msg="Users fetched successfully",
#             data=self.serializer_class(users, many=True).data
#         )

class CheckIfUserHasPasswordView(APIView):
    """
    API to check if a user has a password.
    """
    serializer_class = CheckIfUserHasPasswordSerializer
    permission_classes = [AllowAny]

    @custom_post_schema(CheckIfUserHasPasswordSerializer, CheckIfUserHasPasswordResponseSerializer, status_code=status.HTTP_200_OK)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user = CustomUser.objects.get(email=email)
        if user.has_usable_password():
            return CustomResponse(
                valid=True,
                msg="User has password",
                data=serializer.validated_data)
        else:
            return CustomResponse(
                valid=False,
                msg="User does not have a password",
                data=serializer.validated_data)

class SetPasswordView(APIView):
    """
    API to set a password for a user.
    """
    serializer_class = SetPasswordSerializer
    permission_classes = [AllowAny]

    @custom_post_schema(SetPasswordSerializer, SetPasswordResponseSerializer, status_code=status.HTTP_200_OK)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        whatsapp_number = serializer.validated_data.get('whatsapp_number')
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        user = CustomUser.objects.get(email=email)
        user.set_password(password)
        user.save()
        
        return CustomResponse(
            valid=True,
            msg="Password set successfully",
            )

class MemberLoginView(APIView):
    """ Endpoint for member login """
    serializer_class = MemberLoginSerializer
    permission_classes = [AllowAny]

    @custom_post_schema(MemberLoginSerializer, MemberLoginResponseSerializer, status_code=status.HTTP_200_OK)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return CustomResponse(
            valid=True,
            msg="Login successful",
            data=serializer.validated_data
        )

class MeView(APIView):
    """ Get the current user """
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return CustomResponse(
            valid=True,
            msg="User fetched successfully",
            data=self.serializer_class(user).data
        )

class LogoutView(APIView):
    """ Logout the current user """
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer
    @custom_post_schema(LogoutSerializer, LogoutResponseSerializer, status_code=status.HTTP_200_OK)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return CustomResponse(
            valid=True,
            msg="Logged out successfully",
        )