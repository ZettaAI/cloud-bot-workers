from typing import Any
from typing import Dict


from requests import post

from . import config


class Response:
    """
    Determines the destination for response based on the `event`.
    `event` is a JSON object received from Slack.
    """

    def __init__(self, event: Dict[str, Any]):
        self.event = event

    def send(self, message: str):
        """Make call to slack api."""
        if "channel_type" in self.event:
            return self.post_to_user(message, self.event["channel"])
        return self.post_to_thread(
            message, self.event["event_ts"], self.event["channel"]
        )

    def post_to_thread(self, message: str, ts: str, channel: str = None):
        response = post(
            config.SLACK_API_POST,
            headers={"Authorization": f"Bearer {config.SLACK_API_TOKEN}"},
            data={"channel": channel, "text": message, "thread_ts": ts},
        )
        return response

    def post_to_channel(self, message: str, channel: str):
        response = post(
            config.SLACK_API_POST,
            headers={"Authorization": f"Bearer {config.SLACK_API_TOKEN}"},
            data={"channel": channel, "text": message,},
        )
        return response

    def post_to_user(self, message: str, user_channel: str):
        response = post(
            config.SLACK_API_POST,
            headers={"Authorization": f"Bearer {config.SLACK_API_TOKEN}"},
            data={"channel": user_channel, "text": message},
        )
        return response

