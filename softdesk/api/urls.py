from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentification
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Profil utilisateur
    path('auth/profile/', views.user_profile, name='user_profile'),
]
