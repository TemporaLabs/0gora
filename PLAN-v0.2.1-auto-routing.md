# 0Gora v0.2.1 — Hybrid Auto Model Routing

**Status:** IMPLEMENTED — phases 1–2 (heuristic + `0gm` classifier, config-driven, cascade guardrail) on branch
`feat/auto-model-routing`, PR → `v0.2.0` (renames to `v0.2.1` once that branch exists). Phases 3–4 (eval harness,
embedding router) remain follow-ups.
**Owner decision captured:** 2026-06-23 with Kevin. Engine = **Option B (LLM classifier on `0gm`)** + heuristic short-circuit.

---

## 1. Goal

Default the model picker to **Auto**, and have the backend choose the best 0G model per query —
the OpusPlus analogy (cheap model for easy turns, strong model for hard ones), plus a domain axis.
Route across the funded roster: `0gm`, `zai-org/GLM-5.1-FP8`, `deepseek-v4-pro`, `qwen3.7-max`.

The answer is still **generated + TEE-verified on 0G** — only the *choice of model* is automated.
The routing decision itself is not user-facing output, so it need not be verified.

## 2. Current state (as built in v0.2.0)

```
webui picker ──model──▶ POST /chat ──▶ rag.answer(query, model)
                                            │  (retrieval already EMBEDS the query)
                                            ▼
                                     zerog.chat(messages, model)
                                            ▼
                              inference /v1/chat/completions
                                            ▼
                         ZerogClient._resolve(model) → provider
                                            ▼
                     wallet-signed call → answer + TEE verification
```

Facts that shape the design:
- **Manual today.** `rag.answer(query, model)` passes the picker's model straight through; `None` → sidecar `defaultModel`.
- **Each model = a separate 0G provider, separately funded.** Unfunded provider → **502** (`main.py:_friendly_error`
  already catches `InsufficientAvailableBalance`). `listChatModels()` filters the picker to the funded `ZEROG_MODELS` allowlist.
- **The query is already embedded** by `retrieve.search_scored` (RAG) → a router can reuse it for free (future option C).
- **Verification already carries the model** (`verification.model = svc.model`) → "which model answered" is already provable.
- Roster (`ZEROG_MODELS`): `0gm` (0G's own 35B-A3B MoE — cheap/fast default), `GLM-5.1-FP8`, `deepseek-v4-pro`, `qwen3.7-max`.

## 3. Routing model — two axes

| Axis | Question | Maps to |
|---|---|---|
| **Tier** (complexity) | trivial or hard? | `0gm` (fast/cheap) ↔ GLM-5.1 / deepseek (strong) |
| **Domain** (specialist) | code/math? multilingual/long? general? | deepseek → code/math · qwen → multilingual/long · 0gm/GLM → general |

Lanes are **intended starting points**, to be validated empirically (§7). No benchmark claims asserted.

## 4. Engine — Option B (decided) with a heuristic layer in front

| Layer | How | Added cost/latency | Role |
|---|---|---|---|
| **Heuristic short-circuit (A)** | features: length, code fences, math, detected language, "explain/prove" keywords → rule | ~0 | **first** — obvious queries skip the classifier entirely |
| **LLM classifier (B)** | one call on **`0gm`**, unverified, JSON-constrained → `{model, reason}` | +1 fast call (small) | **primary** — only runs for ambiguous queries |
| Embedding router (C) | reuse bge query embedding → nearest model-profile centroid | ~0 | **future** optimization (drops the extra call) |
| Cascade (D) | answer cheap → judge confidence → escalate | up to 2× | **opt-in** "best quality" mode, later |

### Why `0gm` is the classifier
1. **Most reliably-funded** (0G's own model, the `default`) → the *routing call itself* won't 502. If the classifier
   model went down, routing would break for every query, so it must run on the most-available model.
2. **Triage ≪ answering** — picking "looks like code → deepseek" is easy; a small fast model handles it. (§7 proves this; if not, swap.)
3. **Cheap/fast** — short prompt, low `max_tokens`, `enable_thinking:false`, **unverified** (skip `processResponse`).

### Two refinements (so we're not locked to `0gm`)
- **Configurable router model** — `models.router` in `0gora.config.json`, defaulting to `default` (`0gm`). Swap in config, no code change.
- **Heuristic short-circuit first** — most turns pay **zero** extra calls; `0gm` only runs on genuinely ambiguous queries.

## 5. Non-negotiable guardrails

1. **Availability filter + cascade-on-fail.** Router chooses only from `allowModels ∩ currently-served`; on a provider 502
   it **retries on the default model**. A query must never die because a specialist's sub-account ran dry. (#1 prod failure mode.)
2. **Transparency.** Surface the choice by the verification seal — *"Routed to deepseek-v4-pro · code/math query"*.
   For a verify-don't-trust product, "why this model" should be visible. Strengthens the story.

## 6. Config-driven (keeps the v0.2.0 framework/example split)

Routing **policy** = config (per-agora); routing **engine** = framework code. New `0gora.config.json` block:

```jsonc
"models": {
  "auto": true,
  "default": "0gm",
  "router": "0gm",              // model that does the classification; defaults to `default`
  "roster": [
    {"id": "0gm",                 "tier": "fast",   "strengths": ["general","short","greetings"]},
    {"id": "zai-org/GLM-5.1-FP8", "tier": "strong", "strengths": ["reasoning","analysis"]},
    {"id": "deepseek-v4-pro",     "tier": "strong", "strengths": ["code","math","logic"]},
    {"id": "qwen3.7-max",         "tier": "large",  "strengths": ["multilingual","long-context"]}
  ]
}
```

The classifier prompt is built from `roster`, so founders tune routing by editing config.
`ZEROG_MODELS` (.env) stays the funding allowlist; the router intersects with it.

## 7. Evaluation — ship the feature with its proof

Auto-routing is only worth it if measurably better/cheaper. Harness:
- ~30–50 labeled queries (code, math, multilingual, simple, RAG-grounded) × each model, scored by an LLM-judge.
- Validates lane assignments empirically; tunes the classifier prompt; confirms `0gm` is a strong-enough router.
- Metrics: answer quality vs **OG cost** vs latency. Also seeds the option-C embedding profiles.

## 8. Code changes (where it lands)

- **`src/api/app/router.py`** (new) — `choose(query, retrieval_signals, roster) → {model, reason}`. Heuristic (A) → `0gm` classifier (B) → availability intersection.
- **`rag.answer`** — when `model in (None, "auto")`, call `router.choose(...)`; feed it `top_score`/`chunks` (grounded-vs-general is a useful, free signal).
- **`zerog` / inference** — unverified fast path for the classification call (skip `processResponse`); cascade-to-default on 502.
- **webui** — picker gains **"Auto (recommended)"** as default; render the routing reason near the seal; keep manual pin available.
- **`/config` + response shape** — expose `roster`; return `routing: {chosen, reason}` alongside `x_0g_verification`.

## 9. Phasing inside v0.2.1

1. **MVP** — Auto default + heuristic router (A) + availability filter + cascade fallback + transparency. Zero extra 0G calls.
2. **Classifier** — add the `0gm` LLM router (B), config-driven roster.
3. **Eval & tune** — harness above; lock the lanes.
4. **Optimize** — embedding router (C) to drop the extra call; optional cascade (D) opt-in "best-quality" mode.

## 10. Open questions (resolve before/at build)

1. **Routing signal** — pure classifier, or also feed RAG signals (grounded-vs-general, top cosine)? *(Lean: yes — free + meaningful.)*
2. **Cost posture** — OK to spend one extra fast/unverified `0gm` call per ambiguous query, or make embedding router (C) the MVP instead?
3. **User override** — keep the manual picker alongside Auto (Auto default, power users can pin)? *(Lean: yes.)*

---
*Internal roadmap doc (sibling to `PLAN.md`); kept out of `docs/` so it does not surface on the public docs site. Uncommitted until Kevin commits it.*
