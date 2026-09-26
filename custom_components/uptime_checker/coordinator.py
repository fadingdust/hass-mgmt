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
        # always_update=True: semantically correct for an uptime monitor —
        # repeated "still up"/"still down" results are still fresh reports.
        # Per-target RTT (see checks.py) also means fetch results almost
        # never compare equal cycle-to-cycle, so external API/UI views of
        # last_reported stay live rather than freezing on cached state.
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
            f"{target['type']}:{target['address']}": result
            for target, result in zip(self.targets, results)
        }
        return compute_group_status(target_status, self.min_up)
