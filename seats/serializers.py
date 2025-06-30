from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from helpers.exceptions import CustomValidationException
from accounts.models import CustomUser 
from seats.models import Seat, SeatBookings


class SeatStateSerializer(serializers.ModelSerializer):
    is_taken = serializers.SerializerMethodField()
    
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'is_taken']
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_taken(self, obj):
        return SeatBookings.objects.filter(seat=obj, is_active=True).exists()
    

class BookSeatSerializer(serializers.Serializer):
    seat_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    
    class Meta:
        fields = ['seat_id', 'user_id']

    def validate(self, attrs):
        seat_id = attrs.get('seat_id')
        user_id = attrs.get('user_id')

        try:
            seat = Seat.objects.get(id=seat_id)
            CustomUser.objects.get(id=user_id)
            
            if SeatBookings.objects.filter(seat=seat, is_active=True).exists():
                raise CustomValidationException("Seat is already booked")
        except Seat.DoesNotExist:
            raise CustomValidationException("Seat does not exist")
        except CustomUser.DoesNotExist:
            raise CustomValidationException("User does not exist")
        return attrs

    def book_seat(self):
        seat_id = self.validated_data.get('seat_id')
        user_id = self.validated_data.get('user_id')
        seat = Seat.objects.get(id=seat_id)
        user = CustomUser.objects.get(id=user_id)
        SeatBookings.objects.create(
            seat=seat,
            user=user,
            is_active=True
        )