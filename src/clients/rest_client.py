"""
Generic REST client.
"""

from typing import Any

import httpx

from core.exceptions import (
    ApiError,
    AuthenticationError,
    ConnectionError,
)


class RestClient:
    """Generic REST client."""

    def __init__(
        self,
        base_url: str,
        verify_ssl: bool = True,
        timeout: int = 30,
    ) -> None:

        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            verify=verify_ssl,
            timeout=timeout,
            follow_redirects=True,
        )

    def get(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
    ) -> dict:

        return self._request(
            "GET",
            endpoint,
            headers=headers,
        )

    def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict:

        return self._request(
            "POST",
            endpoint,
            json=json,
            headers=headers,
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> dict:

        try:

            response = self._client.request(
                method,
                endpoint,
                **kwargs,
            )

        except httpx.ConnectError as exc:
            raise ConnectionError(str(exc)) from exc

        except httpx.HTTPError as exc:
            raise ApiError(str(exc)) from exc

        if response.status_code in (401, 403):
            raise AuthenticationError("Authentication failed.")

        response.raise_for_status()

        if not response.content:
            return {}

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        if "application/json" in content_type:
            return response.json()

        return response.text

    def close(self) -> None:
        self._client.close()
