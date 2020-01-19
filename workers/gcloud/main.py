from json import dumps
from json import loads

from requests import post
from requests import codes
from click import Context
from click.exceptions import MissingParameter

from . import ROUTING_KEY
from . import gcloud as cmd_grp
from .. import config
from .. import amqp_cnxn
from ..slack import Response as SlackResponse


def invoke_cmd(cmd: str) -> str:
    try:
        ctx = Context(cmd_grp, info_name=cmd_grp.name, obj={})
        cmd_grp.parse_args(ctx, cmd.split()[1:])
        return cmd_grp.invoke(ctx)
    except MissingParameter as err:
        return f":warning: Something went wrong.\n```{err.format_message()}```"
    except Exception as err:
        return f":warning: Something went wrong. Please refer `help`.\n```{err}```"


def callback(ch, method, properties, body):
    event = loads(body)["event"]
    # print(dumps(event, indent=2))
    msg = invoke_cmd(event["user_cmd"])
    response = SlackResponse(event)
    assert response.send(msg).status_code == codes.ok  # pylint: disable=no-member


channel = amqp_cnxn.channel()
channel.exchange_declare(exchange=config.EXCHANGE_NAME, exchange_type="topic")

queue_name = channel.queue_declare("", exclusive=True).method.queue
channel.queue_bind(
    exchange=config.EXCHANGE_NAME, queue=queue_name, routing_key=ROUTING_KEY
)
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print(" [*] Waiting for work. To exit press CTRL+C")
channel.start_consuming()

