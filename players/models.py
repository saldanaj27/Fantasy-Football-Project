from django.db import models
from teams.models import Team
from django.conf import settings

class Player(models.Model):
    POSITION_CHOICES = [
        ("QB", "Quarterback"),
        ("RB", "Running Back"),
        ("WR", "Wide Receiver"),
        ("TE", "Tight End"),
        ("K", "Kicker"),
        ("DEF", "Defense"),
    ]
    
    name = models.CharField(max_length=100)
    number = models.IntegerField(default=0)
    college = models.CharField(max_length=100)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.position})"
    
# class UserPlayer(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     player = models.ForeignKey(Player, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ("user", "player")