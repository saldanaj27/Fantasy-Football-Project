from django.core.management.base import BaseCommand
from games.models import Game
from teams.models import Team
from teams.constants import TEAM_IDS
import nflreadpy as nfl
import datetime

class Command(BaseCommand):
    help = "Seed Games table with NFl team data from nflreadpy (using 2025 season)"
    
    def handle(self, *args, **kwargs):
        curr_season = 2025
        games_df = nfl.load_schedules(seasons=curr_season)

        for row in games_df.iter_rows(named=True):
            game_id = row['game_id']
            game_season = row['season']
            game_stage = row['game_type']
            game_week = row['week']
            game_day = row['gameday'].split('-')
            game_time = row['gametime']
            away_team_id = TEAM_IDS.get(row['away_team'])
            away_score = row['away_score']
            home_team_id = TEAM_IDS.get(row['home_team'])
            home_score = row['home_score']
            location = row['location']
            total_score = row['total']
            overtime = True if row['overtime'] == 1 else False
            game_roof = row['roof']
            game_temp = row['temp']
            game_wind = row['wind']

            date = datetime.date(int(game_day[0]), int(game_day[1]), int(game_day[2]))
            away_team_obj = Team.objects.get(id=away_team_id)
            home_team_obj = Team.objects.get(id=home_team_id)

            Game.objects.update_or_create(
                id=game_id,
                defaults={
                    'season': game_season,
                    'week': game_week,
                    'time': game_time,
                    'date': date,
                    'away_team': away_team_obj,
                    'home_team': home_team_obj,
                    'stage': game_stage,
                    'away_score': away_score,
                    'home_score': home_score,
                    'total_score': total_score,
                    'overtime': overtime,
                    'location': location,
                    'roof': game_roof,
                    'temp': game_temp,
                    'wind': game_wind,
                }
            )



