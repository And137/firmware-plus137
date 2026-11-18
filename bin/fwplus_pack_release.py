"""Pack FW+ release files from .pio/build into one folder.

Usage: python bin/fwplus_pack_release.py <build dir, e.g. .pio/build> <out dir> <fw+ version, e.g. 1373>
Used by .github/workflows/fwplus_release.yml and for local releases. The base version (2.8.3) comes from
version.properties.

- Checks the version string baked into every image (2.8.3.<fw+ version><board suffix>); stops on a mismatch.
- Hydra: writes -ota (full factory.bin with the MeshtasticOTA loader in ota_1 @ 0x260000) and -noota (factory.bin cut
  at the end of the app; checks that only 0xFF lies between the app and 0x260000).
- Other ESP32-S3 boards: factory.bin. nRF52: .uf2 and .zip.
- File names carry the board suffix (PROGNAME does not), then SHA256SUMS.txt.
- For updates from the Mesh+ 137 app, also the upstream-named files without the suffix: ESP32 app image
  firmware-<env>-<version>.bin, nRF52 firmware-<env>-<version>-ota.zip (BLE DFU) and .uf2 (USB).
Add a board: put its env and suffix in SUF and the env in the matching list below.
"""
import configparser, glob, hashlib, os, re, sys

build, out, B = sys.argv[1], sys.argv[2], sys.argv[3]
_props = configparser.ConfigParser()
_props.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "version.properties"))
BASE = "{major}.{minor}.{build}".format(**{k: v.strip() for k, v in _props["VERSION"].items()})
SUF = {"hydra": "Hy", "hydra_psram": "HyR", "hydraE22P": "HyP", "hydraE22P_psram": "HyPR",
       "seeed-xiao-s3": "Xs", "heltec-wsl-v3": "HeW", "heltec-v3": "He3", "heltec-v4": "He4",
       "nrf52_promicro_diy_tcxo": "nF", "seeed_xiao_nrf52840_kit": "Xn"}
HYDRA = ["hydra", "hydra_psram", "hydraE22P", "hydraE22P_psram"]
ESP32S3 = ["seeed-xiao-s3", "heltec-wsl-v3", "heltec-v3", "heltec-v4"]
NRF52 = ["nrf52_promicro_diy_tcxo", "seeed_xiao_nrf52840_kit"]
OTA_1 = 0x260000
os.makedirs(out, exist_ok=True)


def one(env, pattern):
    hits = [p for p in glob.glob(os.path.join(build, env, pattern)) if "littlefs" not in p]
    assert len(hits) == 1, (env, pattern, hits)
    return hits[0]


def check_version(env, path):
    # Skips the ESP-IDF app descriptor ("v2.8.3.1373", from git describe when HEAD carries the release tag): only the
    # firmware's own version string, which ends in the board suffix, is checked.
    data = open(path, "rb").read()
    want = f"{BASE}.{B}{SUF[env]}"
    found = set(m.group().decode() for m in re.finditer(rb"(?<![v\w.])" + re.escape(BASE.encode()) + rb"\.137\d+(?:[A-Za-z][A-Za-z0-9]{0,3})?(?=\x00)", data))
    assert found == {want}, (env, "expected", want, "found", found)
    return want


def copy(src, dst):
    open(os.path.join(out, dst), "wb").write(open(src, "rb").read())


for env in HYDRA:
    app = one(env, f"firmware-{env}-{BASE}.{B}.bin")
    v = check_version(env, app)
    fac = open(one(env, f"firmware-{env}-{BASE}.{B}.factory.bin"), "rb").read()
    end = 0x10000 + os.path.getsize(app)
    gap = fac[end:OTA_1]
    assert gap == b"\xff" * len(gap), env + ": non-0xFF data between app end and ota_1"
    assert fac[OTA_1:OTA_1 + 4] != b"\xff\xff\xff\xff", env + ": no OTA loader at 0x260000"
    open(os.path.join(out, f"firmware-{env}-{v}-ota.factory.bin"), "wb").write(fac)
    open(os.path.join(out, f"firmware-{env}-{v}-noota.factory.bin"), "wb").write(fac[:end])
    copy(app, f"firmware-{env}-{BASE}.{B}.bin")   # OTA: the app image, under the name the app downloads
    print(env, v, "ok")

for env in ESP32S3:
    app = one(env, f"firmware-{env}-{BASE}.{B}.bin")
    v = check_version(env, app)
    copy(one(env, f"firmware-{env}-{BASE}.{B}.factory.bin"), f"firmware-{env}-{v}.factory.bin")
    copy(app, f"firmware-{env}-{BASE}.{B}.bin")   # OTA app image
    print(env, v, "ok")

for env in NRF52:
    v = check_version(env, one(env, f"firmware-{env}-{BASE}.{B}.elf"))   # .hex stores bytes as text, so check the .elf
    for ext in ("uf2", "zip"):
        copy(one(env, f"firmware-{env}-{BASE}.{B}.{ext}"), f"firmware-{env}-{v}.{ext}")
    # OTA / USB update from the app: upstream names, no board suffix (the app builds them from the env and version)
    copy(one(env, f"firmware-{env}-{BASE}.{B}.zip"), f"firmware-{env}-{BASE}.{B}-ota.zip")
    copy(one(env, f"firmware-{env}-{BASE}.{B}.uf2"), f"firmware-{env}-{BASE}.{B}.uf2")
    print(env, v, "ok")

with open(os.path.join(out, "SHA256SUMS.txt"), "w", newline="\n") as f:
    for p in sorted(glob.glob(os.path.join(out, "firmware-*"))):
        f.write(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {os.path.basename(p)}\n")
print("done:", out)
