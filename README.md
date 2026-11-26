# gPlug Web Installer

Install gPlug firmware ([gplug.ch](https://gplug.ch)) from a web browser – no tools, no command line.

**→ https://gplug-ch.github.io/web-installer/**

The gPlug firmware is closed source and is not hosted here. The gPlug team sends the firmware file
(Tasmota app image, `.bin` or `.bin.gz`) to the user; the user picks it on this page. The file never
leaves the user's computer.

## How the user installs

The steps fold like an accordion: only the step in focus is open, and the page opens the next one as
the user goes on.

1. **Pick a method.**
   - **Wi-Fi (recommended).** The gPlug stays on the meter. The user enters its address, the page
     opens the gPlug's own Tasmota update page (`http://<gplug>/up`), and the user picks the file
     there, the only time they pick it. Settings are kept. The gPlug checks the file itself.
   - **USB (fallback).** For a gPlug that is not reachable over Wi-Fi.
2. **USB: choose the file.** The page checks it locally: ESP image magic, chip = ESP32-C3, size fits
   app0. A `.bin.gz` is unpacked for the check. A full (factory) image is recognised and written at 0x0.
3. **USB: install** with Chrome/Edge + Web Serial via
   [ESP Web Tools](https://esphome.github.io/esp-web-tools/); the manifest is built in the browser.
4. **USB: first setup**, if the gPlug is not on the user's Wi-Fi yet.
5. **Reach by name** (last step on both paths, Wi-Fi: step 3, USB: step 5). Tasmota's mDNS
   (`SetOption55`) is off by default, so `http://<hostname>.local` often does not work. The page checks
   it and, if only the address answers, offers "Turn on name": it opens
   `http://<address>/cm?cmnd=SetOption55%201` in a new window (no restart needed) and checks again.
   Checking uses `fetch(url, { mode: "no-cors", targetAddressSpace: "local" })`, so it only works in
   Chrome/Edge (Local Network Access, after a permission prompt) and only learns whether the gPlug
   answered at all. Other browsers get the link and the button without the check.

### Why Wi-Fi goes through the gPlug's own page

The page does not upload to the gPlug itself (issue #8, tested on a gPlug with Tasmota 15.3.0):

- This page is https, the gPlug plain http. A normal `fetch()` to it is blocked as mixed content, and
  the gPlug sends no CORS headers.
- Chrome/Edge do reach it with Local Network Access (`fetch(url, { mode: "no-cors",
  targetAddressSpace: "local" })`, after a permission prompt), but the reply is opaque. With the
  safeboot layout the upload needs a restart into safeboot first (`/u4?u4=fct`, polled until it
  answers `true`), and the page could neither see that answer nor whether the upload worked.
- It would also fail when the user has set a web password (`no-cors` sends no credentials) or set
  `SetOption128 0`: Tasmota's `HttpCheckPriviledgedAccess` then accepts requests only with a
  `Referer` from the device itself. `SetOption128` is on by default (`DISABLE_REFERER_CHK` is not
  set), and the gPlug firmware does not change that.
- Firefox and Safari have no such opening at all.

Opening the device's `/up` page is a normal navigation, works in every browser (also with a web
password) and shows Tasmota's own result. So over Wi-Fi this page does not ask for the file; the
user picks it only there.

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

- `site/index.html` – the page (German, English, French, Italian; `?lang=de|en|fr|it` picks one, otherwise the browser language).
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
