from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

import httpx

from app.rag.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.rag.retriever import RetrievedChunk


@dataclass
class Generator:
    ollama_base_url: str
    model_primary: str
    model_fallback: str
    temperature: float = 0.3
    num_ctx: int = 4096
    timeout_s: float = 120.0

    @staticmethod
    def _build_context(chunks: List[RetrievedChunk], max_chars: int = 6500) -> str:
        parts = []
        used = 0
        for c in chunks:
            block = f"[{c.chunk_id}] {c.title}\n{c.text}\n"
            if used + len(block) > max_chars:
                break
            parts.append(block)
            used += len(block)
        return "\n---\n".join(parts).strip()

    def _ollama_chat(self, model: str, system: str, user: str) -> str:
        url = self.ollama_base_url.rstrip("/") + "/api/chat"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
            },
            "stream": False,
        }

        with httpx.Client(timeout=self.timeout_s) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        msg = data.get("message", {})
        return (msg.get("content") or "").strip()

    def generate(self, question: str, chunks: List[RetrievedChunk]) -> str:
        context = self._build_context(chunks)
        user_prompt = USER_PROMPT_TEMPLATE.format(question=question, context=context)

        # Try primary first (llama3.1:8b), then fallback (mistral:7b)
        try:
            return self._ollama_chat(self.model_primary, SYSTEM_PROMPT, user_prompt)
        except Exception:
            try:
                return self._ollama_chat(self.model_fallback, SYSTEM_PROMPT, user_prompt)
            except Exception:
                # Deterministic fallback (never breaks demo)
                used_ids = ", ".join([c.chunk_id for c in chunks[:3]]) if chunks else "none"
                return (
                    "I’m unable to reach the local LLM server right now. Here is the most relevant context I retrieved:\n\n"
                    f"{context[:1400]}\n\n"
                    f"Sources: {used_ids}"
                )


def from_env() -> Generator:
    return Generator(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model_primary=os.getenv("OLLAMA_MODEL_PRIMARY", "llama3.1:8b"),
        model_fallback=os.getenv("OLLAMA_MODEL_FALLBACK", "mistral:7b"),
        temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.3")),
        num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "4096")),
        timeout_s=float(os.getenv("OLLAMA_TIMEOUT_S", "120")),
    )
