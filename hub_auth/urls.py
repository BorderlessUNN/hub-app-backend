"""
URL configuration for hub_auth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from hub_auth.views import HomeView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny


api_version_prefix = 'api/v1/'

urlpatterns = [
    path(
        api_version_prefix + 'schema/',
        SpectacularAPIView.as_view(
            permission_classes=[AllowAny],
            authentication_classes=[],
        ),
        name='schema'
    ),
    path(
        api_version_prefix + 'docs/',
        SpectacularSwaggerView.as_view(
            permission_classes=[AllowAny],
            authentication_classes=[],
            url_name='schema'
        ),
        name='swagger-ui'
    ),
    path(api_version_prefix + '', HomeView.as_view(), name='home'),
    path(api_version_prefix + 'admin/', include('accounts.urls.admin_urls')),
    path(api_version_prefix + 'member/', include('accounts.urls.member_urls')),
    path(api_version_prefix + 'user/', include('user.urls')),
]
