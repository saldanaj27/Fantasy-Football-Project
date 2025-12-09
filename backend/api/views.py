from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
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

    # add filtering logic for 'week' and 'season' to query
    def get_queryset(self):
        qs = super().get_queryset()

        week = self.request.query_params.get('week')
        season = self.request.query_params.get('season')

        if week:
            qs = qs.filter(week=week)

        if season:
            qs = qs.filter(season=season)
        
        return qs
    
    # path to get current week (/current_week)
    @action(detail=False, methods=['get'])
    def current_week(self, request):
        today = timezone.now().date()

        # find nearest game and use its week
        upcoming = Game.objects.filter(date__gte=today).order_by('date').first()
        if not upcoming:
            return Response([])
        
        week = upcoming.week
        season = upcoming.season

        games = Game.objects.filter(week=week, season=season)
        serializer = self.get_serializer(games, many=True)
        
        return Response(serializer.data)


class PlayerStatViewSet(viewsets.ModelViewSet):
    queryset = FootballPlayerGameStat.objects.all()
    serializer_class = FootballPlayerGameStatSerializer