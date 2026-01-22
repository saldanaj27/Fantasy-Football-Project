from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Sum, F, Q
from django.core.cache import cache
from django.conf import settings
from games.models import Game
from stats.models import FootballTeamGameStat, FootballPlayerGameStat


class AnalyticsViewSet(viewsets.ViewSet):
    """
    GET API --> Recent team statistics over last N games
    Query params: 'team_id' (required), 'games' (default=3)
    """
    @action(detail=False, methods=['get'], url_path='recent-stats')
    def recent_stats(self, request):
        team_id = request.query_params.get('team_id')
        num_games = int(request.query_params.get('games', 3))
        
        if not team_id:
            return Response({'Error': '\'team_id\' is required'}, status=400)
        
        # coureate cache key
        cache_key = f'recent_stats_{team_id}_{num_games}'
        
        # try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # if not in cache, fetch from database
        query = FootballTeamGameStat.objects.filter(team_id=team_id)
        stats = query.order_by('-game__date')[:num_games]
        
        past_stats = stats.aggregate(
            pass_att=Avg('pass_attempts'),
            pass_yds=Avg('pass_yards'),
            pass_tds=Avg('pass_touchdowns'),
            completion_pct=Avg(F('pass_completions') * 100.0 / F('pass_attempts')),
            rush_att=Avg('rush_attempts'),
            rush_yds=Avg('rush_yards'),
            rush_tds=Avg('rush_touchdowns'),
            total_yards=Avg(F('rush_yards') + F('pass_yards')),
            off_turnovers_total=Sum(F('interceptions') + F('fumbles_lost')),
            def_turnovers_total=Sum(F('def_interceptions') + F('def_fumbles_forced'))
        )
        
        games_data = []
        for stat in stats:
            game = stat.game
            if game.home_team_id == int(team_id):
                points = game.home_score
            else:
                points = game.away_score
            games_data.append(points)
        
        points_avg = sum(games_data) / len(games_data) if games_data else 0
        
        response_data = {
            'team_id': team_id,
            'passing': {
                'attempts': round(past_stats['pass_att'] or 0, 2),
                'total_yards_average': round(past_stats['pass_yds'] or 0, 2),
                'touchdowns': round(past_stats['pass_tds'] or 0, 2),
                'completion_percentage': round(past_stats['completion_pct'] or 0, 2),
            },
            'rushing': {
                'attempts': round(past_stats['rush_att'] or 0, 2),
                'total_yards_average': round(past_stats['rush_yds'] or 0, 2),
                'touchdowns': round(past_stats['rush_tds'] or 0, 2),
            },
            'total_yards_per_game': round(past_stats['total_yards'] or 0, 2),
            'off_turnovers_total': past_stats['off_turnovers_total'] or 0,
            'def_turnovers_total': past_stats['def_turnovers_total'] or 0,
            'points_per_game': round(points_avg, 2),
        }
        
        cache.set(cache_key, response_data, settings.CACHE_TTL['analytics'])
        
        return Response(response_data)
    

    """
    GET --> Yards allowed by specific position group over last N games
    Query params: 'team_id' (required), 'games' (default=3), 'position' (default='RB')
    Supported positions: RB, WR, TE, QB
    """
    @action(detail=False, methods=['get'], url_path='defense-allowed')
    def defense_allowed(self, request):
        # TODO can't go over finished games

        team_id = request.query_params.get('team_id')
        num_games = int(request.query_params.get('games', 3))
        position = request.query_params.get('position', 'RB')
        
        if not team_id:
            return Response({'Error': '\'team_id\' is required'}, status=400)
        
        valid_positions = ['RB', 'WR', 'TE', 'QB']
        if position not in valid_positions:
            return Response({
                'Error': f'Invalid position. Must be one of: {", ".join(valid_positions)}'
            }, status=400)

        # get last N games
        games = (Game.objects
                .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
                .exclude(home_score=None)
                .order_by('-date')[:num_games]
                .values_list('id', flat=True))
        
        # get opponent stats from found games and of the specified position
        opponent_stats = (FootballPlayerGameStat.objects
                         .filter(game_id__in=games)
                         .filter(player__position=position)
                         .exclude(player__team_id=team_id))

        aggregate_stats = opponent_stats.aggregate(
            # rushing
            rush_att=Sum('rush_attempts'),
            rush_yds=Sum('rush_yards'),
            rush_tds=Sum('rush_touchdowns'),

            # receiving (for RB, WR, TE)
            targets=Sum('targets'),
            rec_receptions=Sum('receptions'),
            rec_yds=Sum('receiving_yards'),
            rec_tds=Sum('receiving_touchdowns'),

            # passing (for QB)
            pass_att=Sum('pass_attempts'),
            pass_comp=Sum('pass_completions'),
            pass_yds=Sum('pass_yards'),
            pass_tds=Sum('pass_touchdowns'),
            interceptions=Sum('interceptions'),
            sacks=Sum('sacks'),

            fantasy_pts=Sum('fantasy_points_ppr'),
            total_yards_allowed=Sum(F('rush_yards') + F('receiving_yards') + F('pass_yards')),
        )
        
        
        response_data = {
            'team_id': team_id,
            'position': position,
            'games_analyzed': len(games),
        }
        
        # Add rushing stats (relevant for RB, QB, WR, TE)
        if position in ['RB', 'QB', 'WR', 'TE']:
            response_data['rushing'] = {
                'attempts': round((aggregate_stats['rush_att'] or 0) / num_games, 2),
                'yards': round((aggregate_stats['rush_yds'] or 0) / num_games, 2),
                'touchdowns': round((aggregate_stats['rush_tds'] or 0) / num_games, 2),
            }
        
        # Add receiving stats (relevant for RB, WR, TE)
        if position in ['RB', 'WR', 'TE']:
            response_data['receiving'] = {
                'targets': round((aggregate_stats['targets'] or 0) / num_games, 2),
                'receptions': round((aggregate_stats['rec_receptions'] or 0) / num_games, 2),
                'yards': round((aggregate_stats['rec_yds'] or 0) / num_games, 2),
                'touchdowns': round((aggregate_stats['rec_tds'] or 0) / num_games, 2),
            }
        
        # Add passing stats (relevant for QB)
        if position == 'QB':
            pass_att = aggregate_stats['pass_att'] or 0
            pass_comp = aggregate_stats['pass_comp'] or 0
            completion_pct = (pass_comp / pass_att * 100) if pass_att > 0 else 0
            
            response_data['passing'] = {
                'attempts': round(pass_att / num_games, 2),
                'completions': round(pass_comp / num_games, 2),
                'completion_percentage': round(completion_pct, 2),
                'yards': round((aggregate_stats['pass_yds'] or 0) / num_games, 2),
                'touchdowns': round((aggregate_stats['pass_tds'] or 0) / num_games, 2),
                'interceptions': round((aggregate_stats['interceptions'] or 0) / num_games, 2),
                'sacks': round((aggregate_stats['sacks'] or 0) / num_games, 2),
            }
        
        # Add fantasy points and total yards for all positions
        response_data['fantasy_points'] = round((aggregate_stats['fantasy_pts'] or 0) / num_games, 2)
        response_data['total_yards_allowed'] = round((aggregate_stats['total_yards_allowed'] or 0) / num_games, 2)
        
        return Response(response_data)