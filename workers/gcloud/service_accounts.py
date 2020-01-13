# pylint: disable=no-member
import os
import base64

import click
import googleapiclient.discovery
from google.oauth2 import service_account
from cloudvolume.storage import SimpleStorage

from . import utils


class ServiceAccountActions:
    def __init__(self, project_id):
        self._project_id = project_id
        self._resource = googleapiclient.discovery.build("iam", "v1",)

    @property
    def resource(self):
        return self._resource

    @property
    def project_id(self):
        return self._project_id

    def list(self):
        """Lists all service accounts for the current project."""
        sa = (
            self.resource.projects()
            .serviceAccounts()
            .list(name="projects/" + self.project_id)
            .execute()
        )
        msg = "\n".join([f"{_['email']}" for _ in sa["accounts"]])
        return f"```{msg}```"

    def create(self, name, display_name):
        """Creates a service account."""
        options = {
            "name": f"projects/{self.project_id}",
            "body": {
                "accountId": name,
                "serviceAccount": {"displayName": display_name},
            },
        }
        account = self.resource.projects().serviceAccounts().create(**options).execute()
        return f"Service account `{account['email']}` created."

    def rename(self, email, new_display_name):
        """Changes a service account's display name."""
        resource_name = f"projects/-/serviceAccounts/{email}"
        account = (
            self.resource.projects().serviceAccounts().get(name=resource_name).execute()
        )

        old_display_name = account["displayName"]
        account["displayName"] = new_display_name
        account = (
            self.resource.projects()
            .serviceAccounts()
            .update(name=resource_name, body=account)
            .execute()
        )
        msg = f"Updated display name of `{account['email']}`"
        msg = f"{msg} from `{old_display_name}` to `{account['displayName']}`"
        return msg

    def disable(self, email):
        """Disables a service account."""
        self.resource.projects().serviceAccounts().disable(
            name=f"projects/-/serviceAccounts/{email}"
        ).execute()
        return f"Service account `{email}` disabled."

    def enable(self, email):
        """Enables a service account."""
        self.resource.projects().serviceAccounts().enable(
            name=f"projects/-/serviceAccounts/{email}"
        ).execute()
        return f"Service account `{email}` enabled."

    def delete(self, email):
        """Deletes a service account."""
        self.resource.projects().serviceAccounts().delete(
            name=f"projects/-/serviceAccounts/{email}"
        ).execute()
        return f"Service account `{email}` deleted."

    def list_keys(self, email):
        """Lists all keys for a service account."""
        keys = (
            self.resource.projects()
            .serviceAccounts()
            .keys()
            .list(name=f"projects/-/serviceAccounts/{email}")
            .execute()
        )
        msg = "\n".join(f"{key['name']} ({key['keyType']})" for key in keys["keys"])
        return f"```{msg}```"

    def create_key(self, email):
        """Creates a service account key."""
        key = (
            self.resource.projects()
            .serviceAccounts()
            .keys()
            .create(name=f"projects/-/serviceAccounts/{email}", body={})
            .execute()
        )
        bucket_name = "cloud-bot"
        bucket_gs = f"gs://{bucket_name}/keys"
        key_file = f"{key['name']}.json"
        with SimpleStorage(bucket_gs) as storage:
            storage.put_file(
                file_path=key_file,
                content=base64.b64decode(key["privateKeyData"]),
                compress=None,
                cache_control="no-cache",
            )

        url = utils.generate_signed_url(bucket_name, f"keys/{key_file}")
        msg = f"Key created `{key['name'].split('/')[-1]}`."
        return f"{msg}\nAvailable <{url}|here> (link valid for 60s)."

    def delete_key(self, full_key_name):
        """Deletes a service account key."""
        self.resource.projects().serviceAccounts().keys().delete(
            name=full_key_name
        ).execute()
        return f"Deleted {full_key_name}."


@click.group(
    "sa",
    help="List service accounts. See help for sub commands.",
    add_help_option=False,
    invoke_without_command=True,
)
@click.option(
    "--project",
    "-p",
    type=str,
    default=lambda: os.environ["DEFAULT_PROJECT"],
    nargs=1,
    help="Project name.",
    show_default=os.environ["DEFAULT_PROJECT"],
)
@click.pass_context
def service_accounts(ctx, *args, **kwargs):
    """Group for Service Account commands."""
    ctx.obj["sa_actions"] = ServiceAccountActions(kwargs["project"])
    return ctx.obj["sa_actions"].list()


@service_accounts.command(
    "create", help="Create a new service account.", add_help_option=False
)
@click.argument("name", type=str)
@click.argument("display_name", type=str)
@click.pass_context
def create(ctx, *args, **kwargs):
    """Create new service account."""
    sa_actions = ctx.obj["sa_actions"]
    kwargs["email"] = utils.get_sa_email(kwargs["name"], sa_actions.project_id)
    return sa_actions.create(*args, **kwargs)


@service_accounts.command(
    "rename", help="Change service account displayname.", add_help_option=False
)
@click.argument("name", type=str)
@click.argument("display_name", type=str)
@click.pass_context
def rename(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    kwargs["email"] = utils.get_sa_email(kwargs["name"], sa_actions.project_id)
    return sa_actions.rename(*args, **kwargs)


@service_accounts.command(
    "disable", help="Disable service account.", add_help_option=False
)
@click.argument("name", type=str)
@click.pass_context
def disable(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    kwargs["email"] = utils.get_sa_email(kwargs["name"], sa_actions.project_id)
    return sa_actions.disable(*args, **kwargs)


@service_accounts.command(
    "enable", help="Enable service account.", add_help_option=False
)
@click.argument("name", type=str)
@click.pass_context
def enable(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    kwargs["email"] = utils.get_sa_email(kwargs["name"], sa_actions.project_id)
    return sa_actions.enable(*args, **kwargs)


@service_accounts.command(
    "delete", help="Delete service account.", add_help_option=False
)
@click.argument("name", type=str)
@click.pass_context
def delete(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    kwargs["email"] = utils.get_sa_email(kwargs["name"], sa_actions.project_id)
    return sa_actions.delete(*args, **kwargs)


@service_accounts.group(
    "keys",
    help="List service account keys. See help for subcommands.",
    add_help_option=False,
    invoke_without_command=True,
)
@click.argument("name", type=str)
@click.pass_context
def keys(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    kwargs["email"] = utils.get_sa_email(kwargs["name"], sa_actions.project_id)
    ctx.obj["email"] = kwargs["email"]
    ctx.obj["name"] = kwargs["name"]
    return sa_actions.list_keys(ctx.obj["email"])


@keys.command("create", help="Create service account key.", add_help_option=False)
@click.pass_context
def create_key(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    return sa_actions.create_key(ctx.obj["email"])


@keys.command("delete", help="Delete service account key.", add_help_option=False)
@click.argument("key_id", type=str)
@click.pass_context
def delete_key(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    full_key_name = utils.get_sa_full_key_name(
        ctx.obj["name"], sa_actions.project_id, kwargs["key_id"]
    )
    return sa_actions.delete_key(full_key_name)

