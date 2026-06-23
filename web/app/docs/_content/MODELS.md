# 0Gora model catalog — the four models, and why each was selected

0Gora offers exactly four AI models. **All are served on 0G's _direct_ compute broker and all carry
`verifiability = "TeeML"`** — every answer is cryptographically attested inside a hardware Trusted
Execution Environment (TEE) and verifiable on-chain (`processResponse`).

**Selection criteria**
1. The model must be registered on the 0G **direct serving broker** with **TeeML** attestation.
   Router-only models (e.g. GLM-5.2, which uses **TeeTLS** routing — a weaker trust model) are excluded.
2. The lineup favors **lab diversity**, a current (non-deprecated) checkpoint per lab, and a strong,
   on-theme **default**.

| # | Picker model (broker id) | Lab | Role | Source page |
|---|---|---|---|---|
| 1 | `0GM-1.0-35B-A3B` **(default)** | 0G Foundation | 0G's own model | [pc.0g.ai/models/0gm-1.0-35b-a3b](https://pc.0g.ai/models/0gm-1.0-35b-a3b) |
| 2 | `zai-org/GLM-5.1-FP8` | Zhipu AI (Z.ai) | newest verifiable GLM | [pc.0g.ai/models/glm-5.1](https://pc.0g.ai/models/glm-5.1) |
| 3 | `deepseek-v4-pro` | DeepSeek | frontier reasoning + instruction-following | [pc.0g.ai/models/deepseek-v4-pro](https://pc.0g.ai/models/deepseek-v4-pro) |
| 4 | `qwen3.7-max` | Alibaba | strong alternative | [pc.0g.ai/models/qwen3.7-max](https://pc.0g.ai/models/qwen3.7-max) |

### 1. `0GM-1.0-35B-A3B` — default
0G Foundation's own **in-house model**: a 35B-parameter mixture-of-experts with ~3B active params (A3B),
tuned for agentic coding and tool use, 262K context. **Why default:** it's 0G's native model running on
0G's own verifiable compute (the most on-theme choice) and it's the **fastest, lowest-cost-per-token** of
the four.

### 2. `zai-org/GLM-5.1-FP8`
GLM-5.1 from Zhipu AI, served as an **FP8-quantized, broker-attested** build (the `-FP8` suffix = the
TEE-verified broker variant). **Why:** it's the **newest GLM on the verifiable broker** — GLM-5.2 exists on
0G but only via the router, so it can't be cryptographically verified through 0Gora's flow.

### 3. `deepseek-v4-pro`
DeepSeek's current flagship on the verifiable broker. **Why:** strong frontier **reasoning and
instruction-following** (answer-only-from-context + clean citations — exactly 0Gora's RAG discipline), and
a recognizable non-GLM lab for diversity. 0Gora tracks the **current** DeepSeek checkpoint: the older
`deepseek/deepseek-chat-v3-0324` (DeepSeek-V3) is being retired on pc.0g.ai, so the slot moved to
`deepseek-v4-pro`. (A lighter `deepseek-v4-flash` is also TeeML-served on the broker if a faster/cheaper
DeepSeek is ever preferred.)

### 4. `qwen3.7-max`
Qwen3.7-Max from Alibaba. **Why:** a capable, recognizable frontier model from a different lab, broadening
diversity while remaining TeeML-verifiable.

---
**Other models on the verifiable broker (not in 0Gora's curated picker)**
The 0G direct broker also TeeML-serves, among others: `deepseek-v4-flash`, `glm-5`, `glm-5.1` (non-FP8
alias), `qwen3.6-plus`, `qwen/qwen3-vl-30b-a3b-instruct`, `openai/gpt-5.4-mini`, and `MiniMax-M3`. 0Gora
curates a deliberate four rather than exposing every option, but any of these could be swapped in — each is
cryptographically verifiable through the same TeeML flow.

**Retired / excluded**
- `deepseek/deepseek-chat-v3-0324` (DeepSeek-V3) — replaced by `deepseek-v4-pro` as DeepSeek's current
  broker checkpoint; V3 is being deprecated on pc.0g.ai.
- `zai-org/GLM-5-FP8` — previously the only model; retired from the picker in favor of `GLM-5.1-FP8`.
- `glm-5.2` — **router-only (TeeTLS)**, not on the broker, so it cannot be verified through 0Gora's
  TeeML attestation flow. (Ask 0Gora "why isn't GLM-5.2 available?" — it explains this itself.)
