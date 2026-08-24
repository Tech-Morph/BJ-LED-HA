"""Light platform for MohuanLED (BJ_LED) strips.

These strips have no dedicated brightness command, so brightness is
implemented (same approach as 8none1/bj_led) by scaling the RGB values
sent to the device rather than a separate GATT write.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, EFFECT_NAMES, cmd_color, cmd_effect, cmd_power
from .device import MohuanLedDevice

_LOGGER = logging.getLogger(__name__)

EFFECT_NAME_TO_ID = {v: k for k, v in EFFECT_NAMES.items()}


def _scale_rgb(rgb: tuple[int, int, int], brightness: int) -> tuple[int, int, int]:
    factor = brightness / 255
    return tuple(round(c * factor) for c in rgb)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light platform from a config entry."""
    device: MohuanLedDevice = hass.data[DOMAIN][entry.entry_id]
    name: str = entry.data.get("name", "MohuanLED Light")
    async_add_entities([MohuanLedLight(device, name)])


class MohuanLedLight(LightEntity):
    """Representation of a MohuanLED (BJ_LED) BLE light strip."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = list(EFFECT_NAMES.values())

    def __init__(self, device: MohuanLedDevice, name: str) -> None:
        self._device = device
        self._attr_unique_id = device.address
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.address)},
            "name": name,
            "manufacturer": "MohuanLED / BJ_LED",
            "model": "BJ_LED",
        }
        self._brightness = 255
        self._rgb_color = (255, 255, 255)
        self._effect: str | None = None

    @property
    def is_on(self) -> bool:
        return self._device.is_on

    @property
    def brightness(self) -> int:
        return self._brightness

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        return self._rgb_color

    @property
    def effect(self) -> str | None:
        return self._effect

    @property
    def available(self) -> bool:
        return self._device.available

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._device.async_write(cmd_power(True))
        self._device.is_on = True

        if ATTR_RGB_COLOR in kwargs:
            self._rgb_color = kwargs[ATTR_RGB_COLOR]
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]

        if ATTR_RGB_COLOR in kwargs or ATTR_BRIGHTNESS in kwargs:
            scaled = _scale_rgb(self._rgb_color, self._brightness)
            await self._device.async_write(cmd_color(*scaled))

        if ATTR_EFFECT in kwargs:
            effect_name = kwargs[ATTR_EFFECT]
            effect_id = EFFECT_NAME_TO_ID.get(effect_name)
            if effect_id is not None:
                await self._device.async_write(
                    cmd_effect(effect_id, self._device.effect_speed)
                )
                self._effect = effect_name

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._device.async_write(cmd_power(False))
        self._device.is_on = False
        self.async_write_ha_state()
