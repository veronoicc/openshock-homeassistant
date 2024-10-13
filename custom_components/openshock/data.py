"""Custom types for openshock."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import OpenShockApiClient
    from .coordinator import OpenShockDataUpdateCoordinator


type OpenShockConfigEntry = ConfigEntry[OpenShockData]


@dataclass
class OpenShockData:
    """Data for the OpenShock integration."""

    client: OpenShockApiClient
    integration: Integration
    coordinators: dict[str, OpenShockDataUpdateCoordinator] = field(
        default_factory=dict
    )
