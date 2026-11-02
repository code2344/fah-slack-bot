import logging
import os
from turtle import dot
import dotenv

from fah_api import get_team_members
from database import update_member_stats

logger = logging.getLogger(__name__)

dotenv.load_dotenv()
TEAM_ID = os.environ.get("FAH_TEAM_ID")

