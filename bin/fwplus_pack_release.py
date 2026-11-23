"""Pack FW+ release files from .pio/build into one folder.

Usage: python bin/fwplus_pack_release.py <build dir, e.g. .pio/build> <out dir> <fw+ version, e.g. 1373>
Used by .github/workflows/fwplus_release.yml and for local releases. The base version (2.8.3) comes from
version.properties.

- Checks the version string baked into every image (2.8.3.<fw+ version><board suffix>); stops on a mismatch.
- ESP32 (Hydra and, from 1374, the ESP32-S3 boards): writes -ota (full factory.bin with the MeshtasticOTA loader in
  ota_1) and -noota (factory.bin cut at the end of the app; checks that only 0xFF lies between the app and ota_1).
  The ota_1 offset comes from the env's partition table (Hydra 0x260000, 8 MB boards 0x340000, 16 MB 0x650000).
- nRF52: .uf2 and .zip. RP2040: .uf2.
- Native Linux (meshtasticd, from 1375): build/native-<arch>/meshtasticd is packed with the sample config, config.d,
  the systemd unit and the udev rules into meshtasticd-<version>-linux-<arch>.tar.gz.
- File names carry the board suffix (PROGNAME does not), then SHA256SUMS.txt.
- For updates from the Mesh+ 137 app, also the upstream-named files without the suffix: ESP32 app image
  firmware-<env>-<version>.bin, nRF52 firmware-<env>-<version>-ota.zip (BLE DFU) and .uf2 (USB), RP2040 .uf2.
Add a board: put its env and suffix in SUF and the env in the matching list below.
"""
import configparser, glob, hashlib, io, os, re, sys, tarfile

build, out, B = sys.argv[1], sys.argv[2], sys.argv[3]
_props = configparser.ConfigParser()
_props.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "version.properties"))
BASE = "{major}.{minor}.{build}".format(**{k: v.strip() for k, v in _props["VERSION"].items()})
SUF = {"hydra": "Hy", "hydra_psram": "HyR", "hydraE22P": "HyP", "hydraE22P_psram": "HyPR",
       "seeed-xiao-s3": "Xs", "heltec-wsl-v3": "HeW", "heltec-v3": "He3", "heltec-v4": "He4",
       "nrf52_promicro_diy_tcxo": "nF", "seeed_xiao_nrf52840_kit": "Xn", "rak4631": "Rak",
       "tbeam": "Tb", "tlora-v2-1-1_6": "TL16", "tbeam-s3-core": "TbS3", "heltec-wireless-paper": "HeWP",
       "station-g2": "SG2", "t-deck": "TD", "t-echo": "TE", "heltec-mesh-node-t114": "T114",
       "heltec-mesh-node-t096": "T96", "tracker-t1000-e": "T1k", "heltec-mesh-pocket-5000-inkhud": "MP5",
       "heltec-mesh-pocket-10000-inkhud": "MP10", "rp2040-lora": "R24", "picow": "PiW", "native": "Lx",
       "rak_killer_v2": "RK2"}
HYDRA = ["hydra", "hydra_psram", "hydraE22P", "hydraE22P_psram"]
ESP32 = ["tbeam", "tlora-v2-1-1_6"]   # classic ESP32 boards other than Hydra, with the OTA loader from 1375
ESP32S3 = ["seeed-xiao-s3", "heltec-wsl-v3", "heltec-v3", "heltec-v4",
           "tbeam-s3-core", "heltec-wireless-paper", "station-g2", "t-deck"]
NRF52 = ["nrf52_promicro_diy_tcxo", "seeed_xiao_nrf52840_kit", "rak4631", "t-echo", "heltec-mesh-node-t114",
         "heltec-mesh-node-t096", "tracker-t1000-e", "heltec-mesh-pocket-5000-inkhud",
         "heltec-mesh-pocket-10000-inkhud", "rak_killer_v2"]
RP2040 = ["rp2040-lora", "picow"]
NATIVE_ARCHES = ["amd64", "arm64"]   # artifacts build/native-<arch>/meshtasticd
# Partition table of each ESP32 env (board_build.partitions); ota_1 holds the MeshtasticOTA loader.
PARTITIONS = {**{e: "partition-table.csv" for e in HYDRA + ESP32},
              "seeed-xiao-s3": "default_8MB.csv", "heltec-wsl-v3": "default_8MB.csv", "heltec-v3": "default_8MB.csv",
              "heltec-v4": "default_16MB.csv", "tbeam-s3-core": "default_8MB.csv",
              "heltec-wireless-paper": "default_8MB.csv", "station-g2": "default_16MB.csv",
              "t-deck": "default_16MB.csv"}
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
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


def ota1_offset(env):
    for line in open(os.path.join(ROOT, PARTITIONS[env])):
        cols = [c.strip() for c in line.split("#")[0].split(",")]
        if len(cols) >= 4 and cols[1] == "app" and cols[2] == "ota_1":
            return int(cols[3], 0)
    raise AssertionError(env + ": no ota_1 partition in " + PARTITIONS[env])


def copy(src, dst):
    open(os.path.join(out, dst), "wb").write(open(src, "rb").read())


for env in HYDRA + ESP32 + ESP32S3:
    app = one(env, f"firmware-{env}-{BASE}.{B}.bin")
    v = check_version(env, app)
    fac = open(one(env, f"firmware-{env}-{BASE}.{B}.factory.bin"), "rb").read()
    ota1 = ota1_offset(env)
    end = 0x10000 + os.path.getsize(app)
    gap = fac[end:ota1]
    assert gap == b"\xff" * len(gap), env + ": non-0xFF data between app end and ota_1"
    assert fac[ota1:ota1 + 4] != b"\xff\xff\xff\xff", f"{env}: no OTA loader at {ota1:#x}"
    open(os.path.join(out, f"firmware-{env}-{v}-ota.factory.bin"), "wb").write(fac)
    open(os.path.join(out, f"firmware-{env}-{v}-noota.factory.bin"), "wb").write(fac[:end])
    copy(app, f"firmware-{env}-{BASE}.{B}.bin")   # OTA: the app image, under the name the app downloads
    print(env, v, "ok")

for env in NRF52:
    v = check_version(env, one(env, f"firmware-{env}-{BASE}.{B}.elf"))   # .hex stores bytes as text, so check the .elf
    for ext in ("uf2", "zip"):
        copy(one(env, f"firmware-{env}-{BASE}.{B}.{ext}"), f"firmware-{env}-{v}.{ext}")
    # OTA / USB update from the app: upstream names, no board suffix (the app builds them from the env and version)
    copy(one(env, f"firmware-{env}-{BASE}.{B}.zip"), f"firmware-{env}-{BASE}.{B}-ota.zip")
    copy(one(env, f"firmware-{env}-{BASE}.{B}.uf2"), f"firmware-{env}-{BASE}.{B}.uf2")
    print(env, v, "ok")

for env in RP2040:
    v = check_version(env, one(env, f"firmware-{env}-{BASE}.{B}.elf"))
    copy(one(env, f"firmware-{env}-{BASE}.{B}.uf2"), f"firmware-{env}-{v}.uf2")
    copy(one(env, f"firmware-{env}-{BASE}.{B}.uf2"), f"firmware-{env}-{BASE}.{B}.uf2")   # update from the app
    print(env, v, "ok")


def add_file(tar, path, arcname, mode=0o644):
    info = tarfile.TarInfo(arcname)
    data = open(path, "rb").read()
    info.size, info.mode, info.mtime = len(data), mode, 0
    tar.addfile(info, io.BytesIO(data))


for arch in NATIVE_ARCHES:
    binary = os.path.join(build, f"native-{arch}", "meshtasticd")
    v = check_version("native", binary)
    top = f"meshtasticd-{v}-linux-{arch}"
    with tarfile.open(os.path.join(out, f"{top}.tar.gz"), "w:gz") as tar:
        add_file(tar, binary, f"{top}/meshtasticd", 0o755)
        add_file(tar, os.path.join(ROOT, "bin", "config-dist.yaml"), f"{top}/config.yaml")
        add_file(tar, os.path.join(ROOT, "bin", "meshtasticd.service"), f"{top}/meshtasticd.service")
        add_file(tar, os.path.join(ROOT, "bin", "99-meshtasticd-udev.rules"), f"{top}/99-meshtasticd-udev.rules")
        add_file(tar, os.path.join(ROOT, "bin", "fwplus-native-README.txt"), f"{top}/README.txt")
        conf = os.path.join(ROOT, "bin", "config.d")
        for path in sorted(glob.glob(os.path.join(conf, "**", "*"), recursive=True)):
            if os.path.isfile(path):
                add_file(tar, path, f"{top}/available.d/" + os.path.relpath(path, conf).replace(os.sep, "/"))
    print("native", arch, v, "ok")

with open(os.path.join(out, "SHA256SUMS.txt"), "w", newline="\n") as f:
    for p in sorted(glob.glob(os.path.join(out, "firmware-*")) + glob.glob(os.path.join(out, "meshtasticd-*"))):
        f.write(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {os.path.basename(p)}\n")
print("done:", out)
