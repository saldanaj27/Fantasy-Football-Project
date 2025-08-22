from django.db import models
from teams.models import Team

class Game(models.Model): 
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_games')
    date = models.DateTimeField()
    week = models.IntegerField(default=0)
    season = models.IntegerField(default=0)
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.away_team} @ {self.home_team} - Week {self.week}"