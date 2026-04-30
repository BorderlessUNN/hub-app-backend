from django.urls import path
from accounts.views import MeView, LogoutView, AccessTokenView

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', AccessTokenView.as_view(), name='refresh_token')
]