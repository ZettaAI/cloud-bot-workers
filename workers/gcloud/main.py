from json import dumps
from json import loads

from . import ROUTING_KEY
from .buckets import create
from .. import config
from .. import amqp_cnxn


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))

    request_body = loads(body)
    print(dumps(request_body, indent=4))

    bucket_name = request_body["event"]["text"].split()[1]
    print(bucket_name)
    print(create(bucket_name))
    # call relevant function
    # send response

    # response = client.chat_postMessage(
    #     channel="#general", text=f"{bucket.name} created!"
    # )
    # assert response["ok"]


channel = amqp_cnxn.channel()
channel.exchange_declare(exchange=config.EXCHANGE_NAME, exchange_type="topic")

queue_name = channel.queue_declare("", exclusive=True).method.queue
channel.queue_bind(
    exchange=config.EXCHANGE_NAME, queue=queue_name, routing_key=ROUTING_KEY
)
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print(" [*] Waiting for work. To exit press CTRL+C")
channel.start_consuming()

