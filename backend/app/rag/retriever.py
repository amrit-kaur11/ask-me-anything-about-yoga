from __future__ import annotations

import os
from typing import List

from .embedder import Embedder
from .index import get_chroma_client, get_collection, DEFAULT_COLLECTION  # Fixed: relative import
from .chunker import Chunk  # Added for inheritance consistency

from dataclasses import dataclass

@dataclass(frozen=True)
class RetrievedChunk(Chunk):
    score: float = 0.0

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

    def _get_chroma_client(self):
        return get_chroma_client(self.persist_dir)

    def _get_or_create_collection(self):
        return get_collection(self.client, DEFAULT_COLLECTION)

    def retrieve(self, query: str) -> List[RetrievedChunk]:
        query_emb = self.embedder.embed_query(query)
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
            chunks.append(RetrievedChunk(chunk_id=chunk.chunk_id, article_id=chunk.article_id, title=chunk.title, source=chunk.source, text=chunk.text, score=1 - dist))
        return chunks