from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from teams.models import Team
from players.models import Player
from games.models import Game

class User(AbstractUser):
    # ill add some more fields in the future
    pass

User = settings.AUTH_USER_MODEL

class UserTeam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_teams")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ("user", "team")

class UserPlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_players")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ("user", "player")

class UserGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_games")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ("user", "game")