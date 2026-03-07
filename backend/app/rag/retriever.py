from __future__ import annotations

import os
from typing import List

import chromadb
from chromadb.config import Settings

from .embedder import Embedder
from .index import get_chroma_client, get_collection, DEFAULT_COLLECTION  # Fixed: relative import
from .chunker import Chunk  # Added for inheritance consistency

class RetrievedChunk(Chunk):
    score: float

    class Config:
        from_attributes = True

class Retriever:
    def __init__(
        self,
        index_dir: str,
        embedder: Embedder,
        top_k: int = 5,
    ) -> None:
        self.embedder = embedder
        self.top_k = top_k
        self.persist_dir = os.path.abspath(index_dir)
        self.client = self._get_chroma_client()
        self.collection = self._get_or_create_collection()

    def _get_chroma_client(self) -> chromadb.Client:
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.persist_dir,
            anonymized_telemetry=False,
        )
        return chromadb.Client(settings)

    def _get_or_create_collection(self):
        return self.client.get_or_create_collection(
            name=DEFAULT_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def retrieve(self, query: str) -> List[RetrievedChunk]:
        query_emb = self.embedder.embed_text(query).reshape(1, -1)  # Fixed: embed_text, reshape for Chroma
        results = self.collection.query(
            query_embeddings=query_emb.astype(float).tolist(),
            n_results=self.top_k,
            include=["documents", "metadatas", "distances"],
        )
        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0] or [],
            results["metadatas"][0] or [],
            results["distances"][0] or [],
        ):
            chunk = Chunk(
                chunk_id=meta.get("chunk_id", ""),
                article_id=meta.get("article_id", ""),
                title=meta.get("title", ""),
                source=meta.get("source", ""),
                text=doc or "",
            )
            chunks.append(RetrievedChunk(**chunk.dict(), score=1 - dist))
        return chunks