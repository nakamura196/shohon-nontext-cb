#!/usr/bin/env bash
# After the English build (_config.en.yml, into <site>/en), drop its copy of the
# images and IIIF files (objects/) if present and point its pages at the Japanese build's.
# Usage: bash _tools/share_ja_assets.sh <site dir, e.g. _site>
set -euo pipefail
site=${1:?site dir}
en=$site/en
if [[ ! -d $en/objects || ! -d $site/objects ]]; then
  echo "en: no local objects/ directory (external IIIF images); nothing to deduplicate"
  exit 0
fi
rm -rf "$en/objects"
grep -rl --null --include='*.html' --include='*.json' --include='*.js' --include='*.xml' --include='*.csv' '/shohon-nontext-cb/en/objects/' "$en" | while IFS= read -r -d '' f; do
  sed -i.bak -e 's#/shohon-nontext-cb/en/objects/#/shohon-nontext-cb/objects/#g' "$f"
done || true
find "$en" -name '*.bak' -delete
left=$( (grep -rl '/shohon-nontext-cb/en/objects/' "$en" || true) | wc -l | tr -d ' ')
echo "en: images and IIIF shared with the Japanese build ($left files still pointing at en)"
