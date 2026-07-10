"""
High-level Xen Orchestra REST client.
"""

from clients.rest_client import RestClient


class XOClient:
    """High-level Xen Orchestra client."""

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        verify_ssl: bool = True,
    ) -> None:

        self._username = username
        self._password = password

        api_url = url.rstrip("/")
        if not api_url.endswith("/rest/v0"):
            api_url = f"{api_url}/rest/v0"

        self._client = RestClient(
            base_url=api_url,
            verify_ssl=verify_ssl,
        )

    def authenticate(self) -> None:
        """
        Authenticate against Xen Orchestra.

        The REST API supports HTTP Basic authentication.
        Authentication is validated by retrieving the current user's profile.
        """

        self._client.get(
            "/users/me",
            headers=self._basic_auth_header(),
        )

    def disconnect(self) -> None:
        """Close the HTTP session."""

        self._client.close()

    def get_virtual_machines(self) -> list[dict]:
        """Return virtual machines visible to the authenticated user."""

        return self._get_collection(
            "/vms",
            "name_label,power_state,tags",
        )

    def get_pools(self) -> list[dict]:
        """Return pools visible to the authenticated user."""

        return self._get_collection("/pools", "name_label")

    def get_hosts(self) -> list[dict]:
        """Return hosts visible to the authenticated user."""

        return self._get_collection(
            "/hosts",
            "name_label,address,enabled",
        )

    def get_snapshots(self) -> list[dict]:
        """Return VM snapshots visible to the authenticated user."""

        return self._get_collection(
            "/vm-snapshots",
            "name_label,name_description,snapshot_of,snapshot_time",
        )

    def get_storage_repositories(self) -> list[dict]:
        """Return storage repositories visible to the authenticated user."""

        return self._get_collection(
            "/srs",
            "name_label,physical_size,physical_utilisation",
        )

    def _get_collection(
        self,
        endpoint: str,
        fields: str,
    ) -> list[dict]:
        """Retrieve a REST collection with the requested object fields."""

        response = self._client.get(
            f"{endpoint}?fields={fields}",
            headers=self._basic_auth_header(),
        )

        if not isinstance(response, list):
            raise TypeError(
                f"Expected a list from {endpoint}, got {type(response).__name__}."
            )

        return response

    def _basic_auth_header(self) -> dict[str, str]:

        import base64

        credentials = (
            f"{self._username}:{self._password}"
        ).encode()

        token = base64.b64encode(credentials).decode()

        return {
            "Authorization": f"Basic {token}"
        }
