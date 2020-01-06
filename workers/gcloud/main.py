from json import dumps
from json import loads

from click import Context
from requests import post
from requests import codes

from . import cmd_grp
from . import ROUTING_KEY
from .. import config
from .. import amqp_cnxn
from ..slack import Response as SlackResponse

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


def invoke_cmd(cmd: str) -> str:
    ctx = Context(cmd_grp, info_name=cmd_grp.name, obj={})
    cmd_grp.parse_args(ctx, cmd.split()[1:])
    try:
        return cmd_grp.invoke(ctx)
    except Exception as err:
        return f":warning: Something went wrong.\n```{str(err)}```"


def callback(ch, method, properties, body):
    event = loads(body)["event"]
    message = invoke_cmd(event["user_cmd"])
    response = SlackResponse(event)
    req = response.send(message)
    assert req.status_code == codes.ok  # pylint: disable=no-member


channel = amqp_cnxn.channel()
channel.exchange_declare(exchange=config.EXCHANGE_NAME, exchange_type="topic")

queue_name = channel.queue_declare("", exclusive=True).method.queue
channel.queue_bind(
    exchange=config.EXCHANGE_NAME, queue=queue_name, routing_key=ROUTING_KEY
)
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print(" [*] Waiting for work. To exit press CTRL+C")
channel.start_consuming()

