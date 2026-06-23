"""Unit tests for 0Gora backend pure logic (no network / no models needed).

Run inside the backend image:  pytest -q   (deps: pytest, fastapi TestClient)
"""
from __future__ import annotations

import json
import os

import pytest

from app import ingest, main, rag, retrieve


# ---- ingest.chunk ---------------------------------------------------------
def test_chunk_empty_is_empty():
    assert ingest.chunk("") == []
    assert ingest.chunk("   ") == []


def test_chunk_respects_size_and_overlap():
    words = " ".join(str(i) for i in range(500))
    chunks = ingest.chunk(words, size=220, overlap=40)
    assert len(chunks) >= 2
    # every chunk is non-empty and within the word budget
    for c in chunks:
        assert c.strip()
        assert len(c.split()) <= 220
    # overlap means consecutive chunks share words (stride = size - overlap = 180)
    assert chunks[0].split()[180] == chunks[1].split()[0]


def test_chunk_id_is_deterministic():
    assert ingest._id("https://x/y", 3) == ingest._id("https://x/y", 3)
    assert ingest._id("https://x/y", 3) != ingest._id("https://x/y", 4)


# ---- retrieve._rrf (reciprocal rank fusion) -------------------------------
def test_rrf_rewards_agreement():
    a = [{"id": "x"}, {"id": "y"}, {"id": "z"}]
    b = [{"id": "x"}, {"id": "w"}]
    scores = retrieve._rrf([a, b])
    # x is rank-0 in both lists → strictly highest fused score
    assert scores["x"] == max(scores.values())
    assert scores["x"] > scores["y"]


def test_rrf_empty():
    assert retrieve._rrf([[], []]) == {}


# ---- rag.build_prompt -----------------------------------------------------
def test_build_prompt_numbers_citations():
    msgs = rag.build_prompt("what is 0G?", [{"text": "alpha"}, {"text": "beta"}])
    assert msgs[0]["role"] == "system"
    assert msgs[1]["role"] == "user"
    assert "[1] alpha" in msgs[1]["content"]
    assert "[2] beta" in msgs[1]["content"]
    assert "Question: what is 0G?" in msgs[1]["content"]


# ---- main._friendly_error -------------------------------------------------
def test_friendly_error_unfunded_provider():
    msg = main._friendly_error(Exception("Sub-account not found. transfer-fund ..."))
    assert "isn't available" in msg and "default model" in msg


def test_friendly_error_generic():
    assert main._friendly_error(Exception("boom")).startswith("⚠️")


# ---- contribution guard (FastAPI) -----------------------------------------
def test_contribute_locked_without_key():
    from fastapi.testclient import TestClient

    client = TestClient(main.app)
    r = client.post("/contribute", json={"url": "https://example.com"})
    assert r.status_code == 403
    r2 = client.post("/contribute/text", json={"text": "hi"})
    assert r2.status_code == 403


def test_empty_message_short_circuits():
    from fastapi.testclient import TestClient

    client = TestClient(main.app)
    r = client.post("/chat", json={"message": "   "})
    assert r.status_code == 200
    assert r.json()["x_0g_verification"] is None


def test_search_bounds_enforced():
    """/search must reject out-of-range k and empty/oversized query (public endpoint)."""
    from fastapi.testclient import TestClient

    client = TestClient(main.app)
    assert client.post("/search", json={"query": "0g", "k": 0}).status_code == 422
    assert client.post("/search", json={"query": "0g", "k": 1000000}).status_code == 422
    assert client.post("/search", json={"query": "0g", "k": -5}).status_code == 422
    assert client.post("/search", json={"query": ""}).status_code == 422
    assert client.post("/search", json={"query": "x" * 5000}).status_code == 422


# ---- instance config (v0.2.0 config-driven framework) ---------------------
def test_config_public_exposes_no_secrets():
    from app import config

    config._registry.cache_clear()
    pub = config.public()
    assert set(pub) == {"name", "logo", "instanceLabel", "hero", "examples", "placeholder", "voice"}
    blob = json.dumps(pub).lower()
    for leaky in ("private", "wallet", "secret", "0x", "zerog_"):
        assert leaky not in blob, f"/config leaked '{leaky}': {pub}"


def test_config_defaults_match_shipped_example():
    """Guard against drift between config._DEFAULTS and examples/0g/0gora.config.json."""
    path = os.path.join(os.path.dirname(__file__), "../../../examples/0g/0gora.config.json")
    if not os.path.exists(path):
        pytest.skip("example config not in build context (runs in repo checkout / CI)")
    from app import config

    with open(path, encoding="utf-8") as f:
        ex = json.load(f)
    for k in ("name", "logo", "instanceLabel", "hero", "examples", "placeholder"):
        assert config._DEFAULTS[k] == ex[k], f"_DEFAULTS[{k}] drifted from the shipped example"


# ---- auto model routing (v0.2.1) ------------------------------------------
def _strip_comments(o):
    """Drop JSON-doc '$...' keys so a config block can be compared to _DEFAULTS."""
    if isinstance(o, dict):
        return {k: _strip_comments(v) for k, v in o.items() if not k.startswith("$")}
    if isinstance(o, list):
        return [_strip_comments(v) for v in o]
    return o


def test_models_block_matches_example():
    """The routing roster in _DEFAULTS must match the shipped example (minus $comments)."""
    path = os.path.join(os.path.dirname(__file__), "../../../examples/0g/0gora.config.json")
    if not os.path.exists(path):
        pytest.skip("example config not in build context")
    from app import config

    with open(path, encoding="utf-8") as f:
        ex = json.load(f)
    assert config._DEFAULTS["models"] == _strip_comments(ex["models"])


def test_config_models_accessors():
    from app import config

    config._registry.cache_clear()
    assert config.auto_enabled() is True
    assert config.default_model() == "0gm"
    assert config.router_model() == "0gm"
    roster = config.roster()
    assert [m["id"] for m in roster] == ["0gm", "zai-org/GLM-5.1-FP8", "deepseek-v4-pro", "qwen3.7-max"]


def test_config_models_does_not_leak_to_browser():
    """The routing block stays backend-only — /config must not grow a 'models' key."""
    from app import config

    config._registry.cache_clear()
    assert "models" not in config.public()


def test_router_heuristic_tags():
    from app import router

    assert router.heuristic_tag("hi there") == "general"
    assert router.heuristic_tag("```python\nprint(1)\n```") == "code"
    assert router.heuristic_tag("def foo(x): return x") == "code"
    assert router.heuristic_tag("What is the integral of x^2?") == "math"
    assert router.heuristic_tag("これは何ですか") == "multilingual"
    # An ordinary general question is ambiguous → defer to the classifier.
    assert router.heuristic_tag("Tell me about the history of trade routes") is None


def test_router_by_strength_maps_tags_to_roster():
    from app import config, router

    config._registry.cache_clear()
    roster = config.roster()
    assert router._by_strength("code", roster, "0gm") == "deepseek-v4-pro"
    assert router._by_strength("multilingual", roster, "0gm") == "qwen3.7-max"
    assert router._by_strength("general", roster, "fallback-id") == "0gm"
    # Unknown tag → the default.
    assert router._by_strength("nonsense", roster, "fallback-id") == "fallback-id"


def test_router_parse_choice():
    from app import router

    ids = ["0gm", "deepseek-v4-pro"]
    assert router.parse_choice('{"model": "deepseek-v4-pro", "reason": "code"}', ids) == ("deepseek-v4-pro", "code")
    # Surrounding prose is tolerated.
    assert router.parse_choice('ok {"model":"0gm","reason":"simple"} done', ids)[0] == "0gm"
    # A model not in the roster is rejected (would 404 on the broker).
    assert router.parse_choice('{"model": "gpt-4"}', ids) == (None, "")
    assert router.parse_choice("not json at all", ids) == (None, "")


def test_router_choose_heuristic_no_network():
    import asyncio

    from app import config, router

    config._registry.cache_clear()
    out = asyncio.run(router.choose("def add(a, b): return a + b", has_context=False, top_score=0.1))
    assert out["chosen"] == "deepseek-v4-pro"
    assert out["via"] == "heuristic"


def test_router_choose_classifier_unverified(monkeypatch):
    import asyncio

    from app import config, router

    config._registry.cache_clear()
    calls = {}

    async def fake_chat(messages, model=None, *, verify=True, max_tokens=None):
        calls["verify"] = verify
        calls["model"] = model
        return {"answer": '{"model": "deepseek-v4-pro", "reason": "needs reasoning"}', "verification": None}

    monkeypatch.setattr(router.zerog, "chat", fake_chat)
    out = asyncio.run(router.choose("Compare two consensus designs", has_context=False, top_score=0.1))
    assert out["chosen"] == "deepseek-v4-pro"
    assert out["via"] == "classifier"
    assert calls["verify"] is False  # routing call must skip TEE attestation
    assert calls["model"] == "0gm"   # ...and run on the cheap router model


def test_router_choose_falls_back_on_bad_classifier(monkeypatch):
    import asyncio

    from app import config, router

    config._registry.cache_clear()

    async def boom(messages, model=None, *, verify=True, max_tokens=None):
        raise RuntimeError("router model unavailable")

    monkeypatch.setattr(router.zerog, "chat", boom)
    out = asyncio.run(router.choose("Compare two consensus designs", has_context=False, top_score=0.1))
    assert out["chosen"] == "0gm"  # default
    assert out["via"] == "fallback"


def test_rag_cascades_to_default_on_provider_failure(monkeypatch):
    """In auto mode, a provider failure on the chosen model retries the default."""
    import asyncio

    import httpx

    from app import config, rag

    config._registry.cache_clear()
    seen = []

    async def fake_chat(messages, model=None, *, verify=True, max_tokens=None):
        seen.append(model)
        if model == "deepseek-v4-pro":
            # Real provider/availability failures surface as httpx errors (sidecar 5xx;
            # zerog.chat raise_for_status). Only these trigger the cascade now.
            raise httpx.ConnectError("provider unavailable")
        return {"answer": "ok", "verification": {"verified": True, "model": model}}

    async def fake_choose(query, *, has_context, top_score, instance=None):
        return {"chosen": "deepseek-v4-pro", "reason": "code query", "via": "heuristic"}

    monkeypatch.setattr(rag.zerog, "chat", fake_chat)
    monkeypatch.setattr(rag.router, "choose", fake_choose)
    monkeypatch.setattr(rag.retrieve, "search_scored", lambda q, k=8, collection=None: ([], 0.0))

    out = asyncio.run(rag.answer("def f(): pass", model="auto"))
    assert seen == ["deepseek-v4-pro", "0gm"]          # tried specialist, then cascaded
    assert out["routing"]["chosen"] == "0gm"
    assert "cascaded" in out["routing"]["reason"]


def test_config_malformed_value_keeps_structured_default(tmp_path):
    """A non-dict 'hero' in a user config must not blank the structured default (page would render an empty <h1>)."""
    from app import config

    bad = tmp_path / "bad.json"
    bad.write_text('{"hero": "oops", "name": "Custom"}')
    config._registry.cache_clear()
    os.environ["OGORA_CONFIG"] = str(bad)
    try:
        c = config.load()
        assert isinstance(c["hero"], dict) and "title" in c["hero"]  # default kept, not blanked
        assert c["name"] == "Custom"  # well-typed scalar override still applied
    finally:
        os.environ.pop("OGORA_CONFIG", None)
        config._registry.cache_clear()


def test_embed_model_load_is_thread_safe():
    """Concurrent cold-start loads must not race (regression: torch meta-tensor crash)."""
    import threading

    from app import embed

    embed._model = None  # force cold
    results, errors = [], []

    def go():
        try:
            results.append(embed.load_model())
        except Exception as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=go) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"concurrent load raised: {errors}"
    assert len({id(m) for m in results}) == 1  # all threads got the same single instance
