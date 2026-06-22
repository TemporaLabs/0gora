"""Embeddings (open-source bge/e5 via sentence-transformers) — SCAFFOLD STUB (v0.1.0).

Implementation lands in a later version (task 0.4).
"""
from __future__ import annotations

import os

EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-small-en-v1.5")


def load_model():
    """Load + cache the embedding model. TODO(0.4): SentenceTransformer(EMBED_MODEL)."""
    raise NotImplementedError("embed.load_model — implemented in v0.1.x")


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts → list of vectors. TODO(0.4)."""
    raise NotImplementedError


def embed_query(text: str) -> list[float]:
    """Embed a single query (with the model's query prefix if needed). TODO(0.4)."""
    raise NotImplementedError
