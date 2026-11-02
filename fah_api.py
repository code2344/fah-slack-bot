import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

FOLDING_STATS_BASE_URL = os.environ.get("FOLDING_STATS_BASE_URL")

def get_team_members(team_id):
    response = requests.get(
        f"{FOLDING_STATS_BASE_URL}/teams/{team_id}/members",
        timeout=20
    )
    response.raise_for_status()
    return response.json()
    
