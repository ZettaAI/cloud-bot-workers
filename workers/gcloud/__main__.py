from . import cmd_grp
from . import ROUTING_KEY
from ..types import Worker

worker = Worker(cmd_grp)
worker.start(ROUTING_KEY, worker.callback)
