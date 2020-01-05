from requests import post

from . import config


def post_to_channel(message: str, channel: str):
    response = post(
        config.SLACK_API_POST,
        headers={"Authorization": f"Bearer {config.SLACK_API_TOKEN}"},
        data={"channel": channel, "text": message,},
    )
    return response


def post_to_user(message: str):
    response = post(
        config.SLACK_API_POST,
        headers={"Authorization": f"Bearer {config.SLACK_API_TOKEN}"},
        data={"text": message,},
    )
    return response


def post_to_channel_thread(message: str, channel: str, ts):
    response = post(
        config.SLACK_API_POST,
        headers={"Authorization": f"Bearer {config.SLACK_API_TOKEN}"},
        data={"channel": channel, "text": message, "thread_ts": ts},
    )
    return response
