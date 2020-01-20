"""
Display help for avaiable commands.
"""

from os import path
from os import listdir
from json import dumps
from json import loads
from collections import OrderedDict


from requests import post
from requests import codes

from . import config
from . import amqp_cnxn
from .types import HelpWorker
from .slack import Response as SlackResponse


ROUTING_KEY = "help.#"


def load_cmds() -> OrderedDict:
    cmd_grps = OrderedDict()
    cmd_folder = path.abspath(path.join(path.dirname(__file__)))
    for filename in listdir(cmd_folder):
        if filename == "__pycache__":
            continue
        filepath = f"{cmd_folder}/{filename}"
        if path.isdir(filepath):
            mod = __import__("workers." + filename)
            grp = getattr(mod, filename).cmd_grp
            cmd_grps[grp.name] = grp
    return cmd_grps


if __name__ == "__main__":
    worker = HelpWorker(load_cmds())
    worker.start(ROUTING_KEY, worker.callback)
