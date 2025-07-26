# airdrop/urls.py
from django.urls import path,include
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', RegisterView.as_view(), name='register'),
    path('/?reff=<str:referred_by>', RegisterView.as_view(), name='register'),
    path('login/', login, name='login'),
    path('export-csv/<str:wallet>', ExportCSVView.as_view()),
    path("auth/google/callback/", SocialAuthCallbackView.as_view()),
    ]
