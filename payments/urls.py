from django.urls import path
from payments.views import ConfirmPaymentView, PaymentPlansView

urlpatterns = [
    path('plans/', PaymentPlansView.as_view(), name='payment-plans'),
    path('confirm/', ConfirmPaymentView.as_view(), name='confirm-payment')
]