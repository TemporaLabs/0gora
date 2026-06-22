"""RAG orchestration: retrieve → prompt (with citations) → 0G generation — SCAFFOLD STUB (v0.1.0).

Implementation lands in a later version (task 0.7). Ties retrieve.py + zerog.py together.
"""
from __future__ import annotations


def build_prompt(query: str, chunks: list[dict]) -> list[dict]:
    """Assemble chat messages: system + retrieved context (numbered for citations) + query. TODO(0.7)."""
    raise NotImplementedError("rag.build_prompt — implemented in v0.1.x")


async def answer(query: str, model: str | None = None) -> dict:
    """hybrid_search → build_prompt → zerog.chat → {answer, citations, x_0g_verification}. TODO(0.7)."""
    raise NotImplementedError
