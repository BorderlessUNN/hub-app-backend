from django.urls import path
from subscription.views import ActiveSubscriptionView, MemberSubscriptionView, NonMemberSubscriptionView, SubscriptionView

urlpatterns = [
    path('active/', ActiveSubscriptionView.as_view(), name='active-subscription'),
    path('member-subscription/', MemberSubscriptionView.as_view(), name='member-subscription'),
    path('non-member-subscription/', NonMemberSubscriptionView.as_view(), name='non-member-subscription'),
    path('subscription/', SubscriptionView.as_view(), name='subscription'),
]