"""
Workers for automating ground truthing tasks.
"""
from os import environ

import click

from .cmds import volume as volume_grp

ROUTING_KEY = "gt.#"
ENABLED = True if environ.get("GT_WORKER") else False


@click.group(
    "gt",
    help="Type help gt <subcommand> for information on ground truth commands.",
    add_help_option=False,
)
@click.pass_context
def cmd_grp(ctx, *args, **kwargs):
    pass


cmd_grp.add_command(volume_grp)
