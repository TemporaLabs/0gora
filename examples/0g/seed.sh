#!/usr/bin/env bash
# Seed this instance's knowledge base from the `corpus.seeds` in 0gora.config.json.
# Idempotent-ish: re-ingesting a source just refreshes its chunks.
#
#   CONTRIBUTE_KEY=<key> API=http://localhost:8000 ./seed.sh
#
# CONTRIBUTE_KEY must match the backend's (open the /contribute endpoint). API
# defaults to the local backend. Requires `jq`.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$DIR/0gora.config.json"
API="${API:-http://localhost:8000}"

if [[ -z "${CONTRIBUTE_KEY:-}" ]]; then
  echo "error: set CONTRIBUTE_KEY (must match the backend's CONTRIBUTE_KEY)" >&2
  exit 1
fi
command -v jq >/dev/null || { echo "error: jq is required" >&2; exit 1; }

count="$(jq '.corpus.seeds | length' "$CONFIG")"
echo "Seeding $count source(s) into $API …"

jq -c '.corpus.seeds[]' "$CONFIG" | while read -r seed; do
  url="$(jq -r '.url' <<<"$seed")"
  mode="$(jq -r '.mode // "single"' <<<"$seed")"
  max_pages="$(jq -r '.max_pages // 40' <<<"$seed")"
  echo "  → $url ($mode, max $max_pages)"
  curl -sS -X POST "$API/contribute" \
    -H "content-type: application/json" \
    -H "x-contribute-key: $CONTRIBUTE_KEY" \
    -d "{\"url\":\"$url\",\"mode\":\"$mode\",\"max_pages\":$max_pages}" \
    && echo
done

echo "Done."
