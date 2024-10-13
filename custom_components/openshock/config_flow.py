"""Adds config flow for OpenShock."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    OpenShockApiClient,
    OpenShockApiClientAuthenticationError,
    OpenShockApiClientCommunicationError,
    OpenShockApiClientError,
)
from .const import (
    CONF_HUB,
    CONF_UPDATE_INTERVAL,
    DEFAULT_HOST,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)


class OpenShockFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for OpenShock."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            self.client = OpenShockApiClient(
                host=user_input[CONF_HOST],
                token=user_input[CONF_API_KEY],
                session=async_get_clientsession(self.hass),
            )
            try:
                await self.client.get_token()
            except OpenShockApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except OpenShockApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except OpenShockApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                self.host = user_input[CONF_HOST]
                self.token = user_input[CONF_API_KEY]
                self.scan_interval = cv.time_period_dict(
                    user_input[CONF_UPDATE_INTERVAL]
                ).total_seconds()

                devices = [
                    f"{device['name']} ({device['id']})"
                    for device in await self.client.get_devices()
                ]

                return self.async_show_form(
                    step_id="select_device",
                    data_schema=vol.Schema(
                        {
                            vol.Required(
                                CONF_HUB,
                            ): selector.SelectSelector(
                                selector.SelectSelectorConfig(options=devices),
                            ),
                        },
                    ),
                    errors=_errors,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, DEFAULT_HOST),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.URL,
                        ),
                    ),
                    vol.Required(CONF_API_KEY): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=(user_input or {}).get(
                            CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): selector.DurationSelector(),
                },
            ),
            errors=_errors,
        )

    async def async_step_select_device(
        self,
        user_input: dict | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle a flow to select the device."""
        _errors = {}
        if user_input is not None:
            device_id = user_input[CONF_HUB].split(" (")[1][:-1]
            device_name = user_input[CONF_HUB].split(" (")[0]

            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=device_name,
                data={
                    CONF_HOST: self.host,
                    CONF_API_KEY: self.token,
                    CONF_HUB: device_id,
                    CONF_UPDATE_INTERVAL: self.scan_interval,
                },
            )

        devices = [
            f"{device['name']} ({device['id']})"
            for device in await self.client.get_devices()
        ]

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HUB,
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=devices),
                    ),
                },
            ),
            errors=_errors,
        )
