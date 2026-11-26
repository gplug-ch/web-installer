#!/usr/bin/env bash
# Builds the site into _site/ and serves it on http://localhost:8000.
# Web Serial works on localhost without https.
set -euo pipefail
cd "$(dirname "$0")/.."
scripts/build.sh
echo "Open http://localhost:8000 in Chrome or Edge"
python3 -m http.server 8000 --directory _site
