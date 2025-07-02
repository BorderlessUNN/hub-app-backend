from django.urls import path
from checkin.views import MemberCheckInView, GuestCheckInView

urlpatterns = [
    path('member/', MemberCheckInView.as_view(), name='member_checkin'),
    path('guest/', GuestCheckInView.as_view(), name='guest_checkin'),
]
