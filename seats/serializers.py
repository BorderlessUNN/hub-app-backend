from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from seats.models import Seat, SeatBookings


class SeatStateSerializer(serializers.ModelSerializer):
    is_taken = serializers.SerializerMethodField()
    
    class Meta:
        model = Seat
        fields = ['seat_number', 'is_taken']
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_taken(self, obj):
        return SeatBookings.objects.filter(seat=obj, is_active=True).exists()