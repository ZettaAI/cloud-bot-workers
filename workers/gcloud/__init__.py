"""
Workers for doing stuff on gcloud.
"""

from click import Group
from click import Context

from .buckets import bucket as bucket_grp
from .service_accounts import service_accounts as sa_grp

ROUTING_KEY = "gcloud.#"


cmd_grp = Group("gcloud", help="Type help gcloud <subcommand> for information.", add_help_option=False)
cmd_grp.add_command(bucket_grp)
cmd_grp.add_command(sa_grp)

