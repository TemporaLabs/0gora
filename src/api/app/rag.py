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

from . import config, retrieve, router, zerog

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


async def _resolve_target(query: str, model: str | None, has_context: bool, top_score: float):
    """Decide which model answers. Returns (target_model_or_None, routing_or_None).

    - A concrete pin (user picked a specific model) is honored exactly, no routing.
    - None / "auto" with auto routing enabled → router picks; routing dict is returned.
    - None / "auto" with routing disabled → None (let the sidecar use its own default),
      preserving the pre-v0.2.1 behavior.
    """
    if model not in (None, "auto"):
        return model, None
    if config.auto_enabled():
        routing = await router.choose(query, has_context=has_context, top_score=top_score)
        return routing["chosen"], routing
    return None, None


async def _generate(messages: list[dict], target: str | None, routing: dict | None) -> dict:
    """Generate on `target`, cascading to the configured default if the provider fails
    (e.g. an unfunded specialist 502s) — but only in auto mode, so an explicit user pin
    is never silently overridden. Updates `routing` to reflect the model that answered."""
    try:
        return await zerog.chat(messages, target)
    except Exception:  # noqa: BLE001 — provider/availability failure → try the safe default.
        default = config.default_model()
        if routing is not None and default and default != target:
            routing["chosen"] = default
            routing["reason"] = f"{routing.get('reason', '').strip()} · cascaded to default".strip(" ·")
            routing["via"] = "fallback"
            return await zerog.chat(messages, default)
        raise


async def answer(query: str, model: str | None = None) -> dict:
    chunks, top_score = retrieve.search_scored(query, k=8)
    has_context = bool(chunks) and top_score >= RELEVANCE_THRESHOLD

    target, routing = await _resolve_target(query, model, has_context, top_score)

    # Nothing relevant in the KB → plain LLM answer from general knowledge, no citations.
    messages = build_prompt(query, chunks) if has_context else build_chat_prompt(query)
    res = await _generate(messages, target, routing)

    out = {
        "answer": res["answer"],
        "citations": _cited(res["answer"], chunks) if has_context else [],
        "x_0g_verification": res["verification"],
    }
    if routing is not None:
        out["routing"] = {"chosen": routing["chosen"], "reason": routing["reason"], "via": routing["via"]}
    return out
