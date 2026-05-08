from django.urls import path

from check_in.views import CheckInViewSet, NonMemberCheckOutView

urlpatterns = [
    path(
        "check-in/",
        CheckInViewSet.as_view({"get": "list", "post": "create"}),
        name="check-in",
    ),
    path(
        "check-in/<uuid:pk>/",
        CheckInViewSet.as_view({'get': 'retrieve', 'post': 'create'}),
        name="check-in-detail",
    ),
    path('non_member/check-out/', NonMemberCheckOutView.as_view(), name='non-member-check-out'),
]