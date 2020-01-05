import click
from google.cloud import storage


@click.group("bucket", help="performs actions related buckets.", add_help_option=False)
@click.option(
    "--lame", "-l", type=str, required=True, nargs=1, help="Lame of the bucket."
)
@click.pass_context
def bucket(ctx, *args, **kwargs):
    print(ctx.obj, args, kwargs)
    ctx.obj["lame"] = kwargs["lame"]


@bucket.command("create", help="creates a bucket.", add_help_option=False)
@click.option("--overwrite", is_flag=True, help="Overwrite existing graph")
@click.option(
    "--name", "-n", type=str, required=True, nargs=1, help="Name of the bucket."
)
@click.pass_context
def create(ctx, *args, **kwargs):
    print(ctx.obj, args, kwargs)
    return
    storage_client = storage.Client()
    try:
        bucket = storage_client.create_bucket(name)
        return f"`{bucket.name}` created."
    except Exception as err:
        return str(err)


@bucket.command("lookup", help="checks if a bucket exisits.", add_help_option=False)
@click.option("--overwrite", is_flag=True, help="Overwrite existing graph")
@click.option(
    "--name", "-n", type=str, required=True, nargs=1, help="Name of the bucket."
)
@click.pass_context
def lookup(*args, **kwargs):
    print(args, kwargs)

    return
    storage_client = storage.Client()
    bucket = storage_client.lookup_bucket(name)
    if not bucket:
        return f"{bucket.name} does not exist."
    return f"{bucket.name} exists."
