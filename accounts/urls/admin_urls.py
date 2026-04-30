from django.urls import path
from accounts.views import AdminLoginView

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin_login'),
]
