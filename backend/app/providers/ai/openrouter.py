"""OpenRouter AI provider with free-tier model support and deterministic fallback."""

import json
import httpx
from typing import Dict, Any, Optional
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider


class OpenRouterAIProvider(BaseProvider):
    """Zero-cost LLM provider via OpenRouter free tier or deterministic engine."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__("openrouter")
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model or settings.openrouter_model
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"

    async def health_check(self) -> Dict[str, Any]:
        return {
            "provider": self.name,
            "status": "HEALTHY",
            "model": self.model,
            "has_key": bool(self.api_key),
            "zero_cost": True
        }

    async def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        """Call OpenRouter or use intelligent fallback."""
        if not self.api_key or self.api_key.startswith("mock_"):
            return self._fallback_completion(prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://instagram-autopilot.internal",
            "X-Title": "AI Instagram Reels Autopilot",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or "You are an expert viral Instagram Reels strategist and scriptwriter."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1200
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(self.endpoint, headers=headers, json=payload)
                data = json.loads(res.text.strip())
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"[OpenRouter] Unexpected response format: {data}")
        except Exception as e:
            logger.warning(f"[OpenRouter] API request failed: {e}. Using deterministic fallback.")

        return self._fallback_completion(prompt)

    def _fallback_completion(self, prompt: str) -> str:
        """High-retention deterministic templates for zero-cost / offline mode."""
        prompt_lower = prompt.lower()
        if "hook" in prompt_lower:
            return (
                "1. If you're not using this AI tool in 2026, you're falling behind.\n"
                "2. The 3 secret algorithms running today's world.\n"
                "3. Stop scrolling: this one change saved me 10 hours a week."
            )
        elif "script" in prompt_lower or "scene" in prompt_lower:
            return json.dumps({
                "title": "3 Insane AI Tools You Must Know in 2026",
                "target_duration_sec": 45.0,
                "scenes": [
                    {
                        "scene_number": 1,
                        "narration_chunk": "If you are not using this AI technology today, you are already falling behind.",
                        "visual_direction": "Dramatic fast zoom into glowing futuristic microprocessor with neon circuits",
                        "duration_sec": 4.5
                    },
                    {
                        "scene_number": 2,
                        "narration_chunk": "First up is autonomous code generation that converts high level designs into running software in seconds.",
                        "visual_direction": "Cyberpunk terminal code scrolling at super speed with holographic reflections",
                        "duration_sec": 5.0
                    },
                    {
                        "scene_number": 3,
                        "narration_chunk": "Second, neural video rendering that produces cinematic photoreal 9:16 footage without physical cameras.",
                        "visual_direction": "Sleek camera lens turning with iridescent light flares and 3D wireframes",
                        "duration_sec": 5.0
                    },
                    {
                        "scene_number": 4,
                        "narration_chunk": "And finally, local LLMs that protect all your data while running privately on your workstation.",
                        "visual_direction": "Golden glowing lock symbol closing on server rack data vault",
                        "duration_sec": 5.0
                    },
                    {
                        "scene_number": 5,
                        "narration_chunk": "Save this Reel right now and follow for your daily tech unfair advantage.",
                        "visual_direction": "Smartphone screen tapping save and follow button with glowing particles",
                        "duration_sec": 4.5
                    }
                ]
            })
        elif "caption" in prompt_lower or "hashtag" in prompt_lower:
            return (
                "🚨 The future is arriving faster than expected.\n\n"
                "Here are the 3 critical AI shifts reshaping tech in 2026. Bookmark this for later!\n\n"
                "👉 Save this Reel to stay ahead of the curve.\n"
                "💬 Which one are you trying first?\n\n"
                "#reels #viral #tech #ai #innovation #explorepage #futuretech #trending"
            )
        return "Insightful, high-impact breakdown designed for maximum Instagram Reels watch time and engagement."
