from django.db import models
from teams.models import Team
from django.conf import settings

class Score(models.Model):
    quarter_1 = models.IntegerField(default=0)
    quarter_2 = models.IntegerField(default=0)
    quarter_3 = models.IntegerField(default=0)
    quarter_4 = models.IntegerField(default=0)
    overtime = models.IntegerField(default=0)
    
    @property
    def total(self):
        return (
            self.quarter_1
            + self.quarter_2
            + self.quarter_3
            + self.quarter_4
            + (self.overtime or 0)
        )

    def __str__(self):
        return f"Total: {self.total}"

class Game(models.Model): 
    STATUS_CHOICES = [
        ('NS', 'Not Started'),
        ('Q1', 'First Quarter'),
        ('Q2', 'Second Quarter'),
        ('Q3', 'Third Quarter'),
        ('OT', 'Overtime'),
        ('HT', 'Halftime'),
        ('FT', 'Finished'),
        ('CANC', 'Canceled'),
        ('PST', 'Postponed'),
    ]

    STAGE_CHOICES = [
        ('PRE', 'Pre Season'),
        ('REG', 'Regular Season'),
        ('POST', 'Post Season}'),
    ]

    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_games')
    date = models.DateTimeField()
    week = models.IntegerField(default=0)
    season = models.IntegerField(default=0)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='REG')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NS')
    home_score = models.ForeignKey(Score, on_delete=models.CASCADE, related_name='home_score')
    away_score = models.ForeignKey(Score, on_delete=models.CASCADE, related_name='away_score')

    def __str__(self):
        return f"{self.away_team} @ {self.home_team} - Week {self.week}"

# class UserGame(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     game = models.ForeignKey(Game, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ("user", "game")