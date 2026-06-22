"""0Gora backend — FastAPI RAG over 0G Compute.

Scaffold (Phase 0.1). The real ingestion/retrieval/generation land in tasks 0.5–0.7:
- app/ingest.py   — crawl URL -> clean -> chunk -> embed -> upsert (0.5)
- app/embed.py    — bge/e5 embeddings (0.4)
- app/retrieve.py — hybrid vector + BM25 (0.6)
- app/rag.py      — prompt + call 0G compute + citations (0.7)
"""
import os

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

ZEROG_BASE = os.environ.get("ZEROG_BASE_URL", "http://zerog:8090/v1")

app = FastAPI(title="0Gora", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "0gora-backend"}


@app.get("/models")
async def models():
    """Proxy the 0G model list (for the model picker)."""
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{ZEROG_BASE}/models")
        return r.json()


class ChatRequest(BaseModel):
    message: str
    model: str | None = None


@app.post("/chat")
async def chat(_req: ChatRequest):
    # TODO(0.6/0.7): hybrid retrieve -> build prompt with citations -> call 0G compute.
    return {"detail": "not yet implemented — RAG pipeline lands in tasks 0.5–0.7"}
