# backend/app/index_utils.py
from typing import Any
import logging
import os
from pathlib import Path
import re

# Import helpers from the rag package.  We perform these imports
# lazily to avoid circular dependencies and to ensure the functions are
# available when building a new index.  The relative imports assume
# that this file lives inside the `app` package.
from app.rag.retriever import Retriever
from app.rag.embedder import Embedder
from app.rag.chunker import chunk_text, Chunk
from app.rag.index import get_chroma_client, get_collection

logger = logging.getLogger(__name__)
DEFAULT_COLLECTION = "yoga_chunks"

# Determine the backend directory relative to this file.  When this
# module is packaged under `backend/app`, two parents up from this file
# corresponds to the `backend` directory.  We compute it here to avoid
# importing from main.py, which would introduce a circular import.
BACKEND_DIR = Path(__file__).resolve().parent.parent

def build_index_if_empty(retriever: Retriever, embedder: Embedder) -> None:
    """Auto-build Chroma index if empty."""
    try:
        count = retriever.collection.count()
        if count > 0:
            logger.info(f"Index exists: {count} chunks")
            return

        logger.info("Building index...")
        ARTICLES_DIR = BACKEND_DIR / "data" / "articles"
        YOGA_TXT = BACKEND_DIR / "data" / "yoga_docs.txt"
        ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

        # Ensure articles from yoga_docs.txt if empty
        md_files = list(ARTICLES_DIR.glob("*.md"))
        if not md_files and YOGA_TXT.exists():
            raw = YOGA_TXT.read_text(encoding="utf-8", errors="ignore").strip()
            if raw:
                parts = re.split(r"\n(?=# )", raw)
                parts = [p.strip() for p in parts if p.strip()] or re.split(r"\n-{3,}\n", raw)
                parts = [p.strip() for p in parts if p.strip()][:50]
                for i, part in enumerate(parts, 1):
                    title = re.match(r"#\s+(.*)\n", part).group(1).strip() if re.match(r"#\s+", part) else f"Yoga Note {i}"
                    content = f"# {title}\n\nSource: (add citation link)\n\n{part}\n"
                    (ARTICLES_DIR / f"article_{i:02d}.md").write_text(content, encoding="utf-8")

        # Chunk & embed
        chunks: list[Chunk] = []
        for md_path in sorted(ARTICLES_DIR.glob("*.md")):
            article_id = md_path.stem
            text = md_path.read_text(encoding="utf-8", errors="ignore").strip()
            title = md_path.stem
            source = ""
            for line in text.splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
                if line.lower().startswith("source:"):
                    source = line.split(":", 1)[1].strip()
                    break
            chunks.extend(chunk_text(article_id=article_id, title=title, source=source, text=text, max_chars=900, overlap=180))

        if not chunks:
            logger.warning("No chunks to index")
            return

        texts = [c.text for c in chunks]
        embs = embedder.embed_texts(texts)

        # Reset & add
        client = get_chroma_client(retriever.persist_dir)
        try:
            client.delete_collection(DEFAULT_COLLECTION)
        except:
            pass
        collection = get_collection(client, DEFAULT_COLLECTION)
        collection.add(
            ids=[c.chunk_id for c in chunks],
            documents=texts,
            metadatas=[{"article_id": c.article_id, "title": c.title, "source": c.source} for c in chunks],
            embeddings=embs.astype(float).tolist(),
        )
        logger.info(f"Built index: {len(chunks)} chunks in {retriever.persist_dir}")
    except Exception as e:
        logger.error(f"Index build failed: {e}")