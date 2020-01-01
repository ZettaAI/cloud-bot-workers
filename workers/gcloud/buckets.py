from click import Command
from click import Argument
from google.cloud import storage

from . import gcloud_cmds


def create(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(bucket_name)
    return f"{bucket.name} created."


bucket_name_param = Argument(["bucket_name"])
bucket_create_cmd = Command("create", callback=create)

gcloud_cmds.add_command(bucket_create_cmd)
