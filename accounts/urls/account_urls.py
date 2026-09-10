from django.urls import path
from accounts.views import AccountSearchView

urlpatterns = [
    path('search/', AccountSearchView.as_view(), name='account_search'),
]
