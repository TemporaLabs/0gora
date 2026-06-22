<h1 align="center">0Gora</h1>
<p align="center"><em>The community-crowdsourced knowledge commons — verifiable AI answers on 0G.</em></p>

0Gora is a RAG knowledge assistant whose **AI inference runs on [0G](https://0g.ai)'s decentralized,
verifiable compute** (every answer cryptographically verified inside a hardware TEE), and whose knowledge base
is **contributed, curated, and owned by the community** — the *agora*.

Built for the **0G Zero Cup**. See [`PLAN.md`](PLAN.md) for the full design.

## Why 0G is load-bearing
Answers are generated on **0G Compute** via the `@0glabs/0g-serving-broker` direct broker and verified with
`processResponse` (TEE attestation), shown as a **"Verified on 0G"** badge. Remove 0G → 0Gora can't answer.

## Structure
| Path | What |
|------|------|
| `zerog/` | 0G compute service — OpenAI-compatible, runs GLM on 0G + TEE verification (the load-bearing 0G piece) |
| `backend/` | FastAPI — ingestion, embeddings, hybrid retrieval, RAG generation |
| `web/` | Next.js chat UI (citations + Verified-on-0G badge) — _coming_ |
| `deployment/` | docker-compose |

## Quickstart (dev)
```bash
cd deployment
cp ../zerog/.env.example .env     # set ZEROG_PRIVATE_KEY (or ZEROG_MOCK=true for no-funds dev)
docker compose up -d --build
# backend on :8000, 0G compute on :8090, Qdrant on :6333
```

## Stack
Next.js · FastAPI · Qdrant · sentence-transformers (bge/e5) · rank-bm25 · `@0glabs/0g-serving-broker` · Docker.

## Credits
Design influenced by open-source enterprise-search platforms (e.g. [Onyx](https://github.com/onyx-dot-app/onyx), MIT)
and the broader RAG ecosystem. 0Gora is an original implementation composed from open-source libraries — not a fork.
