from django.urls import path
from .views import (
  RegisterAPIView,
  LoginAPIView,
  GoogleLoginView,
  UserProfileView,
)

urlpatterns = [
    path('api/register/',RegisterAPIView.as_view(), name='user_register'),
    path('api/login/', LoginAPIView.as_view(), name='user_login'),
    path('api/google-login/', GoogleLoginView.as_view(), name='google_login'),
    path('api/profile/', UserProfileView.as_view(), name='user_profile'),
]