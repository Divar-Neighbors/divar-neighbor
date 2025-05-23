from django.urls import path
from . import views

urlpatterns = [
    path('api/register-provider/', views.register_provider),
    path('api/request-service/', views.start_request_with_oauth),
    path('oauth/callback/', views.oauth_callback),
]
