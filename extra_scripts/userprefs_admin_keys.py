#!/usr/bin/env python3
# trunk-ignore-all(ruff/F821)
# trunk-ignore-all(flake8/F821): For SConstruct imports
"""Turn base64 admin public keys from `custom_admin_keys` into USERPREFS_USE_ADMIN_KEY_<n>.

`custom_admin_keys` takes up to three keys, one per line, in the base64 form the apps show
(44 characters). Lines starting with ';' or '#' are ignored. Without the option nothing changes.
"""
import base64
import binascii

Import("env")

MAX_KEYS = 3


def _keys():
    try:
        raw = env.GetProjectOption("custom_admin_keys")
    except Exception:
        return []
    out = []
    for line in str(raw).splitlines():
        line = line.split(";", 1)[0].split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def _fail(msg):
    print(f"custom_admin_keys: ERROR {msg}")
    env.Exit(1)


keys = _keys()
if len(keys) > MAX_KEYS:
    _fail(f"{len(keys)} keys given, the firmware holds {MAX_KEYS}")

existing = {d[0] if isinstance(d, (tuple, list)) else str(d).split("=", 1)[0] for d in env.get("CPPDEFINES", [])}
for i, key in enumerate(keys):
    name = f"USERPREFS_USE_ADMIN_KEY_{i}"
    if name in existing:
        _fail(f"{name} is also set in build_flags; use only one of them")
    try:
        raw = base64.b64decode(key, validate=True)
    except (binascii.Error, ValueError) as e:
        _fail(f"key {i + 1} is not valid base64 ({e})")
    if len(raw) != 32:
        _fail(f"key {i + 1} decodes to {len(raw)} bytes, an admin public key is 32")
    env.Append(CPPDEFINES=[(name, "{" + ",".join(f"0x{b:02x}" for b in raw) + "}")])
    print(f"custom_admin_keys: admin key {i + 1} -> {name}")
