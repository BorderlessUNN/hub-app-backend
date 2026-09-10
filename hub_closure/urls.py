from django.urls import path
from hub_closure.views import (
    HubClosureDateListView,
    HubClosureDateCreateView,
    HubClosureDateDeleteView,
)

urlpatterns = [
    path('dates/', HubClosureDateListView.as_view(), name='hub-closure-list'),
    path('dates/create/', HubClosureDateCreateView.as_view(), name='hub-closure-create'),
    path('dates/<uuid:pk>/', HubClosureDateDeleteView.as_view(), name='hub-closure-delete'),
]
