# MohuanLED (BJ-LED-HA)

A custom Home Assistant integration for `BJ_LED` Bluetooth LED strips,
controlled by the MohuanLED app.

## Credit

The protocol used here was originally reverse engineered by
[8none1/bj_led](https://github.com/8none1/bj_led) via btsnoop capture of
the MohuanLED app's BLE traffic. This repo is an independent
reimplementation built around a shared-connection architecture (see
[Tech-Morph/Lotus-Lantern-HA](https://github.com/Tech-Morph/Lotus-Lantern-HA)
for the sibling integration this pattern originated from), rather than a
fork -- if you just want a working BJ_LED integration without any of the
extras here, the original repo is a great option too.

## Why This Version

- Single shared BLE connection per device across all entities (light +
  number), managed by `device.py`, with an `asyncio.Lock` to prevent
  concurrent connection attempts from racing each other.
- Automatic reconnect on unexpected disconnect, plus a periodic 25s
  keep-alive write to prevent idle disconnects through ESPHome Bluetooth
  proxies.
- `available` reflects live connection state, not just recent
  advertisement sightings (proxies pause scanning while a GATT connection
  is open, so relying on advertisements alone causes false "Unavailable"
  flapping).

## Protocol Reference

Write characteristic: `0000ee01-0000-1000-8000-00805f9b34fb`

| Function | Bytes (hex) |
|---|---|
| Power on | `69 96 02 01 01` |
| Power off | `69 96 02 01 00` |
| Set RGB color | `69 96 05 02 RR GG BB` |
| Set effect + speed | `69 96 03 03 MM SS` (MM=0x00-0x15, SS=0x01 fast-0x0a slow) |

There is no dedicated brightness command -- brightness is achieved by
scaling the RGB values sent in the color command, matching the approach
in the original 8none1/bj_led project.

## Installing Locally

1. Copy `custom_components/mohuanled/` into
   `config/custom_components/mohuanled/` on your Home Assistant instance.
2. Restart Home Assistant.
3. Settings → Devices & Services → Add Integration → search "MohuanLED".

## Installing via HACS

Add this repo as a HACS custom repository
(`https://github.com/Tech-Morph/BJ-LED-HA`), category "Integration", then
install and add it the same way as above. A tagged GitHub release (e.g.
`v0.1.0`) is needed for HACS to fully recognize and install the repo.

## Known Limitations

- Effect mode names aren't published anywhere (the MohuanLED app just
  shows a numbered animation preview grid), so they're exposed as generic
  `Effect 0` through `Effect 21`. Feel free to experiment and open a PR
  with real names if you figure out the mapping.
- Effect speed only takes effect the next time an effect is (re)selected,
  since the speed byte is only sent as part of the effect-select command,
  not independently.
