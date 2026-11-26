# gPlug Web Installer

Install gPlug firmware ([gplug.ch](https://gplug.ch)) from a web browser – no tools, no command line.

**→ https://gplug-ch.github.io/web-installer/**

The gPlug firmware is closed source and is not hosted here. The gPlug team sends the firmware file
(Tasmota app image, `.bin` or `.bin.gz`) to the user; the user picks it on this page. The file never
leaves the user's computer.

## How the user installs

1. **Choose the file.** The page checks it locally: ESP image magic, chip = ESP32-C3, size fits
   app0. A `.bin.gz` is unpacked for the check. A full (factory) image is recognised and limited to USB.
2. **Pick a method.**
   - **Wi-Fi (recommended).** The gPlug stays on the meter. The user enters its address, the page
     opens the gPlug's own Tasmota update page (`http://<gplug>/up`), and the user uploads the same
     file there. Settings are kept.
   - **USB (fallback).** For a gPlug that is not reachable over Wi-Fi. Chrome/Edge + Web Serial via
     [ESP Web Tools](https://esphome.github.io/esp-web-tools/); the manifest is built in the browser.

### Why Wi-Fi goes through the gPlug's own page

The page cannot upload to the gPlug itself. Tasmota accepts uploads only when the `Referer` is the
device itself (`HttpCheckPriviledgedAccess`, `SetOption128 0` by default). On top of that, an https page
may not send requests to a plain-http device on the local network. Opening the device's `/up` page is
a normal navigation and works in every browser, including when a web password is set.

### What USB writes

| Offset     | Part                         | Source                                         |
|------------|------------------------------|------------------------------------------------|
| `0x0`      | bootloader                   | stock Tasmota 15.3.0 `tasmota32c3.factory.bin` |
| `0x8000`   | partition table              | 〃                                              |
| `0xE000`   | otadata + safeboot           | 〃                                              |
| `0xE0000`  | **the user's app image**     | the chosen file                                |

NVS (`0x9000–0xE000`, Tasmota settings) and the file system are not written, so Wi-Fi and meter
settings survive unless the user ticks *Erase device*. A full image is written at `0x0` as is.

The base parts are cut from the pinned (SHA-256) stock Tasmota image by `scripts/fetch_base.py`,
which also checks that the partition layout matches the gPlug's (app0 at `0xE0000`, `0x2D0000` bytes).

## Files

- `site/index.html` – the page (German/English).
- `VERSION.txt` – installer version shown on the page.
- `scripts/build.sh` – builds `_site/`: page, `base/` and `version.json` (CI and local).
- `scripts/fetch_base.py` – builds `base/` (bootloader, partitions, safeboot).
- `scripts/serve.sh` – local build + server on http://localhost:8000 (Web Serial works on localhost).
- `.github/workflows/pages.yml` – deploys to GitHub Pages on push to `main`.

Setup once: *Settings → Pages → Source: GitHub Actions*.

## Versions

The page footer shows the installer version from `VERSION.txt`, the commit it was built from (linked,
with its date) and the Tasmota base used for USB, e.g.
`Web-Installer v0.1.0 (5b701d7, 2026-11-26) · USB-Basis: Tasmota 15.3.0`.
To release: bump `VERSION.txt` and push to `main`.
