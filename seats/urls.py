from django.urls import path
from seats.views import SeatView

urlpatterns = [
    path('', SeatView.as_view(), name='seat'),
]