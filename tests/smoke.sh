#!/usr/bin/env bash
# Live smoke test for a 0Gora deployment.
# Usage:  BASE=https://0gora.temporalabs.com bash tests/smoke.sh
set -u
BASE="${BASE:-https://0gora.temporalabs.com}"
pass=0; fail=0
ok()   { echo "  PASS: $1"; pass=$((pass+1)); }
no()   { echo "  FAIL: $1"; fail=$((fail+1)); }

echo "== 0Gora smoke @ $BASE =="

# 1. web root reachable, branded, no Contribute button (contribution locked)
body=$(curl -s --max-time 20 "$BASE/")
echo "$body" | grep -qi "<title>0Gora</title>" && ok "web root branded" || no "web root title"
echo "$body" | grep -q "+ Contribute" && no "Contribute button is exposed (should be hidden)" || ok "Contribute button hidden"

# 2. backend health
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 "$BASE/api/health")
[ "$code" = "200" ] && ok "health 200" || no "health ($code)"

# 3. models list non-empty
n=$(curl -s --max-time 20 "$BASE/api/models" | python3 -c "import sys,json;print(len(json.load(sys.stdin).get('models',[])))" 2>/dev/null || echo 0)
[ "$n" -ge 1 ] 2>/dev/null && ok "models listed ($n)" || no "models listed ($n)"

# 4. default chat → grounded, verified on 0G, with citations
resp=$(curl -s --max-time 150 -X POST "$BASE/api/chat" -H 'content-type: application/json' -d '{"message":"What is 0G?"}')
echo "$resp" | python3 -c "
import sys,json
d=json.load(sys.stdin); v=d.get('x_0g_verification') or {}
assert d.get('answer'), 'no answer'
assert v.get('verified') is True, 'not verified on 0G'
assert len(d.get('citations') or [])>0, 'no citations'
" 2>/dev/null && ok "chat verified + grounded" || no "chat verified + grounded"

# 5. contribution locked (read-only public)
c1=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 -X POST "$BASE/api/contribute" -H 'content-type: application/json' -d '{"url":"https://example.com"}')
[ "$c1" = "403" ] && ok "contribute locked (403)" || no "contribute not locked ($c1)"

# 6. graceful errors: malformed body is a clean 422, never a 500
c2=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 -X POST "$BASE/api/chat" -H 'content-type: application/json' -d '{}')
[ "$c2" = "422" ] && ok "malformed chat -> 422" || no "malformed chat ($c2)"

echo "== $pass passed, $fail failed =="
[ "$fail" -eq 0 ]
