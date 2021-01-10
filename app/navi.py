from datetime import datetime
import json
import os
import random

from dotenv import load_dotenv
from pandas.io.sql import DatabaseError
from slack import WebClient
from tabulate import tabulate

from db import NaviDB
from helpers import get_user_real_name, get_channel_name


load_dotenv()


SLACK_TOKEN = os.getenv('SLACK_BOT_TOKEN')
DEFAULT_NAVI_CHANNEL = os.getenv('DEFAULT_NAVI_CHANNEL')
CREATE_QUERY_REL_PATH = './queries/create_navi_history.sql'

cwd = os.path.abspath(os.path.dirname(__file__))
create_query_path = os.path.abspath(os.path.join(cwd, CREATE_QUERY_REL_PATH))


class Navi:

    def __init__(self):

        self.slack_client = WebClient(SLACK_TOKEN)
        self.current_hero = None
        self.current_hero_channel = None
        self.current_link = None
        self.group_channel_id = None
        self.db = NaviDB()

    def set_group_name(self):
        if self.group_channel_id is not None:
            self.group_channel_name = get_channel_name(self.slack_client,
                                                       self.group_channel_id)
        else:
            e = 'Trying to set channel name but no channel_id has been set.'
            raise Exception(e)

    def send_greeting(self, user_id):
        user_rname = get_user_real_name(self.slack_client, user_id)
        message = f"Hello, {user_rname}! :tada:"
        self.slack_client.chat_postMessage(channel=self.group_channel_id,
                                           text=message)

    def start_navi(self):

        message = "Okay! I'll guide someone on their quest. *~"
        self.slack_client.chat_postMessage(channel=self.group_channel_id,
                                           text=message)

        self.ask_for_link(self.group_channel_id)

    def ask_for_link(self, group_channel_id):

        convo_members = self.slack_client. \
            conversations_members(channel=group_channel_id)

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

    def _create_history_table(self):

        with open(create_query_path, 'r') as fin:
            create_query = fin.read()
        create_query = create_query.format(group_channel_name=self.group_channel_name)

        self.db.write_to_db(create_query)


    def save_and_post_link(self, url):

        self._create_history_table()
        self.save_link_to_db(hero_rname=self.hero_rname, url=url)

        message = "\n".join([
            "Watch out!",
            "",
            f"I've got a :angst_link: from {self.hero_rname.split()[0]}:",
            "",
            url
        ])

        self.slack_client.chat_postMessage(channel=self.group_channel_id,
                                           text=message)


    def save_link_to_db(self, hero_rname, url):

        insert_query = '\n'.join([
               f"INSERT INTO navi_history_{self.group_channel_name}",
                "VALUES (",
                f"'{datetime.now()}',",
                f"'{hero_rname}',",
                f"'{url}'"
                ")"
            ])

        self.db.write_to_db(insert_query)


    def query_navidb(self, command):

        query = command.lower()
        query = query.split("query",1)[1]
        query = query.replace('```', '')
        try:
            df = self.db.read_from_db(query)

            if df.empty:
                message = 'No rows to return!'
            else:
                message = tabulate(df, tablefmt="grid")

        except DatabaseError as e:
            message = f'Query failed!\n\n{e}'

        self.slack_client.chat_postMessage(channel=self.group_channel_id,
                                          text=message)


    def reset_navi(self):
        self.current_hero = None
        self.current_hero_channel = None
        self.current_link = None

if __name__ == '__main__':
    pass

