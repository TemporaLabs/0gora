"""Client to the 0G compute service (the load-bearing 0G integration) — SCAFFOLD STUB (v0.1.0).

The 0G compute *service* (../zerog, Node) is already implemented. This is the backend-side
client that calls it. Wiring lands in task 0.7.
"""
from __future__ import annotations

import os

ZEROG_BASE = os.environ.get("ZEROG_BASE_URL", "http://zerog:8090/v1")


async def chat(messages: list[dict], model: str | None = None) -> dict:
    """POST messages to the 0G compute service → {answer, citations?, x_0g_verification}.
    TODO(0.7): httpx.post(f"{ZEROG_BASE}/chat/completions", json=...); read choices + x_0g_verification.
    """
    raise NotImplementedError("zerog.chat — implemented in v0.1.x")


async def models() -> list[str]:
    """List available 0G models from the service. TODO(0.7)."""
    raise NotImplementedError
