from django.urls import path
from dashboard.reports import (
    PaymentsReportView,
    UsersByStatusReportView,
    DailyCheckinsReportView,
)

urlpatterns = [
    path('payments/', PaymentsReportView.as_view(), name='report-payments'),
    path('users-by-status/', UsersByStatusReportView.as_view(), name='report-users-by-status'),
    path('daily-checkins/', DailyCheckinsReportView.as_view(), name='report-daily-checkins'),
]
