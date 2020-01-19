"""
Workers for commands that involve usage of CloudVolume.
CloudVolume supports multiple storage protocols.

https://github.com/seung-lab/cloud-volume
"""

import os

import click

from ..types import Worker
from .cmds import storage as storage_grp

ROUTING_KEY = "cv.#"


@click.group(
    "cv", help="Type help cv <subcommand> for information.", add_help_option=False,
)
@click.pass_context
def cv(ctx, *args, **kwargs):
    """Group for cloudvolume commands."""


cv.add_command(storage_grp)

worker = Worker(cv)
worker.start(ROUTING_KEY)

