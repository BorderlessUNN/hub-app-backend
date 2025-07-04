from django.urls import path
from .views import ( 
    CheckInStatsView,
)

urlpatterns = [
    path('checkins/', CheckInStatsView.as_view(), name='check_in_stats'),
]