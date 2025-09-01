from rest_framework import viewsets, generics, permissions
from django.contrib.auth import get_user_model
from teams.models import Team
from players.models import Player
from games.models import Game
from users.models import User
from stats.models import FootballPlayerGameStat
from .serializers import (
    TeamSerializer,
    PlayerSerializer,
    GameSerializer,
    FootballPlayerGameStatSerializer,
    UserSerializer,
    RegisterSerializer,
)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]