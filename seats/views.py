from rest_framework.views import APIView
from accounts.permissions import IsAdminUser
from helpers.responses import CustomResponse
from seats.models import Seat
from seats.serializers import SeatStateSerializer


class SeatStateView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = SeatStateSerializer
    
    def get(self, request):
        seats = Seat.objects.all()
        serializer = self.serializer_class(seats, many=True)
        
        return CustomResponse(
            valid=True,
            msg="Seat state fetched successfully",
            data=serializer.data
        )
    

class BookSeatView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        return CustomResponse(
            valid=True,
            msg="Seat booked successfully",
        )