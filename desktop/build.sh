#!/bin/sh
# Builds AyahByAyah.exe (Windows 64-bit) from the current repo files. Run from the repo root: sh desktop/build.sh
set -e
cd "$(dirname "$0")/.."
python3 tools/build_site.py >/dev/null
rm -rf desktop/site && mkdir -p desktop/site
cp index.html quran.json indopak.json indopak-font.woff2 conc.json forms.json tr-bn.json tr-ur.json learn-bn.json desktop/site/
cp -r grammar syntax learn exercise data desktop/site/
cd desktop
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags "-H windowsgui -s -w" -o AyahByAyah.exe .
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -o /tmp/aba-linux .
ls -la AyahByAyah.exe
