import os
import sys
from json import dumps

import pika
import slack
from google.cloud import storage

from . import ROUTING_KEY
from .. import config
from .. import amqp_cnxn


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    # storage_client = storage.Client()
    # bucket_name = "akhilesh-test2"
    # bucket = storage_client.create_bucket(bucket_name)
    # response = client.chat_postMessage(
    #     channel="#general", text=f"{bucket.name} created!"
    # )
    # assert response["ok"]


channel = amqp_cnxn.channel()

channel.exchange_declare(exchange=config.EXCHANGE_NAME, exchange_type="topic")

result = channel.queue_declare("", exclusive=True)
queue_name = result.method.queue
channel.queue_bind(
    exchange=config.EXCHANGE_NAME, queue=queue_name, routing_key=ROUTING_KEY
)
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print(" [*] Waiting for work. To exit press CTRL+C")
channel.start_consuming()

