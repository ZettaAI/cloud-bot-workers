"""
Display help for avaiable commands.
"""
from json import dumps
from json import loads
from typing import List
from typing import Union
from typing import Iterable
from collections import OrderedDict


from click import Group
from click import Context
from click import Command
from requests import post
from requests import codes

from . import config
from . import amqp_cnxn
from .slack import Response as SlackResponse

from .gcloud import cmd_grp as gcloud_grp

ROUTING_KEY = "help.#"
cmd_grps = OrderedDict()

# insert alphabetically
cmd_grps["gcloud"] = gcloud_grp


def _get_main_help_msg():
    """
    Main help message when user types `help`.
    List of available commands registered in `cmd_grps`.
    """
    msg_cmds = "\n".join(f"{cmd}" for cmd in cmd_grps.keys())
    msg = "Following is a list of commands currently available.\n"
    msg += f"```{msg_cmds}```"
    msg += "\nType `help <command>` for more information about the `command`"
    return msg


def _get_nested_command(grp: Group, names: Iterable[str]) -> Union[Group, Command]:
    """Recursively find nested command and get it's help."""
    if len(names) == 1:
        return grp.get_command(Context(grp, info_name=grp.name), names[0])
    else:
        child_grp = grp.get_command(Context(grp, info_name=grp.name), names[0])
        return _get_nested_command(child_grp, names[1:])


def _get_help_msg(cmds: List[str]):
    """Returns main or nested help message."""
    if len(cmds) == 1:
        return _get_main_help_msg()
    else:
        root_grp_or_cmd = cmd_grps[cmds[1]]
        nested_grp_or_cmd = (
            root_grp_or_cmd
            if len(cmds) == 2
            else _get_nested_command(root_grp_or_cmd, cmds[2:])
        )
        ctx = Context(nested_grp_or_cmd, info_name=" ".join(cmds[1:]))
        return f"```{nested_grp_or_cmd.get_help(ctx)}```"


def callback(ch, method, properties, body):
    """
    Entrypoint for the `help` worker.
    It can be started with `python -m workers.help`.
    """
    event = loads(body)["event"]
    cmds = event["user_cmd"].split()
    assert cmds[0] == "help"

    try:
        msg = _get_help_msg(cmds)
    except Exception as err:
        msg = ":warning: Something went wrong. Check help to see "
        msg += f"if your command is properly formatted.\n```{str(err)}```"
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

