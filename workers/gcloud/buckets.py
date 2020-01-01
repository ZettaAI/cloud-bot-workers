from click import Context
from click import Command
from click import Argument
from google.cloud import storage

from . import gcloud_cmds


def create(bucket_name):
    """
    `bucket_name` name of the bucket to create.
    """
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(bucket_name)
    return f"{bucket.name} created."


bucket_name_param = Argument(["bucket_name"], type=str, required=True, nargs=1)
bucket_create_cmd = Command(
    "create",
    callback=create,
    help="Create a bucket.",
    params=[bucket_name_param],
    add_help_option=False,
)

gcloud_cmds.add_command(bucket_create_cmd)
cmd = gcloud_cmds.get_command(None, "create")

gcloud_ctx = Context(gcloud_cmds, info_name="gcloud")
create_ctx = Context(cmd, parent=gcloud_ctx, info_name="create")

print(cmd.get_help(create_ctx))
# print()
# print(gcloud_cmds.get_help(gcloud_ctx))

