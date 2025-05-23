from django.urls import path
from . import views

urlpatterns = [
    path('api/send-message/', views.send_message),
    path('api/get-messages/', views.get_messages),
]