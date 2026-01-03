from django.core.management.base import BaseCommand
from players.constants import OFFENSIVE_POS
from players.models import Player
from games.models import Game
from teams.models import Team
from stats.models import FootballPlayerGameStat, FootballTeamGameStat
from teams.constants import TEAM_IDS
import nflreadpy as nfl

class Command(BaseCommand):
    help = "Seed Stats tables with NFl team data from nflreadpy (using 2025 season)"
    
    def handle(self, *args, **kwargs):
        curr_season = 2025
        player_stats_df = nfl.load_player_stats(seasons=curr_season)
        team_stats_df = nfl.load_team_stats(seasons=curr_season)

        for row in player_stats_df.filter(player_stats_df['position'].is_in(OFFENSIVE_POS)).iter_rows(named=True):
            player_obj = Player.objects.get(id=row['player_id'])
            # converts '1' to '01'
            game_id_prefix = str(row['season']) + '_' + str(row['week']).zfill(2) + '_'
            
            # checks both 'id's of 'team' first or 'opponent_team'  
            try:
                game_obj = Game.objects.get(id=game_id_prefix+row['team']+'_'+row['opponent_team'])
            except:
                game_obj = Game.objects.get(id=game_id_prefix+row['opponent_team']+'_'+row['team'])

            pass_comp = row['completions']
            pass_att = row['attempts']
            pass_yds = row['passing_yards']
            pass_tds = row['passing_tds']
            pass_ints = row['passing_interceptions']
            sacks = row['sacks_suffered']
            sack_yds_loss = row['sack_yards_lost']
            # fumbles = row['sack_fumbles']+row['rushing_fumbles']+row['receiving_fumbles']
            rush_att = row['carries']
            rush_yds = row['rushing_yards']
            rush_tds = row['rushing_tds']
            receptions = row['receptions']
            targets = row['targets']
            rec_yds = row['receiving_yards']
            rec_tds = row['receiving_tds']
            fantasy_ppr = row['fantasy_points_ppr']

            FootballPlayerGameStat.objects.update_or_create(
                player = player_obj,
                game = game_obj,
                defaults={
                    'rush_attempts': rush_att,
                    'rush_yards': rush_yds,
                    'rush_touchdowns': rush_tds,
                    # 'fumbles': fumbles,
                    'pass_yards': pass_yds,
                    'pass_attempts': pass_att,
                    'pass_completions': pass_comp,
                    'pass_touchdowns': pass_tds,
                    'interceptions': pass_ints,
                    'sacks': sacks,
                    'sack_yards_loss': sack_yds_loss,
                    'targets': targets,
                    'receptions': receptions,
                    'receiving_yards': rec_yds,
                    'receiving_touchdowns': rec_tds,
                    'fantasy_points_ppr': fantasy_ppr,
                }
            )

        for row in team_stats_df.iter_rows(named=True):
            team_obj = Team.objects.get(id=TEAM_IDS.get(row['team']))
            game_id_prefix = str(row['season']) + '_' + str(row['week']).zfill(2) + '_'
            
            try:
                game_obj = Game.objects.get(id=game_id_prefix+row['team']+'_'+row['opponent_team'])
            except:
                game_obj = Game.objects.get(id=game_id_prefix+row['opponent_team']+'_'+row['team'])
            
            pass_comp = row['completions']
            pass_att = row['attempts']
            pass_yds = row['passing_yards']
            pass_tds = row['passing_tds']
            pass_ints = row['passing_interceptions']
            sacks = row['sacks_suffered']
            fumbles = row['sack_fumbles']+row['rushing_fumbles']+row['receiving_fumbles']
            fumbles_lost = row['sack_fumbles_lost']+row['rushing_fumbles_lost']+row['receiving_fumbles_lost']
            rush_att = row['carries']
            rush_yds = row['rushing_yards']
            rush_tds = row['rushing_tds']
            receptions = row['receptions']
            # targets = row['targets']
            rec_yds = row['receiving_yards']
            rec_tds = row['receiving_tds']
            spec_teams_tds = row['special_teams_tds']
            def_tfl = row['def_tackles_for_loss']
            def_fumbles_forced = row['def_fumbles_forced']
            def_sacks = row['def_sacks']
            def_qb_hits = row['def_qb_hits']
            def_interceptions = row['def_interceptions']
            def_tds = row['def_tds']
            penalties = row['penalties']
            penalty_yards = row['penalty_yards']
            fg_att = row['fg_att']
            fg_made = row['fg_made']

            FootballTeamGameStat.objects.update_or_create(
                team = team_obj,
                game = game_obj,
                defaults={
                    'pass_attempts': pass_att,
                    'pass_completions': pass_comp,
                    'pass_yards': pass_yds,
                    'pass_touchdowns': pass_tds,
                    'rush_attempts': rush_att,
                    'rush_yards': rush_yds,
                    'rush_touchdowns': rush_tds,
                    'interceptions': pass_ints,
                    'sacks': sacks,
                    'fumbles': fumbles,
                    'fumbles_lost': fumbles_lost,
                    # 'targets': targets,
                    'receptions': receptions,
                    'receiving_yards': rec_yds,
                    'receiving_touchdowns': rec_tds,
                    'special_teams_touchdowns': spec_teams_tds,
                    'def_tackles_for_loss': def_tfl,
                    'def_fumbles_forced': def_fumbles_forced,
                    'def_sacks': def_sacks,
                    'def_qb_hits': def_qb_hits,
                    'def_interceptions': def_interceptions,
                    'def_touchdowns': def_tds,
                    'penalties': penalties,
                    'penalty_yards': penalty_yards,
                    'fg_attempts': fg_att,
                    'fg_made': fg_made,
                }
            )


