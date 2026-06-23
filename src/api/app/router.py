"""Auto model routing (v0.2.1).

Picks the best 0G model for a query — the OpusPlus analogy: cheap/fast model for
easy turns, a stronger or specialist model for hard ones. The chosen model still
generates + TEE-verifies the answer on 0G; only the *choice* is automated, so the
routing decision itself does not need verification.

Two layers, cheapest first:
  1. HEURISTIC short-circuit — obvious queries (greeting, code fence, math symbols,
     non-Latin script, very long) route by rule with ZERO extra model calls.
  2. LLM CLASSIFIER — for ambiguous queries, one short *unverified* call on the
     configured router model (default `0gm`, the most reliably-funded model) returns
     the best model id.
Both resolve only to ids in the configured roster; true availability is handled by
the caller's cascade-to-default on a provider error (see rag._generate).

Routing POLICY (roster, default, router model) lives in 0gora.config.json; this
ENGINE is framework code. A founder tunes routing by editing config, no code change.
"""
from __future__ import annotations

import json
import re

from . import config, zerog

# Heuristic signals → a strength tag. We resolve the tag to whichever roster model
# advertises that strength, so the rules stay config-driven (never hardcode model ids).
_GREETING = re.compile(r"^(hi|hello|hey|yo|gm|thanks|thank you|sup|howdy)\b", re.I)
_CODE = re.compile(
    r"```|\bdef \w+\(|\bfunction \w*\(|\bclass \w+\b|=>|console\.log|\bimport \w|"
    r"\bSELECT\b.+\bFROM\b|</\w+>|\bpublic static\b|#include\b",
    re.I,
)
_MATH = re.compile(r"[∫∑√π≤≥≠±∞]|\b(integral|derivative|theorem|prove that|eigen|factorial|matrix|equation)\b", re.I)


def _nonlatin_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    nonlatin = sum(1 for c in letters if ord(c) > 0x024F)  # beyond Latin Extended-A/B
    return nonlatin / len(letters)


def heuristic_tag(query: str) -> str | None:
    """Confident, high-precision routing signal, or None to defer to the classifier."""
    q = query.strip()
    if not q:
        return "general"
    words = q.split()
    if len(words) <= 4 and _GREETING.match(q):
        return "general"
    if _CODE.search(q):
        return "code"
    if _MATH.search(q):
        return "math"
    if _nonlatin_ratio(q) > 0.20:
        return "multilingual"
    if len(words) > 400:
        return "long-context"
    return None


def _by_strength(tag: str, roster: list[dict], default: str) -> str:
    """First roster model that advertises `tag` as a strength; else the default."""
    for m in roster:
        if tag in (m.get("strengths") or []):
            return m["id"]
    return default


def _classify_messages(query: str, roster: list[dict]) -> list[dict]:
    lines = "\n".join(
        f"- {m['id']} — {', '.join(m.get('strengths') or []) or 'general'} ({m.get('tier', 'general')} tier)"
        for m in roster
    )
    system = (
        "You are a fast routing classifier for a verifiable-RAG assistant. Given a user "
        "query, pick the single best model to answer it from the list. Prefer the fast/cheap "
        "model for simple or general questions; use a stronger or specialist model only when "
        "the query clearly needs it (code, math, multilingual, long/complex reasoning). "
        'Reply with ONLY a JSON object: {"model": "<exact id>", "reason": "<=6 words"}.\n'
        f"Models:\n{lines}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": query.strip()[:600]},
    ]


def parse_choice(text: str, valid_ids: list[str]) -> tuple[str | None, str]:
    """Extract {"model","reason"} from the classifier output; validate against the roster."""
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None, ""
    try:
        obj = json.loads(m.group(0))
    except (ValueError, TypeError):
        return None, ""
    chosen = obj.get("model")
    if chosen in valid_ids:
        reason = str(obj.get("reason") or "").strip()[:60]
        return chosen, reason
    return None, ""


async def choose(query: str, *, has_context: bool, top_score: float) -> dict:
    """Return {"chosen": id, "reason": str, "via": heuristic|classifier|fallback}.

    `has_context`/`top_score` are passed for future use (grounded RAG vs general chat
    is a meaningful, free routing signal) and to keep the call site stable.
    """
    roster = config.roster()
    default = config.default_model()
    ids = [m["id"] for m in roster] or ([default] if default else [])

    if not ids:  # no roster configured → let the sidecar default decide
        return {"chosen": default, "reason": "no roster", "via": "fallback"}

    # 1. Heuristic — free.
    tag = heuristic_tag(query)
    if tag:
        return {"chosen": _by_strength(tag, roster, default or ids[0]), "reason": f"{tag} query", "via": "heuristic"}

    # 2. Classifier — one short, unverified call on the cheap router model.
    try:
        res = await zerog.chat(
            _classify_messages(query, roster),
            model=config.router_model() or default,
            verify=False,
            max_tokens=80,
        )
        chosen, reason = parse_choice(res.get("answer", ""), ids)
        if chosen:
            return {"chosen": chosen, "reason": reason or "model-selected", "via": "classifier"}
    except Exception:  # noqa: BLE001 — routing must never break the answer; fall back.
        pass

    # 3. Fallback — the safe default.
    return {"chosen": default or ids[0], "reason": "default", "via": "fallback"}
