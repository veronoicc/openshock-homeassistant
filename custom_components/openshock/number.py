"""Support for OpenShock buttons."""

from homeassistant.components.number import (
    NumberEntityDescription,
    RestoreNumber,
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
    """Set up the number platform."""
    entities = [
        [
            OpenShockNumber(
                coordinator=coordinator,
                entity_description=NumberEntityDescription(
                    key="openshock-shock-intensity",
                    translation_key="shock_intensity",
                    icon="mdi:lightning-bolt",
                    native_unit_of_measurement="%",
                ),
                related_command="shock",
                related_type="intensity",
                default_value=20,
            ),
            OpenShockNumber(
                coordinator=coordinator,
                entity_description=NumberEntityDescription(
                    key="openshock-vibrate-intensity",
                    translation_key="vibrate_intensity",
                    icon="mdi:vibrate",
                    native_unit_of_measurement="%",
                ),
                related_command="vibrate",
                related_type="intensity",
                default_value=20,
            ),
            OpenShockNumber(
                coordinator=coordinator,
                entity_description=NumberEntityDescription(
                    key="openshock-sound-intensity",
                    translation_key="sound_intensity",
                    icon="mdi:bell",
                    native_unit_of_measurement="%",
                ),
                related_command="sound",
                related_type="intensity",
                default_value=20,
            ),
            OpenShockNumber(
                coordinator=coordinator,
                entity_description=NumberEntityDescription(
                    key="openshock-shock-duration",
                    translation_key="shock_duration",
                    icon="mdi:lightning-bolt",
                    native_unit_of_measurement="ms",
                    native_max_value=30000,
                    native_min_value=300,
                ),
                related_command="shock",
                related_type="duration",
                default_value=10000,
            ),
            OpenShockNumber(
                coordinator=coordinator,
                entity_description=NumberEntityDescription(
                    key="openshock-vibrate-duration",
                    translation_key="vibrate_duration",
                    icon="mdi:vibrate",
                    native_unit_of_measurement="ms",
                    native_max_value=30000,
                    native_min_value=300,
                ),
                related_command="vibrate",
                related_type="duration",
                default_value=10000,
            ),
            OpenShockNumber(
                coordinator=coordinator,
                entity_description=NumberEntityDescription(
                    key="openshock-sound-duration",
                    translation_key="sound_duration",
                    icon="mdi:bell",
                    native_unit_of_measurement="ms",
                    native_max_value=30000,
                    native_min_value=300,
                ),
                related_command="sound",
                related_type="duration",
                default_value=10000,
            ),
        ]
        for coordinator in entry.runtime_data.coordinators.values()
    ]

    async_add_entities(x for xs in entities for x in xs)


class OpenShockNumber(OpenShockEntity, RestoreNumber):
    """OpenShock number class."""

    def __init__(
        self,
        coordinator: OpenShockDataUpdateCoordinator,
        entity_description: NumberEntityDescription,
        related_command: str,
        related_type: str,
        default_value: int,
    ) -> None:
        """Initialize the number class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.hub['id']}-{coordinator.shocker["id"]}-{related_command}-{related_type}"  # noqa: E501
        self.command = related_command
        self.type = related_type
        self.default_value = default_value

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        last_data = await self.async_get_last_number_data()
        if last_data is not None and last_data.native_value is not None:
            self.set_native_value(last_data.native_value)
        else:
            self.set_native_value(self.default_value)

    def set_native_value(self, value: float) -> None:
        """Set the native value of the sensor."""
        self.coordinator.intensities[f"{self.command}_{self.type}"] = int(value)

    @property
    def native_value(self) -> float:
        """Return the native value of the sensor."""
        return self.coordinator.intensities.get(
            f"{self.command}_{self.type}", self.default_value
        )
