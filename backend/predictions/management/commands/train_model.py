"""
Django Management Command: Train Prediction Model

This command orchestrates the entire training pipeline:
1. Load historical game data from specified seasons
2. Extract features for each game
3. Train the ML models
4. Evaluate performance with cross-validation
5. Save the trained models to disk
6. Record the model version in the database

Usage:
    python manage.py train_model --start-season 2020 --end-season 2024

This will:
- Train on games from 2020-2024 seasons
- Save models to backend/predictions/trained_models/
- Create a PredictionModelVersion record in the database
"""

import os
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from predictions.features import FeatureExtractor
from predictions.ml_models import GamePredictionModel, get_feature_importance
from predictions.models import PredictionModelVersion
from predictions.training import TrainingDataBuilder


class Command(BaseCommand):
    help = "Train the game prediction ML model on historical data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--start-season",
            type=int,
            default=2020,
            help="First season to include in training (default: 2020)",
        )
        parser.add_argument(
            "--end-season",
            type=int,
            default=2024,
            help="Last season to include in training (default: 2024)",
        )
        parser.add_argument(
            "--model-version",
            type=str,
            default=None,
            help="Version identifier (default: auto-generated from date)",
        )
        parser.add_argument(
            "--activate",
            action="store_true",
            help="Make this the active model for predictions",
        )
        parser.add_argument(
            "--num-games",
            type=int,
            default=5,
            help="Number of prior games to use for feature averaging (default: 5)",
        )

    def handle(self, *args, **options):
        start_season = options["start_season"]
        end_season = options["end_season"]
        num_games = options["num_games"]

        # Generate version identifier
        version = options["model_version"] or datetime.now().strftime("v%Y%m%d_%H%M%S")

        self.stdout.write(
            self.style.NOTICE(
                f'\n{"="*60}\n'
                f"Training Game Prediction Model\n"
                f'{"="*60}\n'
                f"Seasons: {start_season} - {end_season}\n"
                f"Version: {version}\n"
                f"Features from last {num_games} games\n"
                f'{"="*60}\n'
            )
        )

        # Step 1: Build training data
        self.stdout.write(
            self.style.NOTICE("\n[Step 1/4] Building training dataset...")
        )
        seasons = list(range(start_season, end_season + 1))
        builder = TrainingDataBuilder(seasons=seasons, num_games_for_features=num_games)

        try:
            X, y_winner, y_spread, y_total = builder.build()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error building training data: {e}"))
            return

        if len(X) < 100:
            self.stdout.write(
                self.style.ERROR(
                    f"Insufficient training data: only {len(X)} games found. "
                    f"Need at least 100 games for reliable training."
                )
            )
            return

        # Step 2: Train the models
        self.stdout.write(self.style.NOTICE("\n[Step 2/4] Training ML models..."))
        model = GamePredictionModel()
        metrics = model.train(X, y_winner, y_spread, y_total)

        # Step 3: Save trained models to disk
        self.stdout.write(self.style.NOTICE("\n[Step 3/4] Saving models to disk..."))
        model_dir = os.path.join(settings.BASE_DIR, "predictions", "trained_models")
        paths = model.save(model_dir, version)

        # Step 4: Get feature importance (educational insight)
        self.stdout.write(
            self.style.NOTICE("\n[Step 4/4] Analyzing feature importance...")
        )
        feature_names = FeatureExtractor.get_feature_names()
        importance = get_feature_importance(model, feature_names)

        # Show top 10 most important features
        self.stdout.write("\nTop 10 Most Important Features:")
        self.stdout.write("-" * 40)
        for i, (name, score) in enumerate(list(importance.items())[:10], 1):
            bar = "█" * int(score * 100)
            self.stdout.write(f"{i:2}. {name:35} {score:.3f} {bar}")

        # Save model version to database
        model_version = PredictionModelVersion.objects.create(
            version=version,
            training_seasons=seasons,
            training_samples=len(X),
            winner_accuracy=metrics["winner_accuracy"],
            spread_mae=metrics["spread_mae"],
            total_mae=metrics["total_mae"],
            winner_model_path=paths["winner_model_path"],
            spread_model_path=paths["spread_model_path"],
            total_model_path=paths["total_model_path"],
        )

        if options["activate"]:
            model_version.activate()
            self.stdout.write(self.style.SUCCESS(f"\nModel {version} is now ACTIVE"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"\nModel saved but not activated. Run with --activate flag or use:\n"
                    f'  PredictionModelVersion.objects.get(version="{version}").activate()'
                )
            )

        # Final summary
        self.stdout.write(self.style.SUCCESS(f"""
{"="*60}
TRAINING COMPLETE
{"="*60}
Version:          {version}
Training samples: {len(X)} games
Seasons:          {start_season} - {end_season}

Performance Metrics:
  Winner Accuracy: {metrics["winner_accuracy"]:.1%}
  Spread MAE:      {metrics["spread_mae"]:.2f} points
  Total MAE:       {metrics["total_mae"]:.2f} points

Model files saved to:
  {model_dir}/

WHAT DO THESE METRICS MEAN?
---------------------------
- Winner Accuracy: How often the model correctly picks the winner
  (60-65% is good for NFL, where any team can beat any other)

- Spread MAE (Mean Absolute Error): Average error in point spread
  (7-10 points is typical; NFL games are hard to predict exactly)

- Total MAE: Average error in total points prediction
  (8-12 points is typical)
{"="*60}
"""))
