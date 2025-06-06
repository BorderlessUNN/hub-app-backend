from rest_framework import serializers
from accounts.models import CustomUser
from django.utils import timezone

class MemberCheckInSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.lower()
        try:
            self.member = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No registered member found with this email.")
        return value

    def validate(self, attrs):
        # Check if already checked in today
        last_checkin = self.member.last_checkin
        if last_checkin and last_checkin.date() == timezone.now().date():
            raise serializers.ValidationError(f"{self.member.user_name} has already been checked in today.")
        return attrs

    def save(self):
        self.member.last_checkin = timezone.now()
        self.member.save(update_fields=["last_checkin"])
        return {
            "id": self.member.id,
            "name": self.member.user_name,
            "email": self.member.email,
            "last_checkin": self.member.last_checkin
        }