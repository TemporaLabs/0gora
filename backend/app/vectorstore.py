"""Vector store (Qdrant) wrapper — SCAFFOLD STUB (v0.1.0).

Implementation lands in a later version (task 0.3). Defines the interface only.
"""
from __future__ import annotations

import os

QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
COLLECTION = os.environ.get("QDRANT_COLLECTION", "0gora")


def client():
    """Return a Qdrant client. TODO(0.3): qdrant_client.QdrantClient(url=QDRANT_URL)."""
    raise NotImplementedError("vectorstore.client — implemented in v0.1.x")


def ensure_collection(dim: int) -> None:
    """Create the collection if missing (cosine, `dim`). TODO(0.3)."""
    raise NotImplementedError


def upsert(points: list[dict]) -> int:
    """Upsert {id, vector, payload} points. Returns count. TODO(0.3)."""
    raise NotImplementedError


def search(query_vector: list[float], k: int = 8) -> list[dict]:
    """Vector similarity search → top-k payloads with scores. TODO(0.3)."""
    raise NotImplementedError
