from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg

from players.models import Player
from stats.models import FootballPlayerGameStat
from .models import DraftSession, DraftPick
from .services import DraftAI


class DraftViewSet(viewsets.ViewSet):
    """Endpoints for the fantasy draft simulator."""

    @action(detail=False, methods=['post'], url_path='create')
    def create_session(self, request):
        """Create a new draft session with configuration."""
        num_teams = int(request.data.get('num_teams', 10))
        num_rounds = int(request.data.get('num_rounds', 15))
        user_team_position = int(request.data.get('user_team_position', 1))
        scoring_format = request.data.get('scoring_format', 'PPR')

        if not 1 <= user_team_position <= num_teams:
            return Response(
                {'error': 'user_team_position must be between 1 and num_teams'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = DraftSession.objects.create(
            num_teams=num_teams,
            num_rounds=num_rounds,
            user_team_position=user_team_position,
            scoring_format=scoring_format,
            status='active',
        )

        # Auto-pick AI turns before user's first pick
        DraftAI.auto_pick_until_user(session)
        session.refresh_from_db()

        return Response({
            'session_id': session.id,
            'status': session.status,
            'current_pick': session.current_pick,
            'current_round': session.current_round,
            'total_picks': session.total_picks,
            'user_team_position': session.user_team_position,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='pick')
    def make_pick(self, request, pk=None):
        """User makes a pick, then AI auto-advances until user's next turn."""
        try:
            session = DraftSession.objects.get(pk=pk)
        except DraftSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        if session.status != 'active':
            return Response({'error': 'Draft is not active'}, status=status.HTTP_400_BAD_REQUEST)

        player_id = request.data.get('player_id')
        if not player_id:
            return Response({'error': 'player_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify it's the user's turn
        current_team = session.get_team_for_pick(session.current_pick)
        if current_team != session.user_team_position:
            return Response({'error': 'Not your turn'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify player is available
        try:
            player = Player.objects.get(pk=player_id)
        except Player.DoesNotExist:
            return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)

        if session.picks.filter(player=player).exists():
            return Response({'error': 'Player already drafted'}, status=status.HTTP_400_BAD_REQUEST)

        # Make the user's pick
        round_num = (session.current_pick - 1) // session.num_teams + 1
        DraftPick.objects.create(
            session=session,
            player=player,
            team_number=session.user_team_position,
            round_number=round_num,
            overall_pick=session.current_pick,
            is_user=True,
        )

        session.current_pick += 1
        session.current_round = (session.current_pick - 1) // session.num_teams + 1
        session.save()

        # AI auto-picks until user's next turn
        ai_picks = DraftAI.auto_pick_until_user(session)
        session.refresh_from_db()

        return Response({
            'status': session.status,
            'current_pick': session.current_pick,
            'current_round': session.current_round,
            'ai_picks': [
                {
                    'overall_pick': p.overall_pick,
                    'round_number': p.round_number,
                    'team_number': p.team_number,
                    'player_id': p.player_id,
                    'player_name': p.player.name,
                    'player_position': p.player.position,
                }
                for p in ai_picks
            ],
        })

    @action(detail=True, methods=['get'], url_path='board')
    def board(self, request, pk=None):
        """Full draft board state."""
        try:
            session = DraftSession.objects.get(pk=pk)
        except DraftSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        picks = session.picks.select_related('player', 'player__team').all()
        board = []
        for pick in picks:
            board.append({
                'overall_pick': pick.overall_pick,
                'round_number': pick.round_number,
                'team_number': pick.team_number,
                'is_user': pick.is_user,
                'player': {
                    'id': pick.player.id,
                    'name': pick.player.name,
                    'position': pick.player.position,
                    'team': pick.player.team.abbreviation if pick.player.team else None,
                    'image_url': pick.player.image_url,
                },
            })

        return Response({
            'session_id': session.id,
            'status': session.status,
            'current_pick': session.current_pick,
            'current_round': session.current_round,
            'total_picks': session.total_picks,
            'num_teams': session.num_teams,
            'num_rounds': session.num_rounds,
            'user_team_position': session.user_team_position,
            'scoring_format': session.scoring_format,
            'picks': board,
        })

    @action(detail=True, methods=['get'], url_path='available')
    def available(self, request, pk=None):
        """Available players sorted by avg FPTS."""
        try:
            session = DraftSession.objects.get(pk=pk)
        except DraftSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        players = DraftAI.get_available_players(session)

        # Optional filters
        position = request.query_params.get('position')
        search = request.query_params.get('search')
        if position:
            players = players.filter(position=position)
        if search:
            players = players.filter(name__icontains=search)

        players = players[:100]

        return Response({
            'players': [
                {
                    'id': p.id,
                    'name': p.name,
                    'position': p.position,
                    'team': p.team.abbreviation if p.team else None,
                    'image_url': p.image_url,
                    'avg_fpts': round(p.avg_fpts or 0, 1),
                    'games_played': p.games_played or 0,
                }
                for p in players
            ],
        })

    @action(detail=True, methods=['get'], url_path='roster')
    def roster(self, request, pk=None):
        """User's roster with projected total."""
        try:
            session = DraftSession.objects.get(pk=pk)
        except DraftSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        picks = (
            session.picks
            .filter(team_number=session.user_team_position)
            .select_related('player', 'player__team')
        )

        roster = []
        total_projected = 0
        for pick in picks:
            avg = FootballPlayerGameStat.objects.filter(
                player=pick.player
            ).aggregate(avg=Avg('fantasy_points_ppr'))['avg'] or 0

            roster.append({
                'round_number': pick.round_number,
                'overall_pick': pick.overall_pick,
                'player': {
                    'id': pick.player.id,
                    'name': pick.player.name,
                    'position': pick.player.position,
                    'team': pick.player.team.abbreviation if pick.player.team else None,
                    'image_url': pick.player.image_url,
                },
                'avg_fpts': round(avg, 1),
            })
            total_projected += avg

        return Response({
            'roster': roster,
            'projected_weekly_total': round(total_projected, 1),
        })
