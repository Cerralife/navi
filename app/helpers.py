def get_user_real_name(slack_client, user_id):
    user_info = slack_client.users_info(user=user_id)
    user = user_info["user"]
    user_rname = user["real_name"]
    return user_rname

def get_channel_name(slack_client, channel_id):
    channel_info = slack_client.conversations_info(channel=channel_id)
    channel = channel_info["channel"]
    channel_name = channel["name"]
    return channel_name

def read_app_mention(payload):
    message = payload["event"]

    if message.get("subtype") is None:
        channel_id = message["channel"]
        user_id = message["user"]
        command = message.get("text")

        return channel_id, user_id, command

def read_link_shared(event_data):
    return event_data["links"][0]["url"]



