"""
Display help for avaiable commands.
"""
from json import dumps
from json import loads

from requests import post
from requests import codes

from . import config
from . import amqp_cnxn

from .gcloud import ctx as gcloud_ctx

ROUTING_KEY = "help.#"

cmd_ctxs = {"gcloud": gcloud_ctx}


def callback(ch, method, properties, body):
    request_body = loads(body)
    event = request_body["event"]

    message = request_body["event"]["text"].split()[1:]
    assert message[0] == "help"

    ctx = cmd_ctxs[message[1]]
    text = ctx.get_help()
    r = post(
        config.SLACK_API_POST,
        headers={"Authorization": f"Bearer {config.SLACK_API_TOKEN}"},
        data={"channel": event["channel"], "thread_ts": event["ts"], "text": text,},
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

