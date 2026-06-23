# Inside 0Gora

For developers: how 0Gora works, and how to run your own. *(In v0.2.0 this becomes the `src/` of a clean
framework-vs-example split.)*

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
| RAG API (FastAPI) | ingest, retrieve, generate · endpoints `/chat`, `/search`, `/models` |
| 0G inference (Node) | OpenAI-compatible front to the 0G broker; runs the model in a TEE and verifies (`processResponse`) |
| MCP server | agent surface (`ask` / `search` / `list`) |
| Web | landing, chat, docs |
| Qdrant | vector store |

## Deploy your own
0Gora runs as Docker containers wired by Docker Compose:

```bash
git clone https://github.com/TemporaLabs/0gora
cd 0gora
# set your 0G wallet key + config in .env
docker compose -f deployment/docker-compose.yml up -d
```

That brings up the RAG API, the 0G inference service, the MCP server, the web app, and Qdrant. Put it behind any
reverse proxy with TLS for production. Point ingestion at **your own sources** and you have your own 0Gora.

---
Next: [What is 0Gora?](README.md) · [Why 0G?](WHY-0G.md)
