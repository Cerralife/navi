def get_user_real_name(slack_client, user_id):
    user_info = slack_client.users_info(user=user_id)
    user = user_info["user"]
    user_rname = user["real_name"]
    return user_rname

def read_app_mention(payload):
    message = payload["event"]

    if message.get("subtype") is None:
        channel_id = message["channel"]
        user_id = message["user"]
        command = message.get("text")

        return channel_id, user_id, command

def read_link_shared(event_data):
    return event_data["links"][0]["url"]



