"""
Workers for doing stuff on gcloud.
"""

from click import Group

ROUTING_KEY = "gcloud.#"

gcloud_cmds = Group("gcloud")

