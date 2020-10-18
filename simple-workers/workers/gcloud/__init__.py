"""
Workers for doing stuff on gcloud.
"""
from os import environ

import click

from .buckets import bucket as bucket_grp
from .buckets import buckets as buckets_grp
from .service_accounts import service_accounts as sa_grp

ROUTING_KEY = "gcloud.#"
ENABLED = True if environ.get("GCLOUD_WORKER") else False


@click.group(
    "gcloud",
    help="Type help gcloud <subcommand> for information.",
    add_help_option=False,
)
@click.option(
    "--project",
    "-p",
    type=str,
    nargs=1,
    help="Project name.",
    default=lambda: environ["DEFAULT_GCP_PROJECT"],
    show_default=environ["DEFAULT_GCP_PROJECT"],
)
@click.pass_context
def cmd_grp(ctx, *args, **kwargs):
    ctx.obj["project"] = kwargs["project"]


cmd_grp.add_command(bucket_grp)
cmd_grp.add_command(buckets_grp)
cmd_grp.add_command(sa_grp)
