"""Binary sensor platform for uptime_checker."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import UptimeGroupCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: UptimeGroupCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([UptimeGroupBinarySensor(coordinator, entry)])


class UptimeGroupBinarySensor(
    CoordinatorEntity[UptimeGroupCoordinator], BinarySensorEntity
):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: UptimeGroupCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_name = entry.data["name"]
        self._attr_unique_id = f"{entry.entry_id}_uptime"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data["is_up"])

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "up_count": self.coordinator.data["up_count"],
            "total": self.coordinator.data["total"],
            "average_rtt_ms": self.coordinator.data["average_rtt_ms"],
            "targets": self.coordinator.data["targets"],
        }
