"""Instance configuration for the 0Gora framework.

0Gora is a framework: one codebase that can run *any* verifiable knowledge agora.
What makes a given deployment about a specific topic — its name, branding, example
questions, seed corpus, and system prompts — is declared in an external JSON file
(see examples/0g/0gora.config.json), NOT baked into the code.

The path is taken from the OGORA_CONFIG env var (the example mounts the file at
/example/0gora.config.json). If it is unset or unreadable, we fall back to the
built-in defaults below — which mirror the shipped 0G example — so the framework
always runs and a missing mount degrades gracefully instead of blanking the app.

Secrets never appear here: the wallet key and runtime toggles come from the
environment (.env), never from this declarative config.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache

# Built-in defaults — mirror examples/0g/0gora.config.json so the framework behaves
# identically to the shipped 0G instance even when no config file is mounted.
# (corpus.seeds is intentionally empty here, unlike the example: the backend never
# reads it — seed.sh reads the config JSON directly — so the default needs no seeds.)
_DEFAULTS: dict = {
    "name": "0Gora",
    "logo": "ØGora",
    "instanceLabel": "the 0G agora · an example built on 0Gora",
    "ecosystem": "the 0G ecosystem",
    "hero": {
        "title": "ØGora",
        "lead": "Ask. Verify. Trust.",
        "sub": (
            "A marketplace of knowledge on 0G. Every answer is generated and "
            "cryptographically verified inside a 0G TEE — so you can trust where it came from."
        ),
    },
    "examples": [
        "What is 0G?",
        "What is 0G Storage?",
        "How does TEE verification work?",
        "Which models can I use?",
    ],
    "placeholder": "Ask 0Gora…",
    "corpus": {"seeds": []},
    "prompts": {"grounded": None, "chat": None},
}


def _deep_merge(base: dict, over: dict) -> dict:
    """Overlay `over` onto `base` recursively; keys absent in `over` keep the default.

    A malformed config must never break rendering: if the default for a key is a
    dict (e.g. `hero`) but the override supplies a non-dict, we KEEP the default
    rather than letting a scalar blank out a structured field downstream.
    """
    out = dict(base)
    for k, v in over.items():
        if k.startswith("$"):  # JSON-doc comment keys (e.g. "$comment") — ignore.
            continue
        default = out.get(k)
        if isinstance(default, dict):
            # Only merge when the override is also a dict; otherwise ignore the
            # type-mismatched value and keep the structured default.
            if isinstance(v, dict):
                out[k] = _deep_merge(default, v)
        elif v is not None:
            out[k] = v
    return out


@lru_cache(maxsize=1)
def load() -> dict:
    """Load the instance config (env path overlaid on defaults). Cached for the process."""
    path = os.getenv("OGORA_CONFIG", "").strip()
    if not path or not os.path.exists(path):
        return dict(_DEFAULTS)
    try:
        with open(path, encoding="utf-8") as f:
            user = json.load(f)
        return _deep_merge(_DEFAULTS, user if isinstance(user, dict) else {})
    except (OSError, ValueError):
        # Malformed config must not take the service down — fall back to defaults.
        return dict(_DEFAULTS)


def public() -> dict:
    """Non-secret instance config safe to expose to the browser (GET /config)."""
    c = load()
    return {
        "name": c["name"],
        "logo": c["logo"],
        "instanceLabel": c["instanceLabel"],
        "hero": c["hero"],
        "examples": c["examples"],
        "placeholder": c["placeholder"],
    }


def grounded_system() -> str:
    c = load()
    if c["prompts"].get("grounded"):
        return c["prompts"]["grounded"]
    return (
        f"You are {c['name']}, a knowledge assistant for {c['ecosystem']}. Use the numbered "
        "context passages to answer, citing facts inline as [n] to match the numbered context. "
        "If the context does not fully answer the question, supplement with your own general "
        "knowledge — but never attach a [n] citation to anything that is not in the context. "
        "Be helpful and concise; do not refuse outright."
    )


def chat_system() -> str:
    c = load()
    if c["prompts"].get("chat"):
        return c["prompts"]["chat"]
    return (
        f"You are {c['name']}, a helpful assistant for {c['ecosystem']} and general questions. "
        "The knowledge base has no relevant sources for this message, so answer naturally and "
        "concisely from your own general knowledge. Do not invent citations, sources, or [n] markers."
    )
