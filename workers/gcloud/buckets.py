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

    properties = [f"Owner: {bucket.owner}"]
    properties.append(f"Created: {bucket.time_created}")
    properties.append(f"Location: {bucket.location}")
    properties.append(f"Location Type: {bucket.location_type}")
    properties.append(f"Storage Class: {bucket.storage_class}")
    msg = "\n".join(properties)
    return f"```{msg}```"


@bucket.command("iam", help="View IAM Policy for a bucket.", add_help_option=False)
@click.option(
    "--name", "-n", type=str, required=True, nargs=1, help="Name of the bucket."
)
@click.pass_context
def iam(ctx, *args, **kwargs):
    storage_client = storage.Client()
    bucket = storage_client.bucket(kwargs["name"])
    policy = bucket.get_iam_policy()
    msg = "\n".join(f"Role: {k}, members: {v}" for k, v in policy.items())
    return f"```{msg}```"
