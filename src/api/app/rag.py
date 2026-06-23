"""RAG orchestration: hybrid retrieve → prompt (with citations) → generate on 0G.

Relevance gate: we score the query against the corpus (top vector cosine). When
nothing is relevant (below RELEVANCE_THRESHOLD), we skip retrieval entirely and
let the model answer from its own general knowledge — so greetings and
off-topic questions get a natural reply instead of an "I don't have that
information" refusal. Relevant questions get a grounded answer; the grounded
prompt may still supplement with general knowledge rather than flatly refuse.
Citations returned are filtered to those the answer actually cites inline.
"""
from __future__ import annotations

import os
import re

from . import config, retrieve, zerog

# Top bge cosine below this → treat the corpus as having nothing relevant.
# bge cosines run compressed-high: ~0.47 unrelated, ~0.73+ on-topic, so ~0.70 separates.
RELEVANCE_THRESHOLD = float(os.environ.get("RELEVANCE_THRESHOLD", "0.70"))

# System prompts are templated from the instance config (name + ecosystem) so the
# same framework serves any agora; the 0G defaults live in config._DEFAULTS.


def build_prompt(query: str, chunks: list[dict]) -> list[dict]:
    ctx = "\n\n".join(f"[{i + 1}] {c.get('text', '')}" for i, c in enumerate(chunks))
    return [
        {"role": "system", "content": config.grounded_system()},
        {"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {query}"},
    ]


def build_chat_prompt(query: str) -> list[dict]:
    return [
        {"role": "system", "content": config.chat_system()},
        {"role": "user", "content": query},
    ]


def _cited(answer: str, chunks: list[dict]) -> list[dict]:
    """Only return citations the answer actually references inline as [n]."""
    used = {int(n) for n in re.findall(r"\[(\d+)\]", answer) if 1 <= int(n) <= len(chunks)}
    return [
        {"n": i + 1, "url": c.get("url"), "bin": c.get("bin")}
        for i, c in enumerate(chunks)
        if (i + 1) in used
    ]


async def answer(query: str, model: str | None = None) -> dict:
    chunks, top_score = retrieve.search_scored(query, k=8)

    # Nothing relevant in the KB → plain LLM answer from general knowledge, no citations.
    if not chunks or top_score < RELEVANCE_THRESHOLD:
        res = await zerog.chat(build_chat_prompt(query), model)
        return {"answer": res["answer"], "citations": [], "x_0g_verification": res["verification"]}

    res = await zerog.chat(build_prompt(query, chunks), model)
    return {
        "answer": res["answer"],
        "citations": _cited(res["answer"], chunks),
        "x_0g_verification": res["verification"],
    }
