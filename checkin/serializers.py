from rest_framework import serializers

class CheckInSerializer(serializers.Serializer):
    email = serializers.EmailField()