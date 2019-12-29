"""
Package for workers.
The workers listen to messages in queues from an exchange.
RabbitMQ is the messsage broker.
"""

from dotenv import load_dotenv

load_dotenv()

EXCHANGE_NAME = "cloud_bot"
