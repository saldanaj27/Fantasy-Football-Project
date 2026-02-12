import nflreadpy as nfl
from django.core.management.base import BaseCommand

from games.models import Game
from players.constants import OFFENSIVE_POS
from players.models import Player
from stats.models import FootballPlayerGameStat, FootballTeamGameStat
from teams.constants import TEAM_IDS
from teams.models import Team


class Command(BaseCommand):
    help = "Seed Stats tables with NFL data from nflreadpy"

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

        self.stdout.write(f"Loading stats for seasons: {seasons}")

        player_stats_df = nfl.load_player_stats(seasons=seasons)
        team_stats_df = nfl.load_team_stats(seasons=seasons)

        # Load snap counts for advanced metrics
        try:
            snap_counts_df = nfl.load_snap_counts(seasons=seasons)
            self.stdout.write(self.style.SUCCESS("Loaded snap counts data"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not load snap counts: {e}"))
            snap_counts_df = None

        # Process player stats
        offensive_stats = player_stats_df.filter(
            player_stats_df["position"].is_in(OFFENSIVE_POS)
        )
        total_player_stats = len(offensive_stats)
        self.stdout.write(f"Processing {total_player_stats} player stat records...")

        processed = 0
        skipped = 0
        for row in offensive_stats.iter_rows(named=True):
            try:
                player_obj = Player.objects.get(id=row["player_id"])
            except Player.DoesNotExist:
                skipped += 1
                continue

            # converts '1' to '01'
            game_id_prefix = str(row["season"]) + "_" + str(row["week"]).zfill(2) + "_"

            # checks both 'id's of 'team' first or 'opponent_team'
            try:
                game_obj = Game.objects.get(
                    id=game_id_prefix + row["team"] + "_" + row["opponent_team"]
                )
            except Game.DoesNotExist:
                try:
                    game_obj = Game.objects.get(
                        id=game_id_prefix + row["opponent_team"] + "_" + row["team"]
                    )
                except Game.DoesNotExist:
                    skipped += 1
                    continue

            pass_comp = row["completions"]
            pass_att = row["attempts"]
            pass_yds = row["passing_yards"]
            pass_tds = row["passing_tds"]
            pass_ints = row["passing_interceptions"]
            sacks = row["sacks_suffered"]
            sack_yds_loss = row["sack_yards_lost"]
            rush_att = row["carries"]
            rush_yds = row["rushing_yards"]
            rush_tds = row["rushing_tds"]
            receptions = row["receptions"]
            targets = row["targets"]
            rec_yds = row["receiving_yards"]
            rec_tds = row["receiving_tds"]
            fantasy_ppr = row["fantasy_points_ppr"]

            # Advanced metrics from load_player_stats
            air_yards = row.get("receiving_air_yards", 0) or 0
            yac = row.get("receiving_yards_after_catch", 0) or 0

            # Look up snap counts if available
            snap_count = 0
            snap_pct = 0.0
            if snap_counts_df is not None:
                try:
                    player_snaps = snap_counts_df.filter(
                        (snap_counts_df["player_id"] == row["player_id"])
                        & (snap_counts_df["week"] == row["week"])
                    )
                    if len(player_snaps) > 0:
                        snap_row = player_snaps.row(0, named=True)
                        snap_count = snap_row.get("offense_snaps", 0) or 0
                        snap_pct = snap_row.get("offense_pct", 0.0) or 0.0
                except Exception:
                    pass

            FootballPlayerGameStat.objects.update_or_create(
                player=player_obj,
                game=game_obj,
                defaults={
                    "rush_attempts": rush_att,
                    "rush_yards": rush_yds,
                    "rush_touchdowns": rush_tds,
                    "pass_yards": pass_yds,
                    "pass_attempts": pass_att,
                    "pass_completions": pass_comp,
                    "pass_touchdowns": pass_tds,
                    "interceptions": pass_ints,
                    "sacks": sacks,
                    "sack_yards_loss": sack_yds_loss,
                    "targets": targets,
                    "receptions": receptions,
                    "receiving_yards": rec_yds,
                    "receiving_touchdowns": rec_tds,
                    "fantasy_points_ppr": fantasy_ppr,
                    "air_yards": air_yards,
                    "yards_after_catch": yac,
                    "snap_count": snap_count,
                    "snap_pct": snap_pct,
                },
            )

            processed += 1
            if processed % 500 == 0:
                self.stdout.write(
                    f"Processed {processed}/{total_player_stats} player stats..."
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Player stats: {processed} processed, {skipped} skipped"
            )
        )

        # Process team stats
        total_team_stats = len(team_stats_df)
        self.stdout.write(f"Processing {total_team_stats} team stat records...")

        processed = 0
        skipped = 0
        for row in team_stats_df.iter_rows(named=True):
            team_id = TEAM_IDS.get(row["team"])
            if not team_id:
                skipped += 1
                continue

            try:
                team_obj = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                skipped += 1
                continue

            game_id_prefix = str(row["season"]) + "_" + str(row["week"]).zfill(2) + "_"

            try:
                game_obj = Game.objects.get(
                    id=game_id_prefix + row["team"] + "_" + row["opponent_team"]
                )
            except Game.DoesNotExist:
                try:
                    game_obj = Game.objects.get(
                        id=game_id_prefix + row["opponent_team"] + "_" + row["team"]
                    )
                except Game.DoesNotExist:
                    skipped += 1
                    continue

            pass_comp = row["completions"]
            pass_att = row["attempts"]
            pass_yds = row["passing_yards"]
            pass_tds = row["passing_tds"]
            pass_ints = row["passing_interceptions"]
            sacks = row["sacks_suffered"]
            fumbles = (
                row["sack_fumbles"] + row["rushing_fumbles"] + row["receiving_fumbles"]
            )
            fumbles_lost = (
                row["sack_fumbles_lost"]
                + row["rushing_fumbles_lost"]
                + row["receiving_fumbles_lost"]
            )
            rush_att = row["carries"]
            rush_yds = row["rushing_yards"]
            rush_tds = row["rushing_tds"]
            receptions = row["receptions"]
            rec_yds = row["receiving_yards"]
            rec_tds = row["receiving_tds"]
            spec_teams_tds = row["special_teams_tds"]
            def_tfl = row["def_tackles_for_loss"]
            def_fumbles_forced = row["def_fumbles_forced"]
            def_sacks = row["def_sacks"]
            def_qb_hits = row["def_qb_hits"]
            def_interceptions = row["def_interceptions"]
            def_tds = row["def_tds"]
            penalties = row["penalties"]
            penalty_yards = row["penalty_yards"]
            fg_att = row["fg_att"]
            fg_made = row["fg_made"]

            FootballTeamGameStat.objects.update_or_create(
                team=team_obj,
                game=game_obj,
                defaults={
                    "pass_attempts": pass_att,
                    "pass_completions": pass_comp,
                    "pass_yards": pass_yds,
                    "pass_touchdowns": pass_tds,
                    "rush_attempts": rush_att,
                    "rush_yards": rush_yds,
                    "rush_touchdowns": rush_tds,
                    "interceptions": pass_ints,
                    "sacks": sacks,
                    "fumbles": fumbles,
                    "fumbles_lost": fumbles_lost,
                    "receptions": receptions,
                    "receiving_yards": rec_yds,
                    "receiving_touchdowns": rec_tds,
                    "special_teams_touchdowns": spec_teams_tds,
                    "def_tackles_for_loss": def_tfl,
                    "def_fumbles_forced": def_fumbles_forced,
                    "def_sacks": def_sacks,
                    "def_qb_hits": def_qb_hits,
                    "def_interceptions": def_interceptions,
                    "def_touchdowns": def_tds,
                    "penalties": penalties,
                    "penalty_yards": penalty_yards,
                    "fg_attempts": fg_att,
                    "fg_made": fg_made,
                },
            )

            processed += 1
            if processed % 100 == 0:
                self.stdout.write(
                    f"Processed {processed}/{total_team_stats} team stats..."
                )

        self.stdout.write(
            self.style.SUCCESS(f"Team stats: {processed} processed, {skipped} skipped")
        )
        self.stdout.write(self.style.SUCCESS("Stats seeding complete!"))
