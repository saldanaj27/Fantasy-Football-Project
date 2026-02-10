from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .viewsets import analytics

router = DefaultRouter()

router.register(r'teams', views.TeamViewSet, basename='team')
router.register(r'players', views.PlayerViewSet, basename='player')
router.register(r'games', views.GameViewSet, basename='game')
router.register(r'analytics', analytics.AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path("", include(router.urls)),
    path("predictions/", include('predictions.urls')),
]