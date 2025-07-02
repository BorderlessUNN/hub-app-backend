from django.urls import path
from user.views import UserExistsView

urlpatterns = [
    path('exists/', UserExistsView.as_view(), name='user_exists'),
]
