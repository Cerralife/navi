import os
import random

from dotenv import load_dotenv
from slack import WebClient

from helpers import get_user_real_name

load_dotenv()

SLACK_TOKEN = os.getenv('SLACK_BOT_TOKEN')
DEFAULT_NAVI_CHANNEL = os.getenv('DEFAULT_NAVI_CHANNEL')


class Navi:

    def __init__(self):

        self.slack_client = WebClient(SLACK_TOKEN)
        self.current_hero = None
        self.current_hero_channel = None
        self.current_link = None
        self.group_channel_id = None


    def send_greeting(self, channel_id, user_id):
        user_rname = get_user_real_name(self.slack_client, user_id)
        message = f"Hello, {user_rname}! :tada:"
        self.slack_client.chat_postMessage(channel=channel_id, text=message)


    def start_navi(self, channel_id, scheduled=False):

        self.group_channel_id = channel_id

        if not scheduled:
            message = "Okay! I'll guide someone on their quest. *~"

        else:
            message = "\n".join([
                " ".join([
                    "Hey! The Great Deku Tree tasked me with finding the",
                    "next hero of song.",
                ]),

               "I'll be back with a tune for your ocarinas!"
            ])

        self.slack_client.chat_postMessage(channel=self.group_channel_id,
                                           text=message)

        self.ask_for_link(self.group_channel_id)


    def ask_for_link(self, channel_id):

        convo_members = self.slack_client. \
            conversations_members(channel=channel_id)

        member_list = convo_members["members"]

        self.hero_rname = 'Navi'
        while self.hero_rname == 'Navi':
            self.current_hero = random.choice(member_list)
            self.hero_rname = get_user_real_name(self.slack_client,
                                            self.current_hero)

        response = self.slack_client. \
            conversations_open(users=[self.current_hero])
        self.current_hero_channel = response["channel"]["id"]

        message = "\n".join([
            "Hey, listen! You've been chosen to share a song with your chums.",
            "",
            "Please share a Spotify or YouTube :toon_link: and I'll pass it along.",
            "",
            f"Remember, {self.hero_rname.split()[0]}, it's dangerous to go alone."
        ])

        self.slack_client.chat_postMessage(channel=self.current_hero_channel,
                                           text=message)


    def post_link(self, url):
        message = "\n".join([
            "Watch out!",
            "",
            f"I've got a :angst_link: from {self.hero_rname.split()[0]}:",
            "",
            url
        ])

        self.slack_client.chat_postMessage(channel=self.group_channel_id,
                                           text=message)

    def reset_navi(self):
        self.current_hero = None
        self.current_hero_channel = None
        self.current_link = None
        self.group_channel_id = None
