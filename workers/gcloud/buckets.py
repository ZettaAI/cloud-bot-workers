from click import Option
from click import Context
from click import Command
from google.cloud import storage

from . import gcloud_cmds


def create(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(bucket_name)
    return f"{bucket.name} created."


bucket_name_param = Option(
    ["-n", "--name"], type=str, required=True, nargs=1, help="Name of the bucket."
)
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

# create_ctx.invoke(bucket_create_cmd, bucket_name="akhilesh-test-click")

