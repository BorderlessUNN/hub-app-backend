from rest_framework.views import APIView
from helpers.responses import CustomResponse
from .serializers import CheckInStatsSerializer, UserStatsSerializer
from accounts.permissions import IsAdminUser

class CheckInStatsView(APIView):
    """
    API view for fetching check-in statistics
    """
    permission_classes = [IsAdminUser]
    def get(self, request):
        serializer = CheckInStatsSerializer(instance={})
        return CustomResponse(
            valid=True,
            msg="Check-in statistics fetched successfully",
            data=serializer.data
        )

class UserStatsView(APIView):
    """
    API view for fetching user statistics
    """
    permission_classes = [IsAdminUser]
    def get(self, request):
        months = request.query_params.get('months', 1)
        serializer = UserStatsSerializer(instance={}, context={'months': months})
        return CustomResponse(
            valid=True,
            msg="User statistics fetched successfully",
            data=serializer.data
        )