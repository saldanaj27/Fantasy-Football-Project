from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

router = DefaultRouter()

router.register(r'users', views.UserViewSet, basename='user')
router.register(r'userteams', views.UserTeamViewSet, basename='userteam')
router.register(r'players', views.PlayerViewSet, basename='player')
router.register(r'userplayers', views.UserPlayerViewSet, basename='userplayer')
router.register(r'games', views.GameViewSet, basename='game')
router.register(r'usergames', views.UserGameViewSet, basename='usergame')
router.register(r'stats', views.PlayerStatViewSet, basename='stat')

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/jwt/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/jwt/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]