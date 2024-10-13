"""OpenShockEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import OpenShockDataUpdateCoordinator


class OpenShockEntity(CoordinatorEntity[OpenShockDataUpdateCoordinator]):
    """OpenShockEntity class."""

    def __init__(self, coordinator: OpenShockDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.shocker["id"],
                ),
            },
            name=coordinator.shocker["name"],
            model=coordinator.shocker["model"],
            serial_number=coordinator.shocker["rfId"],
            via_device=(coordinator.config_entry.domain, coordinator.hub["id"]),
        )
