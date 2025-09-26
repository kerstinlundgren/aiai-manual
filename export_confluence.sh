#!/bin/bash
set -euo pipefail
DEST="./docs"
TMP="./tmp_export"
rm -rf "$DEST" "$TMP"
mkdir -p "$TMP" "$DEST"
curl -s -u "$CONFLUENCE_USER:$CONFLUENCE_TOKEN" \
  "$CONFLUENCE_BASE/rest/api/space/$CONFLUENCE_SPACE/export" \
  -o "$TMP/manual.zip"
unzip -q "$TMP/manual.zip" -d "$DEST"
echo "User-agent: *" > "$DEST/robots.txt"
echo "Allow: /" >> "$DEST/robots.txt"
