import json
import os
import requests
from pathlib import Path

from flask import Flask, Response
from dotenv import load_dotenv

env_path = Path('../') / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
VERIFICATION_TOKEN = os.getenv('VERIFICATION_TOKEN')

def post_request_to_navi(url, data):
    r = requests.post(url,data)
    return r

if __name__ == '__main__':

    url = 'http://7c52e481f984.ngrok.io/slack/events'
    data_dict = {'token': VERIFICATION_TOKEN,
                 'type':' url_verification',
                 'challenge': 'challenge_response!'}
    jsonData = json.dumps(data_dict)

    r = post_request_to_navi(url=url, data=jsonData)
    print(r.status_code)
    print(r.content)
