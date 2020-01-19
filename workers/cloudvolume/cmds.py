import os

import click
from cloudvolume import Storage


@click.group(
    "storage",
    help="Subset of functionality supported by CloudVolume Storage.",
    add_help_option=False,
)
@click.option(
    "--n-threads",
    "-n",
    type=int,
    required=False,
    nargs=1,
    help="Number of threads to perform the operation.",
    default=lambda: os.environ["CV_STORAGE_THREADS"],
    show_default=os.environ["CV_STORAGE_THREADS"],
)
@click.pass_context
def storage(ctx, *args, **kwargs):
    """Group for Storage commands."""
    ctx.obj["n_threads"] = kwargs["n_threads"]


@storage.command(
    "copy",
    help="Copy from source to destination. Paths must be protocols supported by CloudVolume.",
    add_help_option=False,
)
@click.argument("src_path", type=str, required=True)
@click.argument("dst_path", type=str, required=True)
@click.pass_context
def copy(ctx, *args, **kwargs):
    with Storage(kwargs["src_path"], n_threads=ctx.obj["n_threads"]) as src, Storage(
        kwargs["dst_path"], n_threads=ctx.obj["n_threads"]
    ) as dst:
        files = src.list_files(flat=True)
        contents = src.get_files(files)
        print(list(files), src._layer_path)
        dst.put_files(zip(files, contents))  # pylint: disable=no-member
    return f"Copied files from `{kwargs['src_path']}` to `{kwargs['dst_path']}`"


@storage.command(
    "move",
    help="Move from source to destination. "
    "Paths must be protocols supported by CloudVolume."
    "Warning: This will delete files in SRC_PATH.",
    add_help_option=False,
)
@click.argument("src_path", type=str, required=True)
@click.argument("dst_path", type=str, required=True)
@click.pass_context
def move(ctx, *args, **kwargs):
    with Storage(kwargs["src_path"], n_threads=ctx.obj["n_threads"]) as src, Storage(
        kwargs["dst_path"], n_threads=ctx.obj["n_threads"]
    ) as dst:
        files = src.list_files()
        dst.put_files(src.get_files(files))  # pylint: disable=no-member
        src.delete_files(files)
    return f"Moved files from `{kwargs['src_path']}` to `{kwargs['dst_path']}`"
