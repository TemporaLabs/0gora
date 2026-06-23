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

# Loop in the main shell (process substitution, not a pipe) so a failure can set
# `fail` and we exit non-zero — a piped `while` runs in a subshell and loses that.
fail=0
while read -r seed; do
  url="$(jq -r '.url' <<<"$seed")"
  mode="$(jq -r '.mode // "single"' <<<"$seed")"
  max_pages="$(jq -r '.max_pages // 40' <<<"$seed")"
  echo "  → $url ($mode, max $max_pages)"
  # Build the JSON body with jq so a url containing quotes/backslashes can't
  # produce malformed JSON, and max_pages is always a real number.
  payload="$(jq -nc --arg url "$url" --arg mode "$mode" --argjson max_pages "$max_pages" \
    '{url: $url, mode: $mode, max_pages: $max_pages}')"
  # --fail-with-body: curl exits non-zero on HTTP 4xx/5xx (e.g. a 403 from a
  # mismatched CONTRIBUTE_KEY) while still printing the error body. Without it a
  # fully-rejected seed would print "Done." and exit 0 — a silent no-op.
  if curl -sS --fail-with-body -X POST "$API/contribute" \
       -H "content-type: application/json" \
       -H "x-contribute-key: $CONTRIBUTE_KEY" \
       -d "$payload"; then
    echo
  else
    echo >&2 "  ✗ failed to seed $url (HTTP error — check CONTRIBUTE_KEY matches the backend and that $API is reachable)"
    fail=1
  fi
done < <(jq -c '.corpus.seeds[]' "$CONFIG")

if [[ "$fail" -ne 0 ]]; then
  echo >&2 "Done with errors — one or more sources failed to seed."
  exit 1
fi
echo "Done."
