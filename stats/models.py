from django.db import models
from players.models import Player
from games.models import Game

class FootballPlayerGameStat(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="game_stats")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="player_stats")

    rush_attempts = models.PositiveIntegerField(default=0)
    rush_yards = models.IntegerField(default=0)
    rushing_touchdowns = models.PositiveIntegerField(default=0)
    fumbles = models.PositiveIntegerField(default=0)

    pass_yards = models.IntegerField(default=0)
    pass_completions = models.PositiveIntegerField(default=0)
    pass_attempts = models.PositiveIntegerField(default=0)
    sacks = models.PositiveIntegerField(default=0)
    passing_touchdowns = models.PositiveIntegerField(default=0)
    interceptions = models.PositiveIntegerField(default=0)

    targets = models.PositiveIntegerField(default=0)
    receptions = models.PositiveIntegerField(default=0)
    receiving_yards = models.IntegerField(default=0)
    receiving_touchdowns = models.IntegerField(default=0)

    two_pt = models.PositiveIntegerField(default=0)
    
    # completion_pct + fantasy_points could be @property

    def __str__(self):
        return f"{self.player} - {self.game}"
