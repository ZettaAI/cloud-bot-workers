"""
Workers for doing stuff on gcloud.
"""
import os

from click import Group
from click import Context
from click import Option

from .buckets import bucket as bucket_grp
from .service_accounts import service_accounts as sa_grp

ROUTING_KEY = "gcloud.#"


project = Option(
    ["--project", "-p",],
    type=str,
    nargs=1,
    help="Project name.",
    default=lambda: os.environ["DEFAULT_PROJECT"],
    show_default=os.environ["DEFAULT_PROJECT"],
)


cmd_grp = Group(
    "gcloud",
    help="Type help gcloud <subcommand> for information.",
    add_help_option=False,
    params=[project],
)
cmd_grp.add_command(bucket_grp)
cmd_grp.add_command(sa_grp)

