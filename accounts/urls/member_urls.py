from django.urls import path
from accounts.views import CreateMemberView, UserExistsView, SetPasswordView, CheckIfUserHasPasswordView, MemberLoginView

urlpatterns = [
    path('create/', CreateMemberView.as_view(), name='create-user'),
    path('record/exists/', UserExistsView.as_view(), name='user_exists'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('check-if-member-has-password/', CheckIfUserHasPasswordView.as_view(), name='check-if-member-has-password'),
    path('login/', MemberLoginView.as_view(), name='member-login'),
    # path('users/', CustomUserView.as_view(), name='users'),
]
