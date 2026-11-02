import logging
import os

from dotenv import load_dotenv
from slack_sdk.errors import SlackApiError
from slack_sdk.web import WebClient

from database import (
    get_pending_announcements,
    get_slack_user,
    mark_announncement_sent,
    process_team_members,
)
from fah_api import get_team_members

logger = logging.getLogger(__name__)

load_dotenv()
TEAM_ID = int(os.environ["FAH_TEAM_ID"])

def build_contribution_blocks(
    contributor,
    donor_id,
    donor_name,
    new_wus,
    new_points,
    total_wus,
    team_points):
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "*New Folding@home contribution!*\n"
                        f"{contributor} just completed "
                        f"*{new_wus:,} new work "
                        f"unit{'s' if new_wus != 1 else ''}* "
                        "for the Hack Club Unofficial team!"
                    )
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*+{new_points:,}*\nPoints earned"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*{total_wus:,}*\nTotal work units"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": (
                            f"Team points: {team_points / 1_000_000:.1f}M"
                            "\n"
                            f"<https://stats.foldingathome.org/donor/id/{donor_id}"
                            "|View donor stats>"
                        )
                    }
                ]
            }
        ]


def send_pending_announcements(client: WebClient, channel_id: str):
    pending = get_pending_announcements()

    for announcement in pending:
        donor_id = announcement["fah_donor_id"]
        donor_name = announcement["donor_name"]
        wus = announcement["wus_delta"]
        points = announcement["points_delta"]

        slack_user = get_slack_user(donor_id)

        if slack_user:
            contributor = f"<@{slack_user}>"
        else:
            contributor = donor_name

        blocks = build_contribution_blocks(
            contributor=contributor,
            donor_id=donor_id,
            donor_name=donor_name,
            new_wus=wus,
            new_points=points,
            total_wus=announcement["total_wus"],
            team_points=announcement["team_points"],
        )

        try:
            response = client.chat_postMessage(
                channel=channel_id,
                text=None,
                blocks=blocks
            )

            mark_announncement_sent(announcement["id"], response["ts"])

            logger.info("sent announcement #%d for %s", announcement["id"], donor_name)
        except SlackApiError:
            logger.exception("Slack failed to send announcement #%d", announcement["id"])
            break

def check_team_updates(client: WebClient, channel_id: str):
    try:
        members = get_team_members(TEAM_ID)

        logger.info(
            "Checking %d Folding@home members",
            len(members)
        )

        queued = process_team_members(TEAM_ID, members)

        logger.info(
            "Queued %d new announcements",
            queued
        )

    except Exception:
        logger.exception("Failed to fetch or process team statistics")

    # Always retry previously queued announcements,
    # even if the Folding@home API is unavailable.
    send_pending_announcements(client, channel_id)

#def check_team_updates(client, channel_id):
#    members = get_team_members(TEAM_ID)

#    logger.info("Checking %d Folding@home members", len(members))

#    for member in members:
#        donor_id = member["id"]
#        donor_name = member["name"]
#        donor_rank = member["rank"]
#        points = member["score"]
#        wus = member["wus"]

#        changes = update_donor_stats(TEAM_ID, donor_id, points, wus)

#        if changes is None:
#            logger.info("no changes yet, baseline created for %s!", donor_name)
#            continue

#        if changes["wus"] <= 0:
#            continue

#        slack_user = get_slack_user(donor_id)

#        if slack_user:
#            contributor = f"<@{slack_user}>"
#        else:
#            contributor = donor_name
#
#        logger.info(
#            "%s: +%d WUs, +%d points", donor_name, changes["wus"], changes["points"]
#        )
#
#        # Announcement would go here but i'm going to just log it for now!
#        logger.info("would announce that %s earned %d WUs", contributor, changes["wus"])
