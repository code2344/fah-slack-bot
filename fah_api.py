import requests
import logger
import os
from dotenv import load_dotenv

load_dotenv()

FOLDING_STATS_BASE_URL = os.environ.get("FOLDING_STATS_BASE_URL")

def get_team_members(team_id):
    response = requests.get(

    )
