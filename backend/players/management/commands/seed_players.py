import nflreadpy as nfl
from django.core.management.base import BaseCommand

from players.constants import STATUS
from players.models import Player
from teams.constants import TEAM_IDS
from teams.models import Team


class Command(BaseCommand):
    help = "Seed Players table with NFL roster data from nflreadpy"

    def add_arguments(self, parser):
        parser.add_argument(
            "--start-year",
            type=int,
            default=2025,
            help="Start year for seeding (default: 2025)",
        )
        parser.add_argument(
            "--end-year",
            type=int,
            default=2025,
            help="End year for seeding (default: 2025)",
        )

    def handle(self, *args, **kwargs):
        start_year = kwargs["start_year"]
        end_year = kwargs["end_year"]
        seasons = list(range(start_year, end_year + 1))

        self.stdout.write(f"Loading rosters for seasons: {seasons}")

        # from nflreadpy, load roster from the defined seasons (will return DataFrame)
        roster_df = nfl.load_rosters(seasons=seasons)

        VALID_STATUS = {code for code, _ in STATUS}
        total_rows = len(roster_df)
        self.stdout.write(f"Found {total_rows} roster entries to process")

        processed = 0
        skipped = 0

        # 'iter_rows(named)' returns dictionaries instead of tuples
        for row in roster_df.iter_rows(named=True):
            player_id = row["gsis_id"]  # use GSIS ID as 'id' (primary key)
            player_name = row["full_name"]
            player_depth_chart = row["depth_chart_position"]
            player_team = row["team"]
            player_season = row["season"]
            player_position = row["position"]
            player_status = row["status"]
            player_height = row["height"]
            player_weight = row["weight"]
            player_headshot = row["headshot_url"]

            # Skip invalid entries
            if player_id is None or player_status not in VALID_STATUS:
                skipped += 1
                continue

            # get the Team ID from dict constant
            team_id = TEAM_IDS.get(player_team)
            if not team_id:
                skipped += 1
                continue

            try:
                team_obj = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                skipped += 1
                continue

            # creates/updates based if the object exists or not
            Player.objects.update_or_create(
                id=player_id,
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
                },
            )

            processed += 1
            if processed % 500 == 0:
                self.stdout.write(f"Processed {processed}/{total_rows} players...")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded {processed} players ({skipped} skipped)"
            )
        )
