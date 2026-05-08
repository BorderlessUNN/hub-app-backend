from django.urls import path
from payments.views import ConfirmPaymentView, PaymentWebhookView, VerifyPaymentView, PaymentView

urlpatterns = [
    path('confirm/', ConfirmPaymentView.as_view(), name='confirm-payment'),
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('payment/', PaymentView.as_view(), name='payment'),
]