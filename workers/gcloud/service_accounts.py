from google.oauth2 import service_account
import googleapiclient.discovery


class ServiceAccountActions:
    def __init__(self, project_id):
        self._project_id = project_id
        self._service = googleapiclient.discovery.build("iam", "v1",)

    @property
    def service(self):
        return self._service

    @property
    def project_id(self):
        return self._project_id

    def list(self):
        """Lists all service accounts for the current project."""
        sa = (
            self.service.projects()  # pylint: disable=no-member
            .serviceAccounts()
            .list(name="projects/" + self.project_id)
            .execute()
        )
        msg = "\n".join([f"{_['name']}{_['email']}" for _ in sa["accounts"]])
        return f"```{msg}```"

    def create(self, name, display_name):
        """Creates a service account."""
        account = (
            self.service.projects()  # pylint: disable=no-member
            .serviceAccounts()
            .create(
                name="projects/" + self.project_id,
                body={
                    "accountId": name,
                    "serviceAccount": {"displayName": display_name},
                },
            )
            .execute()
        )
        return f"Service account `{account['email']}` created."

    def rename_service_account(self, email, new_display_name):
        """Changes a service account's display name."""
        account = (
            self.service.projects()  # pylint: disable=no-member
            .serviceAccounts()
            .get(name=f"projects/-/serviceAccounts/{email}")
            .execute()
        )

        # Then you can update the display name
        old_display_name = account["displayName"]
        account["displayName"] = new_display_name
        account = (
            service.projects()  # pylint: disable=no-member
            .serviceAccounts()
            .update(name=resource, body=account)
            .execute()
        )
        return f"Updated display name of {account['email']} from {old_display_name} to {account['displayName']}"

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
