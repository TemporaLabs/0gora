"""Hybrid retrieval: vector (Qdrant) + BM25, fused with Reciprocal Rank Fusion."""
from __future__ import annotations

from . import embed, vectorstore


def _rrf(rankings: list[list[dict]], kconst: int = 60) -> dict:
    scores: dict = {}
    for ranking in rankings:
        for rank, doc in enumerate(ranking):
            scores[doc["id"]] = scores.get(doc["id"], 0.0) + 1.0 / (kconst + rank)
    return scores


def hybrid_search(query: str, k: int = 8) -> list[dict]:
    # Vector candidates
    vec_hits = vectorstore.search(embed.embed_query(query), k=k * 2)

    # BM25 over the stored corpus
    corpus = vectorstore.scroll_all()
    bm25_hits: list[dict] = []
    if corpus:
        from rank_bm25 import BM25Okapi

        bm25 = BM25Okapi([d.get("text", "").lower().split() for d in corpus])
        scores = bm25.get_scores(query.lower().split())
        ranked = sorted(zip(corpus, scores), key=lambda x: x[1], reverse=True)
        bm25_hits = [d for d, _ in ranked[: k * 2]]

    by_id = {d["id"]: d for d in (vec_hits + bm25_hits)}
    fused = _rrf([vec_hits, bm25_hits])
    top = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:k]
    return [by_id[did] for did, _ in top]
