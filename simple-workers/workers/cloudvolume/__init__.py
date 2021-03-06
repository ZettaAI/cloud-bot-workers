"""
Workers for commands that involve usage of CloudVolume.
CloudVolume supports multiple storage protocols.

https://github.com/seung-lab/cloud-volume
"""

from os import environ

import click

from .cmds import storage as storage_grp

ROUTING_KEY = "cv.#"
ENABLED = True if environ.get("CV_WORKER") else False


@click.group(
    "cv", help="Type help cv <subcommand> for information.", add_help_option=False,
)
@click.pass_context
def cmd_grp(ctx, *args, **kwargs):
    """Group for cloudvolume commands."""


cmd_grp.add_command(storage_grp)
