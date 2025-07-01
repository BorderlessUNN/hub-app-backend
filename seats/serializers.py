from django.utils import timezone
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from helpers.exceptions import CustomValidationException
from accounts.models import CustomUser
from payments.models import Payment
from seats.models import Seat, SeatBookings


class SeatStateSerializer(serializers.ModelSerializer):
    is_taken = serializers.SerializerMethodField()
    
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'is_taken']
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_taken(self, obj):
        return obj.is_booked
    

class BookSeatSerializer(serializers.Serializer):
    seat_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    
    class Meta:
        fields = ['seat_id', 'user_id']

    def validate(self, attrs):
        seat_id = attrs.get('seat_id')
        user_id = attrs.get('user_id')

        try:
            self.seat = Seat.objects.get(id=seat_id)
            self.user =CustomUser.objects.get(id=user_id)

            if not self.user.is_member:
                payment = Payment.objects.filter(user=self.user).first()
                if not payment or payment.is_expired:
                    raise CustomValidationException('User does not have an active payment', code=403)
            
            if self.seat.is_booked:
                raise CustomValidationException("Seat is already booked", code=409)
        except Seat.DoesNotExist:
            raise CustomValidationException("Seat does not exist", code=404)
        except CustomUser.DoesNotExist:
            raise CustomValidationException("User does not exist", code=404)
        return attrs

    def book_seat(self):     
        self.is_valid(raise_exception=True)
        SeatBookings.objects.create(
            seat=self.seat,
            user=self.user,
            is_active=True
        )
        self.seat.is_booked = True
        self.seat.save()


class CheckoutSeatSerializer(serializers.Serializer):
    seat_id = serializers.UUIDField()

    def validate(self, attrs):
        seat_id = attrs.get('seat_id')
        
        try:
            self.seat = Seat.objects.get(id=seat_id)
            self.seat_booking = SeatBookings.objects.filter(seat=self.seat, is_active=True).first()
            if not self.seat.is_booked:
                raise CustomValidationException("Seat is not booked")
        except Seat.DoesNotExist:
            raise CustomValidationException("Seat does not exist", code=404)
        return attrs
    
    def checkout(self):
        self.seat_booking.checkout_at = timezone.now()
        self.seat_booking.is_active = False
        self.seat.is_booked = False
        self.seat_booking.save()
        self.seat.save()