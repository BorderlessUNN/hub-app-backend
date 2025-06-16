from rest_framework.views import APIView
from rest_framework import status
from helpers.responses import CustomResponse
from checkin.serializers import MemberCheckInSerializer
from accounts.permissions import IsAdminUser


class MemberCheckInView(APIView):
    """
    API for community member check-in
    """

    serializer_class = MemberCheckInSerializer
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return CustomResponse(
            valid=True,
            status=status.HTTP_200_OK,
            msg="Check-in successful.",
            data=serializer.validated_data
        )
