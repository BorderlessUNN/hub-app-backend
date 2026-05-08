from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsAdminUser
from check_in.filters import CheckInFilter
from check_in.models import CheckIn
from check_in.serializers import (
    CheckInResponseSerializer,
    CheckInSerializer,
    NonMemberCheckOutSerializer,
)
from helpers.responses import CustomResponse, custom_post_schema


class CheckInViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = CheckIn.objects.all()

    filter_backends = [DjangoFilterBackend]
    filterset_class = CheckInFilter

    def get_serializer_class(self):
        if self.action == "create":
            return CheckInSerializer
        return CheckInResponseSerializer

    @custom_post_schema(CheckInSerializer, CheckInResponseSerializer, status_code=200)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return CustomResponse(
            valid=True,
            msg="Check-in successful",
            data=CheckInResponseSerializer(serializer.instance).data,
        )

class NonMemberCheckOutView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = NonMemberCheckOutSerializer
    @custom_post_schema(NonMemberCheckOutSerializer, CheckInResponseSerializer, status_code=200)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return CustomResponse(
            valid=True,
            msg="Check-out successful",
            data=CheckInResponseSerializer(serializer.instance).data,
        )
