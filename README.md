<div align="center" markdown="1">

<img src=".github/meshtastic_logo.png" alt="Meshtastic Logo" width="80"/>

<h1>firmware+ for Meshtastic routers (Meshtastic develop 2.8.3)</h1>

</div>

## Overview

Fork of the Meshtastic firmware `develop` branch for router nodes (ROUTER / ROUTER_LATE).
Build environments:

| Environment | Board | Suffix in 1371 | Suffix from 1372 |
| ----------- | ----- | -------------- | ---------------- |
| `hydra` | Meshtastic DIY v1 Hydra, ESP32 without PSRAM, standard E22 (hardware model `HYDRA`) | none | `Hy` |
| `hydra_psram` | Hydra on an ESP32-WROVER with PSRAM, standard E22 (up to 1000 nodes) | `R` | `HyR` |
| `hydraE22P` | Hydra, ESP32 without PSRAM, E22P module | `P` | `HyP` |
| `hydraE22P_psram` | Freenove ESP32-WROVER with PSRAM, E22P module (up to 1000 nodes) | `PR` | `HyPR` |
| `nrf52_promicro_diy_tcxo` | nRF52840 Pro-micro DIY with an E22 / HT-RA62 module (TCXO) | none | `nF` |
| `seeed_xiao_nrf52840_kit` | Seeed Xiao nRF52840 Kit (Wio-SX1262) | none | `Xn` |
| `seeed-xiao-s3` | Seeed Xiao ESP32-S3 (Wio-SX1262, 8 MB flash, PSRAM) | none | `Xs` |
| `heltec-wsl-v3` | Heltec Wireless Stick Lite V3 (ESP32-S3, SX1262, 8 MB flash) | - | `HeW` |

Tested on hardware: the Hydra variants. The nRF52 Pro-micro build was checked on the bench (boots, Bluetooth,
configuration) without a radio module. The Xiao and Heltec WSL V3 builds are not tested yet.
Builds for Heltec V3 (`He3`) and Heltec V4 (`He4`) will follow in an upcoming release.

> [!NOTE]
> **Version suffixes from build 1372.** Every build names its board at the end of the version: Hydra `Hy`
> (`2.8.3.1372Hy`, `HyR`, `HyP`, `HyPR`), Pro-micro `nF`, Xiao nRF52840 `Xn`, Xiao ESP32-S3 `Xs`. `P` (E22P module)
> and `R` (PSRAM) keep their meaning. Release 1371 used the old form (`2.8.3.1371`, `R`, `P`, `PR`).

> [!WARNING]
> **Never flash an E22P build (`hydraE22P`, `hydraE22P_psram`, version suffix `P` / `PR`, from build 1372 `HyP` / `HyPR`) onto a board with a standard E22 module.**
> It damages the radio. Match the build to the module on the board: standard E22 -> `hydra` or `hydra_psram`
> (none / `R`, later `Hy` / `HyR`), E22P -> `hydraE22P` or `hydraE22P_psram` (`P` / `PR`, later `HyP` / `HyPR`). The suffix is the last part of the
> firmware version shown in the app, so check it before updating over OTA as well.

> [!CAUTION]
> The Pro-micro build does not limit TX power for an external PA: with the default settings the SX1262 transmits
> at 22 dBm. With an E22-900M30S or M33S module, set a low `tx_power` in the app before setting the region.

Main additions over upstream: node statistics on demand (OnDemand), telemetry and position limiters,
opportunistic flooding, NodeMod / SignalReply, Wi-Fi and Bluetooth TX power settings, and extra
diagnostics (channel utilization, flash and heap counters, relay and duplicate counters).
Wi-Fi / Bluetooth TX power settings and the NodeDB write fixes apply to Hydra only; the other boards have the
FW+ modules and statistics.
Based on upstream `develop` from 2026-11-02.

## Version string

`2.8.3.137<build><suffix>`, for example `2.8.3.1372HyPR` for build 2. The build number comes from `hydra_build.txt`
and is shared by every environment; the firmware-plus137 numbering restarted at 1 (builds up to 40 used
`2.8.3.<build><suffix>`). The same `137<build>` number is the FW+ version reported over OnDemand. The suffix
marks the board (see the table above): Hydra `Hy`, plus `P` for the E22P module and `R` for PSRAM; `nF` =
Pro-micro, `Xn` = Xiao nRF52840, `Xs` = Xiao ESP32-S3. In build 1371 only the Hydra PSRAM / E22P builds had a
suffix (`R`, `P`, `PR`).

## Flashing

- **Hydra, Xiao ESP32-S3 and Heltec WSL V3:** flash `firmware-<env>-<version>.factory.bin` at offset `0x0` with esptool.
- **nRF52 (Pro-micro, Xiao nRF52840):** double-tap reset to open the UF2 bootloader drive, then copy
  `firmware-<env>-<version>.uf2` onto it. The `.zip` is for DFU updates over USB or Bluetooth.

## Hydra configuration

All Hydra settings live in the `[hydra_userprefs]` section at the top of
`variants/esp32/diy/hydra/platformio.ini` and apply to every Hydra environment.
Values marked `USERPREFS_*` are applied on the first boot after a clean flash or a factory reset.

| Option | Default | Effect |
| ------ | ------- | ------ |
| `ota_loader` | `yes` | Adds the Meshtastic OTA loader (`mt-esp32-ota.bin`, partition `ota_1`) to `factory.bin` and to upload. |
| `USERPREFS_CONFIG_OWNER_LONG_NAME` / `_SHORT_NAME` | off | Node name. |
| `USERPREFS_CONFIG_DEVICE_ROLE` + `USERPREFS_ALLOW_ROUTER_ROLES` | `ROUTER_LATE` | Initial role; router roles are allowed. |
| `HYDRA_NO_USER_BUTTON` | on | No user button on GPIO39; comment out on boards that have one (with a pull-up). |
| `USERPREFS_LORACONFIG_TX_POWER` | `2` | Initial LoRa power on the SX1262 chip, dBm. The E22P amplifier adds gain; measure and tune. |
| `ROUTER_MIN_TELEMETRY_INTERVAL_SECS` | `14400` | Lowest telemetry interval for ROUTER / ROUTER_LATE (upstream 12 h). |
| `NEIGHBORINFO_ALLOW_DEFAULT_CHANNEL` | `1` | NeighborInfo over LoRa also on the default channel (interval floor 4 h). |
| `HYDRA_NODEDB_ATOMIC_SAVE` | `1` | Write `nodes.proto` via temp file + rename; a crash during the write keeps the old database. |
| `HYDRA_NODEDB_DEFER_WHILE_BLE` | `1800000` | Hold routine NodeDB flash writes while a phone is connected over BLE, at most this many ms. |
| `USERPREFS_FIXED_GPS*` | off | Fixed position. |
| `USERPREFS_NETWORK_WIFI_*` | off | Wi-Fi client (disables Bluetooth on ESP32). |
| `HYDRA_WIFI_TX_POWER_QDBM` | `8` | Wi-Fi TX power in 0.25 dBm, range 8..84. |
| `newlib_nano` | `no` | Full newlib: keeps `memcpy`/`memset` in IRAM. Needed for Bluetooth on the classic ESP32. |
| `admin_keys` | empty | Up to three admin public keys in base64, as shown in the app. |

## Change log

Full change log: [HYDRA.md](HYDRA.md).

- **Build 1372 (2026-11-18):** new build for Heltec WSL V3 (`HeW`), board suffixes in the version (`Hy`, `HyR`, `HyP`, `HyPR`, `nF`, `Xn`, `Xs`), OnDemand noise floor history (10 averages of 20 samples, request type 26).
- **Build 1371 (2026-11-17):** new numbering `2.8.3.137<build>`, compatibility with the new FW+ app (`wifi_power` / `bt_power` moved to fields 200/201, Broadcast Assist over admin), BLE kept up on routers, new builds for nRF52 Pro-micro, Xiao nRF52840 Kit and Xiao ESP32-S3; board suffixes (`Hy`, `nF`, `Xn`, `Xs`) start with build 1372.
- **Build 40 (2026-11-16):** Bluetooth crash fix (full newlib), atomic NodeDB save, `hydra_psram` environment, no user button on GPIO39.
- **Build 39 (2026-11-15):** shared `[hydra_userprefs]`, bundled OTA loader, admin keys in base64, version `2.8.3.39P/PR`, traceroute limit 10 s, Bluetooth stability fixes.
- **Build 38 (2026-11-07):** NodeMod, SignalReply, noise floor in OnDemand, `wifi_power` / `bt_power` LoRa fields, admin origin gate.
- **Builds 30-37 (2026-11-06):** Store & Forward off by default, PSRAM variant on Freenove WROVER, opportunistic flooding, NodeModAdmin in the config dump.
- **Builds 2-8 (2026-11-05):** FW+ port (airtime windows, CPU sampler, port counters, telemetry, admin), `local_stats` chain, limiters.

## Credits

Special thanks to:

- [musznik/firmware](https://github.com/musznik/firmware), the original FW+ (Meshtastic+, [loranet.pl](https://loranet.pl)).
  Without him there would be no FW+.
- [JacekVV](https://github.com/JacekVV), whose fork
  [Meshtastic-develop---2.8.3-hdev](https://github.com/JacekVV/Meshtastic-develop---2.8.3-hdev) became the base of
  this FW+ version.

Also:

- Upstream firmware: the [Meshtastic](https://meshtastic.org) project and its contributors.
- Board designs: [NanoVHF/Meshtastic-DIY](https://github.com/NanoVHF/Meshtastic-DIY/tree/main).
