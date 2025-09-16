import requests
from django.core.management.base import BaseCommand
from games.models import Game
from teams.models import Team
from django.conf import settings


class Command(BaseCommand):
    help = "Seed Teams data from Sports API from specific season"
    def handle(self, *args, **kwargs):
        season = "2023"
        api_key = settings.SPORTS_API_KEY
        url = "https://v1.american-football.api-sports.io/teams?league=1&season=" + season

        headers = {
            "x-apisports-key": api_key,
            "x-rapidapi-host": "v1.american-football.api-sports.io"
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            self.stderr.write(self.style.ERROR("Failed to fetch teams from API"))
            return
        
        data = response.json().get("response", [])

        for item in data:
            if item["name"] != 'NFC' or item["name"] != 'AFC':
                team_id = item["id"]
                name = item["name"]
                city = item.get("city", "")
                abbreviation = item.get("code", "")
                logo_url = item.get("logo", "")
                
                Team.objects.update_or_create(
                    id=team_id,
                    defaults={"name": name, "city": city, "abbreviation": abbreviation, "logo_url": logo_url},
                )
