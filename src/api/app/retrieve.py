"""Hybrid retrieval: vector (Qdrant) + BM25, fused with Reciprocal Rank Fusion."""
from __future__ import annotations

from . import embed, vectorstore


def _rrf(rankings: list[list[dict]], kconst: int = 60) -> dict:
    scores: dict = {}
    for ranking in rankings:
        for rank, doc in enumerate(ranking):
            scores[doc["id"]] = scores.get(doc["id"], 0.0) + 1.0 / (kconst + rank)
    return scores


def search_scored(query: str, k: int = 8) -> tuple[list[dict], float]:
    """Hybrid retrieval that also returns the best vector cosine score, used to
    gauge whether the corpus actually has anything relevant to the query."""
    # Vector candidates (always carry a cosine `score`).
    vec_hits = vectorstore.search(embed.embed_query(query), k=k * 2)
    top_vector_score = max((h.get("score") or 0.0) for h in vec_hits) if vec_hits else 0.0

    # BM25 over the stored corpus
    corpus = vectorstore.scroll_all()
    bm25_hits: list[dict] = []
    if corpus:
        from rank_bm25 import BM25Okapi

        bm25 = BM25Okapi([d.get("text", "").lower().split() for d in corpus])
        scores = bm25.get_scores(query.lower().split())
        ranked = sorted(zip(corpus, scores), key=lambda x: x[1], reverse=True)
        bm25_hits = [d for d, _ in ranked[: k * 2]]

    # vec_hits last so the scored version of a doc wins on id collisions.
    by_id = {d["id"]: d for d in (bm25_hits + vec_hits)}
    fused = _rrf([vec_hits, bm25_hits])
    top = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:k]
    return [by_id[did] for did, _ in top], top_vector_score


def hybrid_search(query: str, k: int = 8) -> list[dict]:
    return search_scored(query, k)[0]
