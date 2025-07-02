from django.urls import path
from seats.views import ( 
    SeatStateView,
    BookSeatView,
    CheckoutSeatView
)

urlpatterns = [
    path('state/', SeatStateView.as_view(), name='seat_state'),
    path('book/', BookSeatView.as_view(), name='book_seat'),
    path('checkout/', CheckoutSeatView.as_view(), name='checkout')
]