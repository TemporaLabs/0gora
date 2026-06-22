"""0Gora backend — FastAPI RAG over 0G Compute."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from . import ingest, rag, zerog

app = FastAPI(title="0Gora", version="0.1.1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "0gora-backend"}


@app.get("/models")
async def models():
    return {"models": await zerog.models()}


class ChatRequest(BaseModel):
    message: str
    model: str | None = None


@app.post("/chat")
async def chat(req: ChatRequest):
    """Hybrid retrieve → prompt with citations → generate + verify on 0G."""
    return await rag.answer(req.message, req.model)


class ContributeRequest(BaseModel):
    url: str
    bin: str = "0g"


@app.post("/contribute")
async def contribute(req: ContributeRequest):
    """Community contribute: ingest a URL into the knowledge commons."""
    n = await run_in_threadpool(ingest.ingest_url, req.url, req.bin)
    return {"url": req.url, "bin": req.bin, "chunks": n}
