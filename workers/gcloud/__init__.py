"""
Workers for doing stuff on gcloud.
"""
import os

import click

from .buckets import bucket as bucket_grp
from .buckets import buckets as buckets_grp
from .service_accounts import service_accounts as sa_grp
from ..types import Worker

ROUTING_KEY = "gcloud.#"


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
    default=lambda: os.environ["DEFAULT_PROJECT"],
    show_default=os.environ["DEFAULT_PROJECT"],
)
@click.pass_context
def gcloud(ctx, *args, **kwargs):
    ctx.obj["project"] = kwargs["project"]


gcloud.add_command(bucket_grp)
gcloud.add_command(buckets_grp)
gcloud.add_command(sa_grp)


worker = Worker(gcloud)
worker.start(ROUTING_KEY)

