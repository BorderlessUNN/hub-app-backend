from rest_framework.views import APIView
from rest_framework import status
from accounts.models import CustomUser
from helpers.responses import CustomResponse, custom_post_schema
from accounts.permissions import IsAdminUser, IsSuperAdminUser
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
    MeSerializer,
    LogoutSerializer,
    LogoutResponseSerializer,
    AccountSearchSerializer,
    AdminCreateSerializer,
    AdminResponseSerializer,
    AdminDeactivateSerializer,
    CustomUserSerializer,
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

    Community members are added by an admin (Staff or Super), individually
    or via CSV import (see MemberImport* views) - not self-service.
    """
    permission_classes = [IsAdminUser]
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

class CheckIfUserHasPasswordView(APIView):
    """
    API to check if a member has a password (first-login detection for the
    phone/password member login flow).
    """
    serializer_class = CheckIfUserHasPasswordSerializer
    permission_classes = [AllowAny]

    @custom_post_schema(CheckIfUserHasPasswordSerializer, CheckIfUserHasPasswordResponseSerializer, status_code=status.HTTP_200_OK)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        if user.has_usable_password():
            return CustomResponse(
                valid=True,
                msg="User has password",
                data={'has_password': True})
        else:
            return CustomResponse(
                valid=False,
                msg="User does not have a password",
                data={'has_password': False})

class SetPasswordView(APIView):
    """
    API for a member to set their password on first login.
    """
    serializer_class = SetPasswordSerializer
    permission_classes = [AllowAny]

    @custom_post_schema(SetPasswordSerializer, SetPasswordResponseSerializer, status_code=status.HTTP_200_OK)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        password = serializer.validated_data.get('password')
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


class AccountSearchView(APIView):
    """
    Fast phone-number lookup for front-desk staff (Staff or Super Admin).
    """
    serializer_class = AccountSearchSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        return CustomResponse(
            valid=True,
            msg="User found",
            data=CustomUserSerializer(user).data
        )


class MemberListView(APIView):
    """
    List existing community members (any admin tier). Supports an optional
    ?search= filter over name, email, and phone number.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        members = CustomUser.objects.filter(is_member=True, is_active=True)
        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            members = members.filter(
                Q(user_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone_number__icontains=search)
            )
        members = members.order_by('user_name')
        return CustomResponse(
            valid=True,
            msg="Members fetched successfully",
            data=CustomUserSerializer(members, many=True).data,
        )


class AdminListView(APIView):
    """ List all admin accounts (Super Admin only). """
    permission_classes = [IsSuperAdminUser]

    def get(self, request):
        admins = CustomUser.objects.filter(is_superuser=True).order_by('user_name')
        return CustomResponse(
            valid=True,
            msg="Admins fetched successfully",
            data=AdminResponseSerializer(admins, many=True).data
        )


class AdminCreateView(APIView):
    """ Create a new admin account, Staff or Super (Super Admin only). """
    serializer_class = AdminCreateSerializer
    permission_classes = [IsSuperAdminUser]

    @custom_post_schema(AdminCreateSerializer, AdminResponseSerializer, status_code=status.HTTP_201_CREATED)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = serializer.save()
        return CustomResponse(
            valid=True,
            msg="Admin created successfully",
            status=status.HTTP_201_CREATED,
            data=AdminResponseSerializer(admin).data
        )


class AdminDeactivateView(APIView):
    """
    Deactivate an admin account (Super Admin only). Refuses to deactivate
    yourself or the last remaining active Super Admin.
    """
    serializer_class = AdminDeactivateSerializer
    permission_classes = [IsSuperAdminUser]

    @custom_post_schema(AdminDeactivateSerializer, AdminResponseSerializer, status_code=status.HTTP_200_OK)
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        admin = serializer.save()
        return CustomResponse(
            valid=True,
            msg="Admin deactivated successfully",
            data=AdminResponseSerializer(admin).data
        )