"""
Package for workers.
The workers listen to messages in queues from an exchange.
RabbitMQ is the messsage broker.
"""
import os
from collections import namedtuple

from dotenv import load_dotenv
from pika import BlockingConnection
from pika import ConnectionParameters
from pika.credentials import PlainCredentials


load_dotenv()

_config_fields = (
    "SLACK_API_TOKEN",
    "SLACK_SIGNING_SECRET",
    "AMQP_SERVICE_HOST",
    "AMQP_USERNAME",
    "AMQP_PASSWORD",
    "EXCHANGE_NAME",
)
_config_defaults = (
    os.environ["SLACK_API_TOKEN"],
    os.environ["SLACK_SIGNING_SECRET"],
    os.environ.get("AMQP_SERVICE_HOST", "localhost"),
    os.environ.get("AMQP_USERNAME", "guest"),
    os.environ.get("AMQP_PASSWORD", "guest"),
    os.environ.get("EXCHANGE_NAME", "cloud_bot"),
)
Config = namedtuple("Config", _config_fields, defaults=_config_defaults,)
config = Config()

amqp_cnxn = BlockingConnection(
    ConnectionParameters(
        host=config.AMQP_SERVICE_HOST,
        credentials=PlainCredentials(config.AMQP_USERNAME, config.AMQP_PASSWORD,),
    )
)

