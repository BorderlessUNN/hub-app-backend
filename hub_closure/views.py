from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from accounts.permissions import IsAdminUser, IsSuperAdminUser
from helpers.responses import CustomResponse, custom_post_schema
from hub_closure.models import HubClosureDate
from hub_closure.serializers import HubClosureDateSerializer


class HubClosureDateListView(ListAPIView):
    """ List hub closure dates - any admin tier can view. """
    serializer_class = HubClosureDateSerializer
    permission_classes = [IsAdminUser]
    queryset = HubClosureDate.objects.all().order_by('-date')


class HubClosureDateCreateView(APIView):
    """
    Mark a day as closed (Super Admin only). May be added retroactively, up
    to MAX_RETROACTIVE_DAYS days in the past. Any subscription whose open
    window (7-day partial or 30-day active) contains this date is extended
    by one day so the closure doesn't cost the member access time.
    """
    serializer_class = HubClosureDateSerializer
    permission_classes = [IsSuperAdminUser]

    @custom_post_schema(HubClosureDateSerializer, HubClosureDateSerializer, status_code=201)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        closure = serializer.save()
        return CustomResponse(
            valid=True,
            msg="Hub closure date added successfully",
            status=201,
            data=self.serializer_class(closure).data
        )


class HubClosureDateDeleteView(APIView):
    """ Remove a closure date entry (Super Admin only). """
    permission_classes = [IsSuperAdminUser]

    def delete(self, request, pk):
        try:
            closure = HubClosureDate.objects.get(id=pk)
        except HubClosureDate.DoesNotExist:
            return CustomResponse(valid=False, msg="Closure date not found", status=404)
        closure.delete()
        return CustomResponse(valid=True, msg="Closure date removed successfully")
