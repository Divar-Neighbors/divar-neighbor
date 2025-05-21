from django.urls import path
from . import views

urlpatterns = [
    path('api/register-provider/', views.register_provider),
    path('api/request-service/', views.request_service),
]