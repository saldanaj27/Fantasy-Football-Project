from django.db import models
from players.models import Player
from games.models import Game
from teams.models import Team

class FootballPlayerGameStat(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_id')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='player_game_id')

    rush_attempts = models.PositiveIntegerField(default=0)
    rush_yards = models.IntegerField(default=0)
    rush_touchdowns = models.PositiveIntegerField(default=0)
    fumbles = models.PositiveIntegerField(default=0)

    pass_yards = models.IntegerField(default=0)
    pass_attempts = models.PositiveIntegerField(default=0)
    pass_completions = models.PositiveIntegerField(default=0)
    pass_touchdowns = models.PositiveIntegerField(default=0)
    interceptions = models.PositiveIntegerField(default=0)
    sacks = models.PositiveIntegerField(default=0)
    sack_yards_loss = models.IntegerField(default=0) # counts against pass yds (NFL)

    targets = models.PositiveIntegerField(default=0)
    receptions = models.PositiveIntegerField(default=0)
    receiving_yards = models.IntegerField(default=0)
    receiving_touchdowns = models.IntegerField(default=0)

    two_pt = models.PositiveIntegerField(default=0)

    fantasy_points_ppr = models.FloatField(default=0.0)
    
    # completion_pct @property

    def __str__(self):
        return f"{self.player} - {self.game}"

class FootballTeamGameStat(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_id')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='team_game_id')
    
    pass_attempts = models.PositiveIntegerField(default=0)
    pass_completions = models.PositiveIntegerField(default=0)
    pass_yards = models.IntegerField(default=0)
    pass_touchdowns = models.PositiveIntegerField(default=0)

    rush_attempts = models.PositiveIntegerField(default=0)
    rush_yards = models.IntegerField(default=0)
    rush_touchdowns = models.PositiveIntegerField(default=0)

    interceptions = models.PositiveIntegerField(default=0)
    sacks = models.PositiveIntegerField(default=0)
    fumbles = models.PositiveIntegerField(default=0)
    fumbles_lost = models.PositiveIntegerField(default=0)

    targets = models.PositiveIntegerField(default=0)
    receptions = models.PositiveIntegerField(default=0)
    receiving_yards = models.IntegerField(default=0)
    receiving_touchdowns = models.IntegerField(default=0)

    special_teams_touchdowns = models.PositiveIntegerField(default=0)
    def_tackles_for_loss = models.PositiveIntegerField(default=0)
    def_fumbles_forced = models.PositiveIntegerField(default=0)
    def_sacks = models.PositiveIntegerField(default=0)
    def_qb_hits = models.PositiveIntegerField(default=0)
    def_interceptions = models.PositiveIntegerField(default=0)
    def_touchdowns = models.PositiveIntegerField(default=0)

    penalties = models.PositiveIntegerField(default=0)
    penalty_yards = models.PositiveIntegerField(default=0)

    fg_attempts = models.PositiveIntegerField(default=0)
    fg_made = models.PositiveIntegerField(default=0)

