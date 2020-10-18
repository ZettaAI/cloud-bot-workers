"""
Display help for avaiable commands.
"""
from collections import OrderedDict


from CloudBotWorkersCommon import config
from CloudBotWorkersCommon import amqp_connection


ROUTING_KEY = "help-simple-workers.#"


def load_cmds() -> OrderedDict:
    from os import path
    from os import listdir

    cmd_grps = OrderedDict()
    cmd_folder = path.abspath(path.join(path.dirname(__file__)))
    for filename in listdir(cmd_folder):
        if filename == "__pycache__":
            continue
        filepath = f"{cmd_folder}/{filename}"
        if path.isdir(filepath):
            mod = __import__("workers." + filename)
            mod = getattr(mod, filename)
            if mod.ENABLED:
                grp = mod.cmd_grp
                cmd_grps[grp.name] = grp
    return cmd_grps


if __name__ == "__main__":
    from CloudBotWorkersCommon.types import HelpWorker

    worker = HelpWorker(load_cmds())
    worker.start(ROUTING_KEY, worker.callback)
