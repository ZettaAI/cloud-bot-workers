import click
from google.cloud import storage


@click.group("bucket", help="Actions related to buckets.", add_help_option=False)
@click.pass_context
def bucket(ctx, *args, **kwargs):
    """Group for bucket commands."""


@bucket.command("create", help="Creates a bucket.", add_help_option=False)
@click.option(
    "--name", "-n", type=str, required=True, nargs=1, help="Name of the bucket."
)
@click.pass_context
def create(ctx, *args, **kwargs):
    bucket = storage.Client().create_bucket(kwargs["name"])
    return f"Bucket `{bucket.name}` created."


@bucket.command("lookup", help="Checks if a bucket exisits.", add_help_option=False)
@click.option(
    "--name", "-n", type=str, required=True, nargs=1, help="Name of the bucket."
)
@click.pass_context
def lookup(ctx, *args, **kwargs):
    bucket = storage.Client().lookup_bucket(kwargs["name"])
    if not bucket:
        return f"Bucket `{bucket.name}` does not exist."
    return f"Bucket `{bucket.name}` exists."
