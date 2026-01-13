from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import List


@dataclass
class Embedder:
    sbert_model_name: str
    _model: object = None

    def _ensure_loaded(self) -> None:
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.sbert_model_name)

    @staticmethod
    def _normalize(x: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
        return (x / norms).astype(np.float32)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        self._ensure_loaded()
        if not texts:
            return np.zeros((0, 384), dtype=np.float32)
        vecs = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        vecs = np.asarray(vecs, dtype=np.float32)
        return self._normalize(vecs)

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_texts([query])[0:1]
