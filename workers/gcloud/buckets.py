from click import Option
from click import Context
from click import Command
from google.cloud import storage

from . import ctx as parent_ctx
from . import cmd_grp


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

cmd_grp.add_command(bucket_create_cmd)
cmd = cmd_grp.get_command(None, "create")

create_ctx = Context(cmd, parent=parent_ctx, info_name="create")

# print(cmd.get_help(create_ctx))
# # print()
# print(cmd_grp.get_help(parent_ctx))

text = parent_ctx.get_help()
print(text)
print("haha")

# create_ctx.invoke(bucket_create_cmd, bucket_name="akhilesh-test-click")

