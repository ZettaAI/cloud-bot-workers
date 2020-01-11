from google.oauth2 import service_account
import googleapiclient.discovery


def list_service_accounts(project_id):
    """Lists all service accounts for the current project."""

    service = googleapiclient.discovery.build("iam", "v1",)

    service_accounts = (
        service.projects()  # pylint: disable=no-member
        .serviceAccounts()
        .list(name="projects/" + project_id)
        .execute()
    )

    for account in service_accounts["accounts"]:
        print("Name: " + account["name"])
        print("Email: " + account["email"])
        print(" ")
    return service_accounts


def create_service_account(project_id, name, display_name):
    """Creates a service account."""

    service = googleapiclient.discovery.build("iam", "v1")
    my_service_account = (
        service.projects()  # pylint: disable=no-member
        .serviceAccounts()
        .create(
            name="projects/" + project_id,
            body={"accountId": name, "serviceAccount": {"displayName": display_name}},
        )
        .execute()
    )

    print("Created service account: " + my_service_account["email"])
    return my_service_account


def rename_service_account(email, new_display_name):
    """Changes a service account's display name."""

    # First, get a service account using List() or Get()

    service = googleapiclient.discovery.build("iam", "v1",)

    resource = "projects/-/serviceAccounts/" + email

    my_service_account = (
        service.projects()
        .serviceAccounts()
        .get(name=resource)
        .execute()  # pylint: disable=no-member
    )

    # Then you can update the display name
    my_service_account["displayName"] = new_display_name
    my_service_account = (
        service.projects()  # pylint: disable=no-member
        .serviceAccounts()
        .update(name=resource, body=my_service_account)
        .execute()
    )

    print(
        "Updated display name for {} to: {}".format(
            my_service_account["email"], my_service_account["displayName"]
        )
    )
    return my_service_account


def disable_service_account(email):
    """Disables a service account."""

    service = googleapiclient.discovery.build("iam", "v1",)

    service.projects().serviceAccounts().disable(  # pylint: disable=no-member
        name="projects/-/serviceAccounts/" + email
    ).execute()

    print("Disabled service account :" + email)


def enable_service_account(email):
    """Enables a service account."""

    service = googleapiclient.discovery.build("iam", "v1")

    service.projects().serviceAccounts().enable(  # pylint: disable=no-member
        name="projects/-/serviceAccounts/" + email
    ).execute()

    print("Disabled service account :" + email)


def delete_service_account(email):
    """Deletes a service account."""
    service = googleapiclient.discovery.build("iam", "v1")

    service.projects().serviceAccounts().delete(  # pylint: disable=no-member
        name="projects/-/serviceAccounts/" + email
    ).execute()

    print("Deleted service account: " + email)


delete_service_account("sa-test@zetta-lee-fly-vnc-001.iam.gserviceaccount.com")
create_service_account("zetta-lee-fly-vnc-001", "sa-test", "sa-displayname")
delete_service_account("sa-test@zetta-lee-fly-vnc-001.iam.gserviceaccount.com")
