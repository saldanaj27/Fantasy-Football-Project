from django.db import models
from .constants import POSITION_CHOICES, DEPTH_CHART_POSITION_CHOICES, STATUS

class Player(models.Model):    
    name = models.CharField(max_length=100)
    depth_chart_position = models.CharField(max_length=25, choices=DEPTH_CHART_POSITION_CHOICES)
    height = models.IntegerField(default=0, null=True)
    weight = models.IntegerField(default=0, null=True)
    position = models.CharField(max_length=25, choices=POSITION_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.position})"
    
# class UserPlayer(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     player = models.ForeignKey(Player, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ("user", "player")