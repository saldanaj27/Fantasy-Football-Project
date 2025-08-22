from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=5)
    city = models.CharField(max_length=50)
    logo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.city} {self.name}"