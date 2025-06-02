from rest_framework import serializers
from .models import Guest

class CheckInSerializer(serializers.Serializer):
    email = serializers.EmailField()

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['email', 'name', 'phone']

class SeatBookingSerializer(serializers.Serializer):
    email = serializers.EmailField()
    seat_number = serializers.CharField()
