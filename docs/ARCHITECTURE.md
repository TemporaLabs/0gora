# 0Gora architecture

0Gora is a retrieval-augmented (RAG) knowledge assistant whose AI inference runs on 0G's decentralized,
verifiable compute. Ask a question → get a grounded answer **with citations, generated *and* cryptographically
verified on 0G** inside a hardware TEE.

This page covers two things: **the 0G stack** 0Gora builds on, and **how 0Gora sits on top of it**.

## The 0G stack

0G is infrastructure for decentralized AI — four pillars. 0Gora is built on these, but doesn't use all of
them (yet). The diagram is colored by what 0Gora uses today.

![The 0G stack](/diagrams/0g-stack.svg)

- **[Chain](https://docs.0g.ai/concepts/chain)** — an EVM-compatible L1 optimized for AI, for settlement and coordination.
- **[Compute](https://docs.0g.ai/concepts/compute)** — a decentralized compute network that runs model inference **inside a hardware Trusted Execution Environment (TEE)** and attests to it (TeeML). *This is the pillar 0Gora is built on.*
- **[Storage](https://docs.0g.ai/concepts/storage)** — decentralized storage: an immutable **Log** layer and a mutable **key-value** layer (well suited to corpora and embeddings).
- **[DA](https://docs.0g.ai/concepts/da)** — a high-throughput data-availability layer for rollups and appchains.

Full concepts: <https://docs.0g.ai/concepts>.

## What 0Gora uses — and what's next

| 0G pillar | In 0Gora today | Notes |
|-----------|----------------|-------|
| **Compute** | ✅ **Load-bearing** | Every answer is generated and TEE-verified on the 0G direct broker. Remove it and 0Gora cannot answer. |
| **Storage** | ⛏ **Roadmap** | The corpus lives in **Qdrant** (a conventional vector database, off-chain) today. Moving it onto 0G Storage is the planned next integration, so the *data* layer is on 0G too — not just the model call. |
| **Chain** | — *candidate* | Not used yet. A natural fit later for on-chain contribution / attribution records. |
| **DA** | — not used | Out of scope for a knowledge assistant. |

> **In short:** one pillar load-bearing today (**Compute**), one planned (**Storage**), two unused (**Chain**, **DA**). Storage is deliberately deferred — its SDK is far less battle-tested than the compute broker, and we don't want a flaky data path near a working demo.

## 0Gora on 0G

Humans and AI agents share one verifiable brain.

![0Gora on 0G](/diagrams/0gora-architecture.svg)

| Path | Role |
|------|------|
| `zerog/` | **0G compute service** — OpenAI-compatible front for the 0G serving broker. Runs the chosen model on a 0G provider inside a TEE and verifies the response (`processResponse`). This is what makes every answer verifiable. |
| `backend/` | **FastAPI RAG** — ingestion (URL / site / sitemap / paste) → clean → chunk → embed (`bge`) → store; hybrid retrieval (vector + BM25, fused with RRF); generation. Endpoints: `/chat`, `/search`, `/models`. |
| `web/` | **Next.js** — the landing page (`/`), the chat (`/0g`), and these docs (`/docs`); model picker, inline citations, the "Verified on 0G" seal. |
| `mcp/` | **MCP server + example client** — the agent-facing surface (see [`../mcp/README.md`](../mcp/README.md)). |
| Qdrant | **Vector store** — embedded passages + source URLs (off-chain today; → 0G Storage on the roadmap). |
| `deployment/` | docker-compose; nginx + TLS in front. |

### The answer flow
```
question
   │
   ▼
hybrid retrieval over the corpus (vector + BM25 → RRF)   ← Qdrant
   │  numbered context
   ▼
generation on 0G Compute  ── inside a hardware TEE ──▶  response verified (processResponse)
   │
   ▼
answer + citations + verification seal  ("Verified on 0G")
```
If retrieval finds nothing relevant, 0Gora answers from the model's general knowledge instead of refusing — without citations.

## What "Verified on 0G" means
Models are served on the 0G **direct compute broker** and flagged `verifiability = "TeeML"`: the inference runs
**sealed inside a hardware Trusted Execution Environment**, and each response carries an attestation that can be
verified on-chain. 0Gora offers **only** TeeML-attested models.

A model reachable only via the 0G **router** uses **TeeTLS** (verifiable *routing*, a different trust model) and
is therefore not offered — which is why, for example, GLM-5.2 isn't in the picker. See [`MODELS.md`](MODELS.md).

## Two surfaces, one brain
- **Humans** → the web app: landing at [`0gora.temporalabs.com`](https://0gora.temporalabs.com), chat at `/0g`.
- **AI agents** → the **MCP** server (`ask_0gora` / `search_0g_knowledge` / `list_models`), via local stdio or
  the hosted remote endpoint `/mcp`.

Both hit the same verifiable 0G engine.

## Knowledge base & contribution
The corpus is a vector store of embedded passages, each with its source URL. The public chat is **read-only**;
the ingestion pipeline is **admin-curated** today. Open, community-owned contribution — the *agora* — is on the
roadmap.

## Models & license
Four TEE-verified 0G models (0GM as default) — see [`MODELS.md`](MODELS.md). Licensed Apache-2.0
([`../LICENSE`](../LICENSE), [`../NOTICE`](../NOTICE)).
