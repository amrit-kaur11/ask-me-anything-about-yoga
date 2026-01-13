from __future__ import annotations

import os
import chromadb


DEFAULT_COLLECTION = "yoga_chunks"


def get_chroma_client(persist_dir: str) -> chromadb.PersistentClient:
    os.makedirs(persist_dir, exist_ok=True)
    return chromadb.PersistentClient(path=persist_dir)


def get_collection(client: chromadb.PersistentClient, name: str = DEFAULT_COLLECTION):
    # Use cosine distance for embedding similarity
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )
