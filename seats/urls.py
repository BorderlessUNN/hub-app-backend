from django.urls import path
from seats.views import SeatStateView

urlpatterns = [
    path('state/', SeatStateView.as_view(), name='seat_state')
]