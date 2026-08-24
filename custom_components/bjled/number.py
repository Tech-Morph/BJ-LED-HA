"""Number platform for BJ_LED: effect animation speed."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAX_EFFECT_SPEED, MIN_EFFECT_SPEED
from .device import BjLedDevice


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    device: BjLedDevice = hass.data[DOMAIN][entry.entry_id]
    name: str = entry.data.get("name", "BJ_LED Light")
    async_add_entities([BjLedEffectSpeed(device, name)])


class BjLedEffectSpeed(NumberEntity):
    """1 (fastest) - 10 (slowest) animation speed for effect modes."""

    _attr_has_entity_name = True
    _attr_name = "Effect Speed"
    _attr_icon = "mdi:speedometer"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = MIN_EFFECT_SPEED
    _attr_native_max_value = MAX_EFFECT_SPEED
    _attr_native_step = 1

    def __init__(self, device: BjLedDevice, name: str) -> None:
        self._device = device
        self._attr_unique_id = f"{device.address}_effect_speed"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.address)},
            "name": name,
            "manufacturer": "MohuanLED / BJ_LED",
            "model": "BJ_LED",
        }

    @property
    def available(self) -> bool:
        return self._device.available

    @property
    def native_value(self) -> float:
        return self._device.effect_speed

    async def async_set_native_value(self, value: float) -> None:
        # Doesn't write anything by itself -- takes effect the next time
        # an effect mode is (re)selected on the light entity, since the
        # speed byte is only sent as part of the effect command.
        self._device.effect_speed = int(value)
        self.async_write_ha_state()
