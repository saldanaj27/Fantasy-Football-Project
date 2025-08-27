from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from teams.models import Team
from players.models import Player
from games.models import Game

class User(AbstractUser):
    # ill add some more fields in the future
    pass
