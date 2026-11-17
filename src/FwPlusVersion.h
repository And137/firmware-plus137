#pragma once

// FW+ version definition shared across modules.
//
// hydra: the firmware-plus137 line numbers itself "137<build>", where <build> is hydra_build.txt: build 1 is 1371.
// bin/readprops.py builds the number (it is also the last part of the firmware version, "2.8.3.1371") and
// bin/platformio-custom.py passes it in as HYDRA_FW_PLUS_VERSION. OnDemand reports it in
// FwPlusVersion.version_number and NodeStats.fw_plus_version.
#ifdef HYDRA_FW_PLUS_VERSION
#define FW_PLUS_VERSION HYDRA_FW_PLUS_VERSION
#else
#define FW_PLUS_VERSION 1370 // build outside PlatformIO: series 137, build unknown
#endif
