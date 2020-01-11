from google.oauth2 import service_account
import googleapiclient.discovery


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


def delete_service_account(email):
    """Deletes a service account."""
    service = googleapiclient.discovery.build("iam", "v1")

    service.projects().serviceAccounts().delete( # pylint: disable=no-member
        name="projects/-/serviceAccounts/" + email
    ).execute()

    print("Deleted service account: " + email)


create_service_account("zetta-lee-fly-vnc-001", "sa-test", "sa-displayname")
delete_service_account("sa-test@zetta-lee-fly-vnc-001.iam.gserviceaccount.com")
