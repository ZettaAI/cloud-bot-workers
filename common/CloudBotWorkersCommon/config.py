from os import environ
from collections import namedtuple

from pika import BlockingConnection
from pika import ConnectionParameters
from pika.credentials import PlainCredentials


_config_fields = (
    "SLACK_API_USER_INFO",
    "SLACK_API_MESSAGE_POST",
    "SLACK_API_CONVERSATION_HISTORY",
    "SLACK_API_BOT_ACCESS_TOKEN",
    "AMQP_SERVICE_HOST",
    "AMQP_USERNAME",
    "AMQP_PASSWORD",
    "EXCHANGE_NAME",
)
_config_defaults = (
    environ.get("SLACK_API_USER_INFO", "https://slack.com/api/users.info"),
    environ.get("SLACK_API_MESSAGE_POST", "https://slack.com/api/chat.postMessage"),
    environ.get(
        "SLACK_API_CONVERSATION_HISTORY", "https://slack.com/api/conversations.history"
    ),
    environ["SLACK_API_BOT_ACCESS_TOKEN"],
    environ.get("AMQP_SERVICE_HOST", "localhost"),
    environ.get("AMQP_USERNAME", "guest"),
    environ.get("AMQP_PASSWORD", "guest"),
    environ.get("EXCHANGE_NAME", "cloud_bot"),
)
Config = namedtuple("Config", _config_fields, defaults=_config_defaults)
config = Config()

print(f"amqp host {config.AMQP_SERVICE_HOST}")
amqp_connection = BlockingConnection(
    ConnectionParameters(
        host=config.AMQP_SERVICE_HOST,
        credentials=PlainCredentials(config.AMQP_USERNAME, config.AMQP_PASSWORD),
    )
)
