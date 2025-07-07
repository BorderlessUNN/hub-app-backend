from rest_framework.views import APIView
from helpers.responses import CustomResponse
from .serializers import CheckInStatsSerializer, UserStatsSerializer
from accounts.permissions import IsAdminUser

class CheckInStatsView(APIView):
    """
    API view for fetching check-in statistics
    """
    permission_classes = [IsAdminUser]
    serializer_class = CheckInStatsSerializer
    
    def get(self, request):
        serializer = self.serializer_class(instance={})
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
    serializer_class = UserStatsSerializer
    
    def get(self, request):
        serializer = self.serializer_class(data=request.data, instance={})
        serializer.is_valid(raise_exception=True)
        return CustomResponse(
            valid=True,
            msg="User statistics fetched successfully",
            data=serializer.data
        )