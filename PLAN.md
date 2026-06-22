# 0Gora — Project Plan

**0Gora — the community-crowdsourced knowledge commons.** An enterprise-grade RAG knowledge assistant whose AI
inference runs on **0G's decentralized, verifiable compute**, and whose knowledge base is **contributed, curated,
and owned by the community** (the *agora*) — not locked in a corporate silo.

Built for the **0G Zero Cup**.

## Why 0G is core to 0Gora
Every answer is **generated on 0G Compute and cryptographically verified inside a hardware TEE** via the 0G
serving broker (`processResponse`), surfaced as a **"Verified on 0G"** badge on each answer. Remove 0G and
0Gora literally cannot answer — and loses the verifiability guarantee that is its reason to exist. Later phases
deepen this: the knowledge corpus on **0G Storage**, contribution/attribution on **0G Chain**.

## Architecture (MVP: traditional RAG + 0G Compute; 0G Storage later)
```
Community contributors ─► Ingest ─► Chunk + Embed ─► Vector store (Qdrant/pgvector)
        │                                                   │
 Chat UI (Next.js) ─► Hybrid retrieval (vector + BM25) ─► Prompt ─┐
        ▲                                                          ▼
        │                       ┌───────────────────────────────────────────┐
        │                       │  GENERATION on 0G COMPUTE  ★ load-bearing   │
        │                       │  @0glabs/0g-serving-broker → TEE-verified   │
        │                       └───────────────────────────────────────────┘
        │                                                          │
        └────────────── Answer + citations + "Verified on 0G" ◄────┘
 (Phase 1) 0G Chain ◄── contribution & attribution ledger (credit on every cite)
```

## Stack (all open-source libraries)
Next.js · FastAPI · Qdrant or pgvector · sentence-transformers (bge/e5 embeddings) · rank-bm25 (hybrid retrieval)
· `@0glabs/0g-serving-broker` + ethers (0G Compute) · Docker Compose.

## The differentiator — community-crowdsourced knowledge
Most enterprise-search tools rely on private corporate connectors. 0Gora's edge is **open, attributed,
incentivized contribution**:
1. **Contribute** — a public "drop knowledge" flow (URL / GitHub repo / paste / file) with a live preview of how
   the content will be retrieved and cited.
2. **Bins** — community-owned topic collections (the agora's stalls).
3. **On-chain attribution** (Phase 1) — every contribution recorded on 0G Chain; contributors earn credit when
   their knowledge is cited; a contributor leaderboard, with token rewards to follow.
4. **Flagship bin = 0G itself** — seeded with 0G's docs, blog, and GitHub: **"Ask 0Gora anything about 0G."**

## Phases
- **Phase 0 — MVP:** ingest the 0G corpus → hybrid RAG → **0G-verified generation** → Next.js chat with citations
  + "Verified on 0G" badge → one public Contribute path → deploy → README + demo.
- **Phase 1:** 0G-Chain attribution ledger + contributor leaderboard; curation/upvotes; more ingest sources.
- **Phase 2:** community gamification; **migrate the knowledge corpus to 0G Storage** (more of the 0G stack).

## Verification / demo
- Ask *"What is 0G data availability?"* → grounded answer **with citations + a real "Verified on 0G" badge**.
- Show the **Contribute** flow (community adds a source → it becomes retrievable).
- **"Remove 0G → no brain"**: with 0G Compute disabled, 0Gora can't answer — proving 0G is load-bearing.

## Prior art / credits
Design influenced by [Onyx](https://github.com/onyx-dot-app/onyx) (MIT) and the broader RAG ecosystem.
**0Gora was created originally for the 0G Zero Cup** — its own code, composed from open-source libraries,
with 0G Compute as the substrate.
