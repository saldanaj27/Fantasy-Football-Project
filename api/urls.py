from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'users', views.UserViewSet, basename='user')
router.register(r'teams', views.TeamViewSet, basename='team')
router.register(r'players', views.PlayerViewSet, basename='player')
router.register(r'games', views.GameViewSet, basename='game')
router.register(r'stats', views.PlayerStatViewSet, basename='stat')

urlpatterns = [
    path("", include(router.urls)),
]