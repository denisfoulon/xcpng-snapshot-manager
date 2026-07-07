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

        self._client = RestClient(
            base_url=url,
            verify_ssl=verify_ssl,
        )

    def authenticate(self) -> None:
        """
        Authenticate against Xen Orchestra.

        The REST API supports HTTP Basic authentication.
        Authentication is validated by calling the ping endpoint.
        """

        self._client.get(
            "/ping",
            headers=self._basic_auth_header(),
        )

    def disconnect(self) -> None:
        """Close the HTTP session."""

        self._client.close()

    def _basic_auth_header(self) -> dict[str, str]:

        import base64

        credentials = (
            f"{self._username}:{self._password}"
        ).encode()

        token = base64.b64encode(credentials).decode()

        return {
            "Authorization": f"Basic {token}"
        }
