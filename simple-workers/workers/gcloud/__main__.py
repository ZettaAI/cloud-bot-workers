from CloudBotWorkersCommon.types import Worker

from . import cmd_grp
from . import ROUTING_KEY

worker = Worker(cmd_grp)
worker.start(ROUTING_KEY, worker.callback)
