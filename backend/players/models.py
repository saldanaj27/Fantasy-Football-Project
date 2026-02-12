from django.db import models

from teams.models import Team

from .constants import DEPTH_CHART_POSITION_CHOICES, POSITION_CHOICES, STATUS


class Player(models.Model):
    id = models.CharField(max_length=25, primary_key=True)

    name = models.CharField(max_length=100)
    height = models.IntegerField(default=0, null=True)
    weight = models.IntegerField(default=0, null=True)
    image_url = models.URLField(blank=True, null=True)

    depth_chart_position = models.CharField(
        max_length=25, choices=DEPTH_CHART_POSITION_CHOICES
    )
    position = models.CharField(max_length=25, choices=POSITION_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS)

    season = models.IntegerField(default=0000, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name} ({self.position})"
