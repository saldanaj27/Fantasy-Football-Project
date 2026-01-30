from rest_framework import serializers
from teams.models import Team
from players.models import Player
from games.models import Game

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"

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
    # change fields from ID to actual objects
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)

    class Meta:
        model = Game
        fields = "__all__"
