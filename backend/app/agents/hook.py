import json
import re
from typing import List, Optional
from pydantic import BaseModel
from backend.app.agents.base import BaseAgent
from backend.app.providers.ai.openrouter import OpenRouterAIProvider


class HookCandidate(BaseModel):
    text: str
    virality_score: float
    hook_type: str  # curiosity, contrarian, fear_of_missing_out, authority
    selected: bool = False


class HookAgent(BaseAgent):
    """Generates high-retention first 3-second hooks."""

    def __init__(self, ai_provider: Optional[OpenRouterAIProvider] = None):
        super().__init__("HookAgent")
        self.ai = ai_provider or OpenRouterAIProvider()

    async def generate_and_score_hooks(self, topic: str, key_takeaway: str) -> List[HookCandidate]:
        self.log(f"Generating scroll-stopping hooks for: {topic}")

        prompt = f"""You are an elite short-form video retention expert.
Generate 3 distinct, scroll-stopping opening hooks for an Instagram Reel about: "{topic}".
Key angle: "{key_takeaway}"

Return ONLY a JSON array with 3 objects:
[
  {{
    "text": "The exact hook spoken in the first 3 seconds",
    "virality_score": 9.5,
    "hook_type": "fear_of_missing_out"
  }},
  {{
    "text": "Second alternative hook",
    "virality_score": 9.1,
    "hook_type": "curiosity"
  }},
  {{
    "text": "Third alternative hook",
    "virality_score": 8.8,
    "hook_type": "contrarian"
  }}
]
Rules:
- Keep each hook under 14 words so it fits in 2.5 to 3.5 seconds.
- Score virality from 7.0 to 9.9 based on curiosity and stopping power.
- Return ONLY valid JSON array."""

        candidates: List[HookCandidate] = []
        try:
            raw_text = await self.ai.generate_text(prompt)
            cleaned = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.IGNORECASE)
            cleaned = re.sub(r"```$", "", cleaned.strip()).strip()

            start_idx = cleaned.find("[")
            end_idx = cleaned.rfind("]")
            if start_idx != -1 and end_idx != -1:
                data = json.loads(cleaned[start_idx:end_idx + 1])
                for item in data:
                    candidates.append(HookCandidate(
                        text=item.get("text", "").strip(),
                        virality_score=float(item.get("virality_score", 8.5)),
                        hook_type=item.get("hook_type", "curiosity"),
                        selected=False
                    ))
        except Exception as e:
            self.log(f"Dynamic hook parsing note: {e}. Using fallback hooks.")

        if not candidates:
            candidates = [
                HookCandidate(
                    text=f"If you are not paying attention to {topic}, you are falling behind.",
                    virality_score=9.4,
                    hook_type="fear_of_missing_out"
                ),
                HookCandidate(
                    text=f"Nobody is talking about what just happened with {topic}.",
                    virality_score=8.9,
                    hook_type="curiosity"
                ),
                HookCandidate(
                    text=f"Stop scrolling: this one breakthrough in {topic} changes everything.",
                    virality_score=8.7,
                    hook_type="pattern_interrupt"
                )
            ]

        # Mark the highest scoring hook as selected
        best_candidate = max(candidates, key=lambda c: c.virality_score)
        best_candidate.selected = True

        return candidates
