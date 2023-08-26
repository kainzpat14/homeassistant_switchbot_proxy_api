"""Config flow for switchbot_api integration."""
from __future__ import annotations

import logging
from typing import Any

from switchbot_api_proxy import SwitchbotProxyClient

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {vol.Required("url"): str, vol.Required("key"): str}
)


class SwitchBotHub:
    """Class to interface with the SwitchBot API Proxy."""

    def authenticate(self, url: str, key: str) -> bool:
        """Test if we can authenticate with the SwitchBot API."""
        switchbot = SwitchbotProxyClient(url, key)
        try:
            switchbot.listDevices()
        except Exception: 
            return False
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    hub = SwitchBotHub()

    if not await hass.async_add_executor_job(
        hub.authenticate, data["url"], data["key"]
    ):
        raise InvalidAuth

    return {
        "title": "Switchbot API Proxy",
        "url": data["url"],
        "key": data["key"],
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for switchbot_api_proxy"""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Your secret or token is invalid."""
