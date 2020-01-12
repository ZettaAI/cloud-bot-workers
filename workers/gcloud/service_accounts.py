import click
import googleapiclient.discovery
from google.oauth2 import service_account


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
            self.resource.projects()  # pylint: disable=no-member
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
        account = (
            self.resource.projects()  # pylint: disable=no-member
            .serviceAccounts()
            .create(**options)
            .execute()
        )
        return f"Service account `{account['email']}` created."

    def rename(self, email, new_display_name):
        """Changes a service account's display name."""
        resource_name = f"projects/-/serviceAccounts/{email}"
        account = (
            self.resource.projects()  # pylint: disable=no-member
            .serviceAccounts()
            .get(name=resource_name)
            .execute()
        )

        old_display_name = account["displayName"]
        account["displayName"] = new_display_name
        account = (
            self.resource.projects()  # pylint: disable=no-member
            .serviceAccounts()
            .update(name=resource_name, body=account)
            .execute()
        )
        msg = f"Updated display name of `{account['email']}`"
        msg = f"{msg} from `{old_display_name}` to `{account['displayName']}`"
        return msg

    def disable(self, email):
        """Disables a service account."""
        self.resource.projects().serviceAccounts().disable(  # pylint: disable=no-member
            name=f"projects/-/serviceAccounts/{email}"
        ).execute()
        return f"Service account `{email}` disabled."

    def enable(self, email):
        """Enables a service account."""
        self.resource.projects().serviceAccounts().enable(  # pylint: disable=no-member
            name=f"projects/-/serviceAccounts/{email}"
        ).execute()
        return f"Service account `{email}` enabled."

    def delete(self, email):
        """Deletes a service account."""
        self.resource.projects().serviceAccounts().delete(  # pylint: disable=no-member
            name=f"projects/-/serviceAccounts/{email}"
        ).execute()
        return f"Service account `{email}` deleted."


@click.group(
    "sa",
    help="List service accounts.",
    add_help_option=False,
    invoke_without_command=True,
)
@click.option(
    "--project",
    "-p",
    type=str,
    default="zetta-lee-fly-vnc-001",
    nargs=1,
    help="Project name.",
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
    return sa_actions.create(*args)


@service_accounts.command(
    "rename", help="Change service account displayname.", add_help_option=False
)
@click.argument("email", type=str)
@click.argument("display_name", type=str)
@click.pass_context
def rename(ctx, *args, **kwargs):
    """Create new service account."""
    print(kwargs)
    sa_actions = ctx.obj["sa_actions"]
    return sa_actions.rename(*args)


@service_accounts.command(
    "disable", help="Disable service account.", add_help_option=False
)
@click.argument("email", type=str)
@click.pass_context
def disable(ctx, *args, **kwargs):
    """Disable service account."""
    print(args)
    sa_actions = ctx.obj["sa_actions"]
    return sa_actions.disable(*args)


@service_accounts.command(
    "enable", help="Change service account displayname.", add_help_option=False
)
@click.argument("email", type=str)
@click.pass_context
def enable(ctx, *args, **kwargs):
    """Enable service account."""
    sa_actions = ctx.obj["sa_actions"]
    return sa_actions.enable(*args)


@service_accounts.command(
    "delete", help="Change service account displayname.", add_help_option=False
)
@click.argument("email", type=str)
@click.pass_context
def delete(ctx, *args, **kwargs):
    """Delete service account."""
    sa_actions = ctx.obj["sa_actions"]
    return sa_actions.delete(*args)

