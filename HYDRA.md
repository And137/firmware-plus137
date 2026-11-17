# firmware+ for Hydra boards (Meshtastic develop 2.8.3)

Fork of the Meshtastic firmware `develop` branch for Hydra boards (ESP32 with a LoRa E22P-868M30S radio).
Build environments: `hydra`, `hydra_psram` (standard E22, ESP32-WROVER with PSRAM), `hydraE22P` (no PSRAM) and `hydraE22P_psram` (Freenove ESP32-WROVER, up to 1000 nodes).

Main additions over upstream: node statistics on demand (OnDemand), telemetry and position limiters,
opportunistic flooding, NodeMod / SignalReply, Wi-Fi and Bluetooth TX power settings, and extra
diagnostics (channel utilization, flash and heap counters, relay and duplicate counters).
Based on upstream `develop` from 2026-11-02.

## Change log

### Unreleased (build 1371)
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
