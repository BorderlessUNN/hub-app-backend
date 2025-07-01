from rest_framework.views import APIView

from helpers.responses import CustomResponse
from accounts.permissions import IsAdminUser
from payments.models import Plans
from payments.serializers import ConfirmPaymentSerializer, PaymentPlansSerializer


class ConfirmPaymentView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = ConfirmPaymentSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.confirm_payment()     
        return CustomResponse(
            valid=True,
            msg="Payment confirmed successfully",
            data=self.serializer_class(payment).data
        )
    

class PaymentPlansView(APIView):
    serializer_class = PaymentPlansSerializer
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        plans = Plans.objects.all()
        return CustomResponse(
            valid=True,
            msg="Payment plans retrieved successfully",
            data=self.serializer_class(plans, many=True).data
        )