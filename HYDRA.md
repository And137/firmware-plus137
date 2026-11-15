# firmware+ for Hydra boards (Meshtastic develop 2.8.3)

Fork of the Meshtastic firmware `develop` branch for Hydra boards (ESP32 with a LoRa E22P-868M30S radio).
Build environments: `hydra`, `hydraE22P` (no PSRAM), `hydraE22P_psram` (Freenove ESP32-WROVER, up to 1000 nodes)
and `hydraE22P_idf4` (ESP-IDF 4.4 test build, no Bluetooth).

Main additions over upstream: node statistics on demand (OnDemand), telemetry and position limiters,
opportunistic flooding, NodeMod / SignalReply, Wi-Fi and Bluetooth TX power settings, and extra
diagnostics (channel utilization, flash and heap counters, relay and duplicate counters).
Based on upstream `develop` from 2026-11-02.

## Change log

### Build 39 (2026-11-15)
- Configuration: all Hydra settings in `[hydra_userprefs]` (`variants/esp32/diy/hydra_e22p/platformio.ini`), shared by every Hydra environment.
- Initial values: node name, role (router roles allowed via `USERPREFS_ALLOW_ROUTER_ROLES`), LoRa TX power 2 dBm, fixed position, Wi-Fi, Wi-Fi TX power.
- `custom_ota_loader`: Meshtastic OTA loader `mt-esp32-ota.bin` bundled at 0x260000 in `factory.bin` and upload.
- `custom_admin_keys`: admin public keys in base64, as shown in the app.
- `ROUTER_MIN_TELEMETRY_INTERVAL_SECS` (4 h) and `NEIGHBORINFO_ALLOW_DEFAULT_CHANNEL` (NeighborInfo over LoRa on the default channel).
- Traceroute rate limit 10 s (upstream 30 s).
- Version string `2.8.3.<build>` with suffix `P` (E22P), `R` (PSRAM), `PR` (both).
- Bluetooth: NimBLE host task on core 1 (fixes the `npl_freertos_eventq_remove` panic on BLE teardown); settings saved before Bluetooth is disabled; no-reboot module configs (NodeMod) keep Bluetooth on; advertising restarts after a disconnect during config download.

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
- `LoRaConfig.wifi_power = 108`, `LoRaConfig.bt_power = 109`, `NodeStats.noise_floor = 40`, and NodeStats counters.
