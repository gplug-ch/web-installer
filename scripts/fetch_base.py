#!/usr/bin/env python3
"""Prepare the USB fallback's base image: bootloader, partition table, otadata and safeboot.

The gPlug firmware itself is closed source and never hosted here: the user picks the file the
gPlug team sent them. For a USB install the page writes that app image at 0xE0000 (app0) and, so a
device with a damaged or foreign flash layout boots again, the parts below it from stock Tasmota.
The NVS region (0x9000-0xE000, Tasmota settings) is skipped so Wi-Fi and meter settings survive.

ota.tasmota.com sends no CORS headers, so the parts are mirrored next to the page.

Usage: python3 scripts/fetch_base.py [SITE_DIR]   (default: site)
"""

import hashlib
import pathlib
import struct
import sys
import urllib.request

TASMOTA_VERSION = "15.3.0"
URL = f"https://ota.tasmota.com/tasmota32/release-{TASMOTA_VERSION}/tasmota32c3.factory.bin"
SHA256 = "cf326316b340c372306fa4a0d5b08488db1ee7ccbc9a8e0f075f30cf0aeb184d"

# Layout of the gPlug (and stock Tasmota ESP32-C3 4 MB) flash. index.html relies on it.
EXPECTED_PARTITIONS = {
    "nvs": (0x9000, 0x5000),
    "otadata": (0xE000, 0x2000),
    "safeboot": (0x10000, 0xD0000),
    "app0": (0xE0000, 0x2D0000),
}

# (file, start, end) slices of the factory image; NVS (0x9000-0xE000) deliberately left out.
PARTS = [
    ("bootloader.bin", 0x0, 0x8000),
    ("partitions.bin", 0x8000, 0x9000),
    ("safeboot.bin", 0xE000, 0xE0000),  # otadata + safeboot
]


def partitions(image: bytes) -> dict:
    found = {}
    for off in range(0x8000, 0x9000, 32):
        entry = image[off:off + 32]
        if entry[:2] != b"\xaa\x50":
            break
        start, size = struct.unpack("<II", entry[4:12])
        found[entry[12:28].split(b"\0")[0].decode()] = (start, size)
    return found


def main() -> None:
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site") / "base"
    out.mkdir(parents=True, exist_ok=True)

    req = urllib.request.Request(URL, headers={"User-Agent": "gplug-web-installer"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        image = resp.read()

    digest = hashlib.sha256(image).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"{URL}: SHA-256 {digest} does not match the pinned {SHA256}")
    found = partitions(image)
    for name, layout in EXPECTED_PARTITIONS.items():
        if found.get(name) != layout:
            raise SystemExit(f"partition {name}: expected {layout}, image has {found.get(name)}")

    for name, start, end in PARTS:
        (out / name).write_bytes(image[start:end])
        print(f"{name:15} {start:#08x}-{end:#08x}")


if __name__ == "__main__":
    main()
