from django.utils import timezone
from django.db.models import Avg, Sum, Q, F
from django.core.cache import cache
from django.conf import settings
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
    PlayerBasicSerializer,
    GameSerializer,
)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def get_queryset(self):
        qs = super().get_queryset().select_related('team')

        # Filter by search query (name)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)

        # Filter by position
        position = self.request.query_params.get('position')
        if position:
            qs = qs.filter(position=position)

        # Filter by team
        team = self.request.query_params.get('team')
        if team:
            qs = qs.filter(team__abbreviation=team)

        # Filter by status (default to active players)
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        else:
            # Default to active players only
            qs = qs.filter(status='ACT')

        return qs.order_by('name')

    @action(detail=False, methods=['get'], url_path='search')
    def search_with_stats(self, request):
        """
        Search players with their recent fantasy stats
        Query params: search, position, team, games (default=3), limit (default=50)
        """
        search = request.query_params.get('search', '')
        position = request.query_params.get('position')
        team = request.query_params.get('team')
        num_games = int(request.query_params.get('games', 3))
        limit = int(request.query_params.get('limit', 50))

        # Build cache key
        cache_key = f'player_search_{search}_{position}_{team}_{num_games}_{limit}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Base queryset - only fantasy-relevant positions
        qs = Player.objects.filter(
            status='ACT',
            position__in=['QB', 'RB', 'WR', 'TE']
        ).select_related('team')

        if search:
            qs = qs.filter(name__icontains=search)
        if position:
            qs = qs.filter(position=position)
        if team:
            qs = qs.filter(team__abbreviation=team)

        # Get player IDs
        player_ids = list(qs.values_list('id', flat=True)[:limit * 2])

        # Get recent stats for these players
        stats = (FootballPlayerGameStat.objects
            .filter(player_id__in=player_ids)
            .values('player_id')
            .annotate(
                avg_fantasy_points=Avg('fantasy_points_ppr'),
                total_fantasy_points=Sum('fantasy_points_ppr'),
                games_played=Sum(1),
                avg_targets=Avg('targets'),
                avg_receptions=Avg('receptions'),
                avg_receiving_yards=Avg('receiving_yards'),
                avg_rush_attempts=Avg('rush_attempts'),
                avg_rush_yards=Avg('rush_yards'),
                avg_pass_yards=Avg('pass_yards'),
            ))

        # Create a lookup dict for stats
        stats_lookup = {s['player_id']: s for s in stats}

        # Build response
        players_data = []
        for player in qs[:limit]:
            player_stats = stats_lookup.get(player.id, {})
            players_data.append({
                'id': player.id,
                'name': player.name,
                'position': player.position,
                'team': player.team.abbreviation if player.team else None,
                'team_name': player.team.name if player.team else None,
                'image_url': player.image_url,
                'status': player.status,
                'stats': {
                    'avg_fantasy_points': round(player_stats.get('avg_fantasy_points') or 0, 1),
                    'total_fantasy_points': round(player_stats.get('total_fantasy_points') or 0, 1),
                    'games_played': player_stats.get('games_played') or 0,
                    'avg_targets': round(player_stats.get('avg_targets') or 0, 1),
                    'avg_receptions': round(player_stats.get('avg_receptions') or 0, 1),
                    'avg_receiving_yards': round(player_stats.get('avg_receiving_yards') or 0, 1),
                    'avg_rush_attempts': round(player_stats.get('avg_rush_attempts') or 0, 1),
                    'avg_rush_yards': round(player_stats.get('avg_rush_yards') or 0, 1),
                    'avg_pass_yards': round(player_stats.get('avg_pass_yards') or 0, 1),
                }
            })

        # Sort by average fantasy points descending
        players_data.sort(key=lambda x: x['stats']['avg_fantasy_points'], reverse=True)

        response_data = {
            'count': len(players_data),
            'players': players_data
        }

        # Cache for 5 minutes
        cache.set(cache_key, response_data, 300)

        return Response(response_data)

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
    @action(detail=False, methods=['get'], url_path='currentWeek')
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
