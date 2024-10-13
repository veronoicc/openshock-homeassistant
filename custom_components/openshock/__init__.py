"""
Custom integration to integrate openshock with Home Assistant.

For more details about this integration, please refer to
https://github.com/veronoicc/openshock-homeassistabt
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_API_KEY, CONF_HOST, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import OpenShockApiClient
from .const import CONF_HUB, CONF_UPDATE_INTERVAL
from .coordinator import OpenShockDataUpdateCoordinator
from .data import OpenShockData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import OpenShockConfigEntry

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.NUMBER, Platform.BINARY_SENSOR]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: OpenShockConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    entry.runtime_data = OpenShockData(
        client=OpenShockApiClient(
            host=entry.data[CONF_HOST],
            token=entry.data[CONF_API_KEY],
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
    )

    hub = await entry.runtime_data.client.get_device(entry.data[CONF_HUB])

    for shocker in await entry.runtime_data.client.get_shockers_by_device(hub["id"]):
        coordinator = OpenShockDataUpdateCoordinator(
            hass=hass,
            update_interval=entry.data[CONF_UPDATE_INTERVAL],
            shocker=shocker,
            hub=hub,
        )
        entry.runtime_data.coordinators[shocker["id"]] = coordinator

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    for coordinator in entry.runtime_data.coordinators.values():
        await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: OpenShockConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: OpenShockConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
