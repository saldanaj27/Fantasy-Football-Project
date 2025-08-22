from django.db import models
from teams.models import Team

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
    position = models.CharField(max_length=10)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.position})"