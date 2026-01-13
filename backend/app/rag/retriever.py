from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.rag.embedder import Embedder
from app.rag.index import get_chroma_client, get_collection


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    article_id: str
    title: str
    source: str
    text: str
    score: float


class Retriever:
    def __init__(self, index_dir: str, embedder: Embedder, top_k: int = 5):
        self.persist_dir = index_dir
        self.embedder = embedder
        self.top_k = top_k

        client = get_chroma_client(self.persist_dir)
        self.collection = get_collection(client)

    def retrieve(self, query: str) -> List[RetrievedChunk]:
        q_emb = self.embedder.embed_query(query)[0].tolist()

        res = self.collection.query(
            query_embeddings=[q_emb],
            n_results=self.top_k,
            include=["documents", "metadatas", "distances"],
        )

        # Chroma returns nested lists: one list per query
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]

        results: List[RetrievedChunk] = []
        for chunk_id, doc, meta, dist in zip(ids, docs, metas, dists):
            # With cosine distance: lower is better. Convert to a similarity-like score.
            score = 1.0 - float(dist)

            results.append(
                RetrievedChunk(
                    chunk_id=str(chunk_id),
                    article_id=str(meta.get("article_id", "")),
                    title=str(meta.get("title", "")),
                    source=str(meta.get("source", "")),
                    text=str(doc or ""),
                    score=score,
                )
            )

        return results
