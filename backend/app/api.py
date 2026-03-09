from __future__ import annotations

import os
import time
import uuid
import traceback
from pathlib import Path
from typing import List, Literal, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# Load env if needed
load_dotenv(Path(__file__).resolve().parents[1] / "storage" / ".env")

from app.db import Mongo, attach_feedback, log_request, utc_now
from app.safety import check_safety, unsafe_response_text
from app.rag.embedder import Embedder
# Prefer relative imports within the `app` package.  Using a relative
# import here avoids confusion in some IDEs and keeps all modules
# consistently resolved from the package root.
from .index_utils import build_index_if_empty
from app.rag.retriever import Retriever, RetrievedChunk
from app.rag.generator import Generator

router = APIRouter()

# -------------------------
# Request / Response Models
# -------------------------

class AskRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)


class SourceItem(BaseModel):
    chunk_id: str
    title: str
    article_id: str
    source: str
    score: float


class AskResponse(BaseModel):
    request_id: str
    is_unsafe: bool
    safety_reasons: List[str]
    answer: str
    sources: List[SourceItem]


class FeedbackRequest(BaseModel):
    request_id: str
    rating: Literal["up", "down"]
    comment: Optional[str] = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    ok: bool = True


# -------------------------
# Dependency helpers
# -------------------------

def get_mongo(request: Request) -> Mongo:
    return request.app.state.mongo


def get_retriever(request: Request) -> Retriever:
    return request.app.state.retriever


def get_generator(request: Request) -> Generator:
    return request.app.state.generator


# -------------------------
# Main Ask Endpoint
# -------------------------

@router.post("/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    mongo: Mongo = Depends(get_mongo),
    retriever: Retriever = Depends(get_retriever),
    generator: Generator = Depends(get_generator),
) -> AskResponse:
    start = time.time()
    query = payload.query.strip()
    request_id = str(uuid.uuid4())
    logger.info(f"[ASK] {request_id}: {query}")

    # 🔐 Safety detection (system-level, BEFORE generation)
    safety = check_safety(query)

    sources: List[SourceItem] = []
    retrieved_chunks: List[RetrievedChunk] = []
    answer = ""

    try:
        # -------------------------
        # Retrieval (ALWAYS runs)
        # -------------------------
        if not hasattr(request.app.state, 'embedder') or not hasattr(request.app.state, 'retriever'):
            # Initialise a fresh embedder and retriever on demand.  We do not
            # rely on request.app.state.sbert_model here because that field
            # isn't set during startup.  Instead, fall back to the same
            # environment variable used in the startup routine.
            sbert_model = os.getenv(
                "SBERT_MODEL", "sentence-transformers/paraphrase-MiniLM-L3-v2"
            ).strip()
            embedder = Embedder(sbert_model_name=sbert_model)
            # Preload the model once to avoid cold start latency on the first call.
            embedder.embed_texts(["Warmup embed"])

            index_dir = os.getenv("INDEX_DIR", "./storage")
            top_k = int(os.getenv("TOP_K", "5"))
            retriever = Retriever(index_dir=index_dir, embedder=embedder, top_k=top_k)
            # Use the helper from index_utils to build an index only if no
            # documents are currently indexed.  This avoids the circular
            # import that previously existed when `_build_index_if_empty` was
            # referenced from main.py.
            build_index_if_empty(retriever, embedder)
            request.app.state.embedder = embedder
            request.app.state.retriever = retriever
            logger.info("Embedder/Retriever lazy-loaded")
        retriever = request.app.state.retriever
        retrieved_chunks = retriever.retrieve(query)
        logger.info(f"[ASK] Retrieved {len(retrieved_chunks)} chunks")

        answer = await generator.generate(query, retrieved_chunks)

        # -------------------------
        # Enforce safety framing AFTER generation
        # -------------------------
        if safety.is_unsafe:
            answer = (
                "⚠️ **Medical Safety Notice**\n\n"
                "This response is provided for general wellness education only and "
                "is **not medical advice**.\n\n"
                + answer +
                "\n\nPlease consult a qualified healthcare professional or a certified "
                "yoga therapist before attempting any breathing or physical practices."
            )

        # -------------------------
        # Build sources for UI
        # -------------------------
        sources = [
            SourceItem(
                chunk_id=str(getattr(c, "chunk_id", "")),
                title=str(getattr(c, "title", "")),
                article_id=str(getattr(c, "article_id", "")),
                source=str(getattr(c, "source", "")),
                score=float(getattr(c, "score", 0.0)),
            )
            for c in retrieved_chunks
        ]

    except Exception as e:
        logger.error(f"[ASK] Error: {e}")
        raise HTTPException(status_code=500, detail=f"RAG pipeline error: {e}")

    # -------------------------
    # Logging (MongoDB)
    # -------------------------
    latency_ms = int((time.time() - start) * 1000)

    log_doc = {
        "request_id": request_id,
        "query": query,
        "is_unsafe": safety.is_unsafe,
        "safety_reasons": safety.reasons,
        "severities": safety.severities,
        "retrieved_chunks": [
            {
                "chunk_id": str(getattr(c, "chunk_id", "")),
                "article_id": str(getattr(c, "article_id", "")),
                "title": str(getattr(c, "title", "")),
                "source": str(getattr(c, "source", "")),
                "score": float(getattr(c, "score", 0.0)),
                "text_preview": (
                    (str(getattr(c, "text", ""))[:240] + "...")
                    if len(str(getattr(c, "text", ""))) > 240
                    else str(getattr(c, "text", ""))
                ),
            }
            for c in retrieved_chunks
        ],
        "answer": answer,
        "latency_ms": latency_ms,
        "llm_primary": os.getenv("GROQ_MODEL_PRIMARY", ""),
        "llm_fallback": os.getenv("GROQ_MODEL_FALLBACK", ""),
        "created_at": utc_now(),
    }
    await log_request(mongo, log_doc)

    return AskResponse(
        request_id=request_id,
        is_unsafe=safety.is_unsafe,
        safety_reasons=safety.reasons,
        answer=answer,
        sources=sources,
    )


# -------------------------
# Feedback Endpoint
# -------------------------

@router.post("/feedback", response_model=FeedbackResponse)
async def feedback(
    payload: FeedbackRequest,
    mongo: Mongo = Depends(get_mongo),
) -> FeedbackResponse:
    await attach_feedback(mongo, payload.request_id, payload.rating, payload.comment)
    return FeedbackResponse(ok=True)
