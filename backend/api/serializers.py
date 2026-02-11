from rest_framework import serializers
from django.db.models import Q
from teams.models import Team
from players.models import Player
from games.models import Game

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"


class TeamWithRecordSerializer(serializers.ModelSerializer):
    record = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'abbreviation', 'city', 'logo_url', 'record']

    def get_record(self, obj):
        # Get the current season from context or default to latest
        season = self.context.get('season')
        if not season:
            latest_game = Game.objects.order_by('-season').first()
            season = latest_game.season if latest_game else 2024

        # Get all completed games for this team in the season
        completed_games = Game.objects.filter(
            Q(home_team=obj) | Q(away_team=obj),
            season=season,
            home_score__isnull=False,
            away_score__isnull=False
        )

        # In simulation mode, only count games before the simulated week
        simulation_week = self.context.get('simulation_week')
        if simulation_week is not None:
            completed_games = completed_games.filter(week__lt=simulation_week)

        wins = 0
        losses = 0
        ties = 0

        for game in completed_games:
            if game.home_team_id == obj.id:
                # Team is home
                if game.home_score > game.away_score:
                    wins += 1
                elif game.home_score < game.away_score:
                    losses += 1
                else:
                    ties += 1
            else:
                # Team is away
                if game.away_score > game.home_score:
                    wins += 1
                elif game.away_score < game.home_score:
                    losses += 1
                else:
                    ties += 1

        if ties > 0:
            return f"{wins}-{losses}-{ties}"
        return f"{wins}-{losses}"

class PlayerSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Player
        fields = "__all__"

class PlayerBasicSerializer(serializers.ModelSerializer):
    """Lightweight serializer without nested team for list views"""
    team_abbr = serializers.CharField(source='team.abbreviation', read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'name', 'position', 'team_abbr', 'image_url', 'status']

class GameSerializer(serializers.ModelSerializer):
    # change fields from ID to actual objects with records
    home_team = TeamWithRecordSerializer(read_only=True)
    away_team = TeamWithRecordSerializer(read_only=True)

    class Meta:
        model = Game
        fields = "__all__"

    def to_representation(self, instance):
        # Pass season context to nested team serializers
        self.fields['home_team'].context['season'] = instance.season
        self.fields['away_team'].context['season'] = instance.season
        # Pass simulation context to nested team serializers
        simulation_week = self.context.get('simulation_week')
        if simulation_week is not None:
            self.fields['home_team'].context['simulation_week'] = simulation_week
            self.fields['away_team'].context['simulation_week'] = simulation_week
        return super().to_representation(instance)
