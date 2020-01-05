"""
Workers for doing stuff on gcloud.
"""

from click import Group
from click import Context

from .buckets import cmd_grp as bucket_grp

ROUTING_KEY = "gcloud.#"


cmd_grp = Group("gcloud", add_help_option=False)
cmd_grp.add_command(bucket_grp)

