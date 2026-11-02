import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.environ.get("API_BASE_URL")

def get_team_members(team_id):
    response = requests.get(
        f"{API_BASE_URL}/teams/{team_id}/members",
        timeout=20
    )
    response.raise_for_status()
    data = response.json()

    headers = data[0]
    members = [
        dict(zip(headers, row))
        for row in data[1:]
    ]

    return members
    
    
