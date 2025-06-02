from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Member, Guest
from .serializers import CheckInSerializer, GuestSerializer


class UserCheckinView(APIView):
    """
    This is the api view for user check-in.
    It checks if the user is a member or a guest.
    If the user is a member, it returns a success message.
    If the user is not a member, it returns a not found message.    """
    def post(self, request):
        serializer = CheckInSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            if Member.objects.filter(email=email).exists():
                return Response({"message": "Is member"}, status=200)
            return Response({"message": "Not a member"}, status=404)
        return Response(serializer.errors, status=400)
    
class GuestRegisterView(APIView):
    """
    This is the api view for guest registration.
    It allows guests to register by providing their email, name, and phone number.
    If the guest already exists, it updates their information.
    """
    def post(self, request):
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            guest, created = Guest.objects.update_or_create(
                email=serializer.validated_data['email'],
                defaults={
                    'name': serializer.validated_data['name'],
                    'phone': serializer.validated_data['phone'],
                    'payment_confirmed': False
                }
            )
            return Response({"message": "Guest registered. Proceed to payment."}, status=200)
        return Response(serializer.errors, status=400)
