"""The BJ_LED light integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .device import BjLedDevice

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.NUMBER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BJ_LED from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    device = BjLedDevice(hass, entry.data["address"])
    device.start_keep_alive()
    hass.data[DOMAIN][entry.entry_id] = device
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        device: BjLedDevice = hass.data[DOMAIN].pop(entry.entry_id)
        await device.async_shutdown()
    return unload_ok
