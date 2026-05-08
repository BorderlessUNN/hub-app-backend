from django.urls import path
from payments.views import PaymentPlansView

urlpatterns = [
    path('plans/', PaymentPlansView.as_view(), name='payment-plans'),
]