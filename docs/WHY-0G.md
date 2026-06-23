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
Four TEE-verified models; **0GM** is default.

| Model | Lab | Role |
|-------|-----|------|
| `0GM-1.0-35B-A3B` *(default)* | 0G Foundation | 0G's own model; fastest, lowest cost |
| `zai-org/GLM-5.1-FP8` | Zhipu AI | newest verifiable GLM |
| `deepseek-v4-pro` | DeepSeek | frontier reasoning |
| `qwen3.7-max` | Alibaba | strong alternative |

All on the direct broker, all TeeML. The broker serves others too (`deepseek-v4-flash`, `glm-5`,
`qwen3.6-plus`, `gpt-5.4-mini`, `MiniMax-M3`, …) — any can be swapped in. Per-model pages: <https://pc.0g.ai/models>.

---
Next: [Inside 0Gora](INSIDE.md)
