from rest_framework.views import APIView
from helpers.responses import CustomResponse
from django.db import transaction

from accounts.permissions import IsAdminUser
from seats.models import Seat
from seats.serializers import SeatStateSerializer, BookSeatSerializer, CheckoutSeatSerializer


class SeatStateView(APIView):
    """
    API view for fetching seat state
    """
    permission_classes = [IsAdminUser]
    serializer_class = SeatStateSerializer
    
    @transaction.atomic
    def get(self, request):
        seats = Seat.objects.all()
        serializer = self.serializer_class(seats, many=True)
        
        return CustomResponse(
            valid=True,
            msg="Seat state fetched successfully",
            data=serializer.data
        )
    

class BookSeatView(APIView):
    """
    API view for booking a seat
    """
    permission_classes = [IsAdminUser]
    serializer_class = BookSeatSerializer

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.book_seat()
        return CustomResponse(
            valid=True,
            msg="Seat booked successfully",
        )
    

class CheckoutSeatView(APIView):
    """
    API view for checking out a seat
    """
    permission_classes = [IsAdminUser]
    serializer_class = CheckoutSeatSerializer

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.checkout()
        return CustomResponse(
            valid=True,
            msg="Seat checkout successful",
            status=200
        )