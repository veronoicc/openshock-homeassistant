"""Support for OpenShock buttons."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import OpenShockDataUpdateCoordinator
from .data import OpenShockConfigEntry
from .entity import OpenShockEntity


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument
    entry: OpenShockConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    entities = [
        [
            OpenShockBinarySensor(
                coordinator=coordinator,
                entity_description=BinarySensorEntityDescription(
                    key="openshock-paused",
                    translation_key="paused",
                    icon="mdi:pause",
                    device_class=BinarySensorDeviceClass.LOCK,
                ),
            ),
        ]
        for coordinator in entry.runtime_data.coordinators.values()
    ]

    async_add_entities(x for xs in entities for x in xs)


class OpenShockBinarySensor(OpenShockEntity, BinarySensorEntity):
    """OpenShock binary_sensor class."""

    def __init__(
        self,
        coordinator: OpenShockDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.hub['id']}-{coordinator.shocker["id"]}-paused"
        )

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        return bool(self.coordinator.data.get("isPaused"))
