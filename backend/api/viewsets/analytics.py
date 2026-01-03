from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Sum, F, Q
from games.models import Game
from stats.models import FootballTeamGameStat, FootballPlayerGameStat


class AnalyticsViewSet(viewsets.ViewSet):
    """
    GET API --> Recent team statistics over last N games
    Query params: 'team_id' (required), 'games' (default=3)
    """
    @action(detail=False, methods=['get'], url_path='recent-stats')
    def recent_stats(self, request):
        # query params
        team_id = request.query_params.get('team_id')
        num_games = int(request.query_params.get('games', 3))
        
        if not team_id:
            return Response({'Error': '\'team_id\' is required'}, status=400)
        
        # the actual query to the 'FootballTeamGameStat' table
        query = FootballTeamGameStat.objects.filter(team_id=team_id)
        
        stats = query.order_by('-game__date')[:num_games]
        
        # get all past stats
        past_stats = stats.aggregate(
            # passing
            pass_att=Avg('pass_attempts'),
            pass_yds=Avg('pass_yards'),
            pass_tds=Avg('pass_touchdowns'),
            completion_pct=Avg(F('pass_completions') / F('pass_attempts')),

            # rushing
            rush_att=Avg('rush_attempts'),
            rush_yds=Avg('rush_yards'),
            rush_tds=Avg('rush_touchdowns'),

            # total yds
            total_yards=Avg(F('rush_yards') + F('pass_yards')),

            # offensive turnovers
            off_turnovers_total=Sum(F('interceptions') + F('fumbles_lost')),

            # defensive turnovers
            def_turnovers_total=Sum(F('def_interceptions') + F('def_fumbles_forced'))
        )
        
        # get the team's 'points' from the Game model (home or away)
        games_data = []
        for stat in stats:
            game = stat.game
            
            if game.home_team_id == int(team_id):
                points = game.home_score
            else:
                points = game.away_score
            games_data.append(points)
        
        # get total points scored avg
        points_avg = sum(games_data) / len(games_data) if games_data else 0
        
        return Response({
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
        })
    

    """
    GET --> Yards allowed by specific position group over last N games
    Query params: 'team_id' (required), 'games' (default=3), 'position' (default='RB')
    """
    @action(detail=False, methods=['get'], url_path='defense-allowed')
    def defense_allowed(self, request):
        # TODO can't go over finished games

        team_id = request.query_params.get('team_id')
        num_games = int(request.query_params.get('games', 3))
        position = request.query_params.get('position', 'RB')
        
        if not team_id:
            return Response({'Error': '\'team_id\' is required'}, status=400)
        
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
            # rush_yds_avg=Avg(F('rush_yards')/F('rush_attempts')) or 0,
            rush_tds=Sum('rush_touchdowns'),

            # receiving
            targets=Sum('targets'),
            rec_receptions=Sum('receptions'),
            rec_yds=Sum('receiving_yards'),
            # rec_yds_avg=Avg(F('receiving_yards')/F('receptions')) or 0,
            rec_tds=Sum('receiving_touchdowns'),

            fantasy_pts=Sum('fantasy_points_ppr'),
            total_yards_allowed=Sum(F('rush_yards') + F('receiving_yards')),
        )
        
        return Response({
            'team_id': team_id,
            'position': position,
            'rushing': {
                'attempts': round(aggregate_stats['rush_att']/num_games or 0, 2),
                'yards': round(aggregate_stats['rush_yds']/num_games or 0, 2),
                # 'avg': round(aggregate_stats['rush_yds_avg'] or 0, 2),
                'touchdowns': round(aggregate_stats['rush_tds']/num_games or 0, 2),
            },
            'receiving': {
                'targets': round(aggregate_stats['targets']/num_games or 0, 2),
                'receptions': round(aggregate_stats['rec_receptions']/num_games or 0, 2),
                'yards': round(aggregate_stats['rec_yds']/num_games or 0, 2),
                # 'avg': round(aggregate_stats['rec_yds_avg'] or 0, 2),
                'touchdowns': round(aggregate_stats['rec_tds']/num_games or 0, 2),
            },
            'fantasy_points': round(aggregate_stats['fantasy_pts']/num_games or 0, 2),
            'total_yards_allowed': round(aggregate_stats['total_yards_allowed']/num_games or 0, 2),
        })