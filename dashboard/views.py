from rest_framework.views import APIView
from helpers.responses import CustomResponse
from .serializers import CheckInStatsSerializer
from accounts.permissions import IsAdminUser

class CheckInStatsView(APIView):
    """
    API view for fetching check-in statistics
    """
    permission_classes = [IsAdminUser]
    def get(self, request):
        serializer = CheckInStatsSerializer()
        return CustomResponse(
            valid=True,
            msg="Check-in statistics fetched successfully",
            data=serializer.data
        )
