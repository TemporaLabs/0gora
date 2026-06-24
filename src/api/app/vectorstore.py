"""Vector store (Qdrant) wrapper."""
from __future__ import annotations

import os
from functools import lru_cache

QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
COLLECTION = os.environ.get("QDRANT_COLLECTION", "0gora")


@lru_cache(maxsize=1)
def client():
    from qdrant_client import QdrantClient

    return QdrantClient(url=QDRANT_URL)


# All ops take an optional `collection`: a deployment can host several agoras, each
# with its own collection (resolved per-request from the instance). None = the
# process default (QDRANT_COLLECTION), preserving single-instance behavior.


def ensure_collection(dim: int, collection: str | None = None) -> None:
    from qdrant_client.models import Distance, VectorParams

    coll = collection or COLLECTION
    c = client()
    if not c.collection_exists(coll):
        c.create_collection(
            coll, vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
        )


def upsert(points: list[dict], collection: str | None = None) -> int:
    """points: [{id, vector, payload}]"""
    from qdrant_client.models import PointStruct

    c = client()
    c.upsert(
        collection or COLLECTION,
        points=[PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"]) for p in points],
    )
    return len(points)


def search(query_vector: list[float], k: int = 8, collection: str | None = None) -> list[dict]:
    coll = collection or COLLECTION
    c = client()
    # A never-seeded instance has no collection yet — return empty rather than 500.
    if not c.collection_exists(coll):
        return []
    hits = c.search(coll, query_vector=query_vector, limit=k, with_payload=True)
    return [{"id": h.id, "score": h.score, **(h.payload or {})} for h in hits]


def scroll_all(limit: int = 5000, collection: str | None = None) -> list[dict]:
    """All stored chunks (for the BM25 corpus). Fine for an MVP-sized corpus."""
    coll = collection or COLLECTION
    c = client()
    if not c.collection_exists(coll):
        return []
    out: list[dict] = []
    offset = None
    while True:
        pts, offset = c.scroll(coll, limit=256, offset=offset, with_payload=True)
        out.extend({"id": p.id, **(p.payload or {})} for p in pts)
        if offset is None or len(out) >= limit:
            break
    return out
