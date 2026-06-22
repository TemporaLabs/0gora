"""Hybrid retrieval (vector + BM25) — SCAFFOLD STUB (v0.1.0).

Implementation lands in a later version (task 0.6).
"""
from __future__ import annotations


def hybrid_search(query: str, k: int = 8) -> list[dict]:
    """Fuse vector (vectorstore.search) + BM25 (rank-bm25) → top-k chunks. TODO(0.6)."""
    raise NotImplementedError("retrieve.hybrid_search — implemented in v0.1.x")
