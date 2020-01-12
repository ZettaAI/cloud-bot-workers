from google.oauth2 import service_account
import googleapiclient.discovery


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
        msg = "\n".join([f"{_['name']}{_['email']}" for _ in sa["accounts"]])
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
        return f"Updated display name of `{account['email']}` \
            from `{old_display_name}` to `{account['displayName']}`"

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
