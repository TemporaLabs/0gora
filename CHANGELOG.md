# Changelog

All notable changes to **0Gora** — the verifiable AI knowledge engine on 0G.
Live: <https://0gora.temporalabs.com> · Built for the 0G Zero Cup.

Versioning uses `0.x.0` minor bumps for substantial changes during the tournament,
leading to a `1.0.0` final. Tags mark each release; the newest version is at the top.

## [Unreleased] — planned
- **0G Storage** for the corpus; on-chain settlement-tx link on the verification badge.
- **Community commons** (post-tournament) — open contribution, topic bins, on-chain attribution & rewards.

## [0.2.3] — 2026-06-23 — Multi-agora hosting + the ERC-8226 agora
### Added
- **Co-hosted agoras + in-app switcher.** One deployment can now serve **several agoras side by side** on a
  **single 0G wallet**. The chat (moved from `/0g` to **`/app`**) gains a **knowledge-base switcher** (labeled
  **0Gora**) to the left of the model picker; flipping it swaps the example questions + input placeholder and
  routes retrieval to that agora's corpus, clearing the conversation (a chat belongs to one corpus). The
  switcher hides itself when a deployment hosts only one agora — single-instance behavior is unchanged.
  - **Backend** resolves an `instance` per request to its **own Qdrant collection**, so co-hosted corpora
    never mix. Config is now a **registry**: `OGORA_INSTANCES` lists several `0gora.config.json` files (first
    = default); the prior single `OGORA_CONFIG` still works. New `id` / `collection` / `switcherLabel` config
    fields. New **`GET /instances`**; `GET /config`, `POST /chat`, `POST /search`, and `POST /contribute[/text]`
    accept `instance`.
  - **MCP** gains a **`list_agoras`** tool and an optional `instance` argument on `ask_0gora` /
    `search_0g_knowledge`, so agents can discover and target a specific co-hosted agora.
- **The ERC-8226 agora** — a verifiable public forum for [ERC-8226 (Regulated Agent Mandate)](https://github.com/ethereum/ERCs/blob/master/ERCS/erc-8226.md),
  corpus seeded from the ERC text + the [Ethereum Magicians thread](https://ethereum-magicians.org/t/erc-8226-regulated-agent-mandate).
  New [`examples/erc-8226/`](examples/erc-8226/) (standalone) and [`examples/multi/`](examples/multi/) (the
  production layout co-hosting it with the 0G agora). Answers still **generate + TEE-verify on 0G**.
- **App button** on the landing nav (top-right, right of Docs) → the chat.

### Changed
- **Brand is constant across co-hosted agoras.** When a deployment hosts more than one agora, the chat header
  and hero stay the **0Gora / ØGora** chrome regardless of which agora is selected — only the example bubbles
  and the input placeholder (e.g. *"Ask ERC-8226 0Gora…"*) change. A **single-agora** deployment (the "fork it,
  edit the config, deploy your own" path) still shows its **own** configured logo / tag / hero.

### Fixed
- **Landing route regression.** The chat moved to `app/chat/` served at `/app` via a Next rewrite, avoiding a
  literal `app/app/` route folder that broke the standalone build's root `/` (landing) route.
- `POST /contribute[/text]` echo the **resolved** instance id (default for an empty/unknown value), so a
  response can't report an agora the data didn't land in.

## [0.2.2] — 2026-06-23 — Voice, citations & a sharper KB
### Added
- **Clickable inline citations** — the `[n]` markers in answers link to their source
  (rendered as small superscript pills), ChatGPT/Perplexity-style. The source cards remain.
- **Self-hosted voice input (opt-in).** A `faster-whisper` STT service (`src/stt`, `POST
  /transcribe`); the web mic records via `MediaRecorder` and transcribes **on-box** — works
  in every browser (Brave/Firefox/Chrome/Safari) and the audio never leaves the stack
  (unlike the browser Web Speech API, which is Chrome-only and ships audio to Google). It is
  **OFF by default and profile-gated** (`profiles: ["voice"]`), so a default deploy builds
  and runs nothing voice-related — zero footprint. An instance opts in via `voice.enabled`
  in its config + the `voice` compose profile.
- **`Model` label** on the picker and a **"What is Auto model?"** example chip.
### Changed
- **Knowledge base.** Ingested 0Gora's own `/docs` (so the agora answers questions about
  itself, e.g. Auto routing) and declared `pc.0g.ai/models` as a corpus seed; **purged the
  stale, deleted `docs/MODELS.md` chunks** that were 404-citing and outranking the live
  per-model pages — model questions now cite `pc.0g.ai/models/<model>`.

## [0.2.1] — 2026-06-23 — Auto model routing
### Added
- **Auto model routing.** The model picker now defaults to **Auto**: the backend chooses the best 0G model
  per query (cheap/fast model for simple turns, a stronger or specialist model when the query needs it),
  then generates **and TEE-verifies** the answer on that model. A short line under each answer shows which
  model was routed to and why. Manual model pinning is still available.
  - **How it routes:** a free heuristic short-circuit (greeting / code / math / non-Latin script / very long)
    handles obvious queries; ambiguous ones get one short **unverified** classification call on the cheap
    router model (`0gm`). Routing is **config-driven** via the new `models` block in `0gora.config.json`
    (`auto` / `default` / `router` / `roster` with per-model lanes) — tune it without touching code.
  - **Never strands a query:** the router only chooses from the funded roster, and if a chosen provider is
    unavailable it cascades to the default model automatically.

## [0.2.0] — 2026-06-23 — Framework / example split
### Changed
- **0Gora is now a reusable framework.** The services moved under a single `src/` umbrella —
  `src/api` (RAG), `src/inference` (0G compute), `src/mcp` (agent surface), `src/webui` (Next.js),
  `src/deploy` (compose + nginx). Behavior-preserving: Docker service names are unchanged, so every
  compose-network reference still resolves.
### Added
- **Config-driven instances under `examples/`.** A deployment is now a small config folder that drives
  the framework — the shipped one is [`examples/0g/`](examples/0g/). `0gora.config.json` declares branding,
  example questions, seed corpus, and prompt overrides (committed, **secret-free**); `.env` holds only the
  wallet key + runtime toggles (gitignored). To found your own agora, copy the folder and edit config.
- **`GET /config`** — the backend serves the non-secret instance branding; the web UI renders whatever
  agora a deployment is configured for. System prompts are templated from the instance name + ecosystem.
- **Three ways to use 0Gora.** Beyond forking the repo: the **`0gora-mcp`** npm package (`npx 0gora-mcp`)
  connects any agent to a running 0Gora; **`create-0gora`** (`npm create 0gora@latest`) scaffolds a new
  instance from the framework; and an **agent skill** ([`src/skill/`](src/skill/)) teaches an agent to join
  an existing agora and found its own. (Packages are publish-ready; not yet published.)
### Fixed
- **Backend env wiring** — `CONTRIBUTE_KEY` and `RELEVANCE_THRESHOLD` are now passed to the backend
  container, so an `--env-file` value takes effect (the documented seed flow works). `seed.sh` fails fast
  on an HTTP error instead of silently reporting success.
### Removed
- **GitBook config** (`.gitbook.yaml`, `docs/SUMMARY.md`) — docs are served in-site at `/docs`.

## [0.1.5] — 2026-06-23 — The public square
### Added
- **Landing page** at `/` — explains 0Gora as a community-crowdsourced commons / public square of
  verifiable knowledge: *create any town square, for anything, for anyone — human or agent.* Agora hero
  with a staggered pop-in animation, a "Build your 0Gora today" GitHub CTA, and a docs CTA.
- **The chat moved to `/0g`** — reframed as the live example: the *0G 0Gora*, a knowledge base about 0G
  itself. The landing's "Open the 0G 0Gora app" button links to it.
- **GitBook-ready docs** — `docs/README.md` overview, `docs/SUMMARY.md`, and `.gitbook.yaml` so the docs
  can be rendered by a GitHub-synced GitBook. Social/OG preview image wired up.

## [0.1.4] — 2026-06-22 — Look & feel
### Added
- **Landing hero** — empty-state hero with the *agora* as a duotone purple/pink backdrop, the
  "Ask. Verify. Trust." value prop, and clickable example-prompt chips for a strong first impression.
- **Markdown rendering** for answers (`react-markdown` + `remark-gfm`) — headings, lists, tables, code
  blocks, and links now render properly instead of plain text.
- **Verification seal** — the small badge is now a prominent trust seal showing the TEE attestation,
  model, and chatID, so the thing that makes 0Gora different is celebrated, not hidden.
- "Built for agents too — connect over MCP" footer linking the agent surface.
- **General-knowledge fallback** — when the knowledge base has nothing relevant (top vector score below a
  threshold), 0Gora answers naturally from the model instead of replying "I don't have that information",
  so greetings and off-topic questions get a real reply. Grounded, cited answers still serve KB questions.
### Changed
- **Model lineup** — DeepSeek slot moved from `deepseek-chat-v3-0324` (DeepSeek-V3, being deprecated) to
  **`deepseek-v4-pro`**, DeepSeek's current TeeML-verified checkpoint on the broker. `docs/MODELS.md`
  refreshed with the rationale and the broader list of verifiable broker models.
- **Citations** — only sources the answer actually cites inline (`[n]`) are shown, so a refusal or a
  general-knowledge reply no longer displays unrelated retrieved passages.
- **Brand refresh** — gradient ØGora wordmark, 0G pink/purple palette, citation cards, sticky header,
  animated "Thinking on 0G…" state, and a mobile-responsive layout.
- **Mock-mode hardening** — the prod overlay pins `ZEROG_MOCK=false`, and the 0G service logs a loud
  warning if mock is ever enabled, so production can never silently serve unverified answers.

## [0.1.3] — 2026-06-22 — Agents, throughput, license
### Added
- **MCP service** (`mcp/`) — the agent-facing side of the *agora*. Exposes `ask_0gora`,
  `search_0g_knowledge`, and `list_models` over **two transports**: a local **stdio** server (for Claude
  Code et al.) and a **hosted remote endpoint** at `https://0gora.temporalabs.com/mcp` (Streamable HTTP —
  agents connect by URL, no local install). Dual-surface: humans → web, agents → MCP, same TEE-verified brain.
- Backend `/search` endpoint — raw hybrid retrieval (no LLM) powering the `search_0g_knowledge` tool.
- **Apache-2.0 license** (`LICENSE` + `NOTICE`) — explicit patent grant + liability disclaimer so anyone can
  adapt 0Gora into their own verifiable knowledge agora and commercialize it.
### Changed
- **Inference parallelization** — `chatCompletion` no longer serializes the whole call; only the
  nonce-bound broker steps (ack + `getRequestHeaders`, and each `processResponse` attempt) are serialized,
  while the slow LLM fetch + verify backoff run concurrently, so throughput scales with concurrency
  instead of one call at a time.

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
  (`@0glabs/0g-serving-broker`) with `processResponse` TEE verification (the core 0G piece).
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
