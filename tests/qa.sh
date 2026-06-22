#!/usr/bin/env bash
# Live QA suite for a 0Gora deployment: per-model functional + grounding + read concurrency.
# Usage:  BASE=https://0gora.temporalabs.com bash tests/qa.sh
set -u
BASE="${BASE:-https://0gora.temporalabs.com}"
MODELS=("0GM-1.0-35B-A3B" "zai-org/GLM-5.1-FP8" "deepseek/deepseek-chat-v3-0324" "qwen3.7-max")
pass=0; fail=0

chk() { # model question
  local M="$1"; local Q="$2"
  curl -s --max-time 170 -o /tmp/qa.json -w "%{http_code} %{time_total}" \
    -X POST "$BASE/api/chat" -H 'content-type: application/json' \
    -d "{\"message\":\"$Q\",\"model\":\"$M\"}" > /tmp/qa.meta
  read CODE T < /tmp/qa.meta
  local r
  r=$(python3 -c "
import json
d=json.load(open('/tmp/qa.json')); v=d.get('x_0g_verification') or {}; a=d.get('answer') or ''
ok=($CODE==200) and v.get('verified') is True and len(a)>40 and not a.startswith(chr(0x26a0))
print('PASS' if ok else 'FAIL', 't=${T}s', 'verified='+str(v.get('verified')), 'cites='+str(len(d.get('citations') or [])))
" 2>/dev/null) || r="FAIL parse ($CODE)"
  echo "  [$M] $r"
  [[ "$r" == PASS* ]] && pass=$((pass+1)) || fail=$((fail+1))
}

echo "== functional: each model answers a grounded 0G question =="
chk "${MODELS[0]}" "What is 0G Storage?"
chk "${MODELS[1]}" "What is 0G data availability?"
chk "${MODELS[2]}" "What is the 0G compute network?"
chk "${MODELS[3]}" "What is the 0G Private Computer?"

echo "== grounding: off-topic must be refused (not fabricated) =="
curl -s --max-time 120 -o /tmp/qa.json -X POST "$BASE/api/chat" -H 'content-type: application/json' \
  -d '{"message":"Who won the 2014 FIFA World Cup final?"}'
if python3 -c "import json;a=json.load(open('/tmp/qa.json')).get('answer','').lower();exit(0 if (\"don't have\" in a or 'not contain' in a or 'no information' in a) else 1)" 2>/dev/null; then
  echo "  [grounding] PASS (refused)"; pass=$((pass+1)); else echo "  [grounding] FAIL (did not refuse)"; fail=$((fail+1)); fi

echo "== read concurrency: 8 parallel requests, all must verify =="
pids=""; for i in $(seq 0 7); do
  ( curl -s --max-time 200 -o /tmp/qc_$i.json -X POST "$BASE/api/chat" -H 'content-type: application/json' \
      -d '{"message":"What is 0G?"}' ) & pids="$pids $!"
done
wait $pids
cok=0; for i in $(seq 0 7); do
  python3 -c "import json;v=json.load(open('/tmp/qc_$i.json')).get('x_0g_verification') or {};exit(0 if v.get('verified') is True else 1)" 2>/dev/null && cok=$((cok+1))
done
if [ "$cok" -eq 8 ]; then echo "  [concurrency] PASS (8/8 verified)"; pass=$((pass+1)); else echo "  [concurrency] FAIL ($cok/8)"; fail=$((fail+1)); fi

echo "== $pass passed, $fail failed =="
[ "$fail" -eq 0 ]
