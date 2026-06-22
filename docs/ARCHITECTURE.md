# 0Gora architecture

0Gora is a retrieval-augmented (RAG) knowledge assistant whose AI inference runs on 0G's decentralized,
verifiable compute. Ask a question → get a grounded answer **with citations, generated *and* cryptographically
verified on 0G** inside a hardware TEE.

## Components
| Path | Role |
|------|------|
| `zerog/` | **0G compute service** — OpenAI-compatible front for the 0G serving broker. Runs the chosen model on a 0G provider inside a TEE and verifies the response (`processResponse`). This is what makes every answer verifiable. |
| `backend/` | **FastAPI RAG** — ingestion (URL / site / sitemap / paste) → clean → chunk → embed (`bge`) → store; hybrid retrieval (vector + BM25, fused with RRF); generation. Endpoints: `/chat`, `/search`, `/models`. |
| `web/` | **Next.js chat UI** — model picker, inline citations, the "Verified on 0G" badge. |
| `mcp/` | **MCP server + example client** — the agent-facing surface (see [`../mcp/README.md`](../mcp/README.md)). |
| `deployment/` | docker-compose; nginx + TLS in front. |

## The answer flow
```
question
   │
   ▼
hybrid retrieval over the corpus (vector + BM25 → RRF)
   │  numbered context
   ▼
generation on 0G compute  ── inside a hardware TEE ──▶  response verified (processResponse)
   │
   ▼
answer + citations + verification block  ("Verified on 0G")
```

## What "Verified on 0G" means
Models are served on the 0G **direct compute broker** and flagged `verifiability = "TeeML"`: the inference runs
**sealed inside a hardware Trusted Execution Environment**, and each response carries an attestation that can be
verified on-chain. 0Gora offers **only** TeeML-attested models.

A model that is reachable only via the 0G **router** uses **TeeTLS** (verifiable *routing*, a different trust
model) and is therefore not offered — which is why, for example, GLM-5.2 isn't in the picker. See
[`MODELS.md`](MODELS.md).

## Two surfaces, one brain
- **Humans** → the web app at [`0gora.temporalabs.com`](https://0gora.temporalabs.com).
- **AI agents** → the **MCP** server (`ask_0gora` / `search_0g_knowledge` / `list_models`), via local stdio or
  the hosted remote endpoint `/mcp`.

Both hit the same verifiable 0G engine.

## Knowledge base & contribution
The corpus is a vector store of embedded passages, each with its source URL. The public chat is **read-only**;
the ingestion pipeline is **admin-curated** today. Open, community-owned contribution — the *agora* — is on the
roadmap.

## Models
Four TEE-verified 0G models (0GM as default). See [`MODELS.md`](MODELS.md).

## License
Apache-2.0 — see [`../LICENSE`](../LICENSE) and [`../NOTICE`](../NOTICE).
