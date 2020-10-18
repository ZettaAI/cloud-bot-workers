import click


@click.group("volume", help="Perform actions on a given volume.", add_help_option=False)
@click.pass_context
def volume(ctx, *args, **kwargs):
    """Group for volume commands."""


@volume.command(
    "preview",
    help="Preview volume in Neuroglancer. Takes a GCS path (gs://...) as input.",
    add_help_option=False,
)
@click.argument("path", type=str, required=True)
@click.pass_context
def preview(ctx, *args, **kwargs):
    from .gtbot import preview_helper

    print("running preview")

    ctx.obj["long_job"] = True
    ctx.obj["broadcast"] = True
    return preview_helper(kwargs["path"], ctx.obj["user_id"])


@volume.command(
    "create_cutouts",
    help="Create a cutout of given volume(s). Takes a neuroglancer link as input.",
    add_help_option=False,
)
@click.argument("url", type=str, required=True)
@click.pass_context
def create_cutouts(ctx, *args, **kwargs):
    from .gtbot import cutout_helper

    # https://neuromancer-seung-import.appspot.com/?json_url=https://poyntr.co/json/TVNqdURxQ05iNTZE

    ctx.obj["long_job"] = True
    ctx.obj["broadcast"] = True
    return cutout_helper(kwargs["url"], ctx.obj["user_id"])


@volume.command(
    "create_bboxes",
    help="Create a bbox of given volume(s). Takes a neuroglancer link as input.",
    add_help_option=False,
)
@click.argument("url", type=str, required=True)
@click.pass_context
def create_bboxes(ctx, *args, **kwargs):
    from .gtbot import bbox_helper

    ctx.obj["long_job"] = True
    ctx.obj["broadcast"] = True
    return bbox_helper(kwargs["url"], ctx.obj["user_id"])
