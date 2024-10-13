"""DataUpdateCoordinator for openshock."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    OpenShockApiClientAuthenticationError,
    OpenShockApiClientError,
)
from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import OpenShockConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class OpenShockDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: OpenShockConfigEntry
    intensities: dict[str, int]

    def __init__(
        self,
        hass: HomeAssistant,
        update_interval: int,
        hub: Any,
        shocker: Any,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )
        self.hub = hub
        self.shocker = shocker
        self.intensities = {}

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.get_shocker(
                self.shocker["id"]
            )
        except OpenShockApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except OpenShockApiClientError as exception:
            raise UpdateFailed(exception) from exception
