from rest_framework.views import APIView
from rest_framework import status
from helpers.responses import CustomResponse
from checkin.serializers import MemberCheckInSerializer, GuestCheckInSerializer
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

class GuestCheckInView(APIView):
    """
    API view for guest check-in
    """
    def post(self, request):
        serializer = GuestCheckInSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(
            valid=True,
            status=status.HTTP_200_OK,
            msg="Check-in successful.",
            data=serializer.data
        )
        return CustomResponse(
            valid=False,
            msg=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)