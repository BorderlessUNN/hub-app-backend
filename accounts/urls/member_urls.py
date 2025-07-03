from django.urls import path
from accounts.views import CreateMemberView, UserExistsView

urlpatterns = [
    path('create/', CreateMemberView.as_view(), name='create-user'),
    path('record/exists/', UserExistsView.as_view(), name='user_exists'),
]
