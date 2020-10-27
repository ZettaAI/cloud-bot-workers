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
@click.option(
    "--voxel-size",
    "-v",
    type=float,
    required=False,
    nargs=3,
    help="Voxel Size (x,y,z)",
    default=[10, 10, 40],
    show_default=True,
)
@click.option(
    "--transpose",
    "-t",
    is_flag=True,
    help="Optionally transpose image data with (1, 0, 2)",
)
@click.argument("path", type=str, required=True)
@click.pass_context
def preview(ctx, *args, **kwargs):
    from .preview import upload
    from .utils import get_username

    slack_response = ctx.obj["slack_response"]
    slack_response.long_job = True
    slack_response.send("Working on it, check the thread for updates.")

    author = get_username(slack_response.event["user"])
    voxel_size = kwargs["voxel_size"]
    upload(kwargs["path"], author, voxel_size, slack_response, kwargs["transpose"])
    slack_response.send("Job completed.")


@volume.command(
    "create_cutouts",
    help="Create a cutout of given volume(s). Takes a neuroglancer link as input.",
    add_help_option=False,
)
@click.argument("url", type=str, required=True)
@click.pass_context
def create_cutouts(ctx, *args, **kwargs):
    # https://neuromancer-seung-import.appspot.com/?json_url=https://poyntr.co/json/TVNqdURxQ05iNTZE
    from .cutout import create_cutouts

    slack_response = ctx.obj["slack_response"]
    slack_response.long_job = True
    slack_response.send("Working on it, check the thread for updates.")

    cutout_parameters = {"mip": 1, "pad": [256, 256, 4]}
    create_cutouts(kwargs["url"], cutout_parameters, slack_response)
    slack_response.send("Job completed.")


@volume.command(
    "create_bboxes",
    help="Create a bbox of given volume(s). Takes a neuroglancer link as input.",
    add_help_option=False,
)
@click.argument("url", type=str, required=True)
@click.pass_context
def create_bboxes(ctx, *args, **kwargs):
    from .bbox import convert_pt_to_bbox

    slack_response = ctx.obj["slack_response"]
    slack_response.long_job = True
    slack_response.send("Working on it, check the thread for updates.")

    bbox_parameters = {"dim": [40920, 40920, 2048]}
    result = convert_pt_to_bbox(kwargs["url"], bbox_parameters)
    slack_response.send(result, broadcast=True)
    slack_response.send("Job completed.")
