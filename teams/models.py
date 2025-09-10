from django.db import models
from django.conf import settings

class Team(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=5)
    city = models.CharField(max_length=50)
    color = models.CharField(max_length=15, default="#000000")
    alternate_color = models.CharField(max_length=15, default="#ffffff")
    logo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.city} {self.name}"
    
class UserTeam(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "team")