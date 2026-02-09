"""
Prediction Model Tracking

This model tracks different versions of our trained ML models.
When we retrain the model (e.g., with new season data), we save a new version
and can compare performance metrics over time.

Why track versions?
1. Reproducibility - Know exactly which model made a prediction
2. A/B testing - Compare different model versions
3. Rollback - If a new model performs poorly, switch back to a previous one
4. Audit trail - See how model accuracy improves over time
"""

from django.db import models


class PredictionModelVersion(models.Model):
    """
    Tracks trained ML model versions and their performance metrics.

    Each time we train a new model, we create a record here with:
    - The version identifier
    - Which seasons were used for training
    - How well the model performed on test data
    - File paths to the saved model files
    """

    # Version identifier (e.g., "v1", "v2", "2024-01-15")
    version = models.CharField(max_length=50, primary_key=True)

    # When this model was trained
    created_at = models.DateTimeField(auto_now_add=True)

    # Which seasons were used for training (e.g., [2020, 2021, 2022, 2023, 2024])
    # Stored as JSON array
    training_seasons = models.JSONField(default=list)

    # Number of games used for training
    training_samples = models.IntegerField(default=0)

    # Performance Metrics (evaluated on held-out test data)
    # ---------------------------------------------------------

    # Winner prediction accuracy (0.0 to 1.0)
    # e.g., 0.65 means the model correctly predicted the winner 65% of the time
    winner_accuracy = models.FloatField(default=0.0)

    # Mean Absolute Error for spread prediction
    # e.g., 7.5 means on average, predictions are off by 7.5 points
    spread_mae = models.FloatField(default=0.0)

    # Mean Absolute Error for total points prediction
    total_mae = models.FloatField(default=0.0)

    # File paths to saved model files (relative to trained_models/)
    winner_model_path = models.CharField(max_length=255, blank=True)
    spread_model_path = models.CharField(max_length=255, blank=True)
    total_model_path = models.CharField(max_length=255, blank=True)

    # Is this the currently active model for predictions?
    # Only one version should be active at a time
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = " (active)" if self.is_active else ""
        return f"Model {self.version}{status} - Accuracy: {self.winner_accuracy:.1%}"

    def activate(self):
        """
        Make this the active model.
        Deactivates all other versions first.
        """
        PredictionModelVersion.objects.update(is_active=False)
        self.is_active = True
        self.save()
