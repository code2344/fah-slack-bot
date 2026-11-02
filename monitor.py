import logging
import os

import dotenv

from database import get_slack_user, update_donor_stats
from fah_api import get_team_members

logger = logging.getLogger(__name__)

dotenv.load_dotenv()
TEAM_ID = os.environ.get("FAH_TEAM_ID")


def check_team_updates(client, channel_id):
    members = get_team_members(TEAM_ID)

    logger.info("Checking %d Folding@home members", len(members))

    for member in members:
        donor_id = member["id"]
        donor_name = member["name"]
        donor_rank = member["rank"]
        points = member["score"]
        wus = member["wus"]

        changes = update_donor_stats(
            TEAM_ID,
            donor_id,
            points,
            wus
        )

        if changes is None:
            logger.info("no changes yet, baseline created for %s!", donor_name)
            continue

        if changes["wus"] <=0:
            continue

        slack_user = get_slack_user(donor_id)

        if slack_user:
            contributor = f"<@{slack_user}>"
        else:
            contributor = donor_name

        logger.info(
            "%s: +%d WUs, +%d points",
            donor_name,
            changes["wus"],
            changes["points"]
        )

        # Announcement would go here but i'm going to just log it for now!
        logger.info("would announce that %s earned %d WUs", contributor, changes["wus"])
