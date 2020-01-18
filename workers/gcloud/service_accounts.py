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
        bucket_name = os.environ["KEY_FILES_BUCKET"]
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
        msg = f"{msg}\nAvailable <{url}|here> (link valid for"
        return f"{msg} {int(os.environ['KEY_LINK_EXPIRATION'])/60}m)."

    def delete_key(self, full_key_name):
        """Deletes a service account key."""
        self.resource.projects().serviceAccounts().keys().delete(
            name=full_key_name
        ).execute()
        return f"Deleted `{full_key_name}`."


################
# Util functions
################


def _get_email(sa_actions: ServiceAccountActions, **kwargs) -> str:
    ERR = "Either NAME or EMAIL of service account is required."
    assert kwargs["email"] or kwargs["name"], ERR
    return (
        kwargs["email"]
        if kwargs["email"]
        else utils.get_sa_email(kwargs["name"], sa_actions.project_id)
    )


def _get_full_key_name(
    sa_email: str, sa_actions: ServiceAccountActions, **kwargs
) -> str:
    ERR = "Either FULL_KEY_NAME or KEY_ID is required."
    assert kwargs["full_key_name"] or kwargs["key_id"], ERR
    return (
        kwargs["full_key_name"]
        if kwargs["full_key_name"]
        else utils.get_sa_full_key_name(
            sa_email, sa_actions.project_id, kwargs["key_id"]
        )
    )


##########################
# SERVICE ACCOUNT COMMANDS
##########################


@click.group(
    "sa",
    help="List service accounts. See help for sub commands.",
    add_help_option=False,
    invoke_without_command=True,
)
@click.pass_context
def service_accounts(ctx, *args, **kwargs):
    """Group for Service Account commands."""
    ctx.obj["sa_actions"] = ServiceAccountActions(ctx.obj["project"])
    return ctx.obj["sa_actions"].list()


@service_accounts.command(
    "create", help="Create a new service account.", add_help_option=False
)
@click.argument("name", type=str)
@click.argument("display_name", type=str, required=False)
@click.pass_context
def create(ctx, *args, **kwargs):
    """Create new service account."""
    kwargs["display_name"] = (
        kwargs["display_name"] if kwargs["display_name"] else kwargs["name"]
    )
    sa_actions = ctx.obj["sa_actions"]
    return sa_actions.create(*args, **kwargs)


@service_accounts.command(
    "rename", help="Change service account display_name.", add_help_option=False
)
@click.argument("name", type=str, required=False)
@click.option(
    "--email", "-e", type=str, help="Service account email.",
)
@click.argument("display_name", type=str)
@click.pass_context
def rename(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    return sa_actions.rename(_get_email(sa_actions, **kwargs))


@service_accounts.command(
    "disable", help="Disable service account.", add_help_option=False
)
@click.argument("name", type=str, required=False)
@click.option(
    "--email", "-e", type=str, help="Service account email.",
)
@click.pass_context
def disable(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    return sa_actions.disable(_get_email(sa_actions, **kwargs))


@service_accounts.command(
    "enable", help="Enable service account.", add_help_option=False
)
@click.argument("name", type=str, required=False)
@click.option(
    "--email", "-e", type=str, help="Service account email.",
)
@click.pass_context
def enable(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    return sa_actions.enable(_get_email(sa_actions, **kwargs))


@service_accounts.command(
    "delete", help="Delete service account.", add_help_option=False
)
@click.argument("name", type=str, required=False)
@click.option(
    "--email", "-e", type=str, help="Service account email.",
)
@click.pass_context
def delete(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    return sa_actions.delete(_get_email(sa_actions, **kwargs))


##############################
# SERVICE ACCOUNT KEY COMMANDS
##############################


@service_accounts.group(
    "keys",
    help="List service account keys. See help for subcommands.",
    add_help_option=False,
    invoke_without_command=True,
)
@click.argument("name", type=str, required=False)
@click.option(
    "--email", "-e", type=str, help="Service account email.",
)
@click.pass_context
def keys(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    kwargs["email"] = _get_email(sa_actions, **kwargs)
    ctx.obj["email"] = kwargs["email"]
    return sa_actions.list_keys(ctx.obj["email"])


@keys.command("create", help="Create service account key.", add_help_option=False)
@click.pass_context
def create_key(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    return sa_actions.create_key(ctx.obj["email"])


@keys.command("delete", help="Delete service account key.", add_help_option=False)
@click.argument("key_id", type=str, required=False)
@click.option(
    "--full-key-name", "-f", type=str, help="Full key name.",
)
@click.pass_context
def delete_key(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    full_key_name = _get_full_key_name(ctx.obj["email"], sa_actions, **kwargs)
    return sa_actions.delete_key(full_key_name)


@keys.command(
    "get_link",
    help="Get temporary signed download link for key file.",
    add_help_option=False,
)
@click.argument("key_id", type=str, required=False)
@click.option(
    "--full-key-name", "-f", type=str, help="Full key name.",
)
@click.option(
    "--expires",
    "-x",
    type=int,
    help="Timeout for link expiration in seconds.",
    default=lambda: os.environ["KEY_LINK_EXPIRATION"],
    show_default=os.environ["KEY_LINK_EXPIRATION"],
    nargs=1,
)
@click.pass_context
def get_link(ctx, *args, **kwargs):
    sa_actions = ctx.obj["sa_actions"]
    full_key_name = _get_full_key_name(ctx.obj["email"], sa_actions, **kwargs)
    key_file = f"{full_key_name}.json"
    url = utils.generate_signed_url(
        os.environ["KEY_FILES_BUCKET"], f"keys/{key_file}", expiration=kwargs["expires"]
    )
    return f"Download key <{url}|here> (link valid for {kwargs['expires']//60}m)."

