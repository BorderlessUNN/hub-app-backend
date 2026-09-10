from django.urls import path
from accounts.views import (
    AdminLoginView,
    AdminListView,
    AdminCreateView,
    AdminDeactivateView,
)

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('list/', AdminListView.as_view(), name='admin_list'),
    path('create/', AdminCreateView.as_view(), name='admin_create'),
    path('deactivate/', AdminDeactivateView.as_view(), name='admin_deactivate'),
]
