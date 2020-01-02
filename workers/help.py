"""
Display help for avaiable commands.
"""
from typing import Union
from typing import Iterable
from json import dumps
from json import loads


from click import Group
from click import Context
from click import Command
from requests import post
from requests import codes

from . import config
from . import amqp_cnxn

from .gcloud import cmd_grp as gcloud_grp

ROUTING_KEY = "help.#"

cmd_grps = {"gcloud": gcloud_grp}


def _get_nested_command(grp: Group, names: Iterable[str]) -> Union[Group, Command]:
    if len(names) == 1:
        return grp.get_command(Context(grp, info_name=grp.name), names[0])
    else:
        child_grp = grp.get_command(Context(grp, info_name=grp.name), names[0])
        return _get_nested_command(child_grp, names[1:])


def callback(ch, method, properties, body):
    request_body = loads(body)
    event = request_body["event"]

    cmds = request_body["event"]["text"].split()[1:]
    assert cmds[0] == "help"

    root_grp_or_cmd = cmd_grps[cmds[1]]
    nested_grp_or_cmd = (
        root_grp_or_cmd
        if len(cmds) == 2
        else _get_nested_command(root_grp_or_cmd, cmds[2:])
    )

    ctx = Context(nested_grp_or_cmd, info_name=" ".join(cmds[1:]))
    r = post(
        config.SLACK_API_POST,
        headers={"Authorization": f"Bearer {config.SLACK_API_TOKEN}"},
        data={
            "channel": event["channel"],
            # "thread_ts": event["ts"],
            "text": nested_grp_or_cmd.get_help(ctx),
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

