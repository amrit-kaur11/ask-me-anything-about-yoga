from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from groq import Groq

from app.rag.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.rag.retriever import RetrievedChunk


@dataclass
class Generator:
    model_primary: str
    model_fallback: str
    temperature: float = 0.3
    timeout_s: float = 60.0

    @staticmethod
    def _build_context(chunks: List[RetrievedChunk], max_chars: int = 3500) -> str:
        parts = []
        used = 0
        for c in chunks:
            block = f"[{c.chunk_id}] {c.title}\n{c.text}\n"
            if used + len(block) > max_chars:
                break
            parts.append(block)
            used += len(block)
        return "\n---\n".join(parts).strip()


    def _groq_chat(self, model: str, system: str, user: str) -> str:
        """
        Uses Groq API instead of Ollama.
        """

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        full_prompt = f"""
{system}

IMPORTANT SAFETY RULES (NON-NEGOTIABLE):
- You are a wellness and yoga assistant, NOT a medical professional.
- If the user mentions serious illness (e.g. cancer, heart disease, pregnancy, surgery, chronic pain):
- DO NOT provide medical advice
- DO NOT suggest intense or advanced practices
- ALWAYS recommend consulting a qualified healthcare professional
- Use cautious, supportive, non-absolute language

USER QUESTION:
{user}
""".strip()

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": full_prompt},
            ],
            model=model,
            temperature=self.temperature,
        )

        return chat_completion.choices[0].message.content.strip()

    def generate(self, question: str, chunks: List[RetrievedChunk]) -> str:
        context = self._build_context(chunks)
        user_prompt = USER_PROMPT_TEMPLATE.format(
            question=question,
            context=context
        )

        try:
            return self._groq_chat(self.model_primary, SYSTEM_PROMPT, user_prompt)
        except Exception as e:
            print("GROQ PRIMARY ERROR:", e)
            try:
                return self._groq_chat(self.model_fallback, SYSTEM_PROMPT, user_prompt)
            except Exception as e:
                print("GROQ FALLBACK ERROR:", e)
                used_ids = ", ".join([c.chunk_id for c in chunks[:3]]) if chunks else "none"
                return (
                    "I’m unable to reach the LLM service right now. "
                    "Here is the most relevant context I retrieved:\n\n"
                    f"{context[:1400]}\n\n"
                    f"Sources: {used_ids}"
                )


def from_env() -> Generator:
    return Generator(
        model_primary=os.getenv("GROQ_MODEL_PRIMARY", "llama3-8b-8192"),
        model_fallback=os.getenv("GROQ_MODEL_FALLBACK", "gemma-7b-it"),
        temperature=float(os.getenv("GROQ_TEMPERATURE", "0.3")),
    )
