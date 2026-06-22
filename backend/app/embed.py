"""Embeddings — open-source bge/e5 via sentence-transformers (local, no external API)."""
from __future__ import annotations

import os
from functools import lru_cache

EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-small-en-v1.5")


@lru_cache(maxsize=1)
def load_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBED_MODEL)


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
