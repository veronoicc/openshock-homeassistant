"""Sample API Client."""

from __future__ import annotations

import socket
from typing import Any

import aiohttp
import async_timeout

from custom_components.openshock.const import LOGGER


class OpenShockApiClientError(Exception):
    """Exception to indicate a general API error."""


class OpenShockApiClientCommunicationError(
    OpenShockApiClientError,
):
    """Exception to indicate a communication error."""


class OpenShockApiClientAuthenticationError(
    OpenShockApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise OpenShockApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class OpenShockApiClient:
    """OpenShock API Client."""

    def __init__(
        self,
        host: str,
        token: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """OpenShock API Client."""
        self._host = host
        self._token = token
        self._session = session

    async def get_token(self) -> Any:
        """Get information about current token from the API."""
        return await self._api_wrapper(
            method="get",
            url="/1/tokens/self",
            skip_to_data=False,
        )

    async def get_devices(self) -> Any:
        """Get information about devices from the API."""
        return await self._api_wrapper(
            method="get",
            url="/1/devices",
        )

    async def get_device(self, device: str) -> Any:
        """Get information about a device from the API."""
        return await self._api_wrapper(
            method="get",
            url=f"/1/devices/{device}",
        )

    async def get_shockers_by_device(self, device: str) -> Any:
        """Get information about shockers by device from the API."""
        return await self._api_wrapper(
            method="get",
            url=f"/1/devices/{device}/shockers",
        )

    async def get_shocker(self, shocker: str) -> Any:
        """Get information about a shocker from the API."""
        return await self._api_wrapper(
            method="get",
            url=f"/1/shockers/{shocker}",
        )

    async def control_shocker(
        self,
        shocker: str,
        shocks: list[dict],
    ) -> Any:
        """Control a shocker from the API."""
        for shock in shocks:
            shock["id"] = shocker
        return await self._api_wrapper(
            method="post",
            url="/2/shockers/control",
            data={
                "shocks": shocks,
                "customName": "Home Assistant",
            },
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
        *,
        skip_to_data: bool = True,
    ) -> Any:
        """Get information from the API."""
        url = f"{self._host}{url}"
        headers = headers or {}
        headers["Open-Shock-Token"] = self._token
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                if skip_to_data:
                    return (await response.json())["data"]
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise OpenShockApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            LOGGER.info(await response.text())
            msg = f"Error fetching information - {exception}"
            raise OpenShockApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise OpenShockApiClientError(
                msg,
            ) from exception
