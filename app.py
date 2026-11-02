import argparse
import logging
import os
import threading
import time

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import database

load_dotenv()

parser = argparse.ArgumentParser(description="Folding@home slack bot")

parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")

parser.add_argument(
    "--invalid-slack-id",
    action="store_true",
    help="make it always think a slack id is like a random one",
)

py_args = parser.parse_args()

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
logger = logging.getLogger(__name__)

team_id = os.environ.get("FAH_TEAM_ID")

db = database

logging.basicConfig(
    level=logging.DEBUG if py_args.debug else logging.INFO,
    # Capture INFO, WARNING, ERROR, and CRITICAL
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log", mode="a")],
)


def can_you_convert_it_to_int(arg):
    try:
        int(arg)
        return True
    except ValueError:
        return False


@app.command("/fah")
def handle_fah(ack, respond, command):
    ack()  # send acknowledgement to slack otherwise it will error

    try:
        # bolt returns the command as a dictionary and the part after
        # the /fah [here] is the text part
        text = command["text"].strip()

        # split it into the parts of the command so we know the
        # subcommand and args
        parts = text.split(maxsplit=1)

        # the subcommand is the first element of parts which is index zero,
        # if it's empty then display help
        subcommand = parts[0].lower() if parts else "help"

        # argument is the bit after subcmd if there actually is one
        argument = parts[1] if len(parts) > 1 else None

        if py_args.invalid_slack_id:
            user_id = "X1234567890"
        else:
            user_id = command["user_id"]

        logger.info(
            user_id + " ran command: " + command["command"] + " " + command["text"]
        )

        if subcommand == "help":
            respond(
                "*Available commands*:\n"
                "`/fah help` - prints this help dialog\n"
                "You ran: "
                + "`"
                + str(command["command"])
                + " "
                + str(command["text"] + "`")
            )
        elif subcommand == "link":
            if not argument:
                logger.debug("Responding with usage because no argument was provided")
                respond(
                    "Usage: `/fah link <donor id>`\n"
                    "This is from the link you get if you click your username on <https://stats.foldingathome.org/team/"
                    + str(team_id)
                    + "|this page>."
                )
            else:
                if can_you_convert_it_to_int(argument):
                    logger.debug("ID is a number, saving as donor_id!")
                    donor_id = int(argument)
                    logger.debug(
                        "linking user " + str(user_id) + " to donor id " + str(donor_id)
                    )
                    result = db.link_user(user_id, donor_id)
                    if result == "link_success":
                        logger.INFO(
                            str(user_id)
                            + " was successfully linked to donor id "
                            + str(donor_id)
                        )
                        respond(
                            "Success! <@"
                            + str(user_id)
                            + "> linked to <https://stats.foldingathome.org/donor/id/"
                            + str(donor_id)
                            + "|Donor "
                            + str(donor_id)
                            + ">! run `/fah unlink <donor_id>` to unlink a specific donor ID, or run `/fah unlink all` to unlink all of your donor IDs."
                        )
                    elif result == "already_linked":
                        logger.info(
                            str(user_id) + " was already linked to " + str(donor_id)
                        )
                        respond("That account's already linked to you.")
                    elif result == "claimed":
                        respond(
                            "That account's already claimed!"
                        )  # TODO: add "who's claimed it" logic
                else:
                    respond(
                        "Usage: `/fah link <donor id>`\n"
                        "Error: it appears you put in an invalid donor id.\n"
                        "This is from the link you get if you click your username on <https://stats.foldingathome.org/team/"
                        + str(team_id)
                        + "|this page>."
                    )
        elif subcommand == "unlink":
            if not argument:
                logger.info("No user ID was provided")
                respond(
                    "Error: No user ID was provided. Use `all` to unlink all linked ids.\nUsage: `/fah unlink <donor id>` or `/fah unlink all`."
                )
            else:
                if can_you_convert_it_to_int(argument):
                    logger.debug("ID is a number, saving as donor_id!")
                    donor_id = int(argument)
                elif argument == "all":
                    logger.info("user requested deletion of all")
                    user_accounts = db.get_accounts(user_id)

                    for account in user_accounts:
                        print(account)
                else:
                    logger.info("Couldn't convert to int, invalid number.")
                    respond(
                        "Usage: `/fah unlink <donor id>` or `/fah unlink all`."
                        "Error: it appears you put in an invalid donor id.\n"
                        "This is from the link you get if you click your username on "
                        "<https://stats.foldingathome.org/team/"
                        + str(team_id)
                        + "|this page>."
                    )

    except Exception:
        logger.exception("Error handling command")

        respond("Oops! an unexpected error occured while processing your command.")


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    logger.info("App started!")
