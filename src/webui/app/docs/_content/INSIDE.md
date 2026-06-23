# Inside 0Gora

For developers: how 0Gora works, and how to run your own. The reusable framework lives in **`src/`**; a
deployment is a small config folder under **`examples/`** that drives it (the shipped one is
[`examples/0g/`](https://github.com/TemporaLabs/0gora/tree/main/examples/0g)). You found your own agora by
copying that folder and editing config — you never touch `src/`.

0Gora's RAG design is **influenced by Onyx**; the implementation here is its own, built for this cup.

## Retrieval (RAG)
- **Ingest** — fetch a URL / site / sitemap → clean (trafilatura) → chunk → embed (`bge-small`) → store.
- **Query** — hybrid retrieval: vector search (Qdrant) + BM25 keyword, fused with Reciprocal Rank Fusion (RRF) → top-k passages.
- **Ground** — passages become numbered context; the model cites them inline as `[n]`.
- **Relevance gate** — if the top match is weak, skip retrieval and answer from the model's general knowledge (no citations) instead of refusing.

## Corpus & storage
- The corpus is a **Qdrant** vector store. Each record = embedding + text + source URL.
- **Updated** by re-ingesting sources (re-run ingestion on a URL → chunks refreshed). Admin-curated today; open contribution is on the roadmap.
- Off-chain today; **0G Storage** is the planned home, so the data layer is on 0G too.

## Components
| Service | Role |
|---------|------|
| RAG API (FastAPI) | ingest, retrieve, generate · endpoints `/chat`, `/search`, `/models`, `/config` |
| 0G inference (Node) | OpenAI-compatible front to the 0G broker; runs the model in a TEE and verifies (`processResponse`) |
| MCP server | agent surface (`ask` / `search` / `list`) |
| Web | landing, chat, docs |
| Qdrant | vector store |

## Deploy your own
0Gora runs as Docker containers wired by Docker Compose. The base compose in `src/deploy/` defines the generic
services; an example's `compose.override.yml` layers its config on top:

```bash
git clone https://github.com/TemporaLabs/0gora
cd 0gora
cp examples/0g/.env.example examples/0g/.env   # set your 0G wallet key (or keep ZEROG_MOCK=true)
docker compose -f src/deploy/docker-compose.yml \
               -f examples/0g/compose.override.yml \
               --env-file examples/0g/.env up -d
```

That brings up the RAG API, the 0G inference service, the MCP server, the web app, and Qdrant. The instance's
branding, example questions, and seed corpus come from `examples/0g/0gora.config.json` — no secrets, mounted at
runtime. Seed the corpus with `examples/0g/seed.sh`. Add `-f src/deploy/docker-compose.prod.yml` for TLS in
production.

**Found your own:** copy `examples/0g` to `examples/<your-topic>`, edit `0gora.config.json` (name, questions,
seed URLs) and `.env` (your funded 0G wallet + models), and bring it up with your folder's overlay. Same
framework, a brand-new verifiable agora.

---
Next: [What is 0Gora?](README.md) · [Why 0G?](WHY-0G.md)
