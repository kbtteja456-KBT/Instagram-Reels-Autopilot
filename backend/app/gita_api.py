"""Grounded, multilingual Bhagavad Gita companion endpoint."""

from typing import Literal

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.config import settings

router = APIRouter(prefix="/gita", tags=["gita"])


class GitaTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1800)


class GitaQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=1800)
    language: str = Field(default="English", min_length=2, max_length=40)
    history: list[GitaTurn] = Field(default_factory=list, max_length=8)


SYSTEM_PROMPT = """You are Gita, a kind, thoughtful study companion devoted to the Bhagavad Gita. Help people explore the text and apply its ideas with humility, clarity, and care.

Answer in the user's selected language. When the user asks about life, connect your guidance to relevant Gita teachings without claiming the scripture is a substitute for professional medical, mental-health, legal, or financial help. Never shame, proselytize, or claim to be Krishna, a guru, or a spiritual authority.

Be faithful to the text. Distinguish a paraphrase from a direct quotation; do not invent quotations, verse numbers, or historical certainty. Give chapter-and-verse references only when confident, and note that translations and interpretations differ. If uncertain, say so and offer a careful general explanation. Keep the answer warm, conversational, and useful, normally 2–5 short paragraphs. For a practical question, end with one gentle reflection or small action."""


@router.post("/ask")
async def ask_gita_question(payload: GitaQuestion) -> dict[str, str]:
    """Answer one question using the configured server-side OpenRouter credential."""
    api_key = settings.openrouter_api_key or settings.openrouter_api_key_2
    if not api_key or api_key.startswith("mock_"):
        raise HTTPException(status_code=503, detail="The Gita companion is not configured yet. Please try again later.")

    messages = [{"role": "system", "content": SYSTEM_PROMPT + f"\n\nRespond in: {payload.language}."}]
    for turn in payload.history[-8:]:
        messages.append({"role": turn.role, "content": turn.content})
    messages.append({"role": "user", "content": payload.question.strip()})

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(35.0, connect=8.0)) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": settings.openrouter_model,
                    "messages": messages,
                    "temperature": 0.45,
                    "max_tokens": 900,
                },
            )
            response.raise_for_status()
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("The model returned an empty response")
            return {"answer": answer.strip()}
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 429:
            raise HTTPException(status_code=429, detail="The companion is resting for a moment. Please try again shortly.") from exc
        raise HTTPException(status_code=502, detail="The companion could not reach its reflection service. Please try again.") from exc
    except (httpx.HTTPError, ValueError, KeyError, IndexError):
        raise HTTPException(status_code=502, detail="The companion could not complete that reflection. Please try again.")
