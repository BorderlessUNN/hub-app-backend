from rest_framework.views import APIView
from rest_framework import status
from helpers.responses import CustomResponse
from user.serializers import UserExistsSerializer
from accounts.permissions import IsAdminUser


class UserExistsView(APIView):
    """
    API to check if a hub user exists by email.
    """

    serializer_class = UserExistsSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):
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
