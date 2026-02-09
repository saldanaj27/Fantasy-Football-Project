"""
Feature Extraction for Game Predictions

This module converts raw game/team/player data into numerical features
that machine learning models can use to make predictions.

FEATURE ENGINEERING CONCEPTS:
-----------------------------
1. Features should capture information relevant to predicting the outcome
2. Features should be available BEFORE the game (can't use game results as features)
3. Features should be normalized/scaled for better model performance
4. More features isn't always better - can lead to overfitting

Our features fall into categories:
- Offensive features: How well does the team score?
- Defensive features: How well does the team prevent scoring?
- Situational features: Home/away, weather, rest days
- Trend features: Win streaks, recent form
"""

import numpy as np
from datetime import date
from django.db.models import Avg, Q

from games.models import Game
from stats.models import FootballTeamGameStat


class FeatureExtractor:
    """
    Extracts numerical features from historical game data.

    The key insight: For each game, we extract features for BOTH teams
    (home and away), then combine them into a single feature vector.

    Example feature vector for a game:
    [home_avg_pass_yds, home_avg_rush_yds, ..., away_avg_pass_yds, away_avg_rush_yds, ...]
    """

    def __init__(self, num_games: int = 5):
        """
        Args:
            num_games: Number of recent games to average for features.
                       More games = more stable but less responsive to recent form.
                       Fewer games = more responsive but more noisy.
        """
        self.num_games = num_games

    def extract_team_offensive_features(self, team_id: int, before_date: date) -> dict:
        """
        Extract offensive performance features for a team.

        We look at games BEFORE the target date to avoid data leakage
        (using future information to predict the past).

        Args:
            team_id: The team to extract features for
            before_date: Only consider games before this date

        Returns:
            Dictionary of offensive features
        """
        # Get recent games for this team (before the target date)
        games = (Game.objects
                 .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
                 .filter(date__lt=before_date)
                 .filter(home_score__isnull=False)  # Only completed games
                 .order_by('-date')[:self.num_games])

        game_ids = [g.id for g in games]

        if len(game_ids) < 3:
            # Not enough historical data
            raise InsufficientDataError(f"Team {team_id} has less than 3 games before {before_date}")

        # Aggregate team stats from these games
        stats = FootballTeamGameStat.objects.filter(
            team_id=team_id,
            game_id__in=game_ids
        ).aggregate(
            # Passing stats
            avg_pass_yards=Avg('pass_yards'),
            avg_pass_tds=Avg('pass_touchdowns'),
            avg_pass_attempts=Avg('pass_attempts'),
            avg_pass_completions=Avg('pass_completions'),

            # Rushing stats
            avg_rush_yards=Avg('rush_yards'),
            avg_rush_tds=Avg('rush_touchdowns'),
            avg_rush_attempts=Avg('rush_attempts'),

            # Turnovers (bad for offense)
            avg_interceptions=Avg('interceptions'),
            avg_fumbles_lost=Avg('fumbles_lost'),
        )

        # Calculate points scored (need to handle home/away)
        points_scored = []
        for game in games:
            if game.home_team_id == team_id:
                points_scored.append(game.home_score or 0)
            else:
                points_scored.append(game.away_score or 0)

        avg_points = np.mean(points_scored) if points_scored else 0

        # Compute derived features
        pass_attempts = stats['avg_pass_attempts'] or 1  # Avoid division by zero
        completion_pct = (stats['avg_pass_completions'] or 0) / pass_attempts * 100

        return {
            'off_pass_yards': stats['avg_pass_yards'] or 0,
            'off_pass_tds': stats['avg_pass_tds'] or 0,
            'off_completion_pct': completion_pct,
            'off_rush_yards': stats['avg_rush_yards'] or 0,
            'off_rush_tds': stats['avg_rush_tds'] or 0,
            'off_total_yards': (stats['avg_pass_yards'] or 0) + (stats['avg_rush_yards'] or 0),
            'off_points_scored': avg_points,
            'off_turnovers': (stats['avg_interceptions'] or 0) + (stats['avg_fumbles_lost'] or 0),
        }

    def extract_team_defensive_features(self, team_id: int, before_date: date) -> dict:
        """
        Extract defensive performance features for a team.

        For defense, we look at what the OPPONENT did against this team
        (i.e., how many yards/points did opponents score against them).
        """
        # Get recent games
        games = (Game.objects
                 .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
                 .filter(date__lt=before_date)
                 .filter(home_score__isnull=False)
                 .order_by('-date')[:self.num_games])

        game_ids = [g.id for g in games]

        if len(game_ids) < 3:
            raise InsufficientDataError(f"Team {team_id} has less than 3 games before {before_date}")

        # Get opponent stats from these games (what opponents did AGAINST this team)
        opponent_stats = FootballTeamGameStat.objects.filter(
            game_id__in=game_ids
        ).exclude(
            team_id=team_id  # Exclude this team's own stats
        ).aggregate(
            avg_pass_yards_allowed=Avg('pass_yards'),
            avg_rush_yards_allowed=Avg('rush_yards'),
            avg_pass_tds_allowed=Avg('pass_touchdowns'),
            avg_rush_tds_allowed=Avg('rush_touchdowns'),
        )

        # Defensive team stats (sacks, interceptions)
        def_stats = FootballTeamGameStat.objects.filter(
            team_id=team_id,
            game_id__in=game_ids
        ).aggregate(
            avg_def_sacks=Avg('def_sacks'),
            avg_def_ints=Avg('def_interceptions'),
            avg_def_fumbles_forced=Avg('def_fumbles_forced'),
        )

        # Points allowed
        points_allowed = []
        for game in games:
            if game.home_team_id == team_id:
                points_allowed.append(game.away_score or 0)  # Opponent is away team
            else:
                points_allowed.append(game.home_score or 0)  # Opponent is home team

        avg_points_allowed = np.mean(points_allowed) if points_allowed else 0

        return {
            'def_pass_yards_allowed': opponent_stats['avg_pass_yards_allowed'] or 0,
            'def_rush_yards_allowed': opponent_stats['avg_rush_yards_allowed'] or 0,
            'def_total_yards_allowed': (opponent_stats['avg_pass_yards_allowed'] or 0) +
                                       (opponent_stats['avg_rush_yards_allowed'] or 0),
            'def_points_allowed': avg_points_allowed,
            'def_sacks': def_stats['avg_def_sacks'] or 0,
            'def_interceptions': def_stats['avg_def_ints'] or 0,
            'def_turnovers_forced': (def_stats['avg_def_ints'] or 0) +
                                    (def_stats['avg_def_fumbles_forced'] or 0),
        }

    def extract_situational_features(self, game: Game, team_id: int) -> dict:
        """
        Extract situational/contextual features for a specific game.

        These capture the circumstances of the game, not team performance.
        """
        is_home = game.home_team_id == team_id

        # Check if it's a dome game (weather doesn't matter indoors)
        is_dome = game.roof in ['dome', 'closed', 'retractable']

        # Calculate rest days since last game
        last_game = (Game.objects
                     .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
                     .filter(date__lt=game.date)
                     .filter(home_score__isnull=False)
                     .order_by('-date')
                     .first())

        if last_game:
            rest_days = (game.date - last_game.date).days
        else:
            rest_days = 7  # Default to normal rest

        return {
            'is_home': 1 if is_home else 0,  # Binary: 1 = home, 0 = away
            'temperature': game.temp if game.temp and not is_dome else 70,  # Default to 70°F for domes
            'wind': game.wind if game.wind and not is_dome else 0,
            'is_dome': 1 if is_dome else 0,
            'rest_days': min(rest_days, 14),  # Cap at 14 (bye week)
        }

    def extract_trend_features(self, team_id: int, before_date: date) -> dict:
        """
        Extract trend/momentum features.

        Win streaks and recent form can indicate team confidence and momentum.
        """
        # Get last 5 games
        games = (Game.objects
                 .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
                 .filter(date__lt=before_date)
                 .filter(home_score__isnull=False)
                 .order_by('-date')[:5])

        wins = 0
        current_streak = 0
        streak_type = None  # 'W' or 'L'

        for game in games:
            if game.home_team_id == team_id:
                won = game.home_score > game.away_score
            else:
                won = game.away_score > game.home_score

            if won:
                wins += 1
                if streak_type is None:
                    streak_type = 'W'
                    current_streak = 1
                elif streak_type == 'W':
                    current_streak += 1
                else:
                    break  # Streak ended
            else:
                if streak_type is None:
                    streak_type = 'L'
                    current_streak = -1
                elif streak_type == 'L':
                    current_streak -= 1
                else:
                    break  # Streak ended

        win_pct = wins / len(games) if games else 0.5

        return {
            'recent_win_pct': win_pct,
            'current_streak': current_streak,  # Positive = winning, negative = losing
        }

    def build_game_features(self, game: Game) -> np.ndarray:
        """
        Build complete feature vector for a game.

        This combines features for BOTH teams into a single vector.
        The model learns how the difference/interaction between
        home and away team features predicts the outcome.

        Returns:
            numpy array of features, ready for ML model
        """
        home_team_id = game.home_team_id
        away_team_id = game.away_team_id
        game_date = game.date

        # Extract all features for home team
        home_off = self.extract_team_offensive_features(home_team_id, game_date)
        home_def = self.extract_team_defensive_features(home_team_id, game_date)
        home_sit = self.extract_situational_features(game, home_team_id)
        home_trend = self.extract_trend_features(home_team_id, game_date)

        # Extract all features for away team
        away_off = self.extract_team_offensive_features(away_team_id, game_date)
        away_def = self.extract_team_defensive_features(away_team_id, game_date)
        away_sit = self.extract_situational_features(game, away_team_id)
        away_trend = self.extract_trend_features(away_team_id, game_date)

        # Combine into feature vector
        # Order matters and must be consistent between training and prediction!
        features = [
            # Home team offensive features
            home_off['off_pass_yards'],
            home_off['off_pass_tds'],
            home_off['off_completion_pct'],
            home_off['off_rush_yards'],
            home_off['off_rush_tds'],
            home_off['off_total_yards'],
            home_off['off_points_scored'],
            home_off['off_turnovers'],

            # Home team defensive features
            home_def['def_pass_yards_allowed'],
            home_def['def_rush_yards_allowed'],
            home_def['def_total_yards_allowed'],
            home_def['def_points_allowed'],
            home_def['def_sacks'],
            home_def['def_interceptions'],
            home_def['def_turnovers_forced'],

            # Home situational
            home_sit['is_home'],  # Always 1 for home team
            home_sit['temperature'],
            home_sit['wind'],
            home_sit['is_dome'],
            home_sit['rest_days'],

            # Home trends
            home_trend['recent_win_pct'],
            home_trend['current_streak'],

            # Away team offensive features
            away_off['off_pass_yards'],
            away_off['off_pass_tds'],
            away_off['off_completion_pct'],
            away_off['off_rush_yards'],
            away_off['off_rush_tds'],
            away_off['off_total_yards'],
            away_off['off_points_scored'],
            away_off['off_turnovers'],

            # Away team defensive features
            away_def['def_pass_yards_allowed'],
            away_def['def_rush_yards_allowed'],
            away_def['def_total_yards_allowed'],
            away_def['def_points_allowed'],
            away_def['def_sacks'],
            away_def['def_interceptions'],
            away_def['def_turnovers_forced'],

            # Away situational
            away_sit['is_home'],  # Always 0 for away team
            away_sit['temperature'],
            away_sit['wind'],
            away_sit['is_dome'],
            away_sit['rest_days'],

            # Away trends
            away_trend['recent_win_pct'],
            away_trend['current_streak'],
        ]

        return np.array(features, dtype=np.float32)

    @staticmethod
    def get_feature_names() -> list:
        """
        Return names of all features in order.
        Useful for feature importance analysis.
        """
        prefixes = ['home', 'away']
        names = []

        for prefix in prefixes:
            # Offensive
            names.extend([
                f'{prefix}_off_pass_yards',
                f'{prefix}_off_pass_tds',
                f'{prefix}_off_completion_pct',
                f'{prefix}_off_rush_yards',
                f'{prefix}_off_rush_tds',
                f'{prefix}_off_total_yards',
                f'{prefix}_off_points_scored',
                f'{prefix}_off_turnovers',
            ])
            # Defensive
            names.extend([
                f'{prefix}_def_pass_yards_allowed',
                f'{prefix}_def_rush_yards_allowed',
                f'{prefix}_def_total_yards_allowed',
                f'{prefix}_def_points_allowed',
                f'{prefix}_def_sacks',
                f'{prefix}_def_interceptions',
                f'{prefix}_def_turnovers_forced',
            ])
            # Situational
            names.extend([
                f'{prefix}_is_home',
                f'{prefix}_temperature',
                f'{prefix}_wind',
                f'{prefix}_is_dome',
                f'{prefix}_rest_days',
            ])
            # Trends
            names.extend([
                f'{prefix}_recent_win_pct',
                f'{prefix}_current_streak',
            ])

        return names


class InsufficientDataError(Exception):
    """Raised when there's not enough historical data to extract features."""
    pass
