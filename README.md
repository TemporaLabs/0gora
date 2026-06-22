<h1 align="center">0Gora</h1>
<p align="center"><em>Verifiable AI answers, computed on 0G — a knowledge engine you can trust.</em></p>
<p align="center">
  🌐 <a href="https://0gora.temporalabs.com"><b>Live demo: 0gora.temporalabs.com</b></a> &nbsp;·&nbsp; Built for the <a href="https://0g.ai/arena/zero-cup">0G Zero Cup</a>
</p>

---

**0Gora** is an enterprise-grade knowledge assistant: ask a question, get a **grounded answer with citations** —
and **every answer is generated *and* cryptographically verified on [0G](https://0g.ai)'s decentralized
compute** (TEE-attested via the 0G serving broker), surfaced as a **"Verified on 0G"** badge.

Out of the box it's seeded with **0G's own documentation and blog** — so you can literally **"Ask 0Gora anything
about 0G"** and get a verifiable, cited answer. It's evolving toward a **community-owned knowledge commons** (the
*agora*) where anyone can contribute knowledge.

## Why 0G is load-bearing (not a bolt-on)
Every answer is produced by an open model (e.g. `GLM-5-FP8`) running on a **0G compute provider inside a hardware
TEE**, and the response is **verified on-chain** via `@0glabs/0g-serving-broker`'s `processResponse`. The result:

> **Remove 0G and 0Gora can't answer — and loses the cryptographic verifiability that is its whole point.**

That's something a centralized LLM API fundamentally cannot offer. Later phases deepen this further (corpus on
**0G Storage**, contribution records on **0G Chain**).

## What it does
- 🔎 **Grounded RAG** — hybrid retrieval (vector + BM25) over a seeded 0G corpus, answers with inline citations.
- ✅ **Verified on 0G** — per-answer TEE attestation (real `chatID`, on-chain verification).
- 🧠 **Pick any 0G model** — 13 verifiable models served on 0G (GLM, DeepSeek-V4, Qwen, MiniMax, …).
- ➕ **Contribute** — paste a URL and it's crawled, embedded, and instantly retrievable.

## Architecture
```
Contributors ─► Ingest ─► Chunk + Embed (bge) ─► Qdrant (vector store)
       │                                              │
 Next.js chat ─► Hybrid retrieval (vector + BM25) ─► Prompt ─┐
       ▲                                                      ▼
       │                   ┌──────────────────────────────────────────┐
       │                   │  GENERATION on 0G COMPUTE  ★ load-bearing  │
       │                   │  @0glabs/0g-serving-broker → TEE-verified  │
       │                   └──────────────────────────────────────────┘
       │                                                      │
       └──────────── Answer + citations + "Verified on 0G" ◄──┘
```

| Path | What |
|------|------|
| `zerog/` | 0G compute service — OpenAI-compatible; runs GLM on 0G via the direct broker + TEE verification |
| `backend/` | FastAPI — ingestion (URL/site/sitemap/paste), bge embeddings, hybrid retrieval, RAG |
| `web/` | Next.js chat UI — model picker, citations, "Verified on 0G" badge, Contribute |
| `deployment/` | docker-compose (+ prod overlay: nginx + Let's Encrypt) |

## Stack
Next.js · FastAPI · Qdrant · sentence-transformers (bge/e5) · rank-bm25 · `@0glabs/0g-serving-broker` + ethers · Docker.
All open-source; the 0G integration is our own code on the public 0G SDK.

## Run it

**Local (mock 0G — no funds):**
```bash
cd deployment
echo "ZEROG_MOCK=true" > .env
docker compose up -d --build          # web :3000 · backend :8000 · qdrant :6333
# seed: curl -X POST localhost:8000/contribute -H 'content-type: application/json' \
#            -d '{"url":"https://0g.ai/blog","mode":"site","max_pages":30}'
```

**Real mode (0G mainnet):** set `ZEROG_MOCK=false` + `ZEROG_PRIVATE_KEY` (a funded 0G wallet) in
`deployment/.env`, confirm the live model id with `cd zerog && npm i && npm run probe`, then bring up.
Prod (TLS): `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`.

## Access, contribution & storage
- **Access:** the live demo is **public** — anyone can use the chat (no login). It's **read-only**: you can
  ask questions, but **contribution is closed**.
- **Contribution (coming):** the ingestion pipeline (`POST /contribute` → crawl → clean → chunk → embed) is
  built and admin-gated behind a key today. Open, community-owned contribution — with on-chain attribution —
  is the *agora* on the roadmap; the knowledge base is curated until then.
- **Where the knowledge lives:** a **Qdrant** vector database (collection `0gora`) — each chunk stored as an
  embedding vector + `{text, source url, bin}`. It is **not** in S3 or a file bucket; it's the vector store.
  The seeded 0G blog + docs were crawled → chunked → embedded into it. *(Roadmap: migrate the corpus to **0G Storage**.)*

## Roadmap
- **Now:** verifiable 0G knowledge engine, seeded with 0G docs + blog (live).
- **Next:** more sources; on-chain settlement-tx link on the badge; **0G Storage** for the corpus.
- **Community commons (future):** open contribution + topic bins + **on-chain attribution & contributor rewards** on 0G Chain.

## Eligibility (Zero Cup)
Own work built in the tournament window, composed from **open-source libraries**; **0G does real work**
(verifiable inference is load-bearing). Design influenced by open-source enterprise-search platforms (e.g.
[Onyx](https://github.com/onyx-dot-app/onyx), MIT) and the broader RAG ecosystem — **0Gora is an original
implementation, not a fork.**
