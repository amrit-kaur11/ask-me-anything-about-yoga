from __future__ import annotations

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Add backend to path for imports (Render runs from /app)
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.api import router
from app.db import init_mongo, ensure_indexes
from app.rag.embedder import Embedder
from app.rag.retriever import Retriever
from app.rag.generator import from_env as generator_from_env
from app.rag.chunker import chunk_text, Chunk
from app.rag.index import get_chroma_client, get_collection, DEFAULT_COLLECTION
from app.index_utils import build_index_if_empty
import re  # For build

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def _load_env() -> None:
    candidates = [
        BACKEND_DIR / "storage" / ".env",
        BACKEND_DIR / ".env",
        Path(".env"),  # Fixed: Wrap in Path()
    ]
    for p in candidates:
        if p.exists():
            load_dotenv(p, override=False)
            logger.info(f"Loaded env from {p}")
            return
    logger.warning("No .env found")

def build_index_if_empty(retriever: Retriever, embedder: Embedder) -> None:
    """Auto-build Chroma if empty (runs once on startup)."""
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


def create_app() -> FastAPI:
    _load_env()

    app = FastAPI(title="AskMe AI - Yoga RAG")
    cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in cors_origins if o.strip()],
        allow_methods=["*"],
        allow_headers=["*"],
    )


    app.include_router(router, prefix="/api")

    # Health check endpoint (used by frontend)
    @app.get("/health")
    async def health():
        return {"ok": True}
    
    # FastAPI lifecycle hook
    @app.on_event("startup")
    async def startup():
        try:    
            mongo = init_mongo()
            await ensure_indexes(mongo)
            app.state.mongo = mongo
            logger.info("Mongo ready")

            # Embeddings
            sbert_model = os.getenv(
                "SBERT_MODEL", "sentence-transformers/paraphrase-MiniLM-L3-v2").strip()
            embedder = Embedder(sbert_model_name=sbert_model)
            # Pre-load model
            embedder.embed_texts(["Warmup embed"])
            app.state.embedder = embedder

            # Retriever
            index_dir = os.getenv("INDEX_DIR", os.path.join("backend", "storage"))
            top_k = int(os.getenv("TOP_K", "5"))
            retriever = Retriever(index_dir=index_dir, embedder=embedder, top_k=top_k)
            build_index_if_empty(retriever, embedder)
            app.state.retriever = retriever

            app.state.generator = generator_from_env()
            logger.info("Generator ready")
        except Exception as e:
            logger.error(f"Startup failed: {e}")
            raise

    # FastAPI lifecycle hook
    @app.on_event("shutdown")
    async def shutdown():
        app.state.mongo.client.close()

    return app


app = create_app()
