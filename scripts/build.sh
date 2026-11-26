#!/usr/bin/env bash
# Builds the site into _site/: the page, the Tasmota base parts for USB, and version.json
# (installer version from VERSION.txt plus the git commit, shown in the page footer).
# Used by CI and scripts/serve.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf _site && cp -R site _site
touch _site/.nojekyll
python3 scripts/fetch_base.py _site

# "-dirty" on the commit marks a local build with uncommitted changes to tracked files.
python3 -I - _site/version.json \
  "$(tr -d '[:space:]' < VERSION.txt)" \
  "$(git rev-parse HEAD)" \
  "$(git describe --always --dirty --abbrev=7 --exclude='*')" \
  "$(git log -1 --format=%cs)" \
  "$(python3 -B -c 'import sys; sys.path.insert(0, "scripts"); import fetch_base; print(fetch_base.TASMOTA_VERSION)')" <<'PY'
import json, sys
out, version, commit, short, date, tasmota = sys.argv[1:]
if not version:
    sys.exit("VERSION.txt is empty")
json.dump({"version": version, "commit": commit, "short": short, "date": date, "tasmota_base": tasmota},
          open(out, "w"), indent=2)
PY
cat _site/version.json; echo
