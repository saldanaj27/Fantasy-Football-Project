from django.db import models
from teams.models import Team
from django.conf import settings

class Game(models.Model): 
    STATUS_CHOICES = [
        ("SCHED", "Scheduled"),
        ("INPROG", "InProgress"),
        ("FINAL", "Final"),
        ("SUSP", "Suspended"),
        ("POST", "Postponed"),
        ("DELAY", "Delayed"),
        ("CANCEL", "Canceled"),
        ("FORF", "Forfeit"),
    ]
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_games')
    date = models.DateTimeField()
    week = models.IntegerField(default=0)
    season = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.away_team} @ {self.home_team} - Week {self.week}"
    
class UserGame(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "game")