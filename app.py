import os
import sqlite3
import logging

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.command("/fah")
def handle_fah(ack, respond, command):
    ack() # send acknowledgement to slack otherwise it will error

    text = command["text"].strip() # bolt returns the command as a dictionary and the part after the /fah [here] is the text part
    parts = text.split(maxsplit=1) # split it into the parts of the command so we know the subcommand and args

    subcommand = parts[0].lower() if parts else "help" # the subcommand is the first element of parts which is index zero, if it's empty then display help
    argument = parts[1] if len(parts) > 1 else None # argument is the bit after subcmd if there actually is one

    user_id = command["user_id"]

    logging.info(user_id, " ran command: ", command["command"], " ", command["text"])
    
    if subcommand == "help":
        respond(
            "*Available commands*:\n"
            "`/fah help` - prints this help dialog\n"
            "You ran: " + "`" + str(command["command"]) + str(command["text"])
        )


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    logging.info("App started!")
