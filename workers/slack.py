from typing import Any
from typing import Dict
from json import loads

from requests import get
from requests import post

from . import config
import time


class Response:
    """
    Determines the destination for response based on the `event`.
    `event` is a JSON object received from Slack.
    """

    def __init__(self, event: Dict[str, Any]):
        self.event = event
        self.auth_headers = {
            "Authorization": f"Bearer {config.SLACK_API_BOT_ACCESS_TOKEN}"
        }

    def send(self, message: str, long_job: bool = False):
        """
        Make call to slack api.
        If the latest message is not the command run,
        then the response is posted in a thread.
        This is needed for long running jobs.
        """
        if (not "channel_type" in self.event) or (
            long_job and self._check_post_to_thread()
        ):
            return self.post_to_thread(
                message, self.event["event_ts"], self.event["channel"]
            )
        else:
            return self.post_to_user(message, self.event["channel"])

    def post_to_thread(self, message: str, ts: str, channel: str = None):
        response = post(
            config.SLACK_API_MESSAGE_POST,
            headers=self.auth_headers,
            data={"channel": channel, "text": message, "thread_ts": ts},
        )
        return response

    def post_to_channel(self, message: str, channel: str):
        response = post(
            config.SLACK_API_MESSAGE_POST,
            headers=self.auth_headers,
            data={"channel": channel, "text": message,},
        )
        return response

    def post_to_user(self, message: str, user_channel: str):
        response = post(
            config.SLACK_API_MESSAGE_POST,
            headers=self.auth_headers,
            data={"channel": user_channel, "text": message},
        )
        return response

    def _check_post_to_thread(self):
        response = get(
            config.SLACK_API_CONVERSATION_HISTORY,
            headers=self.auth_headers,
            params={"channel": self.event["channel"], "limit": 1},
        )
        response = loads(response.content)
        return not response["messages"][0]["ts"] == self.event["ts"]

