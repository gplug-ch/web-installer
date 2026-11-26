# Intent

## Goal

Provide a web installer, like the one in [jluthiger/esphome-gplug](https://github.com/jluthiger/esphome-gplug), to install the gPlug firmware (see [gplug.ch](https://gplug.ch)) using a web browser.

## Key Requirements

- **Browser-based installation**: flash the gPlug firmware straight from a web browser, with no local toolchain or command-line tools.
- **Usable by non-technical users**: simple, guided steps that anyone can follow without technical knowledge.

## References

- Example web installer: https://github.com/jluthiger/esphome-gplug
- gPlug: https://gplug.ch

## Constraints

- The gPlug firmware is closed source. It is not downloadable or hosted anywhere public; the gPlug team sends the firmware file (app image, `.bin`) to the user.
- The user picks that file in the web installer, which installs it on the gPlug, primarily over Wi-Fi (gPlug stays on the meter), with USB as a fallback.
