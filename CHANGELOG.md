# Changelog

All notable changes to **0Gora** — the verifiable AI knowledge engine on 0G.
Live: <https://0gora.temporalabs.com> · Built for the 0G Zero Cup.

Versioning follows `0.1.x` during the tournament, leading to a `1.0.0` final.
Tags mark each release; the newest version is at the top.

## [0.1.2] — 2026-06-22 — Robustness, multi-model, QA
### Added
- **4 TEE-verified 0G models** in the picker, each funded on the direct broker with `TeeML` attestation:
  **`0GM-1.0-35B-A3B`** (default — 0G Foundation's own model), `zai-org/GLM-5.1-FP8`,
  `deepseek/deepseek-chat-v3-0324`, `qwen3.7-max`.
- `docs/MODELS.md` — model catalog with broker ids, source pages, and selection rationale.
- KB explainer for why GLM-5.2 isn't offered (router-only `TeeTLS` vs. broker `TeeML`); 0Gora answers it itself.
- Test suites: backend `pytest` (11), zerog `node --test` (5), live `tests/smoke.sh`, live `tests/qa.sh`
  (per-model functional, grounding-refusal, read-concurrency).
- KB expanded to ~651 chunks (added `pc.0g.ai` + `docs.0g.ai`).
### Fixed
- **nginx routes `/api` directly to the backend** (300s) — fixes a Next.js proxy timeout that aborted any 0G
  answer slower than 30s (root cause of "Error reaching the backend").
- **Thread-safe embedding-model load + startup warmup** — fixes a cold-start concurrency crash
  (torch "meta tensor") when parallel requests raced the lazy model init.
- Graceful error handling — `/chat` never returns a raw 500; upstream failures map to a friendly message.
- `ZEROG_MODELS` allowlist is now forwarded to the zerog service (picker shows only funded/verified models).

## [0.1.1] — 2026-06-21 — First working release + live deploy
### Added
- **0G compute service** — OpenAI-compatible, runs models on 0G via the direct broker
  (`@0glabs/0g-serving-broker`) with `processResponse` TEE verification (the load-bearing 0G piece).
- **RAG backend** — ingestion (URL / site / sitemap / paste), `bge` embeddings, hybrid retrieval
  (vector + BM25, fused with RRF), grounded answers with inline citations.
- **Next.js chat UI** — model picker, citations, "Verified on 0G" badge.
- Seeded the knowledge base with 0G blog + docs.
- Deployed to <https://0gora.temporalabs.com> (nginx + Let's Encrypt TLS).
- Contribution **admin-locked** (public chat is read-only); submission-grade README; repository made public.

## [0.1.0] — 2026-06-20 — Scaffold
### Added
- Repository skeleton: `zerog/` (0G compute service), `backend/` (FastAPI RAG), `web/` (Next.js),
  `deployment/` (docker-compose) — with stubs for the full RAG pipeline.

## [0.1.3] — 2026-06-22 — Agents, throughput, license
### Added
- **MCP service** (`mcp/`) — the agent-facing side of the *agora*. A stdio MCP server exposing
  `ask_0gora`, `search_0g_knowledge`, and `list_models`, so AI agents (e.g. Claude Code) can consume
  0Gora's **TEE-verified** knowledge. Dual-surface: humans → web, agents → MCP, same verifiable 0G brain.
- Backend `/search` endpoint — raw hybrid retrieval (no LLM) powering the `search_0g_knowledge` tool.
- **Apache-2.0 license** (`LICENSE` + `NOTICE`) — chosen for its explicit patent grant and liability
  disclaimer so anyone can fork 0Gora into their own verifiable knowledge agora and commercialize it.
### Changed
- **Inference parallelization** — `chatCompletion` no longer serializes the whole call; only the
  nonce-bound broker steps (ack + `getRequestHeaders`, and each `processResponse` attempt) are serialized,
  while the slow LLM fetch + verify backoff run concurrently. Measured: 8 concurrent requests **42s → 21s**,
  all verified — throughput now scales with concurrency instead of one-call-at-a-time.

## [Unreleased] — planned
- Remote MCP endpoint on the EC2 (HTTP/SSE) alongside the web app.
- **0G Storage** for the corpus; on-chain settlement-tx link on the verification badge.
- **Community commons** (post-tournament) — open contribution, topic bins, on-chain attribution & rewards.
