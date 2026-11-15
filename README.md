<div align="center" markdown="1">

<img src=".github/meshtastic_logo.png" alt="Meshtastic Logo" width="80"/>

<h1>firmware+ for Hydra boards (Meshtastic develop 2.8.3)</h1>

</div>

## Overview

Fork of the Meshtastic firmware `develop` branch, built for Hydra boards: ESP32 with a LoRa E22P-868M30S radio.
Build environments:

- `hydra` - Meshtastic DIY v1 Hydra board (hardware model `HYDRA`).
- `hydraE22P` - ESP32 without PSRAM, E22P module.
- `hydraE22P_psram` - Freenove ESP32-WROVER board with PSRAM (up to 1000 nodes).
- `hydraE22P_idf4` - test build on ESP-IDF 4.4, without Bluetooth.

Main additions over upstream: node statistics on demand (OnDemand), telemetry and position limiters,
opportunistic flooding, NodeMod / SignalReply, Wi-Fi and Bluetooth TX power settings, and extra
diagnostics (channel utilization, flash and heap counters, relay and duplicate counters).
Based on upstream `develop` from 2026-11-02.

## Version string

`2.8.3.<build><suffix>`, for example `2.8.3.39PR`. The build number comes from `hydra_build.txt`.

| Suffix | Variant |
| ------ | ------- |
| none   | `hydra` |
| `P`    | E22P module (`hydraE22P`, `hydraE22P_idf4`) |
| `PR`   | E22P module with PSRAM (`hydraE22P_psram`) |

`R` alone marks a PSRAM build without E22P.

## Configuration

All Hydra settings live in the `[hydra_userprefs]` section at the top of
`variants/esp32/diy/hydra_e22p/platformio.ini` and apply to every Hydra environment.
Values marked `USERPREFS_*` are applied on the first boot after a clean flash or a factory reset.

| Option | Default | Effect |
| ------ | ------- | ------ |
| `ota_loader` | `yes` | Adds the Meshtastic OTA loader (`mt-esp32-ota.bin`, partition `ota_1`) to `factory.bin` and to upload. |
| `USERPREFS_CONFIG_OWNER_LONG_NAME` / `_SHORT_NAME` | off | Node name. |
| `USERPREFS_CONFIG_DEVICE_ROLE` + `USERPREFS_ALLOW_ROUTER_ROLES` | `ROUTER_LATE` | Initial role; router roles are allowed. |
| `USERPREFS_LORACONFIG_TX_POWER` | `2` | Initial LoRa power on the SX1262 chip, dBm. The E22P amplifier adds gain; measure and tune. |
| `ROUTER_MIN_TELEMETRY_INTERVAL_SECS` | `14400` | Lowest telemetry interval for ROUTER / ROUTER_LATE (upstream 12 h). |
| `NEIGHBORINFO_ALLOW_DEFAULT_CHANNEL` | `1` | NeighborInfo over LoRa also on the default channel (interval floor 4 h). |
| `USERPREFS_FIXED_GPS*` | off | Fixed position. |
| `USERPREFS_NETWORK_WIFI_*` | off | Wi-Fi client (disables Bluetooth on ESP32). |
| `HYDRA_WIFI_TX_POWER_QDBM` | `8` | Wi-Fi TX power in 0.25 dBm, range 8..84. |
| `admin_keys` | empty | Up to three admin public keys in base64, as shown in the app. |
| `sdkconfig` | NimBLE on core 1 | ESP-IDF settings for the Bluetooth environments. |

Do not commit a real Wi-Fi password: the repository is public.

## Change log

Full change log: [HYDRA.md](HYDRA.md).

- **Build 39 (2026-11-15):** shared `[hydra_userprefs]`, bundled OTA loader, admin keys in base64, version `2.8.3.39P/PR`, traceroute limit 10 s, Bluetooth stability fixes.
- **Build 38 (2026-11-07):** NodeMod, SignalReply, noise floor in OnDemand, `wifi_power` / `bt_power` LoRa fields, admin origin gate.
- **Builds 30-37 (2026-11-06):** Store & Forward off by default, PSRAM variant on Freenove WROVER, opportunistic flooding, NodeModAdmin in the config dump.
- **Builds 2-8 (2026-11-05):** FW+ port (airtime windows, CPU sampler, port counters, telemetry, admin), `local_stats` chain, limiters.

## Credits

- Fork description: [musznik](https://github.com/musznik/firmware) (FW+ / Meshtastic+, [loranet.pl](https://loranet.pl)).
- Upstream firmware: the [Meshtastic](https://meshtastic.org) project and its contributors.
- Previous fork: [JacekVV/Meshtastic-develop---2.8.3-hdev](https://github.com/JacekVV/Meshtastic-develop---2.8.3-hdev).
- Board designs: [NanoVHF/Meshtastic-DIY](https://github.com/NanoVHF/Meshtastic-DIY/tree/main).
