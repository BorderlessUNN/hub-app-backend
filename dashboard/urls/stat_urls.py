from django.urls import path
from ..views import ( 
    CheckInStatsView,
    UserStatsView
)

urlpatterns = [
    path('checkins/', CheckInStatsView.as_view(), name='check_in_stats'),
    path('users/', UserStatsView.as_view(), name='user_stats'),
]