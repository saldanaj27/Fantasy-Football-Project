from rest_framework import viewsets
from teams.models import Team
from players.models import Player
from games.models import Game
from stats.models import FootballPlayerGameStat
from .serializers import (
    TeamSerializer,
    PlayerSerializer,
    GameSerializer,
    FootballPlayerGameStatSerializer,
)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class PlayerStatViewSet(viewsets.ModelViewSet):
    queryset = FootballPlayerGameStat.objects.all()
    serializer_class = FootballPlayerGameStatSerializer