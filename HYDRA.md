# firmware+ for Meshtastic devices (Meshtastic develop 2.8.3)

Fork of the Meshtastic firmware `develop` branch with the FW+ additions, for Meshtastic devices in any role.
Build environments: `hydra`, `hydra_psram` (standard E22, ESP32-WROVER with PSRAM), `hydraE22P` (no PSRAM), `hydraE22P_psram` (Freenove ESP32-WROVER, up to 1000 nodes), `nrf52_promicro_diy_tcxo` (nRF52840 Pro-micro DIY), `seeed_xiao_nrf52840_kit`, `seeed-xiao-s3`, `heltec-wsl-v3`, `heltec-v3`, `heltec-v4`, `rak4631` and, from build 1375, `tbeam`, `tlora-v2-1-1_6`, `tbeam-s3-core`, `heltec-wireless-paper`, `station-g2`, `t-deck`, `t-echo`, `heltec-mesh-node-t114`, `heltec-mesh-node-t096`, `tracker-t1000-e`, `heltec-mesh-pocket-5000-inkhud`, `heltec-mesh-pocket-10000-inkhud`, `rak_killer_v2`, `rp2040-lora`, `picow` and `native` (Linux).

Main additions over upstream: node statistics on demand (OnDemand), telemetry and position limiters,
opportunistic flooding, NodeMod / SignalReply, Wi-Fi and Bluetooth TX power settings, and extra
diagnostics (channel utilization, flash and heap counters, relay and duplicate counters).
Based on upstream `develop` from 2026-11-02.

## Change log

### Build 1375 (2026-11-23)
- ShortSlow is the default modem preset after a clean flash or factory reset (`USERPREFS_LORACONFIG_MODEM_PRESET` in `userPrefs.jsonc`).
- Default MQTT server `loranet.pl`: root `msh/PL`, encryption on, TLS off, no login (`USERPREFS_MQTT_*`). MQTT itself stays off until enabled.
- OnDemand "Nodes list (10 recent active)" really returns up to 10 nodes: one 190-byte packet held only 3-4 entries, so the list now continues in further packets (`packet_index` / `packet_total`).
- Heltec V4 (`FWPLUS_LOW_BATT_WAKE`, patch by [rpc](https://github.com/rpce)): low-battery sleep at the third-lowest OCV point (~3.42 V, ~20 %) instead of the empty point, and a timer wake-up after Power -> Super deep sleep duration (`sds_secs`).
- Heltec WSL V3: `HAS_HARDWARE_WATCHDOG` on GPIO35 (the LED), a 1 ms pulse every second plus one at the start of `setup()`, for an external watchdog. The LED heartbeat stopped while charging, so the watchdog reset the board; the LED no longer shows charging.
- New builds: `tbeam` (`Tb`), `tlora-v2-1-1_6` (`TL16`), `tbeam-s3-core` (`TbS3`), `heltec-wireless-paper` (`HeWP`), `station-g2` (`SG2`), `t-deck` (`TD`) - all six with the OTA loader -, `t-echo` (`TE`), `heltec-mesh-node-t114` (`T114`), `heltec-mesh-node-t096` (`T96`), `tracker-t1000-e` (`T1k`), `heltec-mesh-pocket-5000-inkhud` (`MP5`), `heltec-mesh-pocket-10000-inkhud` (`MP10`), `rak_killer_v2` (`RK2`, new variant from musznik/firmware, PRIVATE_HW), `rp2040-lora` (`R24`), `picow` (`PiW`) and `native` (`Lx`, meshtasticd for Linux x86_64 / arm64, built in Debian 12).
- Description: firmware+ for Meshtastic devices in any role, not only routers.

### Build 1374 (2026-11-20)
- Zero-hop between routers: new NodeModAdmin fields `zero_hop_routers` (46, off by default), `zero_hop_max_chutil` (47, percent, 0 = 25) and `zero_hop_direct_only` (48). When on, `Router::shouldDecrementHopLimit()` keeps the hop limit for a packet relayed by any router-role node (ROUTER, ROUTER_LATE, CLIENT_BASE) that the relay byte resolves to unambiguously, without the favorites list, as long as channel utilization is below the threshold; with `zero_hop_direct_only` only for relays heard directly. The first hop always decrements, as before. Set from the Mesh+ 137 app (FW+ Configuration → Zero-hop between routers).
- OnDemand rate limit: each requester gets at most one answer per request type every 25 s (55 s for `REQUEST_NODES_DIRECT_ONLINE`, `REQUEST_ROUTING_TABLE` and `REQUEST_PACKET_EXCHANGE_HISTORY`); repeats are dropped without an answer. Requests from the node's own phone are not limited. Static 16-entry table, no heap use.
- ESP32-S3 boards (`heltec-v3`, `heltec-v4`, `heltec-wsl-v3`, `seeed-xiao-s3`) bundle the Meshtastic OTA loader in `ota_1`; releases carry `-ota` / `-noota` factory images as for Hydra (the pack script reads the `ota_1` offset from the partition table).
- Polish characters on the OLED (`OLED_PL=1`) for Heltec V3, Heltec V4 and RAK4631.
- New build: `rak4631` (RAK WisBlock 4631, suffix `Rak`).

### Build 1373 (2026-11-18)
- New builds: `heltec-v3` (Heltec WiFi LoRa 32 V3, `He3`) and `heltec-v4` (Heltec WiFi LoRa 32 V4, `He4`), added to the 1373 release afterwards (built from the tagged commit).
- OnDemand `REQUEST_NODES_ONLINE` now answers with the 10 most recently heard nodes (within the last 2 hours, never the node itself), newest first, in a single packet (`packet_total` = 1). Before, every request sent all nodes heard in 2 hours as a series of packets, which loaded a large mesh. Request and response types are unchanged, so older apps still work; the Mesh+ 137 app labels the button "Nodes list (10 recent active)". `REQUEST_NODES_DIRECT_ONLINE` (direct neighbours) keeps the full segmented list.
- Release builds run in GitHub Actions (`.github/workflows/fwplus_release.yml`): every release env in parallel, then `bin/fwplus_pack_release.py` checks the version in each image, packs the Hydra `-ota` / `-noota` images and writes `SHA256SUMS.txt`, and a draft release is created. The inherited upstream workflows are disabled in this repository.

### Build 1372 (2026-11-18)
- New build: `heltec-wsl-v3` (Heltec Wireless Stick Lite V3).
- Version suffix names the board: `2.8.3.1372Hy` / `HyR` / `HyP` / `HyPR` (Hydra), `nF` (Pro-micro), `Xn` (Xiao nRF52840), `Xs` (Xiao ESP32-S3), `HeW` (Heltec WSL V3). `He3` (Heltec V3) and `He4` (Heltec V4) are reserved for upcoming builds.
- OnDemand noise floor history: `REQUEST_NOISE_FLOOR_HISTORY` (26) returns `NoiseFloorHistory` (`OnDemandResponse` field 13) with up to 10 averages of 20 consecutive RSSI samples, newest first, each with its age in seconds. Types 26/27 and field 13 are taken over from the dropped DTN overlay. The current value stays in `NodeStats.noise_floor`.

### Build 1371 (2026-11-17)
- New builds: `nrf52_promicro_diy_tcxo` (nRF52840 Pro-micro DIY), `seeed_xiao_nrf52840_kit` and `seeed-xiao-s3`. From build 1372 version suffixes are `Hy` / `HyP` / `HyR` / `HyPR` (Hydra), `nF`, `Xn` and `Xs`. OnDemand node stats and extended local stats report filesystem usage on nRF52 (littlefs block count); before, nRF52 builds did not compile.
- New numbering: version `2.8.3.137<build><suffix>` and FW+ version `137<build>`, counter restarted at 1 (`2.8.3.1371PR`, FW+ version 1371).
- `LoRaConfig.wifi_power` / `bt_power` renumbered 108/109 -> 200/201: field 108 collides with upstream `LoRaConfig.transparent_mode`, which current Meshtastic apps decode as a bool. Saved values from earlier builds reset to defaults once.
- Broadcast Assist config readable and writable over admin (`BROADCAST_ASSIST_CONFIG` get, `broadcast_assist` set, applied without reboot).
- The connect-time config dump now also carries NodeMod and Broadcast Assist, so clients show the real values without a separate request.
- ROUTER / ROUTER_LATE (and `is_power_saving`) no longer light-sleep while a BLE client is connected: the DARK -> LS timer used to fire on a connected but quiet phone, and the 30 s sleep dropped the link. The node now returns to DARK instead and sleeps after the client disconnects.

### Build 40 (2026-11-16)
- Bluetooth crash fix: newlib-nano (`--specs=nano.specs`) linked `memcpy`/`memset`/`memmove` into flash; the classic-ESP32 Bluetooth controller interrupt called them during flash writes and panicked (`Cache error`, `ld_acl.c` / `ea.c` asserts) or broke the write (`Readback failed`). Hydra builds now link the full newlib (`newlib_nano = no`) and drop the IRAM memcpy/memset wrappers.
- NimBLE host task back on the default core 0.
- NodeDB: `nodes.proto` saved atomically (`HYDRA_NODEDB_ATOMIC_SAVE`); routine saves held while a phone is connected over BLE, at most 30 min (`HYDRA_NODEDB_DEFER_WHILE_BLE`).
- `HYDRA_NO_USER_BUTTON`: no user button on GPIO39 (a floating pin read as a held button and put the node into deep sleep).
- New environment `hydra_psram` (standard E22, ESP32-WROVER with PSRAM); all Hydra environments in `variants/esp32/diy/hydra`.
- PSRAM environments: `CONFIG_SPIRAM_MALLOC_RESERVE_INTERNAL=32768`, `CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL=16384`, Bluetooth controller HLI off, 256-byte flash write chunks.
- OnDemand node stats no longer crash when the radio is missing.

### Build 39 (2026-11-15)
- Configuration: all Hydra settings in `[hydra_userprefs]` (`variants/esp32/diy/hydra/platformio.ini`), shared by every Hydra environment.
- Initial values: node name, role (router roles allowed via `USERPREFS_ALLOW_ROUTER_ROLES`), LoRa TX power 2 dBm, fixed position, Wi-Fi, Wi-Fi TX power.
- `custom_ota_loader`: Meshtastic OTA loader `mt-esp32-ota.bin` bundled at 0x260000 in `factory.bin` and upload.
- `custom_admin_keys`: admin public keys in base64, as shown in the app.
- `ROUTER_MIN_TELEMETRY_INTERVAL_SECS` (4 h) and `NEIGHBORINFO_ALLOW_DEFAULT_CHANNEL` (NeighborInfo over LoRa on the default channel).
- Traceroute rate limit 10 s (upstream 30 s).
- Version string `2.8.3.<build>` with suffix `P` (E22P), `R` (PSRAM), `PR` (both).
- Bluetooth: settings saved before Bluetooth is disabled (a NimBLE teardown panic can no longer lose them); no-reboot module configs (NodeMod) keep Bluetooth on; advertising restarts after a disconnect during config download.

### Build 38 (2026-11-07)
- NodeMod, SignalReply, noise floor field in OnDemand.
- New LoRa config fields `wifi_power` (108) and `bt_power` (109), exposed in CLI and firmware.
- Admin origin gate (from upstream): admin messages with `from=0` accepted only from local clients.

### Builds 30-37 (2026-11-06)
- Store & Forward off by default; byte counters; quieter UDP relay log.
- PSRAM variant on the Freenove WROVER board; build labels `vNN` and `vNNp` (replaced in build 39).
- Opportunistic flooding (ported from the fork).
- NodeModAdmin included in the config dump (build hdev-v3).

### Builds 2-8 (2026-11-05)
- FW+ port: airtime windows, CPU sampler, port counters, telemetry, admin.
- `local_stats` chain, `local_stats_extended` (used and total flash on ESP32), RX history, limiters.
- Develop build numbering.

### Submodule `protobufs` (commit 777faea)
- `LoRaConfig.wifi_power = 200`, `LoRaConfig.bt_power = 201` (108/109 until the Unreleased entry), `NodeStats.noise_floor = 40`, and NodeStats counters.
