from rest_framework.views import APIView
from accounts.permissions import IsAdminUser
from helpers.responses import CustomResponse


class SeatView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        return CustomResponse(
            valid=True,
            status=200,
            msg="WIP",
        )