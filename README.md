<div align="center" markdown="1">

<img src=".github/meshtastic_logo.png" alt="Meshtastic Logo" width="80"/>

<h1>firmware+ for Meshtastic devices (Meshtastic develop 2.8.3)</h1>

</div>

## Overview

Fork of the Meshtastic firmware `develop` branch with the FW+ additions, for Meshtastic devices in any role
(client, router, base station). Build environments:

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
| `heltec-v3` | Heltec WiFi LoRa 32 V3 (ESP32-S3, SX1262, OLED), from build 1373 | - | `He3` |
| `heltec-v4` | Heltec WiFi LoRa 32 V4 (ESP32-S3, SX1262, OLED), from build 1373 | - | `He4` |
| `rak4631` | RAK WisBlock 4631 (nRF52840, SX1262, optional RAK1921 OLED), from build 1374 | - | `Rak` |
| `tbeam` | LILYGO T-Beam (ESP32), from build 1375 | - | `Tb` |
| `tlora-v2-1-1_6` | LILYGO T-LoRa V2.1-1.6 (ESP32), from build 1375 | - | `TL16` |
| `tbeam-s3-core` | LILYGO T-Beam Supreme / S3 Core (ESP32-S3), from build 1375 | - | `TbS3` |
| `heltec-wireless-paper` | Heltec Wireless Paper (ESP32-S3, e-paper), from build 1375 | - | `HeWP` |
| `station-g2` | B&Q Station G2 (ESP32-S3), from build 1375 | - | `SG2` |
| `t-deck` | LILYGO T-Deck (ESP32-S3, keyboard, TFT), from build 1375 | - | `TD` |
| `t-echo` | LILYGO T-Echo (nRF52840, e-paper), from build 1375 | - | `TE` |
| `heltec-mesh-node-t114` | Heltec Mesh Node T114 (nRF52840, TFT), from build 1375 | - | `T114` |
| `heltec-mesh-node-t096` | Heltec Mesh Node T096 (nRF52840, TFT), from build 1375 | - | `T96` |
| `tracker-t1000-e` | Seeed SenseCAP T1000-E tracker (nRF52840), from build 1375 | - | `T1k` |
| `heltec-mesh-pocket-5000-inkhud` | Heltec MeshPocket 5000 mAh, InkHUD (nRF52840), from build 1375 | - | `MP5` |
| `heltec-mesh-pocket-10000-inkhud` | Heltec MeshPocket 10000 mAh, InkHUD (nRF52840), from build 1375 | - | `MP10` |
| `rak_killer_v2` | [RAK Killer v2](https://github.com/Uroboros67/rak_killer): SuperMini nRF52840 + HT-RA62 (hardware model `PRIVATE_HW`), from build 1375 | - | `RK2` |
| `rp2040-lora` | RP2040-LoRa (RP2040), from build 1375 | - | `R24` |
| `picow` | Raspberry Pi Pico W with a LoRa module (RP2040), from build 1375 | - | `PiW` |
| `native` | Linux (`meshtasticd`, x86_64 and arm64, Debian 12 / Raspberry Pi OS Bookworm), from build 1375 | - | `Lx` |

Tested on hardware: the Hydra variants, nRF52 Pro-micro with a radio module, Heltec V3, RAK4631 and Xiao nRF52840.
The boards added in build 1375 are not tested yet.

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

Main additions over upstream: ShortSlow as the default LoRa preset (from build 1375), node statistics on demand
(OnDemand), telemetry and position limiters,
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
Pro-micro, `Xn` = Xiao nRF52840, `Xs` = Xiao ESP32-S3, `HeW` / `He3` / `He4` = Heltec WSL V3 / V3 / V4, `Rak` =
RAK4631; from build 1375 also the suffixes of the new boards in the table above. In build 1371 only the Hydra PSRAM / E22P builds had a
suffix (`R`, `P`, `PR`).

## Flashing

- **ESP32 (Hydra, T-Beam, T-LoRa, Xiao ESP32-S3, Heltec WSL V3 / V3 / V4 / Wireless Paper, T-Beam S3, Station G2,
  T-Deck):** flash `firmware-<env>-<version>-ota.factory.bin` at
  offset `0x0` with esptool. The `-ota` image carries the Meshtastic OTA loader, so later updates can come over
  Bluetooth or Wi-Fi from the app; `-noota` leaves it out (USB updates only). From build 1374 the ESP32-S3 boards get
  both variants too (1373 and older: one `factory.bin` without the loader).
- **nRF52 (Pro-micro, Xiao nRF52840, RAK4631, T-Echo, T114, T096, T1000-E, MeshPocket, RAK Killer v2):** double-tap
  reset to open the UF2 bootloader drive, then copy `firmware-<env>-<version>.uf2` onto it. The `.zip` is for DFU
  updates over USB or Bluetooth.
- **RP2040 (RP2040-LoRa, Pico W):** hold BOOTSEL while plugging in USB, then copy `firmware-<env>-<version>.uf2`
  onto the drive.
- **Linux:** unpack `meshtasticd-<version>-linux-<arch>.tar.gz` and follow its `README.txt`.

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

- **Build 1375 (2026-11-23):** ShortSlow is the default modem preset after a clean flash or factory reset, and
  the default MQTT server is `loranet.pl` (root `msh/PL`, encryption on, no login; MQTT stays off until enabled); new
  builds for T-Beam, T-LoRa V2.1-1.6, T-Beam S3 Core, Heltec Wireless Paper, Station G2, T-Deck, T-Echo, T114, T096, T1000-E, MeshPocket 5000 / 10000 InkHUD, RAK Killer v2, RP2040-LoRa, Pico W and Linux (`meshtasticd`,
  x86_64 / arm64); the new ESP32 boards carry the OTA loader (`-ota` / `-noota`). Heltec V4: low-battery sleep at
  about 20 % (~3.4 V) instead of the empty point, and a timed wake-up after Power -> Super deep sleep duration, so the
  node comes back once it is charged again (patch by rpcwol).
  Heltec WSL V3: GPIO35 (the LED) gets a 1 ms pulse every second for an external watchdog, whatever the charge state
  (the LED heartbeat stopped while charging, and the watchdog reset the board); the LED no longer shows charging.
  OnDemand "Nodes list (10 recent active)" really returns up to 10 nodes (one packet held only 3-4; the list now
  continues in 2-3 packets).
- **Build 1374 (2026-11-20):** zero-hop between routers (NodeModAdmin `zero_hop_routers`, off by default; a router relaying a router's packet keeps the hop limit while channel utilization is below `zero_hop_max_chutil`, default 25 %, optionally only for directly heard relays), OnDemand answers each requester and request type at most once per 25 s (55 s for multi-packet lists; our own phone is not limited), OTA loader for the ESP32-S3 boards (`-ota` / `-noota` images), Polish characters on the OLED (Heltec V3 / V4, RAK4631), new build for RAK4631 (`Rak`).
- **Build 1373 (2026-11-18):** OnDemand node list limited to the 10 most recently heard nodes in one packet (direct neighbours list unchanged), release builds in GitHub Actions, new builds for Heltec V3 (`He3`) and Heltec V4 (`He4`).
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
- rpcwol: Heltec V4 low-battery sleep and wake-up patch.
- Board designs: [NanoVHF/Meshtastic-DIY](https://github.com/NanoVHF/Meshtastic-DIY/tree/main),
  [Uroboros67/rak_killer](https://github.com/Uroboros67/rak_killer) (RAK Killer v2; variant from musznik/firmware).
