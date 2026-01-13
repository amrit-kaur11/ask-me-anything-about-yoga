from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv

# --- Fix import path so `from app...` works when running as a script ---
BACKEND_DIR = Path(__file__).resolve().parents[1]  # .../backend
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.chunker import chunk_text, Chunk
from app.rag.embedder import Embedder
from app.rag.index import get_chroma_client, get_collection, DEFAULT_COLLECTION

ROOT = BACKEND_DIR.parent  # repo root
ARTICLES_DIR = BACKEND_DIR / "data" / "articles"
YOGA_TXT = BACKEND_DIR / "data" / "yoga_docs.txt"


def load_env() -> None:
    candidates = [
        BACKEND_DIR / "storage" / ".env",
        BACKEND_DIR / ".env",
        ROOT / ".env",
    ]
    for p in candidates:
        if p.exists():
            load_dotenv(p, override=False)
            return


def ensure_articles_exist() -> None:
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    md_files = list(ARTICLES_DIR.glob("*.md"))
    if md_files:
        return

    if not YOGA_TXT.exists():
        raise FileNotFoundError(f"No articles found and missing {YOGA_TXT}")

    raw = YOGA_TXT.read_text(encoding="utf-8", errors="ignore").strip()
    if not raw:
        raise ValueError("yoga_docs.txt is empty")

    parts = re.split(r"\n(?=# )", raw)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) <= 1:
        parts = re.split(r"\n-{3,}\n", raw)
        parts = [p.strip() for p in parts if p.strip()]

    for i, part in enumerate(parts[:50], start=1):
        title = f"Yoga Note {i}"
        m = re.match(r"#\s+(.*)\n", part)
        if m:
            title = m.group(1).strip()

        content = f"# {title}\n\nSource: (add citation link)\n\n{part}\n"
        (ARTICLES_DIR / f"article_{i:02d}.md").write_text(content, encoding="utf-8")


def parse_markdown_article(path: Path) -> Tuple[str, str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    title = path.stem
    source = ""

    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    for line in text.splitlines():
        if line.lower().startswith("source:"):
            source = line.split(":", 1)[1].strip()
            break

    return title, source, text


def main() -> None:
    load_env()
    ensure_articles_exist()

    sbert_model = os.getenv("SBERT_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    embedder = Embedder(sbert_model_name=sbert_model)

    chunks: List[Chunk] = []
    for md_path in sorted(ARTICLES_DIR.glob("*.md")):
        article_id = md_path.stem
        title, source, body = parse_markdown_article(md_path)
        chunks.extend(
            chunk_text(
                article_id=article_id,
                title=title,
                source=source,
                text=body,
                max_chars=900,
                overlap=180,
            )
        )

    texts = [c.text for c in chunks]
    embs = embedder.embed_texts(texts)

    persist_dir = os.getenv("INDEX_DIR", str(BACKEND_DIR / "storage" / "chroma"))
    client = get_chroma_client(persist_dir)

    # Reset collection to avoid duplicates
    try:
        client.delete_collection(DEFAULT_COLLECTION)
    except Exception:
        pass

    collection = get_collection(client, DEFAULT_COLLECTION)

    collection.add(
        ids=[c.chunk_id for c in chunks],
        documents=[c.text for c in chunks],
        metadatas=[{"article_id": c.article_id, "title": c.title, "source": c.source} for c in chunks],
        embeddings=embs.astype(float).tolist(),
    )

    print(f"Built Chroma store with {len(chunks)} chunks")
    print(f"Persisted to: {persist_dir}")


if __name__ == "__main__":
    main()
