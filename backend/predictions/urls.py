"""
URL routing for prediction API endpoints.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("game/", views.GamePredictionView.as_view(), name="game-prediction"),
    path("week/", views.WeekPredictionsView.as_view(), name="week-predictions"),
    path("model-info/", views.ModelInfoView.as_view(), name="model-info"),
]
