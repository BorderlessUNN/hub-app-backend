from django.urls import path
from accounts.views import CaptureNonMemberDataView

urlpatterns = [
    path('data/capture/', CaptureNonMemberDataView.as_view(), name='capture-non-member-data')
]
