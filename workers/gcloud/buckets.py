from click import Group
from click import Option
from click import Context
from click import Command
from google.cloud import storage


def create(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(bucket_name)
    return f"{bucket.name} created."


def lookup(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.lookup_bucket(bucket_name)
    if not bucket:
        return f"{bucket.name} does not exist."
    return f"{bucket.name} exists."


bucket_name = Option(
    ["-n", "--name"], type=str, required=True, nargs=1, help="Name of the bucket."
)

create_cmd = Command(
    "create",
    callback=create,
    help="- creates a bucket.",
    params=[bucket_name],
    add_help_option=False,
)


lookup_cmd = Command(
    "lookup",
    callback=create,
    help="- check if a bucket exists.",
    params=[bucket_name],
    add_help_option=False,
)


cmd_grp = Group("bucket", add_help_option=False)
cmd_grp.add_command(create_cmd)
cmd_grp.add_command(lookup_cmd)
