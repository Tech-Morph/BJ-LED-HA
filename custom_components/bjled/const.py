"""Constants and packet builders for the BJ_LED (MohuanLED) protocol.

Protocol confirmed against 8none1/bj_led (https://github.com/8none1/bj_led),
which reverse engineered the MohuanLED app's BLE traffic via btsnoop capture.
All credit for the original protocol discovery goes to that project; this
is an independent reimplementation using a shared-connection architecture.
"""

from __future__ import annotations

DOMAIN = "bjled"

WRITE_CHARACTERISTIC_UUID = "0000ee01-0000-1000-8000-00805f9b34fb"

HEADER_1 = 0x69
HEADER_2 = 0x96

# Effect names are not published anywhere; the app just shows a numbered
# grid of animation previews. Exposed as generic indices 0-21.
EFFECT_COUNT = 22
EFFECT_NAMES = {i: f"Effect {i}" for i in range(EFFECT_COUNT)}

MIN_EFFECT_SPEED = 1   # fastest
MAX_EFFECT_SPEED = 10  # slowest


def _clamp(value: int, lo: int = 0, hi: int = 255) -> int:
    return max(lo, min(hi, int(value)))


def cmd_power(on: bool) -> bytearray:
    """69 96 02 01 [01/00]"""
    return bytearray([HEADER_1, HEADER_2, 0x02, 0x01, 0x01 if on else 0x00])


def cmd_color(r: int, g: int, b: int) -> bytearray:
    """69 96 05 02 RR GG BB

    The device also accepts a 4th (white) byte, but these strips have no
    white LED, so it's omitted -- matches what 8none1/bj_led does.
    """
    return bytearray(
        [HEADER_1, HEADER_2, 0x05, 0x02, _clamp(r), _clamp(g), _clamp(b)]
    )


def cmd_effect(mode: int, speed: int = MIN_EFFECT_SPEED) -> bytearray:
    """69 96 03 03 MM SS

    mode: 0x00-0x15 (0-21)
    speed: 0x01 (fastest) - 0x0a (slowest)
    """
    clamped_speed = max(MIN_EFFECT_SPEED, min(MAX_EFFECT_SPEED, int(speed)))
    return bytearray([HEADER_1, HEADER_2, 0x03, 0x03, mode & 0xFF, clamped_speed])
