"""Sensor platform for uptime_checker."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
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
    async_add_entities([UptimeLatencySensor(coordinator, entry)])


class UptimeLatencySensor(CoordinatorEntity[UptimeGroupCoordinator], SensorEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "ms"

    def __init__(self, coordinator: UptimeGroupCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_name = f"{entry.data['name']} Latency"
        self._attr_unique_id = f"{entry.entry_id}_latency"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data["average_rtt_ms"]
