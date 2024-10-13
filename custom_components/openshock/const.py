"""Constants for openshock."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "openshock"

CONF_UPDATE_INTERVAL = "update_interval"
DEFAULT_SCAN_INTERVAL = {"seconds": 30}

CONF_HUB = "hub"

DEFAULT_HOST = "https://api.openshock.app"
