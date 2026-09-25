"""Config flow for uptime_checker."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DEFAULT_MIN_UP, DEFAULT_SCAN_INTERVAL, DOMAIN
from .logic import parse_targets

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Required("targets"): str,
        vol.Required("min_up", default=DEFAULT_MIN_UP): int,
        vol.Required("scan_interval", default=DEFAULT_SCAN_INTERVAL): int,
    }
)


def _validate(user_input: dict[str, Any]) -> tuple[list[dict[str, str]] | None, dict[str, str]]:
    errors: dict[str, str] = {}
    try:
        targets = parse_targets(user_input["targets"])
    except ValueError:
        errors["targets"] = "invalid_targets"
        return None, errors

    if not (1 <= user_input["min_up"] <= len(targets)):
        errors["min_up"] = "min_up_out_of_range"
        return None, errors

    return targets, errors


class UptimeCheckerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            targets, errors = _validate(user_input)
            if targets is not None:
                return self.async_create_entry(
                    title=user_input["name"],
                    data={
                        "name": user_input["name"],
                        "targets": targets,
                        "min_up": user_input["min_up"],
                        "scan_interval": user_input["scan_interval"],
                    },
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "UptimeCheckerOptionsFlow":
        return UptimeCheckerOptionsFlow()


class UptimeCheckerOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        current = self.config_entry.data
        errors: dict[str, str] = {}

        if user_input is not None:
            targets, errors = _validate(user_input)
            if targets is not None:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        "name": current["name"],
                        "targets": targets,
                        "min_up": user_input["min_up"],
                        "scan_interval": user_input["scan_interval"],
                    },
                )
                return self.async_create_entry(title="", data={})

        targets_str = ",".join(
            f"{t['type']}:{t['address']}" for t in current["targets"]
        )
        schema = vol.Schema(
            {
                vol.Required("targets", default=targets_str): str,
                vol.Required("min_up", default=current["min_up"]): int,
                vol.Required("scan_interval", default=current["scan_interval"]): int,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
