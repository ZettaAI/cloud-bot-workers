from click import Group
from click import Option
from click import Context
from click import Command
from google.cloud import storage


def create(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(bucket_name)
    return f"{bucket.name} created."


create_param_name = Option(
    ["-n", "--name"], type=str, required=True, nargs=1, help="Name of the bucket."
)

create_cmd = Command(
    "create",
    callback=create,
    help="- creates a bucket.",
    params=[create_param_name],
    add_help_option=False,
)


cmd_grp = Group("bucket", add_help_option=False)
cmd_grp.add_command(create_cmd)
