from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import List, Literal, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.db import Mongo, attach_feedback, log_request, utc_now
from app.safety import check_safety, unsafe_response_text
from app.rag.retriever import Retriever, RetrievedChunk
from app.rag.generator import Generator

# Ensure env is loaded when this module is imported (important for startup config)
load_dotenv(Path(__file__).resolve().parents[1] / "storage" / ".env")

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

    # 🔐 Safety detection (system-level, BEFORE generation)
    safety = check_safety(query)

    sources: List[SourceItem] = []
    retrieved_chunks: List[RetrievedChunk] = []
    answer = ""

    try:
        # -------------------------
        # Retrieval (ALWAYS runs)
        # -------------------------
        retrieved_chunks = retriever.retrieve(query)

        # Debug prints (useful for demo & evaluation)
        print("[ASK] query =", query)
        print("[ASK] index_dir =", getattr(retriever, "index_dir", None))
        print("[ASK] hits =", len(retrieved_chunks))
        if retrieved_chunks:
            print(
                "[ASK] top =",
                retrieved_chunks[0].title,
                "score =",
                getattr(retrieved_chunks[0], "score", None),
            )

        # -------------------------
        # Generation (RAG)
        # -------------------------
        answer = generator.generate(query, retrieved_chunks)

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
        "llm_primary": os.getenv("OLLAMA_MODEL_PRIMARY", ""),
        "llm_fallback": os.getenv("OLLAMA_MODEL_FALLBACK", ""),
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
