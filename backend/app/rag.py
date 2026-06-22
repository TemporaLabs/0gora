"""RAG orchestration: hybrid retrieve → prompt (with citations) → generate on 0G."""
from __future__ import annotations

from . import retrieve, zerog

SYSTEM = (
    "You are 0Gora, a knowledge assistant. Answer the question using ONLY the provided context. "
    "Cite sources inline as [n], matching the numbered context. If the context does not contain "
    "the answer, say you don't have that information."
)


def build_prompt(query: str, chunks: list[dict]) -> list[dict]:
    ctx = "\n\n".join(f"[{i + 1}] {c.get('text', '')}" for i, c in enumerate(chunks))
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {query}"},
    ]


async def answer(query: str, model: str | None = None) -> dict:
    chunks = retrieve.hybrid_search(query, k=8)
    res = await zerog.chat(build_prompt(query, chunks), model)
    citations = [
        {"n": i + 1, "url": c.get("url"), "bin": c.get("bin")} for i, c in enumerate(chunks)
    ]
    return {
        "answer": res["answer"],
        "citations": citations,
        "x_0g_verification": res["verification"],
    }
