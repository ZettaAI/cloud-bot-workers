import click
from google.cloud.storage import Client
from google.cloud.storage import Bucket


PREDEFINED_BUKCET_IAM_ROLES = {
    "read": "roles/storage.objectViewer",
    "write": "roles/storage.objectCreator",
    "admin": "roles/storage.objectAdmin",
}


@click.command("buckets", help="List avialable buckets.", add_help_option=False)
@click.pass_context
def buckets(ctx, *args, **kwargs):
    buckets = Client(project=ctx.obj.get("project", None)).list_buckets()
    msg = "\n".join(bucket.name for bucket in buckets)
    return f"```{msg}```"


@click.group(
    "bucket",
    help="Actions related to buckets.",
    add_help_option=False,
    invoke_without_command=True,
)
@click.argument("name", type=str)
@click.pass_context
def bucket(ctx, *args, **kwargs):
    """Group for bucket commands."""
    ctx.obj["client"] = Client(project=ctx.obj.get("project", None))
    ctx.obj["name"] = kwargs["name"]
    bucket = ctx.obj["client"].lookup_bucket(ctx.obj["name"])
    if not bucket:
        return f"Bucket `{ctx.obj['name']}` does not exist."

    properties = [f"Owner: {bucket.owner}"]
    properties.append(f"Created: {bucket.time_created}")
    properties.append(f"Location: {bucket.location}")
    properties.append(f"Location Type: {bucket.location_type}")
    properties.append(f"Storage Class: {bucket.storage_class}")
    msg = "\n".join(properties)
    return f"```{msg}```"


###################
# BUCKET operations
###################


@bucket.command(
    "create", help="Creates a bucket.", add_help_option=False,
)
@click.option(
    "--location",
    "-l",
    type=str,
    required=False,
    nargs=1,
    help="Location of the bucket. (cloud.google.com/storage/docs/locations)",
)
@click.option(
    "--class",
    "-c",
    type=str,
    required=False,
    nargs=1,
    help="Default Storage Class for the bucket. "
    "(cloud.google.com/storage/docs/storage-classes)",
)
@click.pass_context
def create(ctx, *args, **kwargs):
    bucket = Bucket(ctx.obj["client"], name=ctx.obj["name"])
    bucket.location = kwargs["location"].upper()
    bucket.storage_class = kwargs["class"].upper()
    bucket.create()
    return f"Bucket `{bucket.name}` created."


@bucket.command(
    "delete", help="Deletes a bucket.", add_help_option=False,
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force deletion. (If not forced, the bucket must be empty).",
)
@click.pass_context
def delete(ctx, *args, **kwargs):
    bucket = Bucket(ctx.obj["client"], name=ctx.obj["name"])
    bucket.delete(force=kwargs["force"])
    return f"Bucket `{bucket.name}` deleted."


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


def _bucket_iam_helper(bucket: Bucket, member: str, roles: list, add: bool = True):
    policy = bucket.get_iam_policy()
    msg = []
    if add:
        for role in roles:
            policy[role].add(member)
            msg.append(f"Added {member} with role {role} to {bucket.name}.")
    else:
        for role in roles:
            policy[role].discard(member)
            msg.append(f"Removed {member} with role {role} from {bucket.name}.")
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
    bucket = ctx.obj["client"].bucket(ctx.obj["name"])
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
    member = kwargs["member"]
    bucket = ctx.obj["client"].bucket(ctx.obj["name"])
    msg = _bucket_iam_helper(bucket, member, _get_roles(**kwargs), True)
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
    member = kwargs["member"]
    bucket = ctx.obj["client"].bucket(ctx.obj["name"])
    msg = _bucket_iam_helper(bucket, member, _get_roles(**kwargs), False)
    return f"```{msg}```"
