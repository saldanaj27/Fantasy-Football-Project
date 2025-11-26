from django.core.management.base import BaseCommand
from teams.models import Team
import nflreadpy as nfl

class Command(BaseCommand):
    help = "Seed Teams table with NFl team data from nflreadpy (using 2025 season)"
    
    def handle(self, *args, **kwargs):
        curr_season = 2025
        teams_df = nfl.load_teams()

        for row in teams_df.filter(teams_df["season"] == curr_season).iter_rows(named=True):
            team_id = row['nfl_team_id']
            team_name = row['full']
            team_abb = row['team']
            team_city = row['location']

            Team.objects.update_or_create(
                id = team_id,
                defaults={
                    "name": team_name, 
                    "abbreviation": team_abb, 
                    "city": team_city
                }
            )


