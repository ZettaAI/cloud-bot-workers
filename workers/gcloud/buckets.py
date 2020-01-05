from click import Group
from click import Option
from click import Context
from click import Command
from google.cloud import storage


def create(name):
    storage_client = storage.Client()
    try:
        bucket = storage_client.create_bucket(name)
        return f"`{bucket.name}` created."
    except Exception as err:
        return str(err)


def lookup(name):
    storage_client = storage.Client()
    bucket = storage_client.lookup_bucket(name)
    if not bucket:
        return f"{bucket.name} does not exist."
    return f"{bucket.name} exists."


name = Option(
    ["-n", "--name"], type=str, required=True, nargs=1, help="Name of the bucket."
)

create_cmd = Command(
    "create",
    callback=create,
    help="- creates a bucket.",
    params=[name],
    add_help_option=False,
)


lookup_cmd = Command(
    "lookup",
    callback=create,
    help="- check if a bucket exists.",
    params=[name],
    add_help_option=False,
)

lame = Option(
    ["-l", "--lame"], type=str, required=True, nargs=1, help="Lame of the bucket."
)

cmd_grp = Group("bucket", add_help_option=False, params=[lame])
cmd_grp.add_command(create_cmd)
cmd_grp.add_command(lookup_cmd)
