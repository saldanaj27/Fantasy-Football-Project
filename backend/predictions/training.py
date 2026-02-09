"""
Training Data Builder

This module builds the training dataset from historical games.
It coordinates the FeatureExtractor to create feature vectors
and extracts the corresponding target values (what we're predicting).

TRAINING DATA STRUCTURE:
------------------------
For machine learning, we need:
1. X (features): What the model sees when making predictions
2. y (targets): The correct answers the model learns from

For each historical game, we create:
- X: Feature vector from FeatureExtractor (44 features)
- y_winner: 1 if home team won, 0 if away team won
- y_spread: home_score - away_score (e.g., 7 means home won by 7)
- y_total: home_score + away_score (e.g., 45 total points)

WHY EXCLUDE EARLY SEASON GAMES?
-------------------------------
The feature extractor needs historical data to calculate averages.
For Week 1-3 games, there isn't enough prior data for reliable features.
We exclude these to avoid garbage-in-garbage-out.
"""

import numpy as np
from datetime import date
from tqdm import tqdm

from games.models import Game
from .features import FeatureExtractor, InsufficientDataError


class TrainingDataBuilder:
    """
    Builds training datasets from historical game data.

    Example usage:
        builder = TrainingDataBuilder(seasons=[2020, 2021, 2022, 2023])
        X, y_winner, y_spread, y_total = builder.build()
    """

    def __init__(self, seasons: list[int], num_games_for_features: int = 5):
        """
        Args:
            seasons: List of seasons to include (e.g., [2020, 2021, 2022])
            num_games_for_features: How many prior games to average for features
        """
        self.seasons = seasons
        self.feature_extractor = FeatureExtractor(num_games=num_games_for_features)

    def build(self, min_week: int = 4) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Build training data from completed historical games.

        Args:
            min_week: Minimum week number to include (earlier weeks have
                     insufficient history for reliable features)

        Returns:
            Tuple of (X, y_winner, y_spread, y_total):
            - X: Feature matrix of shape (n_games, 44)
            - y_winner: Binary array (1=home win, 0=away win)
            - y_spread: home_score - away_score
            - y_total: home_score + away_score
        """
        # Get all completed games from specified seasons
        games = (Game.objects
                 .filter(season__in=self.seasons)
                 .filter(week__gte=min_week)  # Skip early weeks
                 .filter(home_score__isnull=False)  # Only completed games
                 .filter(stage='REG')  # Regular season only (playoffs might be different)
                 .select_related('home_team', 'away_team')
                 .order_by('date'))

        print(f"Found {games.count()} games from seasons {self.seasons}")
        print(f"Extracting features (this may take a moment)...")

        X_list = []
        y_winner_list = []
        y_spread_list = []
        y_total_list = []

        skipped_count = 0

        for game in tqdm(games, desc="Processing games"):
            try:
                # Extract features for this game
                features = self.feature_extractor.build_game_features(game)

                # Calculate target values
                home_win = 1 if game.home_score > game.away_score else 0
                spread = game.home_score - game.away_score
                total = game.home_score + game.away_score

                X_list.append(features)
                y_winner_list.append(home_win)
                y_spread_list.append(spread)
                y_total_list.append(total)

            except InsufficientDataError:
                # Skip games where we don't have enough history
                skipped_count += 1
                continue

        if skipped_count > 0:
            print(f"Skipped {skipped_count} games due to insufficient historical data")

        print(f"Successfully processed {len(X_list)} games")

        # Convert lists to numpy arrays
        X = np.array(X_list, dtype=np.float32)
        y_winner = np.array(y_winner_list, dtype=np.int32)
        y_spread = np.array(y_spread_list, dtype=np.float32)
        y_total = np.array(y_total_list, dtype=np.float32)

        # Print some statistics about the data
        print(f"\n=== Dataset Statistics ===")
        print(f"Total games: {len(X)}")
        print(f"Feature dimensions: {X.shape[1]}")
        print(f"Home win rate: {y_winner.mean():.1%}")
        print(f"Average spread: {y_spread.mean():.1f} (positive = home team favored)")
        print(f"Average total: {y_total.mean():.1f} points")

        return X, y_winner, y_spread, y_total


def train_test_split_by_season(
    games_seasons: list[int],
    test_season: int
) -> tuple[list[int], list[int]]:
    """
    Split data by season for time-based validation.

    WHY SPLIT BY SEASON?
    --------------------
    In sports prediction, we can't use random train/test splits because:
    1. We'd be training on future games to predict past games (data leakage)
    2. Teams change year-to-year (roster, coaching, etc.)

    Instead, we train on older seasons and test on a newer season.
    This simulates real-world usage: train on 2020-2023, predict 2024.

    Args:
        games_seasons: All available seasons
        test_season: Season to hold out for testing

    Returns:
        Tuple of (train_seasons, test_seasons)
    """
    train_seasons = [s for s in games_seasons if s < test_season]
    test_seasons = [test_season]

    return train_seasons, test_seasons
