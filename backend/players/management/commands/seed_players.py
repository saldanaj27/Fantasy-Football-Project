from django.core.management.base import BaseCommand
from players.models import Player
from teams.models import Team
from players.constants import STATUS
from teams.constants import TEAM_IDS
import nflreadpy as nfl

class Command(BaseCommand):
    help = "Seed Players table with NFl team data from nflreadpy (using 2025 season)"
    
    def handle(self, *args, **kwargs):
        # define the season (all weeks need to be applied)
        season = 2025

        # from nflreadpy, load roster from the defined season (will return DataFrame)
        roster_df = nfl.load_rosters(seasons=season)

        # ???
        VALID_STATUS = {code for code, _ in STATUS}

        # test_player = Player(name = 'test', depth_chart_position = 'C', height = 10, weight = 10, position = 'OL', status = 'ACT')
        # test_player.save()
        
        # 'iter_rows(named)' returns dictionaries instead of tuples
        for row in roster_df.iter_rows(named=True):
            player_id = row['gsis_id'] # use GSIS ID as 'id' (primary key)
            player_name = row['full_name']
            player_depth_chart = row['depth_chart_position']
            player_team = row['team']
            player_season = row['season']
            player_position = row['position']
            player_status = row['status']
            player_height = row['height']
            player_weight = row['weight']
            player_headshot = row['headshot_url']

            # get the Team ID from dict constant
            team_id = TEAM_IDS.get(player_team)

            if player_status in VALID_STATUS:
                if player_id is None:
                    continue


                team_obj = Team.objects.get(id=team_id)

                # print('debug:', player_id, player_name)

                # creates/updates based if the object exists or not
                Player.objects.update_or_create(
                    id = player_id,
                    defaults={
                        "name": player_name,
                        "status": player_status,
                        "weight": player_weight,
                        "height": player_height,
                        "position": player_position,
                        "depth_chart_position": player_depth_chart,
                        "team": team_obj,
                        "season": player_season,
                        "image_url": player_headshot,
                    }
                )

