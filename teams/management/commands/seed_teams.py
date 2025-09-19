import requests
from django.core.management.base import BaseCommand
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

        for team in data:
            if team["name"] != 'NFC' or team["name"] != 'AFC':
                team_id = team["id"]
                name = team["name"]
                city = team.get("city", "") # default is empty string
                abbreviation = team.get("code", "")
                logo_url = team.get("logo", "")
                
                Team.objects.update_or_create(
                    id=team_id,
                    defaults={"name": name, "city": city, "abbreviation": abbreviation, "logo_url": logo_url},
                )
