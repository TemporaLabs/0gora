"""Ingestion: URL → clean text → chunks → embed → upsert. Community-contribute + corpus seeding."""
from __future__ import annotations

import uuid

import httpx

from . import embed, vectorstore


def fetch(url: str) -> str:
    r = httpx.get(url, timeout=30, follow_redirects=True, headers={"User-Agent": "0Gora/0.1"})
    r.raise_for_status()
    return r.text


def clean(html: str) -> str:
    import trafilatura

    return trafilatura.extract(html) or ""


def chunk(text: str, size: int = 220, overlap: int = 40) -> list[str]:
    words = text.split()
    out, i = [], 0
    while i < len(words):
        piece = " ".join(words[i : i + size]).strip()
        if piece:
            out.append(piece)
        i += max(1, size - overlap)
    return out


def _id(url: str, i: int) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{url}#{i}"))


def ingest_url(url: str, bin: str = "0g") -> int:
    """fetch → clean → chunk → embed → upsert. Returns #chunks stored."""
    chunks = chunk(clean(fetch(url)))
    if not chunks:
        return 0
    vecs = embed.embed(chunks)
    vectorstore.ensure_collection(embed.dim())
    points = [
        {"id": _id(url, i), "vector": v, "payload": {"text": ch, "url": url, "bin": bin}}
        for i, (ch, v) in enumerate(zip(chunks, vecs))
    ]
    vectorstore.upsert(points)
    return len(chunks)
