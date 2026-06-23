"""Embeddings — open-source bge/e5 via sentence-transformers (local, no external API)."""
from __future__ import annotations

import os
import threading

EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-small-en-v1.5")

_model = None
_model_lock = threading.Lock()


def load_model():
    """Thread-safe singleton. Lazy init must be guarded: concurrent cold-start
    requests racing to construct the SentenceTransformer corrupt the torch load
    ("Cannot copy out of meta tensor"). Double-checked locking serializes the load."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer

                _model = SentenceTransformer(EMBED_MODEL)
    return _model


def dim() -> int:
    return load_model().get_sentence_embedding_dimension()


def embed(texts: list[str]) -> list[list[float]]:
    """Embed documents → normalized vectors."""
    vecs = load_model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [v.tolist() for v in vecs]


def embed_query(text: str) -> list[float]:
    """Embed a single query. bge models retrieve best with a short query instruction."""
    q = f"Represent this sentence for searching relevant passages: {text}"
    return embed([q])[0]
