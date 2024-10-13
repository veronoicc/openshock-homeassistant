"""Support for OpenShock buttons."""

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.openshock.entity import OpenShockEntity

from .coordinator import OpenShockDataUpdateCoordinator
from .data import OpenShockConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument
    entry: OpenShockConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    entities = [
        [
            OpenShockButton(
                coordinator=coordinator,
                entity_description=ButtonEntityDescription(
                    key="openshock-stop",
                    name="Stop",
                    icon="mdi:stop",
                ),
                button_command="stop",
            ),
            OpenShockButton(
                coordinator=coordinator,
                entity_description=ButtonEntityDescription(
                    key="openshock-shock",
                    translation_key="shock",
                    icon="mdi:lightning-bolt",
                ),
                button_command="shock",
            ),
            OpenShockButton(
                coordinator=coordinator,
                entity_description=ButtonEntityDescription(
                    key="openshock-vibrate",
                    translation_key="vibrate",
                    icon="mdi:vibrate",
                ),
                button_command="vibrate",
            ),
            OpenShockButton(
                coordinator=coordinator,
                entity_description=ButtonEntityDescription(
                    key="openshock-sound",
                    translation_key="sound",
                    icon="mdi:bell",
                ),
                button_command="sound",
            ),
        ]
        for coordinator in entry.runtime_data.coordinators.values()
    ]

    async_add_entities(x for xs in entities for x in xs)


class OpenShockButton(OpenShockEntity, ButtonEntity):
    """OpenShock button class."""

    def __init__(
        self,
        coordinator: OpenShockDataUpdateCoordinator,
        entity_description: ButtonEntityDescription,
        button_command: str,
    ) -> None:
        """Initialize the button class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.hub['id']}-{coordinator.shocker["id"]}-{button_command}"
        )
        self.command = button_command

    async def async_press(self) -> None:
        """Handle the button press."""
        intensity = (
            self.coordinator.intensities[f"{self.command}_intensity"]
            if self.command != "stop"
            else 0
        )
        duration = (
            self.coordinator.intensities[f"{self.command}_duration"]
            if self.command != "stop"
            else 300
        )
        await self.coordinator.config_entry.runtime_data.client.control_shocker(
            self.coordinator.shocker["id"],
            [
                {
                    "type": self.command,
                    "intensity": intensity,
                    "duration": duration,
                    "exlusive": True,
                }
            ],
        )
