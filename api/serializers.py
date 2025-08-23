from rest_framework import serializers
from teams.models import Team
from players.models import Player
from games.models import Game
from stats.models import FootballPlayerGameStat

class TeamSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Team
        fields = ['id', 'name', 'abbreviation', 'logo_url']

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'position', 'team', 'image_url']

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'home_team', 'away_team', 'date', 'week', 'season', 'home_score', 'away_score']

class FootballPlayerGameStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootballPlayerGameStat
        fields = [
            'player', 'game', 'rush_attempts', 'rush_yards', 
            'fumbles', 'pass_yards', 'pass_completions', 'pass_attempts',
            'touchdowns', 'interceptions', 'targets', 'receptions',
            'receiving_yards', 'fantasy_points'
            ]