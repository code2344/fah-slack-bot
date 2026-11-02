import os
import sqlite3
import logging
import database
import argparse

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

parser = argparse.ArgumentParser(
    description="Folding@home slack bot"
)

parser.add_argument(
    "-d", "--debug",
    action="store_true",
    help="Enable debug output"
)

py_args = parser.parse_args()

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
logger = logging.getLogger(__name__)

team_id = os.environ.get("FAH_TEAM_ID")

db = database

logging.basicConfig(
    level=logging.DEBUG if py_args.debug else logging.INFO,  # Capture INFO, WARNING, ERROR, and CRITICAL
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log", mode="a")]
)

def can_you_convert_it_to_int(arg):
    try:
        int(arg)
        return True
    except ValueError:
        return False


@app.command("/fah")
def handle_fah(ack, respond, command):
    ack() # send acknowledgement to slack otherwise it will error

    text = command["text"].strip() # bolt returns the command as a dictionary and the part after the /fah [here] is the text part
    parts = text.split(maxsplit=1) # split it into the parts of the command so we know the subcommand and args

    subcommand = parts[0].lower() if parts else "help" # the subcommand is the first element of parts which is index zero, if it's empty then display help
    argument = parts[1] if len(parts) > 1 else None # argument is the bit after subcmd if there actually is one

    user_id = command["user_id"]

    logger.info(user_id + " ran command: " + command["command"] + " " + command["text"])

    if subcommand == "help":
        respond(
            "*Available commands*:\n"
            "`/fah help` - prints this help dialog\n"
            "You ran: " + "`" + str(command["command"]) + " " + str(command["text"] + "`")
        )
    elif subcommand == "link":
        if not argument:
            respond("Usage: `/fah link <donor id>`\nThis is from the link you get if you click your username on <https://stats.foldingathome.org/team/" + str(team_id) + "|this page>.")
        else:
            if can_you_convert_it_to_int(argument):
                #loop will go here
            else:
                respond("Usage: `/fah link <donor id>`\nError: it appears you put in an invalid donor id.\nThis is from the link you get if you click your username on <https://stats.foldingathome.org/team/" + str(team_id) + "|this page>.")



# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    logger.info("App started!")
