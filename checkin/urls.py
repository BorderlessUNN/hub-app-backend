from django.urls import path
from checkin.views import MemberCheckInView

urlpatterns = [
    path('member/', MemberCheckInView.as_view(), name='member_checkin'),
]
