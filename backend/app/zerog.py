"""Client to the 0G compute service (the load-bearing 0G integration)."""
from __future__ import annotations

import os

import httpx

ZEROG_BASE = os.environ.get("ZEROG_BASE_URL", "http://zerog:8090/v1")


async def chat(messages: list[dict], model: str | None = None) -> dict:
    """POST to the 0G compute service → {answer, verification}."""
    payload: dict = {"messages": messages, "stream": False}
    if model:
        payload["model"] = model
    async with httpx.AsyncClient(timeout=180) as c:
        r = await c.post(f"{ZEROG_BASE}/chat/completions", json=payload)
        r.raise_for_status()
        d = r.json()
    content = (d.get("choices") or [{}])[0].get("message", {}).get("content", "")
    return {"answer": content, "verification": d.get("x_0g_verification")}


async def models() -> list[str]:
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{ZEROG_BASE}/models")
        return [m["id"] for m in r.json().get("data", [])]
