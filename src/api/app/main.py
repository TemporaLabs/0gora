"""0Gora backend — FastAPI RAG over 0G Compute."""
from __future__ import annotations

import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from . import config, ingest, rag, retrieve, zerog

app = FastAPI(title="0Gora", version="0.2.0")


@app.on_event("startup")
async def _warmup() -> None:
    """Eagerly load the embedding model (single-threaded) before serving traffic,
    so concurrent cold-start requests never race the lazy load."""
    from . import embed

    await run_in_threadpool(embed.load_model)

# Contribution is locked by default: open ingestion is deferred until the
# contributor system exists. It is enabled only when CONTRIBUTE_KEY is set in
# the environment AND the caller presents it via the X-Contribute-Key header.
CONTRIBUTE_KEY = os.getenv("CONTRIBUTE_KEY", "")


def _guard_contribute(key: str | None) -> None:
    if not CONTRIBUTE_KEY or key != CONTRIBUTE_KEY:
        raise HTTPException(status_code=403, detail="Contribution is currently closed.")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "0gora-backend"}


@app.get("/instances")
async def instances():
    """The agoras this deployment serves, in order — feeds the in-app instance switcher.
    A single-instance deployment returns one entry; the UI then hides the switcher."""
    return {"instances": config.instances(), "default": config.default_instance()}


@app.get("/config")
async def instance_config(instance: str | None = None):
    """Public (secret-free) instance config — branding, examples, placeholder — so the
    web UI renders whatever agora this deployment is configured for. `instance` selects
    which agora (default when omitted/unknown). Driven by the mounted 0gora.config.json;
    falls back to the built-in 0G defaults."""
    return config.public(instance)


@app.get("/models")
async def models():
    # The model allowlist is the shared 0G sidecar's (one funded wallet serves every
    # agora), so it is instance-independent — the picker shows the same models throughout.
    return {"models": await zerog.models()}


class ChatRequest(BaseModel):
    message: str
    model: str | None = None
    instance: str | None = None


def _friendly_error(exc: Exception) -> str:
    """Turn an upstream 0G/provider failure into a user-facing message."""
    msg = str(exc)
    if "Sub-account" in msg or "InsufficientAvailableBalance" in msg or "depositFund" in msg:
        return (
            "⚠️ That model isn't available on 0G right now (its compute provider isn't "
            "funded yet). Try the default model — it's live and verified on 0G."
        )
    if "503" in msg or "not configured" in msg:
        return "⚠️ The 0G compute service is starting up. Please try again in a moment."
    return "⚠️ Couldn't get a verified answer from 0G just now. Please try again."


@app.post("/chat")
async def chat(req: ChatRequest):
    """Hybrid retrieve → prompt with citations → generate + verify on 0G."""
    if not req.message.strip():
        return {"answer": "Ask me a question about the knowledge base.", "citations": [], "x_0g_verification": None}
    try:
        return await rag.answer(req.message, req.model, req.instance)
    except Exception as exc:  # noqa: BLE001 — never surface a raw 500 to the UI
        return {"answer": _friendly_error(exc), "citations": [], "x_0g_verification": None, "error": str(exc)[:200]}


class SearchRequest(BaseModel):
    # Bounds are enforced server-side (not just in the MCP client) since /search is
    # a public endpoint reachable directly: cap k and query length to prevent abuse.
    query: str = Field(min_length=1, max_length=2000)
    k: int = Field(default=8, ge=1, le=20)
    instance: str | None = None  # which agora's corpus to search; None → default instance


@app.post("/search")
async def search(req: SearchRequest):
    """Raw hybrid retrieval (no LLM) — returns the matching chunks + sources.
    Used by the MCP `search_0g_knowledge` tool so agents can read the corpus directly.
    Scoped to the requested instance's collection so co-hosted agoras stay separate."""
    collection = config.collection_for(req.instance)
    try:
        chunks = await run_in_threadpool(retrieve.hybrid_search, req.query, req.k, collection)
    except Exception as exc:  # noqa: BLE001 — never surface a raw 500
        return {"query": req.query, "results": [], "error": str(exc)[:200]}
    return {
        "query": req.query,
        "results": [
            {"text": c.get("text", ""), "url": c.get("url"), "bin": c.get("bin")} for c in chunks
        ],
    }


class ContributeRequest(BaseModel):
    url: str
    bin: str = "0g"
    mode: str = "single"  # single | site | sitemap
    max_pages: int = 40
    # Which agora's corpus to ingest into (selects the Qdrant collection). Omitted =
    # the default instance — so a single-agora deployment needs no change.
    instance: str | None = None


@app.post("/contribute")
async def contribute(req: ContributeRequest, x_contribute_key: str | None = Header(default=None)):
    """Community contribute: ingest a URL (single page), a site (recursive crawl), or a sitemap."""
    _guard_contribute(x_contribute_key)
    collection = config.collection_for(req.instance)
    if req.mode == "site":
        res = await run_in_threadpool(ingest.ingest_site, req.url, req.bin, req.max_pages, collection)
    elif req.mode == "sitemap":
        res = await run_in_threadpool(ingest.ingest_sitemap, req.url, req.bin, req.max_pages, collection)
    else:
        res = {"chunks": await run_in_threadpool(ingest.ingest_url, req.url, req.bin, collection)}
    return {"url": req.url, "bin": req.bin, "mode": req.mode, "instance": req.instance or config.default_instance(), **res}


class TextRequest(BaseModel):
    text: str
    source: str = "paste"
    bin: str = "0g"
    instance: str | None = None


@app.post("/contribute/text")
async def contribute_text(req: TextRequest, x_contribute_key: str | None = Header(default=None)):
    """Ingest pasted text (e.g. an X post the crawler can't reach)."""
    _guard_contribute(x_contribute_key)
    collection = config.collection_for(req.instance)
    n = await run_in_threadpool(ingest.ingest_text, req.text, req.source, req.bin, collection)
    return {"source": req.source, "instance": req.instance or config.default_instance(), "chunks": n}
