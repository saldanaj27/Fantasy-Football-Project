from django.db import models
from django.conf import settings
from players.models import Player

class Team(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=5)
    city = models.CharField(max_length=50)
    logo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
    

class Team_Players(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)



# * Model will be used in future versions *
# class UserTeam(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     team = models.ForeignKey(Team, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ("user", "team")