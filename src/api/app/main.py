"""0Gora backend — FastAPI RAG over 0G Compute."""
from __future__ import annotations

import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from . import ingest, rag, retrieve, zerog

app = FastAPI(title="0Gora", version="0.1.3")


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


@app.get("/models")
async def models():
    return {"models": await zerog.models()}


class ChatRequest(BaseModel):
    message: str
    model: str | None = None


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
        return await rag.answer(req.message, req.model)
    except Exception as exc:  # noqa: BLE001 — never surface a raw 500 to the UI
        return {"answer": _friendly_error(exc), "citations": [], "x_0g_verification": None, "error": str(exc)[:200]}


class SearchRequest(BaseModel):
    # Bounds are enforced server-side (not just in the MCP client) since /search is
    # a public endpoint reachable directly: cap k and query length to prevent abuse.
    query: str = Field(min_length=1, max_length=2000)
    k: int = Field(default=8, ge=1, le=20)


@app.post("/search")
async def search(req: SearchRequest):
    """Raw hybrid retrieval (no LLM) — returns the matching chunks + sources.
    Used by the MCP `search_0g_knowledge` tool so agents can read the corpus directly."""
    try:
        chunks = await run_in_threadpool(retrieve.hybrid_search, req.query, req.k)
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


@app.post("/contribute")
async def contribute(req: ContributeRequest, x_contribute_key: str | None = Header(default=None)):
    """Community contribute: ingest a URL (single page), a site (recursive crawl), or a sitemap."""
    _guard_contribute(x_contribute_key)
    if req.mode == "site":
        res = await run_in_threadpool(ingest.ingest_site, req.url, req.bin, req.max_pages)
    elif req.mode == "sitemap":
        res = await run_in_threadpool(ingest.ingest_sitemap, req.url, req.bin, req.max_pages)
    else:
        res = {"chunks": await run_in_threadpool(ingest.ingest_url, req.url, req.bin)}
    return {"url": req.url, "bin": req.bin, "mode": req.mode, **res}


class TextRequest(BaseModel):
    text: str
    source: str = "paste"
    bin: str = "0g"


@app.post("/contribute/text")
async def contribute_text(req: TextRequest, x_contribute_key: str | None = Header(default=None)):
    """Ingest pasted text (e.g. an X post the crawler can't reach)."""
    _guard_contribute(x_contribute_key)
    n = await run_in_threadpool(ingest.ingest_text, req.text, req.source, req.bin)
    return {"source": req.source, "chunks": n}
