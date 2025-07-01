from django.urls import path
from accounts.views import CreateMemberView

urlpatterns = [
    path('create/', CreateMemberView.as_view(), name='create-user'),
]
