import configparser
import subprocess
import os
run_number = os.getenv('GITHUB_RUN_NUMBER', '0')
build_location = os.getenv('BUILD_LOCATION', 'local')

# hydra: local build counter, appended to the version as "-v<n>"
HYDRA_BUILD_FILE = "hydra_build.txt"
# hydra: version format "<major>.<minor>.<build>.137<hydra build><board suffix>", e.g. "2.8.3.1372HyPR"; the suffix
# comes from platformio-custom.py (Hy/HyP/HyR/HyPR Hydra, nF, Xn, Xs). 137 marks the firmware-plus137 line; the build counter restarted at 1 with it. The same
# "137<build>" number is the FW+ version OnDemand reports (FW_PLUS_VERSION).
HYDRA_SERIES = 137
# Same shape as upstream "2.8.3.<sha>", so the apps parse it as 2.8.3.
# DeviceMetadata.firmware_version is char[18], so at most 17 chars + NUL
MAX_VERSION_LEN = 17

def readHydraBuild(projectDir):
    try:
        with open(os.path.join(projectDir, HYDRA_BUILD_FILE)) as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return None

def readProps(prefsLoc, buildSuffix=""):
    """Read the version of our project as a string

    buildSuffix is appended to the hydra build number ("2.8.3.1372HyPR"; board suffixes in platformio-custom.py)."""

    config = configparser.RawConfigParser()
    config.read(prefsLoc)
    version = dict(config.items("VERSION"))
    verObj = dict(
        short="{}.{}.{}".format(version["major"], version["minor"], version["build"]),
        long="unset",
        deb="unset",
    )
    # hydra: APP_VERSION_SHORT (screen and OnDemand NodeStats.firmware_version) also carries the build number.
    # "short" stays plain x.y.z because it feeds the .deb version string.
    verObj["display"] = verObj["short"]

    # Try to find current build SHA if if the workspace is clean.  This could fail if git is not installed
    try:
        # Pin abbreviation length to keep local builds and CI matching (avoid auto-shortening)
        sha = (
            subprocess.check_output(["git", "rev-parse", "--short=7", "HEAD"])
            .decode("utf-8")
            .strip()
        )
        isDirty = (
            subprocess.check_output(["git", "diff", "HEAD"]).decode("utf-8").strip()
        )
        suffix = sha
        # if isDirty:
        #     # short for 'dirty', we want to keep our verstrings source for protobuf reasons
        #     suffix = sha + "-d"
        verObj["long"] = "{}.{}".format(verObj["short"], suffix)
        hydraBuild = readHydraBuild(os.path.dirname(os.path.abspath(prefsLoc)))
        if hydraBuild is not None:
            # "2.8.3.1371": the commit sha stays in "deb" and in git, firmware_version only fits 17 chars
            fwPlusVersion = "{}{}".format(HYDRA_SERIES, hydraBuild)
            hydraVersion = "{}.{}{}".format(verObj["short"], fwPlusVersion, buildSuffix)[:MAX_VERSION_LEN]
            verObj["fw_plus_version"] = fwPlusVersion
            verObj["long"] = hydraVersion
            verObj["display"] = hydraVersion
        verObj["deb"] = "{}.{}~{}{}".format(verObj["short"], run_number, build_location, sha)
    except:
        # print("Unexpected error:", sys.exc_info()[0])
        # traceback.print_exc()
        verObj["long"] = verObj["short"]
        verObj["deb"] = "{}.{}~{}".format(verObj["short"], run_number, build_location)

    # print("firmware version " + verStr)
    return verObj


# print("path is" + ','.join(sys.path))