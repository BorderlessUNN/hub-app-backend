from django.urls import path
from accounts.views import CreateMemberView, UserExistsView, SetPasswordView, CheckIfUserHasPasswordView, MemberLoginView, MemberListView
from accounts.import_views import (
    MemberImportTemplateView,
    MemberImportPreviewView,
    MemberImportConfirmView,
)

urlpatterns = [
    path('create/', CreateMemberView.as_view(), name='create-user'),
    path('list/', MemberListView.as_view(), name='member-list'),
    path('record/exists/', UserExistsView.as_view(), name='user_exists'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('check-if-member-has-password/', CheckIfUserHasPasswordView.as_view(), name='check-if-member-has-password'),
    path('login/', MemberLoginView.as_view(), name='member-login'),
    path('import/template/', MemberImportTemplateView.as_view(), name='member-import-template'),
    path('import/preview/', MemberImportPreviewView.as_view(), name='member-import-preview'),
    path('import/confirm/', MemberImportConfirmView.as_view(), name='member-import-confirm'),
    # path('users/', CustomUserView.as_view(), name='users'),
]
