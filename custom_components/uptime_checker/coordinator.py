"""DataUpdateCoordinator for uptime_checker."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .checks import CHECK_FUNCS
from .logic import compute_group_status

_LOGGER = logging.getLogger(__name__)


class UptimeGroupCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        targets: list[dict[str, str]],
        min_up: int,
        scan_interval: int,
    ) -> None:
        # always_update=True: without it, DataUpdateCoordinator skips
        # notifying entities (and bumping last_reported) whenever a fetch
        # returns data equal to the previous fetch. For an uptime monitor,
        # repeated "still up"/"still down" results are the common case and
        # still need to be reported as fresh, or the entity looks frozen.
        super().__init__(
            hass,
            _LOGGER,
            name=f"uptime_checker_{name}",
            update_interval=timedelta(seconds=scan_interval),
            always_update=True,
        )
        self.targets = targets
        self.min_up = min_up

    async def _async_update_data(self) -> dict:
        results = await asyncio.gather(
            *(
                CHECK_FUNCS[target["type"]](target["address"])
                for target in self.targets
            )
        )
        target_status = {
            f"{target['type']}:{target['address']}": ok
            for target, ok in zip(self.targets, results)
        }
        return compute_group_status(target_status, self.min_up)
