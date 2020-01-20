from typing import List
from typing import Union
from typing import Iterable


from click import Group
from click import Context
from click import Command

from .db import is_admin
from .exceptions import PermissionDenied


def _get_main_help_msg(cmd_grps: dict):
    """
    Main help message when user types `help`.
    List of available commands registered in `cmd_grps`.
    """
    msg_cmds = "\n".join(f"{cmd}" for cmd in cmd_grps.keys())
    msg = "Following is a list of commands currently available.\n"
    msg += f"```{msg_cmds}```"
    msg += "\nType `help <command>` for more information about the `command`"
    return msg


def _get_nested_command(grp: Group, names: Iterable[str]) -> Union[Group, Command]:
    """Recursively find nested command and get it's help."""
    if len(names) == 1:
        return grp.get_command(Context(grp, info_name=grp.name), names[0])
    else:
        child_grp = grp.get_command(Context(grp, info_name=grp.name), names[0])
        return _get_nested_command(child_grp, names[1:])


def get_help_msg(cmd: str, cmd_grps: dict) -> str:
    """Returns main or nested help message."""
    cmds = cmd.split()
    assert cmds[0] == "help"
    if len(cmds) == 1:
        return _get_main_help_msg(cmd_grps)
    else:
        root_grp_or_cmd = cmd_grps[cmds[1]]
        nested_grp_or_cmd = (
            root_grp_or_cmd
            if len(cmds) == 2
            else _get_nested_command(root_grp_or_cmd, cmds[2:])
        )
        ctx = Context(nested_grp_or_cmd, info_name=" ".join(cmds[1:]))
        return f"```{nested_grp_or_cmd.get_help(ctx)}```"


def admin_check(user_id: str) -> str:
    if is_admin(user_id):
        return
    raise PermissionDenied(
        "You do not seem to have the necessary permissions to perform this action."
    )
