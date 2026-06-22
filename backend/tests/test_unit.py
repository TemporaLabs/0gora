"""Unit tests for 0Gora backend pure logic (no network / no models needed).

Run inside the backend image:  pytest -q   (deps: pytest, fastapi TestClient)
"""
from __future__ import annotations

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
