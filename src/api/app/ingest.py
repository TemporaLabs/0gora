"""Ingestion: URL/site/sitemap/text → clean → chunk → embed → upsert."""
from __future__ import annotations

import re
import uuid
from collections import deque
from urllib.parse import urljoin, urlparse

import httpx

from . import embed, vectorstore

UA = {"User-Agent": "0Gora/0.1 (+https://0gora.temporalabs.com)"}


def fetch(url: str) -> str:
    r = httpx.get(url, timeout=30, follow_redirects=True, headers=UA)
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


def _id(source: str, i: int) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source}#{i}"))


def _store(text: str, source: str, bin: str) -> int:
    chunks = chunk(text)
    if not chunks:
        return 0
    vecs = embed.embed(chunks)
    vectorstore.ensure_collection(embed.dim())
    points = [
        {"id": _id(source, i), "vector": v, "payload": {"text": ch, "url": source, "bin": bin}}
        for i, (ch, v) in enumerate(zip(chunks, vecs))
    ]
    vectorstore.upsert(points)
    return len(chunks)


def ingest_url(url: str, bin: str = "0g") -> int:
    return _store(clean(fetch(url)), url, bin)


def ingest_text(text: str, source: str = "paste", bin: str = "0g") -> int:
    """Ingest raw pasted text (e.g. an X post the crawler can't reach)."""
    return _store(text, source, bin)


def _prefix(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}{p.path.rstrip('/')}"


def _links(url: str, html: str) -> set[str]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    host = urlparse(url).netloc
    out: set[str] = set()
    for a in soup.find_all("a", href=True):
        u = urljoin(url, a["href"]).split("#")[0].rstrip("/")
        p = urlparse(u)
        if p.scheme in ("http", "https") and p.netloc == host:
            out.add(u)
    return out


def ingest_site(start_url: str, bin: str = "0g", max_pages: int = 40) -> dict:
    """Recursive crawl: follow same-host links under the start path; ingest each page."""
    prefix = _prefix(start_url)
    seen: set[str] = set()
    total = pages = 0
    q: deque[str] = deque([start_url.rstrip("/")])
    while q and pages < max_pages:
        u = q.popleft()
        if u in seen:
            continue
        seen.add(u)
        try:
            html = fetch(u)
        except Exception:
            continue
        pages += 1
        total += _store(clean(html), u, bin)
        for link in _links(u, html):
            if link not in seen and link.startswith(prefix):
                q.append(link)
    return {"pages": pages, "chunks": total}


def ingest_sitemap(sitemap_url: str, bin: str = "0g", max_pages: int = 80) -> dict:
    """Parse a sitemap.xml and ingest each listed URL."""
    try:
        xml = fetch(sitemap_url)
    except Exception:
        return {"pages": 0, "chunks": 0, "error": "sitemap fetch failed"}
    locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", xml)
    total = pages = 0
    for u in locs[:max_pages]:
        try:
            total += ingest_url(u.strip(), bin)
            pages += 1
        except Exception:
            continue
    return {"pages": pages, "chunks": total}
