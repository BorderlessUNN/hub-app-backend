from rest_framework.views import APIView
from rest_framework import status

from helpers.responses import CustomResponse
from accounts.permissions import IsAdminUser
from accounts.serializers import (
    AdminLoginSerializer,
    CustomMemberCreateSerializer,
    AccessTokenSerializer,
    CaptureNonMemberDataSerializer
)


class AdminLoginView(APIView):
    """
    API view for CustomAdmin login
    """

    serializer_class = AdminLoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return CustomResponse(
            valid=True,
            status=status.HTTP_200_OK,
            msg='Login successful',
            data=serializer.validated_data
        )
    

class AdminAccessTokenView(APIView):
    """
    Get the access token for a user from the refresh token
    """

    serializer_class = AccessTokenSerializer

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
    serializer_class = CustomMemberCreateSerializer
    msg = 'User created successfully'
    

class CaptureNonMemberDataView(CaptureDataHelperView):
    """
    API View for capturing non member data
    """
    serializer_class = CaptureNonMemberDataSerializer
    msg = 'Non member data captured successfully'