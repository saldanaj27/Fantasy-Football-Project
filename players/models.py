from django.db import models
from django.conf import settings

class Player(models.Model):
    DEPTH_CHART_POSITION_CHOICES = [
        ("C", "Center"),
        ("CB", "Cornerback"),
        ("DB", "Defensive Back"),
        ("DL", "Defensive Line"),
        ("DT", "Defensive Tackle"),
        ("FS", "Free Safety"),
        ("G", "Offensive Guard"),
        ("ILB", "Inside Linebacker"),
        ("K", "Kicker"),
        ("LB", "Linebacker"),
        ("LS", "Long Snapper"),
        ("MLB", "Middle Linebacker"),
        ("NS", "Nose Tackle"),
        ("OLB", "Outside Linebacker"),
        ("P", "Punter"),
        ("QB", "Quarterback"),
        ("RB", "Running Back"),
        ("SS", "Strong Safety"),
        ("T", "Offensive Tackle"),
        ("TE", "Tight End"),
        ("WR", "Wide Receiver"),
    ]

    POSITION_CHOICES = [
        ("DB", "Defensive Back"),
        ("DL", "Defensive Line"),
        ("K", "Kicker"),
        ("LB", "Linebacker"),
        ("LS", "Long Snapper"),
        ("OL", "Offensive Lineman"),
        ("P", "Punter"),
        ("QB", "Quarterback"),
        ("RB", "Running Back"),
        ("TE", "Tight End"),
        ("WR", "Wide Receiver"),
    ]

    STATUS = [
        ("ACT", "Active"),
        ("CUT", "Cut"),
        ("DEV", "Practice Squad"),
        ("INA", "Inactive"),
        ("RES", "Reserve List"),
    ]
    
    name = models.CharField(max_length=100)
    depth_chart_position = models.CharField(max_length=25, choices=DEPTH_CHART_POSITION_CHOICES)
    height = models.IntegerField(default=0, null=True)
    weight = models.IntegerField(default=0, null=True)
    position = models.CharField(max_length=25, choices=POSITION_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.position})"
    
# class UserPlayer(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     player = models.ForeignKey(Player, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ("user", "player")