#!/usr/bin/env python3
# trunk-ignore-all(ruff/F821)
# trunk-ignore-all(flake8/F821): For SConstruct imports
"""Bundle the Meshtastic unified OTA loader (mt-<mcu>-ota.bin) into ESP32 builds.

Enabled per env with `custom_ota_loader = yes` (optional `custom_ota_loader_url`).
When enabled, the loader is placed in the ota_1 partition by `pio run -t upload`,
merged into firmware.factory.bin, and listed in the mtjson manifest.
When disabled, the build output is the stock one and any stale copy is removed.
"""
import os
import shutil
import time
import urllib.request

from SCons.Script import COMMAND_LINE_TARGETS

Import("env")

OTA_URL_TEMPLATE = (
    "https://github.com/meshtastic/esp32-unified-ota/releases/latest/download/mt-{mcu}-ota.bin"
)
CACHE_MAX_AGE_S = 24 * 3600  # re-check the latest release at most once a day


def _option(name, default=""):
    try:
        return env.GetProjectOption(name)
    except Exception:
        return default


def _enabled():
    return str(_option("custom_ota_loader", "no")).strip().lower() in ("1", "y", "yes", "true", "on")


def _ota1_partition():
    """(offset, size) of the ota_1 partition from the env's partition CSV, or None."""
    csv_path = env.subst("$PARTITIONS_TABLE_CSV")
    if not csv_path or not os.path.isfile(csv_path):
        return None
    with open(csv_path, encoding="utf-8") as f:
        for line in f:
            cols = [c.strip() for c in line.split("#", 1)[0].split(",")]
            if len(cols) >= 5 and cols[1] == "app" and cols[2] == "ota_1" and cols[3]:
                return int(cols[3], 0), int(cols[4], 0)
    return None


def _fetch(url, cache_path):
    """Refresh cache_path from url when stale; return True if a usable copy exists."""
    fresh = os.path.isfile(cache_path) and time.time() - os.path.getmtime(cache_path) < CACHE_MAX_AGE_S
    if fresh:
        return True
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    tmp_path = cache_path + ".part"
    try:
        print(f"OTA loader: downloading {url}")
        with urllib.request.urlopen(url, timeout=30) as resp, open(tmp_path, "wb") as out:
            shutil.copyfileobj(resp, out)
        os.replace(tmp_path, cache_path)
        return True
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.isfile(cache_path):
            print(f"OTA loader: WARNING download failed ({e}), using cached {cache_path}")
            return True
        print(f"OTA loader: WARNING download failed ({e}) and no cached copy")
        return False


def setup():
    if env.PioPlatform().name != "espressif32":
        return
    mcu = env.BoardConfig().get("build.mcu").lower()
    name = f"mt-{mcu}-ota.bin"
    dest = os.path.join(env.subst("$BUILD_DIR"), name)

    if not _enabled():
        # Flag off: drop a copy left by an earlier enabled build so the manifest stays stock.
        if os.path.isfile(dest):
            os.remove(dest)
        return

    part = _ota1_partition()
    if part is None:
        print(f"OTA loader: WARNING no ota_1 partition in {env.subst('$PARTITIONS_TABLE_CSV')}; skipped")
        return
    offset, limit = part

    url = _option("custom_ota_loader_url", "") or OTA_URL_TEMPLATE.format(mcu=mcu)
    cache_path = os.path.join(env.subst("$PROJECT_CORE_DIR"), ".cache", "meshtastic-ota", name)
    if not _fetch(url, cache_path):
        print(f"OTA loader: {name} not bundled")
        return

    size = os.path.getsize(cache_path)
    if size > limit:
        print(f"OTA loader: WARNING {name} is {size} B, ota_1 is {limit} B; not bundled")
        return

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(cache_path, dest)

    image = (hex(offset), dest)
    # factory.bin merge reads FLASH_EXTRA_IMAGES when it runs.
    env.Append(FLASH_EXTRA_IMAGES=[image])
    # The platform builds the esptool upload command before post scripts run, so add it there too.
    if env.subst("$UPLOAD_PROTOCOL") == "esptool" and "uploadfs" not in COMMAND_LINE_TARGETS:
        env.Append(UPLOADERFLAGS=list(image))
    print(f"OTA loader: {name} ({size} B) bundled at {image[0]}")


setup()
