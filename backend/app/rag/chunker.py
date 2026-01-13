from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    article_id: str
    title: str
    source: str
    text: str


def _clean_text(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"[ \t]+\n", "\n", s).strip()


def chunk_text(
    article_id: str,
    title: str,
    source: str,
    text: str,
    max_chars: int = 900,
    overlap: int = 180,
) -> List[Chunk]:
    text = _clean_text(text)
    if not text:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]

    chunks: List[str] = []
    buf = ""

    def flush() -> None:
        nonlocal buf
        if buf.strip():
            chunks.append(buf.strip())
        buf = ""

    for p in paragraphs:
        if len(p) > max_chars:
            sentences = re.split(r"(?<=[.!?])\s+", p)
            for sent in sentences:
                if not sent:
                    continue
                if len(buf) + len(sent) + 1 <= max_chars:
                    buf = (buf + " " + sent).strip()
                else:
                    flush()
                    buf = sent
        else:
            if len(buf) + len(p) + 2 <= max_chars:
                buf = (buf + "\n\n" + p).strip()
            else:
                flush()
                buf = p
    flush()

    final_chunks: List[Chunk] = []
    prev_tail = ""
    for i, c in enumerate(chunks):
        merged = (prev_tail + "\n\n" + c).strip() if prev_tail else c
        chunk_id = f"{article_id}:{i}"
        final_chunks.append(
            Chunk(
                chunk_id=chunk_id,
                article_id=article_id,
                title=title,
                source=source,
                text=merged,
            )
        )
        prev_tail = merged[-overlap:] if overlap > 0 and len(merged) > overlap else ""

    return final_chunks
