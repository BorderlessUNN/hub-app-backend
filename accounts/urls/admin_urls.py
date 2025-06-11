from django.urls import path
from accounts.views import AdminLoginView, AdminAccessTokenView

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('token/refresh/', AdminAccessTokenView.as_view(), name='refresh token')
]
