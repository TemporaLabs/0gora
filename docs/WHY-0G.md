# Why 0G?

0Gora's promise is trust — you can verify where every answer came from. That comes from 0G.

## The 0G stack
0G is infrastructure for decentralized AI: four pillars. 0Gora builds on them (colored by what it uses today).

![The 0G stack](/diagrams/0g-stack.svg)

- **[Chain](https://docs.0g.ai/concepts/chain)** — EVM L1 for AI; settlement and coordination.
- **[Compute](https://docs.0g.ai/concepts/compute)** — inference inside a hardware TEE, attested (TeeML). The pillar 0Gora runs on.
- **[Storage](https://docs.0g.ai/concepts/storage)** — decentralized data: immutable Log + mutable key-value.
- **[DA](https://docs.0g.ai/concepts/da)** — high-throughput data availability.

Concepts: <https://docs.0g.ai/concepts>.

## What 0Gora uses
| Pillar | Today | Notes |
|--------|-------|-------|
| **Compute** | ✅ load-bearing | Every answer generated + TEE-verified on the direct broker. Remove it, 0Gora can't answer. |
| **Storage** | ⛏ roadmap | Corpus is in Qdrant (off-chain) today; moving it to 0G Storage is next. |
| **Chain** | — candidate | Later: on-chain contribution / attribution. |
| **DA** | — unused | Out of scope. |

One pillar load-bearing (Compute), one planned (Storage), two unused.

## Architecture
![0Gora on 0G](/diagrams/0gora-architecture.svg)

`question → hybrid retrieval (Qdrant) → numbered context → generation on 0G Compute (TEE) → verified (processResponse) → answer + citations + seal.`

## What "Verified on 0G" means
Models run on the 0G **direct broker** with `verifiability = "TeeML"`: sealed in a hardware TEE, each response
attested on-chain. 0Gora offers **only** TeeML models. Router-only models use **TeeTLS** (verifiable *routing* —
weaker), so e.g. GLM-5.2 isn't offered.

## Model catalog
Four TEE-verified models. The picker defaults to **Auto** (below); **0GM** is the routing default + fallback.

| Model | Lab | Lane (strengths) |
|-------|-----|------------------|
| `0GM-1.0-35B-A3B` *(default · fallback)* | 0G Foundation | general, short — fastest, lowest cost |
| `zai-org/GLM-5.1-FP8` | Zhipu AI | reasoning, analysis |
| `deepseek-v4-pro` | DeepSeek | code, math, logic |
| `qwen3.7-max` | Alibaba | multilingual, long-context |

All on the direct broker, all TeeML. The broker serves others too (`deepseek-v4-flash`, `glm-5`,
`qwen3.6-plus`, `gpt-5.4-mini`, `MiniMax-M3`, …) — any can be swapped in via config. Per-model pages: <https://pc.0g.ai/models>.

## Auto routing
By default 0Gora picks the best model **per query** — fast/cheap for easy turns, a specialist for hard ones —
and that chosen model then generates **and TEE-verifies** the answer on 0G as normal. Two layers, cheapest first:

1. **Heuristic (free).** Obvious queries route by rule with zero extra model calls: a greeting → the fast model;
   a code fence / `def …` / `SELECT … FROM` → the *code* lane; math symbols → *math*; non-Latin script →
   *multilingual*; a very long query → *long-context*.
2. **LLM classifier (cheap) — on 0G.** For ambiguous queries, one short call on the cheap router model
   (default `0GM`) running on 0G returns the best model id. **That routing call is *unverified*** — it only
   *picks* a model, it isn't the answer, so it stays fast and cheap. The answer the chosen model produces is
   always TEE-verified, with its own **Verified on 0G** seal.

If the chosen model's 0G provider is momentarily unavailable, the answer **cascades to the default** (`0GM`) —
a query never dies because a specialist is unfunded. The footer shows which model actually answered
(*"⤷ Auto routed to …"*).

Routing is **config-driven**: the roster (models + their lanes), the default, and the router model all live in
`0gora.config.json` — `strengths` drives the choice, `tier` is advisory context for the classifier. Tune routing
by editing config, no code change. Prefer a specific model? Pin it from the picker to bypass Auto.

---
Next: [Inside 0Gora](INSIDE.md)
