from django.core.management.base import BaseCommand
from games.models import Game
from teams.models import Team
from teams.constants import TEAM_IDS
import nflreadpy as nfl
import datetime

class Command(BaseCommand):
    help = "Seed Games table with NFL schedule data from nflreadpy"

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-year',
            type=int,
            default=2025,
            help='Start year for seeding (default: 2025)'
        )
        parser.add_argument(
            '--end-year',
            type=int,
            default=2025,
            help='End year for seeding (default: 2025)'
        )

    def handle(self, *args, **kwargs):
        start_year = kwargs['start_year']
        end_year = kwargs['end_year']
        seasons = list(range(start_year, end_year + 1))

        self.stdout.write(f'Loading games for seasons: {seasons}')
        games_df = nfl.load_schedules(seasons=seasons)
        total_games = len(games_df)
        self.stdout.write(f'Found {total_games} games to process')

        processed = 0
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

            # Skip if team not found (e.g., old team abbreviations)
            if not away_team_id or not home_team_id:
                continue

            date = datetime.date(int(game_day[0]), int(game_day[1]), int(game_day[2]))

            try:
                away_team_obj = Team.objects.get(id=away_team_id)
                home_team_obj = Team.objects.get(id=home_team_id)
            except Team.DoesNotExist:
                continue

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

            processed += 1
            if processed % 100 == 0:
                self.stdout.write(f'Processed {processed}/{total_games} games...')

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {processed} games'))



