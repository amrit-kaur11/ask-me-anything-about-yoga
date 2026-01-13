from __future__ import annotations

import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.db import init_mongo, ensure_indexes
from app.rag.embedder import Embedder
from app.rag.retriever import Retriever
from app.rag.generator import from_env as generator_from_env


def _load_env() -> None:
    candidates = [
        os.path.join("backend", "storage", ".env"),
        os.path.join("backend", ".env"),
        ".env",
    ]
    for p in candidates:
        if os.path.exists(p):
            load_dotenv(p, override=False)
            return


def create_app() -> FastAPI:
    _load_env()

    app = FastAPI(title="AskMe AI - Yoga RAG")

    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    cors_origins = [o.strip() for o in cors_origins if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")

    @app.get("/health")
    async def health():
        return {"ok": True}

    @app.on_event("startup")
    async def startup():
        mongo = init_mongo()
        await ensure_indexes(mongo)
        app.state.mongo = mongo

        # Embeddings
        sbert_model = os.getenv("SBERT_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        embedder = Embedder(sbert_model_name=sbert_model)

        # Retriever
        index_dir = os.getenv("INDEX_DIR", os.path.join("backend", "storage"))
        top_k = int(os.getenv("TOP_K", "5"))
        app.state.retriever = Retriever(index_dir=index_dir, embedder=embedder, top_k=top_k)

        # Generator (Ollama primary + fallback)
        app.state.generator = generator_from_env()

    @app.on_event("shutdown")
    async def shutdown():
        app.state.mongo.client.close()

    return app


app = create_app()
