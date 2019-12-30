from json import dumps
from json import loads

from requests import post
from requests import codes

from . import ROUTING_KEY
from .buckets import create
from .. import config
from .. import amqp_cnxn

# TODO
# design as plugins that can be "registered"
# each plugin should perform a task, must have a help description
# plugins planned
#   1. view projects
#   2. view/create/delete buckets
#      support parameters like zone and region
#   3. view permissions
#   4. change permissions?
#   5. transfer between buckets
# Needs topics for each category and one for help
# Worker can return information regarding help command


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    request_body = loads(body)
    event = request_body["event"]
    # print(dumps(request_body, indent=4))

    bucket_name = request_body["event"]["text"].split()[1]
    r = post(
        config.SLACK_API_POST,
        headers={"Authorization": f"Bearer {config.SLACK_API_TOKEN}"},
        data={
            "channel": event["channel"],
            "thread_ts": event["ts"],
            "text": create(bucket_name),
        },
    )
    assert r.status_code == codes.ok  # pylint: disable=no-member


channel = amqp_cnxn.channel()
channel.exchange_declare(exchange=config.EXCHANGE_NAME, exchange_type="topic")

queue_name = channel.queue_declare("", exclusive=True).method.queue
channel.queue_bind(
    exchange=config.EXCHANGE_NAME, queue=queue_name, routing_key=ROUTING_KEY
)
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print(" [*] Waiting for work. To exit press CTRL+C")
channel.start_consuming()

