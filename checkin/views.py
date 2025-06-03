from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from accounts.models import CustomUser 
from .serializers import CheckInSerializer

class CheckInView(APIView):
    def post(self, request):
        serializer = CheckInSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({"detail": "User with this email not found."}, status=404)

            # Prevent multiple check-ins in one day
            if user.last_checkin and user.last_checkin.date() == timezone.now().date():
                return Response({"detail": "You’ve already checked in today."}, status=400)

            # Update last check-in
            CustomUser.update_last_checkin(user)

            return Response({"detail": f"{user.user_name} checked in successfully."}, status=200)

        return Response(serializer.errors, status=400)
