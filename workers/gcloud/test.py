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


cmd = "gcloud bucket iam -n akhilesh-test-1"
cmd = "gcloud bucket iam -n akhilesh-test-1 add -r roles/storage.objectViewer -m user:akhileshhalageri@gmail.com"
ctx = Context(cmd_grp, info_name=cmd_grp.name, obj={})
cmd_grp.parse_args(ctx, cmd.split()[1:])
cmd_grp.invoke(ctx)

