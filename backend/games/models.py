from django.db import models
from teams.models import Team
from .constants import STAGE_CHOICES

# class Score(models.Model):
#     quarter_1 = models.IntegerField(default=0)
#     quarter_2 = models.IntegerField(default=0)
#     quarter_3 = models.IntegerField(default=0)
#     quarter_4 = models.IntegerField(default=0)
#     overtime = models.IntegerField(default=0)
    
#     @property
#     def total(self):
#         return (
#             self.quarter_1
#             + self.quarter_2
#             + self.quarter_3
#             + self.quarter_4
#             + (self.overtime or 0)
#         )

#     def __str__(self):
#         return f"Total: {self.total}"

class Game(models.Model): 
    id = models.CharField(max_length=20, primary_key=True)
    season = models.IntegerField(default=0)
    week = models.IntegerField(default=0)
    date = models.DateField()
    time = models.CharField(max_length=10, default='00:00')

    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team')
    
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='REG')

    # replace if able to retrieve quarter scores
    # home_score = models.ForeignKey(Score, on_delete=models.CASCADE, related_name='home_score')
    # away_score = models.ForeignKey(Score, on_delete=models.CASCADE, related_name='away_score')

    home_score = models.IntegerField(default=0, null=True)
    away_score = models.IntegerField(default=0, null=True)
    total_score = models.IntegerField(default=0, null=True)
    overtime = models.BooleanField(default=False, null=True)

    location = models.CharField(max_length=15, default='Home')
    roof = models.CharField(max_length=15, default='outdoors')
    temp = models.IntegerField(default=0, null=True)
    wind = models.IntegerField(default=0, null=True)

    def __str__(self):
        return f"{self.away_team} @ {self.home_team} - Week {self.week}"
