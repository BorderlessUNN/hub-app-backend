from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from helpers.responses import CustomResponse, custom_post_schema
from accounts.permissions import IsAdminUser
from payments.models import Plans
from payments.serializers import ConfirmPaymentSerializer, PaymentPlansSerializer, PaymentResponseSerializer, VerifyPaymentSerializer
from django.conf import settings
from django.http import HttpResponse
from subscription.models import Subscription
from payments.services import handle_member_success_payment, handle_non_member_success_payment, handle_failed_payment
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiResponse
from payments.models import Payment
import json
import hmac
import hashlib


class ConfirmPaymentView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = ConfirmPaymentSerializer
    
    @custom_post_schema(ConfirmPaymentSerializer, PaymentResponseSerializer, status_code=200)
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
    permission_classes = [IsAuthenticated] 
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get(self, request):
        plans = Plans.objects.all()
        return CustomResponse(
            valid=True,
            msg="Payment plans retrieved successfully",
            data=self.serializer_class(plans, many=True).data
        )

    @custom_post_schema(PaymentPlansSerializer, PaymentPlansSerializer, status_code=200)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.save()
        return CustomResponse(
            valid=True,
            msg="Payment plan created successfully",
            data=self.serializer_class(plan).data
        )


@method_decorator(csrf_exempt, name='dispatch')
class PaymentWebhookView(APIView):
    def post(self, request):
        payload = request.body
        signature = request.headers.get('x-paystack-signature')
        secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')

        computed_hmac = hmac.new(secret, payload, hashlib.sha512).hexdigest()

        if computed_hmac != signature:
            return HttpResponse(status=401) # Unauthorized

        event_data = json.loads(payload)
        data = event_data.get('data', {})
        metadata = data.get('metadata', {})       
        event = event_data.get('event')
        payment_id = metadata.get('payment_id')
        subscription_id = metadata.get('subscription_id')

        payment_reference = data.get('reference')
        payment = Payment.objects.get(id=payment_id)
        print(payment)
        if payment_reference != payment.paystack_reference:
            return HttpResponse(status=200,)

        if event == 'charge.success':
            subscription = Subscription.objects.get(id=subscription_id)
            print(subscription.plan.is_member_only)
            if subscription.plan.is_member_only:
                handle_member_success_payment(subscription_id, payment_id)
            else:
                handle_non_member_success_payment(subscription_id, payment_id)
        elif event == 'charge.failed':
            handle_failed_payment(subscription_id, payment_id)

        return HttpResponse(status=200)

class VerifyPaymentView(APIView):
    serializer_class = VerifyPaymentSerializer
    permission_classes = [AllowAny]
    
    @custom_post_schema(VerifyPaymentSerializer, PaymentResponseSerializer, status_code=200)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        reference = serializer.validated_data.get('reference')
        try:
            payment = Payment.objects.get(paystack_reference=reference)
            if payment.payment_status == Payment.PaymentStatus.SUCCESS:
                return CustomResponse(
                    valid=True,
                    msg="Payment was successfully",
                    data=PaymentResponseSerializer(payment).data
                )
            else:
                return CustomResponse(
                    valid=False,
                    msg="Payment was not successful",
                    data=None
                )
        except Payment.DoesNotExist:
            return CustomResponse(
                valid=False,
                msg="Payment does not exist",
                data=None
            )

    
class PaymentView(APIView):
    serializer_class = PaymentResponseSerializer
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()

    @extend_schema(
        responses={200: OpenApiResponse(response=PaymentResponseSerializer(many=True))},
    )
    def get(self, request):
        payments = Payment.objects.all()
        return CustomResponse(
            valid=True,
            msg="Payments fetched successfully",
            data=self.serializer_class(payments, many=True).data
        )