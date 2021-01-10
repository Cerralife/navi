import os
import logging

from dotenv import load_dotenv
from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
from threading import Thread

from helpers import read_app_mention, read_link_shared
from navi import Navi


load_dotenv()
logging.basicConfig(level=logging.DEBUG)


# This `app` represents the existing Flask app
app = Flask(__name__)

SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
VERIFICATION_TOKEN = os.getenv('VERIFICATION_TOKEN')
GREETINGS = ["hello", "hello there", "hey"]


#instantiating Navi
NAVI = Navi()


# An example of one of the Flask app's routes
@app.route("/")
def event_hook(request):
    json_dict = json.loads(request.body.decode("utf-8"))
    if json_dict["token"] != VERIFICATION_TOKEN:
        return {"status": 403}

    if "type" in json_dict:
        if json_dict["type"] == "url_verification":
            response_dict = {"challenge": json_dict["challenge"]}
            return response_dict
    return {"status": 500}
    # return


slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET, "/slack/events", app
)


@slack_events_adapter.on("app_mention")
def reply_to_mention(payload):
    channel_id, user_id, command = read_app_mention(payload)

    setattr(NAVI, 'group_channel_id', channel_id)
    NAVI.set_group_name()

    if any(item in command.lower() for item in GREETINGS):
        thread = Thread(target=NAVI.send_greeting, kwargs={'user_id':user_id})
        thread.start()
        return Response(status=200)

    elif 'start' in command.lower():
        thread = Thread(target=NAVI.start_navi)
        thread.start()
        return Response(status=200)

    elif 'query' in command.lower():
        thread = Thread(target=NAVI.query_navidb, kwargs={"command":command})
        thread.start()
        return Response(status=200)


@slack_events_adapter.on("link_shared")
def react_to_link(payload):
    event_data = payload["event"]
    channel_id = event_data["channel"]
    url = read_link_shared(event_data)

    if channel_id != NAVI.current_hero_channel:
        logging.debug("Link request channel != Hero channel")

    else:
        thread  = Thread(target=NAVI.save_and_post_link, kwargs={"url":url})
        thread.start()
        return Response(status=200)


# Start the server on port 3000
if __name__ == "__main__":
  app.run(port=4901)


