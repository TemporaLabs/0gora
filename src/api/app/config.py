"""Instance configuration for the 0Gora framework.

0Gora is a framework: one codebase that can run *any* verifiable knowledge agora.
What makes a given deployment about a specific topic — its name, branding, example
questions, seed corpus, and system prompts — is declared in an external JSON file
(see examples/0g/0gora.config.json), NOT baked into the code.

A deployment can serve ONE agora or SEVERAL side by side (e.g. the 0G agora and an
ERC-8226 agora on the same host, behind one in-app switcher). Instances are declared
via env:
  • OGORA_INSTANCES — comma-separated config paths → a multi-instance deployment.
  • OGORA_CONFIG — a single config path (back-compat single-instance).
  • neither → the built-in 0G defaults as one instance.
The FIRST instance is the default (served when no/unknown `instance` is requested).
Each instance keeps its OWN Qdrant collection (its `collection` field, else
QDRANT_COLLECTION, else "0gora") so their corpora never mix. A missing/unreadable
mount degrades to the built-in defaults instead of blanking the app.

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
    # Auto model routing (v0.2.1). `auto` enables the "Auto" picker default; `default`
    # is the safe model used for the classifier fallback + cascade-on-failure; `router`
    # is the model that does the (unverified) classification. `roster` declares the
    # selectable models with their lanes — the router resolves strength tags against it.
    # This is POLICY; the routing engine is framework code (app/router.py). Model ids
    # must match the funded ZEROG_MODELS allowlist in .env.
    "models": {
        "auto": True,
        "default": "0gm",
        "router": "0gm",
        "roster": [
            {"id": "0gm", "tier": "fast", "strengths": ["general", "short", "greetings"]},
            {"id": "zai-org/GLM-5.1-FP8", "tier": "strong", "strengths": ["reasoning", "analysis"]},
            {"id": "deepseek-v4-pro", "tier": "strong", "strengths": ["code", "math", "logic"]},
            {"id": "qwen3.7-max", "tier": "large", "strengths": ["multilingual", "long-context"]},
        ],
    },
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


def _load_one(path: str) -> dict:
    """Load + merge a single instance config file onto the defaults."""
    if not path or not os.path.exists(path):
        return dict(_DEFAULTS)
    try:
        with open(path, encoding="utf-8") as f:
            user = json.load(f)
        return _deep_merge(_DEFAULTS, user if isinstance(user, dict) else {})
    except (OSError, ValueError):
        # Malformed config must not take the service down — fall back to defaults.
        return dict(_DEFAULTS)


def _slug_from_path(path: str) -> str:
    """Fallback instance id from the config's parent dir (examples/<slug>/0gora.config.json)."""
    return os.path.basename(os.path.dirname(path.rstrip("/"))) or ""


@lru_cache(maxsize=1)
def _registry() -> dict:
    """Build the instance registry: {id -> merged config}, plus an ordered id list under
    "__order__". The first id is the default. Cached for the process."""
    paths = [p.strip() for p in os.getenv("OGORA_INSTANCES", "").split(",") if p.strip()]
    if not paths:
        single = os.getenv("OGORA_CONFIG", "").strip()
        paths = [single] if single else []

    default_collection = os.getenv("QDRANT_COLLECTION", "0gora")
    reg: dict = {}
    order: list[str] = []
    for i, p in enumerate(paths):
        cfg = _load_one(p)
        iid = str(cfg.get("id") or "").strip() or _slug_from_path(p) or f"instance{i + 1}"
        cfg["_collection"] = str(cfg.get("collection") or default_collection).strip() or "0gora"
        if iid not in reg:
            order.append(iid)
        reg[iid] = cfg

    if not reg:  # no config mounted at all → built-in defaults as a single instance.
        cfg = dict(_DEFAULTS)
        cfg["_collection"] = default_collection
        reg["0g"] = cfg
        order = ["0g"]

    reg["__order__"] = order
    return reg


def _cfg(instance: str | None = None) -> dict:
    """Resolve an instance id to its config; None/unknown → the default (first) instance."""
    reg = _registry()
    if instance and instance != "__order__" and instance in reg:
        return reg[instance]
    return reg[reg["__order__"][0]]


def load(instance: str | None = None) -> dict:
    """The merged config for an instance (the default instance when unspecified)."""
    return _cfg(instance)


def default_instance() -> str:
    """Id of the default instance (the first declared)."""
    return _registry()["__order__"][0]


def instances() -> list[dict]:
    """The list the UI switcher renders: [{id, label}], in declared order."""
    reg = _registry()
    out: list[dict] = []
    for iid in reg["__order__"]:
        c = reg[iid]
        label = c.get("switcherLabel") or c.get("logo") or c.get("name") or iid
        out.append({"id": iid, "label": label})
    return out


def collection_for(instance: str | None = None) -> str:
    """The Qdrant collection that holds this instance's corpus."""
    return _cfg(instance).get("_collection", "0gora")


def public(instance: str | None = None) -> dict:
    """Non-secret instance config safe to expose to the browser (GET /config)."""
    c = _cfg(instance)
    return {
        "name": c["name"],
        "logo": c["logo"],
        "instanceLabel": c["instanceLabel"],
        "hero": c["hero"],
        "examples": c["examples"],
        "placeholder": c["placeholder"],
    }


def models_cfg(instance: str | None = None) -> dict:
    """The routing/model policy block (auto, default, router, roster). Never secret."""
    m = _cfg(instance).get("models")
    return m if isinstance(m, dict) else {}


def auto_enabled(instance: str | None = None) -> bool:
    return bool(models_cfg(instance).get("auto", False))


def default_model(instance: str | None = None) -> str:
    """Safe fallback model (classifier fallback + cascade target). '' = sidecar default."""
    return str(models_cfg(instance).get("default") or "")


def router_model(instance: str | None = None) -> str:
    """Model used for the (unverified) routing classification; defaults to default_model()."""
    return str(models_cfg(instance).get("router") or "") or default_model(instance)


def roster(instance: str | None = None) -> list[dict]:
    """Selectable models with their lanes; only well-formed entries with an id."""
    r = models_cfg(instance).get("roster")
    if not isinstance(r, list):
        return []
    return [m for m in r if isinstance(m, dict) and m.get("id")]


def grounded_system(instance: str | None = None) -> str:
    c = _cfg(instance)
    if c["prompts"].get("grounded"):
        return c["prompts"]["grounded"]
    return (
        f"You are {c['name']}, a knowledge assistant for {c['ecosystem']}. Use the numbered "
        "context passages to answer, citing facts inline as [n] to match the numbered context. "
        "If the context does not fully answer the question, supplement with your own general "
        "knowledge — but never attach a [n] citation to anything that is not in the context. "
        "Be helpful and concise; do not refuse outright."
    )


def chat_system(instance: str | None = None) -> str:
    c = _cfg(instance)
    if c["prompts"].get("chat"):
        return c["prompts"]["chat"]
    return (
        f"You are {c['name']}, a helpful assistant for {c['ecosystem']} and general questions. "
        "The knowledge base has no relevant sources for this message, so answer naturally and "
        "concisely from your own general knowledge. Do not invent citations, sources, or [n] markers."
    )
