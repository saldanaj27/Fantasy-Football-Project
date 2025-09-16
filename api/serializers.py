from rest_framework import serializers
from django.contrib.auth import get_user_model
from teams.models import Team
from players.models import Player
from games.models import Game
from stats.models import FootballPlayerGameStat
from users.models import User

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class TeamSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Team
        fields = "__all__"

# class UserTeamSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserTeam
#         fields = "__all__"

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"

# class UserPlayerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserPlayer
#         fields = "__all__"

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"

# class UserGameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserGame
#         fields = "__all__"

class FootballPlayerGameStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootballPlayerGameStat
        fields = "__all__"

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) # can't be seen

    class Meta:
        model = User
        fields = ("username", "password", "email")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
        return user