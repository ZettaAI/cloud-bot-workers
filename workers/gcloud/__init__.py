"""
Workers for doing stuff on gcloud.
"""

from click import Group
from click import Context

ROUTING_KEY = "gcloud.#"


cmd_grp = Group("gcloud", add_help_option=False)
ctx = Context(cmd_grp, info_name="gcloud")

