import click
from google.cloud import storage


PREDEFINED_BUKCET_IAM_ROLES = {
    "read": "roles/storage.objectViewer",
    "write": "roles/storage.objectCreator",
    "admin": "roles/storage.objectAdmin",
}


@click.command("buckets", help="List avialable buckets.", add_help_option=False)
def list(ctx, *args, **kwargs):
    bucket = storage.Client().list_buckets()
    return f"Bucket `{bucket.name}` created."


@click.group("bucket", help="Actions related to buckets.", add_help_option=False)
@click.argument("name", type=str)
@click.pass_context
def bucket(ctx, *args, **kwargs):
    ctx.obj["name"] = kwargs["name"]
    """Group for bucket commands."""


###################
# BUCKET operations
###################


@bucket.command("create", help="Creates a bucket.", add_help_option=False)
@click.pass_context
def create(ctx, *args, **kwargs):
    bucket = storage.Client().create_bucket(ctx.obj["name"])
    return f"Bucket `{bucket.name}` created."


@bucket.command("lookup", help="Checks if a bucket exisits.", add_help_option=False)
@click.pass_context
def lookup(ctx, *args, **kwargs):
    bucket = storage.Client().lookup_bucket(ctx.obj["name"])
    if not bucket:
        return f"Bucket `{bucket.name}` does not exist."

    properties = [f"Owner: {bucket.owner}"]
    properties.append(f"Created: {bucket.time_created}")
    properties.append(f"Location: {bucket.location}")
    properties.append(f"Location Type: {bucket.location_type}")
    properties.append(f"Storage Class: {bucket.storage_class}")
    msg = "\n".join(properties)
    return f"```{msg}```"


################
# UTIL functions
################


def _get_roles(**kwargs):
    roles = []
    for role in kwargs["role"]:
        try:
            roles.append(PREDEFINED_BUKCET_IAM_ROLES[role])
        except KeyError:
            roles.append(role)
    return roles


def _bucket_iam_helper(bucket_name: str, member: str, roles: list, add: bool = True):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    policy = bucket.get_iam_policy()

    msg = []
    if add:
        for role in roles:
            policy[role].add(member)
            msg.append(f"Added {member} with role {role} to {bucket_name}.")

    else:
        for role in roles:
            policy[role].discard(member)
            msg.append(f"Removed {member} with role {role} from {bucket_name}.")
    bucket.set_iam_policy(policy)
    return "\n".join(msg)


#######################
# BUCKET IAM operations
#######################


@bucket.group(
    "iam",
    help="View IAM Policy for a bucket.",
    add_help_option=False,
    invoke_without_command=True,
)
@click.pass_context
def iam(ctx, *args, **kwargs):
    """
    Group for bucket IAM commands.
    Lists current IAM roles and members.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(ctx.obj["name"])
    policy = bucket.get_iam_policy()
    msg = "\n".join(f"Role: {k}, members: {v}" for k, v in policy.items())
    return f"```{msg}```"


@iam.command("add", help="Add a new member to an IAM Policy.", add_help_option=False)
@click.option(
    "--member",
    "-m",
    type=str,
    required=True,
    nargs=1,
    help="Email with appropriate prefix. "
    "For external users only accounts associated with Gmail will work. "
    "(cloud.google.com/iam/docs/overview#cloud-iam-policy)",
)
@click.option(
    "--role",
    "-r",
    type=str,
    required=True,
    multiple=True,
    help="Available options: read, write, admin",
)
@click.pass_context
def add_bucket_iam_member(ctx, *args, **kwargs):
    """
    Add a new member to an IAM Policy.
    For users external to the organization, only accounts associated with Gmail will work.
    """
    name = ctx.obj["name"]
    member = kwargs["member"]
    msg = _bucket_iam_helper(name, member, _get_roles(**kwargs), True)
    return f"```{msg}```"


@iam.command("remove", help="Remove member from an IAM Policy.", add_help_option=False)
@click.option(
    "--member",
    "-m",
    type=str,
    required=True,
    nargs=1,
    help="Email with appropriate prefix. "
    "(cloud.google.com/iam/docs/overview#cloud-iam-policy)",
)
@click.option(
    "--role",
    "-r",
    type=str,
    required=True,
    multiple=True,
    help="Available options: read, write, admin",
)
@click.pass_context
def remove_bucket_iam_member(ctx, *args, **kwargs):
    """Remove member from bucket IAM Policy."""
    name = ctx.obj["name"]
    member = kwargs["member"]
    msg = _bucket_iam_helper(name, member, _get_roles(**kwargs), False)
    return f"```{msg}```"
