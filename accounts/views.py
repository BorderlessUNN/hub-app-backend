from rest_framework.views import APIView
from rest_framework import status

from helpers.responses import CustomResponse
from accounts.serializers import AdminLoginSerializer


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

