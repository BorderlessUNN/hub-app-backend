from rest_framework.views import APIView
from rest_framework import status

from helpers.responses import CustomResponse
from accounts.serializers import AdminLoginSerializer, CustomMemberCreateSerializer


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
    

class CreateMemberView(APIView):
    """
    API View for creating a new member.
    """
    serializer_class = CustomMemberCreateSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return CustomResponse(
                valid=True,
                msg='User created successfully',
                status=status.HTTP_201_CREATED,
                data=CustomMemberCreateSerializer(user).data
            )
        return CustomResponse(
            valid=False,
            msg=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

