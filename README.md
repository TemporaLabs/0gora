<h1 align="center">0Gora</h1>
<p align="center"><em>Verifiable AI answers, computed on 0G — a knowledge engine you can trust.</em></p>
<p align="center">
  🌐 <a href="https://0gora.temporalabs.com"><b>Live demo: 0gora.temporalabs.com</b></a> &nbsp;·&nbsp; Built for the <a href="https://0g.ai/arena/zero-cup">0G Zero Cup</a> &nbsp;·&nbsp; <a href="CHANGELOG.md">Changelog</a>
</p>

---

**0Gora** is an enterprise-grade knowledge assistant: ask a question, get a **grounded answer with citations** —
and **every answer is generated *and* cryptographically verified on [0G](https://0g.ai)'s decentralized
compute** (TEE-attested via the 0G serving broker), surfaced as a **"Verified on 0G"** badge.

Out of the box it's seeded with **0G's own documentation and blog** — so you can literally **"Ask 0Gora anything
about 0G"** and get a verifiable, cited answer. It's evolving toward a **community-owned knowledge commons** (the
*agora*) where anyone can contribute knowledge.

## Why 0G is core to 0Gora
Every answer is produced by an open model (e.g. `GLM-5.1-FP8`) running on a **0G compute provider inside a hardware
TEE**, and the response is **verified on-chain** via `@0glabs/0g-serving-broker`'s `processResponse`. The result:

> **Remove 0G and 0Gora can't answer — and loses the cryptographic verifiability that is its whole point.**

That's something a centralized LLM API fundamentally cannot offer. Later phases deepen this further (corpus on
**0G Storage**, contribution records on **0G Chain**).

## What it does
- 🔎 **Grounded RAG** — hybrid retrieval (vector + BM25) over a seeded 0G corpus, answers with inline citations.
- ✅ **Verified on 0G** — per-answer TEE attestation (real `chatID`, on-chain verification).
- 🧠 **4 verifiable 0G models** — answers run on 0G's TEE-attested (`TeeML`) compute. Pick from **0GM**
  (0G Foundation's own in-house model — the default), **GLM-5.1-FP8**, **DeepSeek-v4-pro**, and
  **Qwen3.7-Max** — each response cryptographically verified on 0G. *(Only models registered on the direct
  serving broker with TEE attestation are offered — which is why router-only models like GLM-5.2 aren't listed.)*
- ➕ **Contribute pipeline** — a URL is crawled, embedded, and instantly retrievable (admin-curated today;
  open community contribution is on the roadmap).
- 🤖 **For humans *and* agents** — humans use the web app; AI agents use the [`src/mcp/`](src/mcp/) MCP server
  (`ask_0gora` / `search_0g_knowledge` / `list_models`) to consume the same TEE-verified knowledge.

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
| `src/inference/` | 0G compute service — OpenAI-compatible; runs GLM on 0G via the direct broker + TEE verification |
| `src/api/` | FastAPI — ingestion (URL/site/sitemap/paste), bge embeddings, hybrid retrieval, RAG |
| `src/webui/` | Next.js chat UI — model picker, citations, "Verified on 0G" badge, Contribute |
| `src/mcp/` | **MCP server** — `ask_0gora` / `search_0g_knowledge` / `list_models` for AI agents (the agent-facing *agora*). Hosted at `/mcp`; or run locally over stdio |
| `src/deploy/` | docker-compose (+ prod overlay: nginx + Let's Encrypt) |

## Stack
Next.js · FastAPI · Qdrant · sentence-transformers (bge/e5) · rank-bm25 · `@0glabs/0g-serving-broker` + ethers · Docker.
All open-source; the 0G integration is our own code on the public 0G SDK.

## Three ways to use it
0Gora is a **framework**, not just this one site — the engine lives in [`src/`](src/) and a deployment is a small
config folder under [`examples/`](examples/0g/README.md):

1. **Fork the repo** — clone it, copy [`examples/0g/`](examples/0g/README.md), edit the config, `docker compose up`
   (see [Run it](#run-it)).
2. **npm packages** — `npx 0gora-mcp` connects any agent to a running 0Gora (the agent surface); `npm create
   0gora@latest my-agora` scaffolds your own instance ([`create-0gora`](tools/create-0gora/README.md)).
3. **Agent skill** — [`src/skill/`](src/skill/SKILL.md) teaches an AI agent to *join* an existing 0Gora and
   *found* its own.

## Run it

**Local (mock 0G — no funds):**
```bash
cd src/deploy
echo "ZEROG_MOCK=true" > .env
docker compose up -d --build          # web :3000 · backend :8000 · qdrant :6333
# seed: curl -X POST localhost:8000/contribute -H 'content-type: application/json' \
#            -d '{"url":"https://0g.ai/blog","mode":"site","max_pages":30}'
```

This runs the framework with its **built-in 0G defaults**. To run the configured 0G example
— its branding, example questions, and seed corpus from `examples/0g/0gora.config.json` — use the
example overlay instead: see [`examples/0g/`](examples/0g/README.md).

**Real mode (0G mainnet):** set `ZEROG_MOCK=false` + `ZEROG_PRIVATE_KEY` (a funded 0G wallet) in
`src/deploy/.env`, confirm the live model id with `cd src/inference && npm i && npm run probe`, then bring up.
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
Built from **open-source libraries**, with **0G doing the verifiable inference**. Design influenced by
[Onyx](https://github.com/onyx-dot-app/onyx) (MIT) and the broader RAG ecosystem. **0Gora was created
originally for the 0G Zero Cup.**

## Docs
- [`docs/README.md`](docs/README.md) — **What is 0Gora?** — overview + using it as a human or agent.
- [`docs/WHY-0G.md`](docs/WHY-0G.md) — **Why 0G?** — the 0G stack, what 0Gora uses, architecture, model catalog.
- [`docs/INSIDE.md`](docs/INSIDE.md) — **Inside 0Gora** — RAG/retrieval, storage, and deploying your own with Docker.
- [`src/mcp/README.md`](src/mcp/README.md) — the MCP server (`0gora-mcp`) + example client for AI agents.
- [`tools/create-0gora/README.md`](tools/create-0gora/README.md) — scaffold your own agora (`npm create 0gora`).
- [`src/skill/SKILL.md`](src/skill/SKILL.md) — the 0Gora agent skill (join an agora + found your own).

Rendered docs: <https://0gora.temporalabs.com/docs>.
- [`CHANGELOG.md`](CHANGELOG.md) — version history.

## License
**Apache License 2.0** — see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE). The 0G corpus seeded here is just a
demo exhibit; 0Gora is meant to be reused — adapt it to build your own verifiable knowledge *agora* for any
domain. Apache-2.0 is chosen deliberately: it grants an explicit patent license and a clear liability
disclaimer, so others can adopt and commercialize it with confidence.
