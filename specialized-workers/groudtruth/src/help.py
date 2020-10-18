"""
Display help for avaiable commands.
"""
from collections import OrderedDict

from CloudBotWorkersCommon import config
from CloudBotWorkersCommon import amqp_connection


ROUTING_KEY = "help-gt-workers.#"


if __name__ == "__main__":
    from CloudBotWorkersCommon.types import HelpWorker
    from . import cmd_grp

    worker = HelpWorker({"gt": cmd_grp})
    worker.start(ROUTING_KEY, worker.callback)
