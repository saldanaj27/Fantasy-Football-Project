from rest_framework import serializers
from teams.models import Team
from players.models import Player
from games.models import Game
from stats.models import FootballPlayerGameStat
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class TeamSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Team
        fields = "__all__"

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"

class FootballPlayerGameStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootballPlayerGameStat
        fields = "__all__"