"""Ingestion: URL → clean text → chunks → embed → upsert — SCAFFOLD STUB (v0.1.0).

Implementation lands in a later version (task 0.5). This is the community-contribute
+ corpus-seeding entry point.
"""
from __future__ import annotations


def fetch(url: str) -> str:
    """Fetch a URL (recursive/site option later). TODO(0.5): httpx + crawl."""
    raise NotImplementedError("ingest.fetch — implemented in v0.1.x")


def clean(html: str) -> str:
    """Extract main text from HTML. TODO(0.5): trafilatura / bs4."""
    raise NotImplementedError


def chunk(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks. TODO(0.5)."""
    raise NotImplementedError


def ingest_url(url: str, bin: str = "0g") -> int:
    """fetch → clean → chunk → embed → upsert to vector store. Returns #chunks. TODO(0.5)."""
    raise NotImplementedError
