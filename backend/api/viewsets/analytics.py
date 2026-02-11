from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Sum, F, Q, Count
from django.db.models.functions import NullIf
from django.core.cache import cache
from django.conf import settings
from games.models import Game
from stats.models import FootballTeamGameStat, FootballPlayerGameStat
from collections import defaultdict
from players.models import Player
from teams.models import Team
from django.utils import timezone
from api.simulation import SimulationMixin


class AnalyticsViewSet(SimulationMixin, viewsets.ViewSet):
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
        
        # Create cache key
        cache_key = f'recent_stats_{team_id}_{num_games}'
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # If not in cache, fetch from database
        query = FootballTeamGameStat.objects.filter(team_id=team_id)
        stats = query.order_by('-game__date')[:num_games]
        
        # Aggregate stats from query
        past_stats = stats.aggregate(
            # Passing stats
            pass_att=Avg('pass_attempts'),
            pass_yds=Avg('pass_yards'),
            pass_tds=Avg('pass_touchdowns'),
            completion_pct=Avg(F('pass_completions') * 100.0 / NullIf(F('pass_attempts'), 0)),

            # Rushing stats
            rush_att=Avg('rush_attempts'),
            rush_yds=Avg('rush_yards'),
            rush_tds=Avg('rush_touchdowns'),

            # General + Defensive stats
            total_yards=Avg(F('rush_yards') + F('pass_yards')),
            off_turnovers_total=Sum(F('interceptions') + F('fumbles_lost')),
            def_turnovers_total=Sum(F('def_interceptions') + F('def_fumbles_forced'))
        )
        
        # Calculate points per average
        games_data = []
        for stat in stats:
            game = stat.game
            if game.home_team_id == int(team_id):
                points = game.home_score
            else:
                points = game.away_score
            games_data.append(points)
        
        points_avg = sum(games_data) / len(games_data) if games_data else 0
        
        # Initialize response data
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
        
        # Store in cache
        cache.set(cache_key, response_data, settings.CACHE_TTL['analytics'])
        
        return Response(response_data)
    

    """
    GET --> Player Stats (yards, receptions, touchdowns, etc.) allowed by specific position group over last N games
    Query params: 'team_id' (required), 'games' (default=3), 'position' (default='RB')
    Supported positions: RB, WR, TE, QB
    """
    @action(detail=False, methods=['get'], url_path='defense-allowed')
    def defense_allowed(self, request):
        team_id = request.query_params.get('team_id')
        num_games = int(request.query_params.get('games', 3))
        position = request.query_params.get('position', 'RB')
        
        if not team_id:
            return Response({'Error': '\'team_id\' is required'}, status=400)
        
        # Create cache key
        cache_key = f'defense_allowed_{team_id}_{num_games}_{position}'
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # If not in cache, fetch from database
        valid_positions = ['RB', 'WR', 'TE', 'QB']
        if position not in valid_positions:
            return Response({
                'Error': f'Invalid position. Must be one of: {", ".join(valid_positions)}'
            }, status=400)

        # Get game information using params (# of games, position, team)
        games = (Game.objects
                .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
                .exclude(home_score=None)
                .order_by('-date')[:num_games]
                .values_list('id', flat=True))
        
        # Get opponent stats using params
        opponent_stats = (FootballPlayerGameStat.objects
                         .filter(game_id__in=games)
                         .filter(player__position=position)
                         .exclude(player__team_id=team_id))

        # Aggregate stats from query
        aggregate_stats = opponent_stats.aggregate(
            # Rushing stats
            rush_att=Sum('rush_attempts'),
            rush_yds=Sum('rush_yards'),
            rush_tds=Sum('rush_touchdowns'),

            # Receiving stats (for RB, WR, TE)
            targets=Sum('targets'),
            rec_receptions=Sum('receptions'),
            rec_yds=Sum('receiving_yards'),
            rec_tds=Sum('receiving_touchdowns'),

            # Passing stats (for QB)
            pass_att=Sum('pass_attempts'),
            pass_comp=Sum('pass_completions'),
            pass_yds=Sum('pass_yards'),
            pass_tds=Sum('pass_touchdowns'),
            interceptions=Sum('interceptions'),
            sacks=Sum('sacks'),

            # Other stats
            fantasy_pts=Sum('fantasy_points_ppr'),
            total_yards_allowed=Sum(F('rush_yards') + F('receiving_yards') + F('pass_yards')),
        )
        
        # Initialize response data
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

        # Store in cache
        cache.set(cache_key, response_data, settings.CACHE_TTL['analytics'])

        return Response(response_data)

    """
    GET API --> Individual player stats for a team over last N games
    Query params: 'team_id' (required), 'games' (default=3)
    Returns players grouped by position with averaged stats
    """
    @action(detail=False, methods=['get'], url_path='player-stats')
    def player_stats(self, request):
        team_id = request.query_params.get('team_id')
        num_games = int(request.query_params.get('games', 3))

        if not team_id:
            return Response({'Error': '\'team_id\' is required'}, status=400)

        # Create cache key
        cache_key = f'player_stats_{team_id}_{num_games}'

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Get relevant games for this team
        games = (Game.objects
                .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
                .exclude(home_score=None)
                .order_by('-date')[:num_games]
                .values_list('id', flat=True))

        # Get player stats for this team in these games
        player_stats_qs = (FootballPlayerGameStat.objects
            .filter(game_id__in=games, player__team_id=team_id)
            .values(
                'player_id',
                'player__name',
                'player__position'
            )
            .annotate(
                rush_attempts=Avg('rush_attempts'),
                rush_yards=Avg('rush_yards'),
                rush_touchdowns=Avg('rush_touchdowns'),
                targets=Avg('targets'),
                receptions=Avg('receptions'),
                receiving_yards=Avg('receiving_yards'),
                receiving_touchdowns=Avg('receiving_touchdowns'),
                pass_attempts=Avg('pass_attempts'),
                pass_completions=Avg('pass_completions'),
                pass_yards=Avg('pass_yards'),
                pass_touchdowns=Avg('pass_touchdowns'),
                interceptions=Avg('interceptions'),
                sacks=Avg('sacks'),
                fantasy_points=Avg('fantasy_points_ppr'),
                games_played=Count('id'),
                # Advanced metrics
                avg_snap_count=Avg('snap_count'),
                avg_snap_pct=Avg('snap_pct'),
                avg_air_yards=Avg('air_yards'),
                avg_yac=Avg('yards_after_catch'),
            ))

        # Group by position
        grouped = defaultdict(list)
        valid_positions = ['QB', 'RB', 'WR', 'TE']

        for stat in player_stats_qs:
            pos = stat['player__position']
            if pos in valid_positions:
                # Calculate aDOT
                air_yards = stat['avg_air_yards'] or 0
                targets = stat['targets'] or 0
                adot = round(air_yards / targets, 1) if targets > 0 else 0

                grouped[pos].append({
                    'player_id': stat['player_id'],
                    'name': stat['player__name'],
                    'position': pos,
                    'stats': {
                        'rush_attempts': round(stat['rush_attempts'] or 0, 1),
                        'rush_yards': round(stat['rush_yards'] or 0, 1),
                        'rush_touchdowns': round(stat['rush_touchdowns'] or 0, 1),
                        'targets': round(stat['targets'] or 0, 1),
                        'receptions': round(stat['receptions'] or 0, 1),
                        'receiving_yards': round(stat['receiving_yards'] or 0, 1),
                        'receiving_touchdowns': round(stat['receiving_touchdowns'] or 0, 1),
                        'pass_attempts': round(stat['pass_attempts'] or 0, 1),
                        'pass_completions': round(stat['pass_completions'] or 0, 1),
                        'pass_yards': round(stat['pass_yards'] or 0, 1),
                        'pass_touchdowns': round(stat['pass_touchdowns'] or 0, 1),
                        'interceptions': round(stat['interceptions'] or 0, 1),
                        'sacks': round(stat['sacks'] or 0, 1),
                        'fantasy_points_ppr': round(stat['fantasy_points'] or 0, 1),
                        # Advanced metrics
                        'snap_count': round(stat['avg_snap_count'] or 0, 1),
                        'snap_pct': round(stat['avg_snap_pct'] or 0, 1),
                        'air_yards': round(air_yards, 1),
                        'yards_after_catch': round(stat['avg_yac'] or 0, 1),
                        'adot': adot,
                    },
                    'games_played': stat['games_played']
                })

        # Sort each position group by fantasy points descending
        for pos in grouped:
            grouped[pos].sort(key=lambda x: x['stats']['fantasy_points_ppr'], reverse=True)

        # Ensure all positions have an empty list if no players
        players_dict = {pos: grouped.get(pos, []) for pos in valid_positions}

        response_data = {
            'team_id': team_id,
            'games_analyzed': len(games),
            'players': players_dict
        }

        # Store in cache
        cache.set(cache_key, response_data, settings.CACHE_TTL['analytics'])

        return Response(response_data)

    """
    GET API --> Usage metrics for pie charts (target share, carry share, pass/run split)
    Query params: 'team_id' (required), 'games' (default=3)
    """
    @action(detail=False, methods=['get'], url_path='usage-metrics')
    def usage_metrics(self, request):
        team_id = request.query_params.get('team_id')
        num_games = int(request.query_params.get('games', 3))

        if not team_id:
            return Response({'Error': '\'team_id\' is required'}, status=400)

        # Create cache key
        cache_key = f'usage_metrics_{team_id}_{num_games}'

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Get team stats for pass/run split
        team_stats = (FootballTeamGameStat.objects
            .filter(team_id=team_id)
            .order_by('-game__date')[:num_games]
            .aggregate(
                pass_att=Avg('pass_attempts'),
                rush_att=Avg('rush_attempts')
            ))

        total_plays = (team_stats['pass_att'] or 0) + (team_stats['rush_att'] or 0)
        pass_pct = (team_stats['pass_att'] / total_plays * 100) if total_plays > 0 else 0
        rush_pct = (team_stats['rush_att'] / total_plays * 100) if total_plays > 0 else 0

        # Get games for player stats
        games = (Game.objects
            .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
            .exclude(home_score=None)
            .order_by('-date')[:num_games]
            .values_list('id', flat=True))

        # Target share (WR + TE for receivers chart)
        target_stats = (FootballPlayerGameStat.objects
            .filter(game_id__in=games, player__team_id=team_id)
            .filter(player__position__in=['WR', 'TE'])
            .values('player_id', 'player__name', 'player__position')
            .annotate(total_targets=Sum('targets')))

        total_targets = sum(t['total_targets'] or 0 for t in target_stats)
        target_share = []
        for t in target_stats:
            if t['total_targets'] and t['total_targets'] > 0:
                target_share.append({
                    'player_id': t['player_id'],
                    'name': t['player__name'],
                    'position': t['player__position'],
                    'targets': round(t['total_targets'] / num_games, 1),
                    'target_share_percentage': round(t['total_targets'] / total_targets * 100, 1) if total_targets > 0 else 0
                })
        target_share.sort(key=lambda x: x['target_share_percentage'], reverse=True)

        # Carry share (RB only)
        carry_stats = (FootballPlayerGameStat.objects
            .filter(game_id__in=games, player__team_id=team_id)
            .filter(player__position='RB')
            .values('player_id', 'player__name', 'player__position')
            .annotate(total_carries=Sum('rush_attempts')))

        total_carries = sum(c['total_carries'] or 0 for c in carry_stats)
        carry_share = []
        for c in carry_stats:
            if c['total_carries'] and c['total_carries'] > 0:
                carry_share.append({
                    'player_id': c['player_id'],
                    'name': c['player__name'],
                    'position': c['player__position'],
                    'rush_attempts': round(c['total_carries'] / num_games, 1),
                    'carry_share_percentage': round(c['total_carries'] / total_carries * 100, 1) if total_carries > 0 else 0
                })
        carry_share.sort(key=lambda x: x['carry_share_percentage'], reverse=True)

        response_data = {
            'team_id': team_id,
            'games_analyzed': num_games,
            'pass_run_split': {
                'pass_attempts': round(team_stats['pass_att'] or 0, 1),
                'rush_attempts': round(team_stats['rush_att'] or 0, 1),
                'pass_percentage': round(pass_pct, 1),
                'rush_percentage': round(rush_pct, 1)
            },
            'target_share': target_share,
            'carry_share': carry_share
        }

        # Store in cache
        cache.set(cache_key, response_data, settings.CACHE_TTL['analytics'])

        return Response(response_data)

    """
    GET API --> Box score stats for a specific game
    Query params: 'game_id' (required)
    Returns team totals and top performers for a finished game
    """
    @action(detail=False, methods=['get'], url_path='game-box-score')
    def game_box_score(self, request):
        game_id = request.query_params.get('game_id')

        if not game_id:
            return Response({'Error': '\'game_id\' is required'}, status=400)

        # Get the game
        try:
            game = Game.objects.select_related('home_team', 'away_team').get(id=game_id)
        except Game.DoesNotExist:
            return Response({'Error': 'Game not found'}, status=404)

        if game.home_score is None:
            return Response({'Error': 'Game has not been played yet'}, status=400)

        # Get team stats for this game
        home_team_stats = FootballTeamGameStat.objects.filter(
            game_id=game_id, team=game.home_team
        ).first()
        away_team_stats = FootballTeamGameStat.objects.filter(
            game_id=game_id, team=game.away_team
        ).first()

        def format_team_stats(stats):
            if not stats:
                return None
            return {
                'passing': {
                    'attempts': stats.pass_attempts,
                    'completions': stats.pass_completions,
                    'yards': stats.pass_yards,
                    'touchdowns': stats.pass_touchdowns,
                },
                'rushing': {
                    'attempts': stats.rush_attempts,
                    'yards': stats.rush_yards,
                    'touchdowns': stats.rush_touchdowns,
                },
                'total_yards': stats.pass_yards + stats.rush_yards,
                'turnovers': stats.interceptions + stats.fumbles_lost,
                'sacks': stats.sacks,
                'penalties': stats.penalties,
                'penalty_yards': stats.penalty_yards,
            }

        # Get top performers for each team
        def get_top_performers(team):
            player_stats = FootballPlayerGameStat.objects.filter(
                game_id=game_id, player__team=team
            ).select_related('player').order_by('-fantasy_points_ppr')[:5]

            performers = []
            for ps in player_stats:
                if ps.fantasy_points_ppr > 0:
                    performers.append({
                        'player_id': ps.player.id,
                        'name': ps.player.name,
                        'position': ps.player.position,
                        'fantasy_points': round(ps.fantasy_points_ppr, 1),
                        'pass_yards': ps.pass_yards,
                        'pass_tds': ps.pass_touchdowns,
                        'rush_yards': ps.rush_yards,
                        'rush_tds': ps.rush_touchdowns,
                        'receptions': ps.receptions,
                        'receiving_yards': ps.receiving_yards,
                        'receiving_tds': ps.receiving_touchdowns,
                    })
            return performers

        response_data = {
            'game_id': game.id,
            'home_team': {
                'id': game.home_team.id,
                'abbreviation': game.home_team.abbreviation,
                'name': game.home_team.name,
                'score': game.home_score,
                'stats': format_team_stats(home_team_stats),
                'top_performers': get_top_performers(game.home_team),
            },
            'away_team': {
                'id': game.away_team.id,
                'abbreviation': game.away_team.abbreviation,
                'name': game.away_team.name,
                'score': game.away_score,
                'stats': format_team_stats(away_team_stats),
                'top_performers': get_top_performers(game.away_team),
            },
        }

        return Response(response_data)

    """
    GET API --> Player comparison data for Start/Sit tool
    Query params: 'player_id' (required), 'games' (default=3)
    Returns player stats + upcoming matchup + opponent defense ranking
    """
    @action(detail=False, methods=['get'], url_path='player-comparison')
    def player_comparison(self, request):
        player_id = request.query_params.get('player_id')
        num_games = int(request.query_params.get('games', 3))

        if not player_id:
            return Response({'Error': '\'player_id\' is required'}, status=400)

        # Get player info
        try:
            player = Player.objects.select_related('team').get(id=player_id)
        except Player.DoesNotExist:
            return Response({'Error': 'Player not found'}, status=404)

        # Get player's recent stats
        player_games = (Game.objects
            .filter(Q(home_team=player.team) | Q(away_team=player.team))
            .exclude(home_score=None)
            .order_by('-date')[:num_games]
            .values_list('id', flat=True))

        player_stats = (FootballPlayerGameStat.objects
            .filter(player_id=player_id, game_id__in=player_games)
            .aggregate(
                avg_fantasy_points=Avg('fantasy_points_ppr'),
                avg_targets=Avg('targets'),
                avg_receptions=Avg('receptions'),
                avg_receiving_yards=Avg('receiving_yards'),
                avg_receiving_tds=Avg('receiving_touchdowns'),
                avg_rush_attempts=Avg('rush_attempts'),
                avg_rush_yards=Avg('rush_yards'),
                avg_rush_tds=Avg('rush_touchdowns'),
                avg_pass_yards=Avg('pass_yards'),
                avg_pass_tds=Avg('pass_touchdowns'),
                avg_interceptions=Avg('interceptions'),
                games_played=Count('id'),
                # Advanced metrics
                avg_snap_count=Avg('snap_count'),
                avg_snap_pct=Avg('snap_pct'),
                avg_air_yards=Avg('air_yards'),
                avg_yac=Avg('yards_after_catch'),
            ))

        # Get upcoming game (use simulation cutoff if active)
        sim = self.get_simulation_context(request)
        if sim.is_active and sim.cutoff_date:
            cutoff = sim.cutoff_date
        else:
            cutoff = timezone.now().date()
        upcoming_game = (Game.objects
            .filter(Q(home_team=player.team) | Q(away_team=player.team))
            .filter(date__gte=cutoff)
            .order_by('date')
            .first())

        matchup_data = None
        defense_ranking = None

        if upcoming_game and player.team:
            # Determine opponent
            if upcoming_game.home_team_id == player.team.id:
                opponent = upcoming_game.away_team
                is_home = True
            else:
                opponent = upcoming_game.home_team
                is_home = False

            # Get opponent's defense ranking vs this position
            opp_games = (Game.objects
                .filter(Q(home_team=opponent) | Q(away_team=opponent))
                .exclude(home_score=None)
                .order_by('-date')[:num_games]
                .values_list('id', flat=True))

            # Stats allowed to this position
            position = player.position
            opp_defense_stats = (FootballPlayerGameStat.objects
                .filter(game_id__in=opp_games)
                .filter(player__position=position)
                .exclude(player__team=opponent)
                .aggregate(
                    fantasy_pts_allowed=Avg('fantasy_points_ppr'),
                    yards_allowed=Avg(F('receiving_yards') + F('rush_yards')),
                    tds_allowed=Avg(F('receiving_touchdowns') + F('rush_touchdowns')),
                ))

            matchup_data = {
                'game_id': upcoming_game.id,
                'opponent': opponent.abbreviation,
                'opponent_name': opponent.name,
                'opponent_logo_url': opponent.logo_url,
                'is_home': is_home,
                'game_date': upcoming_game.date.isoformat(),
                'game_time': upcoming_game.time,
                'location': upcoming_game.location,
                'weather': {
                    'temp': upcoming_game.temp,
                    'wind': upcoming_game.wind,
                    'roof': upcoming_game.roof,
                }
            }

            defense_ranking = {
                'fantasy_pts_allowed': round(opp_defense_stats['fantasy_pts_allowed'] or 0, 1),
                'yards_allowed': round(opp_defense_stats['yards_allowed'] or 0, 1),
                'tds_allowed': round(opp_defense_stats['tds_allowed'] or 0, 2),
            }

        response_data = {
            'player': {
                'id': player.id,
                'name': player.name,
                'position': player.position,
                'team': player.team.abbreviation if player.team else None,
                'team_name': player.team.name if player.team else None,
                'image_url': player.image_url,
            },
            'stats': {
                'avg_fantasy_points': round(player_stats['avg_fantasy_points'] or 0, 1),
                'avg_targets': round(player_stats['avg_targets'] or 0, 1),
                'avg_receptions': round(player_stats['avg_receptions'] or 0, 1),
                'avg_receiving_yards': round(player_stats['avg_receiving_yards'] or 0, 1),
                'avg_receiving_tds': round(player_stats['avg_receiving_tds'] or 0, 2),
                'avg_rush_attempts': round(player_stats['avg_rush_attempts'] or 0, 1),
                'avg_rush_yards': round(player_stats['avg_rush_yards'] or 0, 1),
                'avg_rush_tds': round(player_stats['avg_rush_tds'] or 0, 2),
                'avg_pass_yards': round(player_stats['avg_pass_yards'] or 0, 1),
                'avg_pass_tds': round(player_stats['avg_pass_tds'] or 0, 2),
                'avg_interceptions': round(player_stats['avg_interceptions'] or 0, 2),
                'games_played': player_stats['games_played'] or 0,
                # Advanced metrics
                'avg_snap_count': round(player_stats['avg_snap_count'] or 0, 1),
                'avg_snap_pct': round(player_stats['avg_snap_pct'] or 0, 1),
                'avg_air_yards': round(player_stats['avg_air_yards'] or 0, 1),
                'avg_yac': round(player_stats['avg_yac'] or 0, 1),
                'adot': round((player_stats['avg_air_yards'] or 0) / (player_stats['avg_targets'] or 1), 1) if player_stats['avg_targets'] else 0,
            },
            'games_analyzed': num_games,
            'matchup': matchup_data,
            'opponent_defense': defense_ranking,
        }

        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='team-game-log')
    def team_game_log(self, request):
        team_id = request.query_params.get('team_id')
        num_games = int(request.query_params.get('games', 5))

        if not team_id:
            return Response({'Error': '\'team_id\' is required'}, status=400)

        cache_key = f'team_game_log_{team_id}_{num_games}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        team_stats = (FootballTeamGameStat.objects
            .filter(team_id=team_id)
            .select_related('game', 'game__home_team', 'game__away_team')
            .order_by('-game__date')[:num_games])

        games_list = []
        for stat in team_stats:
            game = stat.game
            is_home = game.home_team_id == int(team_id)
            opponent = game.away_team if is_home else game.home_team
            team_score = game.home_score if is_home else game.away_score
            opp_score = game.away_score if is_home else game.home_score

            if team_score is None:
                continue

            if team_score > opp_score:
                result = 'W'
            elif team_score < opp_score:
                result = 'L'
            else:
                result = 'T'

            games_list.append({
                'game_id': game.id,
                'week': game.week,
                'date': game.date.isoformat(),
                'opponent': opponent.abbreviation,
                'opponent_logo_url': opponent.logo_url,
                'is_home': is_home,
                'team_score': team_score,
                'opp_score': opp_score,
                'result': result,
                'pass_yards': stat.pass_yards,
                'rush_yards': stat.rush_yards,
                'total_yards': stat.pass_yards + stat.rush_yards,
                'pass_tds': stat.pass_touchdowns,
                'rush_tds': stat.rush_touchdowns,
                'turnovers': stat.interceptions + stat.fumbles_lost,
                'sacks': stat.sacks,
            })

        response_data = {
            'team_id': team_id,
            'games': games_list,
        }

        cache.set(cache_key, response_data, settings.CACHE_TTL['analytics'])
        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='head-to-head')
    def head_to_head(self, request):
        team1_id = request.query_params.get('team1_id')
        team2_id = request.query_params.get('team2_id')
        limit = int(request.query_params.get('limit', 5))

        if not team1_id or not team2_id:
            return Response({'Error': '\'team1_id\' and \'team2_id\' are required'}, status=400)

        cache_key = f'head_to_head_{team1_id}_{team2_id}_{limit}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        games = (Game.objects
            .filter(
                (Q(home_team_id=team1_id) & Q(away_team_id=team2_id)) |
                (Q(home_team_id=team2_id) & Q(away_team_id=team1_id))
            )
            .exclude(home_score=None)
            .order_by('-date')[:limit])

        matchups = []
        team1_wins = 0
        team2_wins = 0
        ties = 0

        for game in games:
            if game.home_team_id == int(team1_id):
                t1_score = game.home_score
                t2_score = game.away_score
            else:
                t1_score = game.away_score
                t2_score = game.home_score

            if t1_score > t2_score:
                team1_wins += 1
            elif t2_score > t1_score:
                team2_wins += 1
            else:
                ties += 1

            # Get team stats for this game
            t1_stats = FootballTeamGameStat.objects.filter(game=game, team_id=team1_id).first()
            t2_stats = FootballTeamGameStat.objects.filter(game=game, team_id=team2_id).first()

            matchups.append({
                'game_id': game.id,
                'season': game.season,
                'week': game.week,
                'date': game.date.isoformat(),
                'team1_score': t1_score,
                'team2_score': t2_score,
                'team1_total_yards': (t1_stats.pass_yards + t1_stats.rush_yards) if t1_stats else 0,
                'team2_total_yards': (t2_stats.pass_yards + t2_stats.rush_yards) if t2_stats else 0,
                'team1_turnovers': (t1_stats.interceptions + t1_stats.fumbles_lost) if t1_stats else 0,
                'team2_turnovers': (t2_stats.interceptions + t2_stats.fumbles_lost) if t2_stats else 0,
            })

        response_data = {
            'matchups': matchups,
            'series_record': {
                'team1_wins': team1_wins,
                'team2_wins': team2_wins,
                'ties': ties,
            },
        }

        cache.set(cache_key, response_data, settings.CACHE_TTL['analytics'])
        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='common-opponents')
    def common_opponents(self, request):
        team1_id = request.query_params.get('team1_id')
        team2_id = request.query_params.get('team2_id')
        season = request.query_params.get('season')

        if not team1_id or not team2_id:
            return Response({'Error': '\'team1_id\' and \'team2_id\' are required'}, status=400)

        if not season:
            return Response({'Error': '\'season\' is required'}, status=400)

        cache_key = f'common_opponents_{team1_id}_{team2_id}_{season}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        season = int(season)

        # Find opponents each team played
        def get_opponents_and_results(tid):
            games = (Game.objects
                .filter(Q(home_team_id=tid) | Q(away_team_id=tid), season=season)
                .exclude(home_score=None)
                .select_related('home_team', 'away_team'))

            results = defaultdict(list)
            for g in games:
                is_home = g.home_team_id == int(tid)
                opp = g.away_team if is_home else g.home_team
                score = g.home_score if is_home else g.away_score
                opp_score = g.away_score if is_home else g.home_score
                results[opp.id].append({
                    'score': score,
                    'opp_score': opp_score,
                    'week': g.week,
                })
            return results

        t1_results = get_opponents_and_results(team1_id)
        t2_results = get_opponents_and_results(team2_id)

        # Exclude each other
        common_ids = set(t1_results.keys()) & set(t2_results.keys())
        common_ids.discard(int(team1_id))
        common_ids.discard(int(team2_id))

        common_opponents = []
        for opp_id in common_ids:
            try:
                opp_team = Team.objects.get(id=opp_id)
            except Team.DoesNotExist:
                continue
            common_opponents.append({
                'opponent_abbreviation': opp_team.abbreviation,
                'opponent_logo_url': opp_team.logo_url,
                'team1_results': t1_results[opp_id],
                'team2_results': t2_results[opp_id],
            })

        common_opponents.sort(key=lambda x: x['opponent_abbreviation'])

        response_data = {
            'common_opponents': common_opponents,
        }

        cache.set(cache_key, response_data, settings.CACHE_TTL['analytics'])
        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='usage-trends')
    def usage_trends(self, request):
        team_id = request.query_params.get('team_id')
        num_games = int(request.query_params.get('games', 5))

        if not team_id:
            return Response({'Error': '\'team_id\' is required'}, status=400)

        cache_key = f'usage_trends_{team_id}_{num_games}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        games = (Game.objects
            .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
            .exclude(home_score=None)
            .order_by('-date')[:num_games])

        per_game = []
        for game in reversed(list(games)):  # chronological order
            player_stats = (FootballPlayerGameStat.objects
                .filter(game=game, player__team_id=team_id)
                .select_related('player'))

            # Compute totals for the team in this game
            total_targets = sum(ps.targets for ps in player_stats)
            total_carries = sum(ps.rush_attempts for ps in player_stats)

            target_shares = {}
            carry_shares = {}
            for ps in player_stats:
                if ps.player.position in ['WR', 'TE'] and ps.targets > 0 and total_targets > 0:
                    target_shares[ps.player.name] = round(ps.targets / total_targets * 100, 1)
                if ps.player.position == 'RB' and ps.rush_attempts > 0 and total_carries > 0:
                    carry_shares[ps.player.name] = round(ps.rush_attempts / total_carries * 100, 1)

            per_game.append({
                'week': game.week,
                'target_shares': target_shares,
                'carry_shares': carry_shares,
            })

        response_data = {
            'team_id': team_id,
            'per_game': per_game,
        }

        cache.set(cache_key, response_data, settings.CACHE_TTL['analytics'])
        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='player-trend')
    def player_trend(self, request):
        player_id = request.query_params.get('player_id')
        num_games = int(request.query_params.get('games', 10))

        if not player_id:
            return Response({'Error': '\'player_id\' is required'}, status=400)

        cache_key = f'player_trend_{player_id}_{num_games}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        try:
            player = Player.objects.select_related('team').get(id=player_id)
        except Player.DoesNotExist:
            return Response({'Error': 'Player not found'}, status=404)

        games = (Game.objects
            .filter(Q(home_team=player.team) | Q(away_team=player.team))
            .exclude(home_score=None)
            .order_by('-date')[:num_games]
            .values_list('id', flat=True))

        stats = (FootballPlayerGameStat.objects
            .filter(player_id=player_id, game_id__in=games)
            .select_related('game', 'game__home_team', 'game__away_team')
            .order_by('game__date'))

        per_game = []
        all_fpts = []
        for s in stats:
            g = s.game
            opponent = g.away_team if g.home_team_id == player.team_id else g.home_team
            fpts = round(s.fantasy_points_ppr, 1)
            all_fpts.append(fpts)
            per_game.append({
                'week': g.week,
                'opponent': opponent.abbreviation,
                'fantasy_points': fpts,
                'pass_yards': s.pass_yards,
                'rush_yards': s.rush_yards,
                'receiving_yards': s.receiving_yards,
                'targets': s.targets,
                'receptions': s.receptions,
            })

        season_avg = round(sum(all_fpts) / len(all_fpts), 1) if all_fpts else 0
        last_3 = all_fpts[-3:] if len(all_fpts) >= 3 else all_fpts
        last_3_avg = round(sum(last_3) / len(last_3), 1) if last_3 else 0

        if last_3_avg > season_avg * 1.1:
            trend = 'up'
        elif last_3_avg < season_avg * 0.9:
            trend = 'down'
        else:
            trend = 'stable'

        response_data = {
            'player_id': int(player_id),
            'name': player.name,
            'per_game': per_game,
            'season_avg': season_avg,
            'last_3_avg': last_3_avg,
            'trend': trend,
        }

        cache.set(cache_key, response_data, settings.CACHE_TTL['analytics'])
        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='best-team')
    def best_team(self, request):
        num_games = int(request.query_params.get('games', 3))

        cache_key = f'best_team_{num_games}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        from django.db.models import Avg as DjAvg

        # Get players with avg fantasy points
        player_stats = (FootballPlayerGameStat.objects
            .values('player_id', 'player__name', 'player__position', 'player__team__abbreviation', 'player__image_url')
            .annotate(
                avg_fpts=DjAvg('fantasy_points_ppr'),
                games_played=Count('id'),
            )
            .filter(games_played__gte=1)
            .order_by('-avg_fpts'))

        # Filter to recent N games per player
        # For simplicity, we use overall averages but filter by min games
        position_limits = {'QB': 1, 'RB': 2, 'WR': 2, 'TE': 1}
        roster = {'QB': [], 'RB': [], 'WR': [], 'TE': [], 'FLEX': []}
        flex_candidates = []

        for ps in player_stats:
            pos = ps['player__position']
            if pos not in position_limits:
                continue
            entry = {
                'player_id': ps['player_id'],
                'name': ps['player__name'],
                'position': pos,
                'team': ps['player__team__abbreviation'],
                'image_url': ps['player__image_url'],
                'avg_fpts': round(ps['avg_fpts'], 1),
            }
            if len(roster[pos]) < position_limits[pos]:
                roster[pos].append(entry)
            elif pos in ['RB', 'WR', 'TE'] and len(roster['FLEX']) == 0:
                roster['FLEX'].append(entry)

        total = sum(
            p['avg_fpts']
            for slot in roster.values()
            for p in slot
        )

        response_data = {
            'roster': roster,
            'projected_weekly_total': round(total, 1),
        }

        cache.set(cache_key, response_data, settings.CACHE_TTL['analytics'])
        return Response(response_data)