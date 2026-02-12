from django.db import models
from players.models import Player


class DraftSession(models.Model):
    SCORING_CHOICES = [
        ('PPR', 'PPR'),
        ('HALF', 'Half PPR'),
        ('STD', 'Standard'),
    ]
    STATUS_CHOICES = [
        ('setup', 'Setup'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    num_teams = models.IntegerField(default=10)
    num_rounds = models.IntegerField(default=15)
    user_team_position = models.IntegerField(default=1)
    current_round = models.IntegerField(default=1)
    current_pick = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='setup')
    scoring_format = models.CharField(max_length=10, choices=SCORING_CHOICES, default='PPR')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_picks(self):
        return self.num_teams * self.num_rounds

    def get_team_for_pick(self, overall_pick):
        """Snake draft order: odd rounds 1->N, even rounds N->1"""
        round_num = (overall_pick - 1) // self.num_teams + 1
        position_in_round = (overall_pick - 1) % self.num_teams
        if round_num % 2 == 1:
            return position_in_round + 1
        else:
            return self.num_teams - position_in_round

    def __str__(self):
        return f"Draft #{self.id} ({self.status})"


class DraftPick(models.Model):
    session = models.ForeignKey(DraftSession, on_delete=models.CASCADE, related_name='picks')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team_number = models.IntegerField()
    round_number = models.IntegerField()
    overall_pick = models.IntegerField()
    is_user = models.BooleanField(default=False)

    class Meta:
        ordering = ['overall_pick']
        unique_together = [('session', 'overall_pick'), ('session', 'player')]

    def __str__(self):
        return f"Pick #{self.overall_pick}: {self.player.name} (Team {self.team_number})"
