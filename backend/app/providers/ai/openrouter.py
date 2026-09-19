"""OpenRouter AI provider with free-tier model support and deterministic fallback."""

import asyncio
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
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await asyncio.wait_for(
                    client.post(self.endpoint, headers=headers, json=payload),
                    timeout=10.0
                )
                data = json.loads(res.text.strip())
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                logger.warning(f"[OpenRouter] Unexpected response format: {data}")
        except Exception as e:
            logger.warning(f"[OpenRouter] API request note: {e}. Using intelligent fallback.")

        return self._fallback_completion(prompt)

    def _fallback_completion(self, prompt: str) -> str:
        """High-retention deterministic templates for zero-cost / offline mode."""
        prompt_lower = prompt.lower()
        is_quiz = any(k in prompt_lower for k in ["quiz", "python", "code", "card", "programming"])

        if "hook" in prompt_lower:
            if is_quiz:
                return (
                    "1. Only 10% of Python developers can predict the output of this code.\n"
                    "2. Bet you can't guess what Python prints in this tricky snippet!\n"
                    "3. Stop scrolling: test your Python programming skills right now."
                )
            return (
                "1. If you're not using this AI tool in 2026, you're falling behind.\n"
                "2. The 3 secret algorithms running today's world.\n"
                "3. Stop scrolling: this one change saved me 10 hours a week."
            )
        elif "script" in prompt_lower or "scene" in prompt_lower:
            if is_quiz:
                return json.dumps([
                    {
                        "scene_number": 1,
                        "narration_chunk": "Only 10% of developers get this Python question right. Can you?",
                        "visual_direction": "Glowing Python terminal with dark mode syntax highlighting code editor",
                        "duration_sec": 3.5
                    },
                    {
                        "scene_number": 2,
                        "narration_chunk": "Look closely at this snippet: print([1, 2] * 2). What does it print? Option A, B, C, or D?",
                        "visual_direction": "Clean Python code card with multiple choice options A B C D",
                        "duration_sec": 4.0
                    },
                    {
                        "scene_number": 3,
                        "narration_chunk": "Pause the video and drop your answer in the comments. 3, 2, 1...",
                        "visual_direction": "Neon digital stopwatch timer countdown on programming workstation",
                        "duration_sec": 3.0
                    },
                    {
                        "scene_number": 4,
                        "narration_chunk": "The correct answer is Option B! In Python, list multiplication duplicates the sequence into a single flat list [1, 2, 1, 2].",
                        "visual_direction": "Terminal executing python code showing output in green font",
                        "duration_sec": 4.5
                    },
                    {
                        "scene_number": 5,
                        "narration_chunk": "Did you get it right? Save this Reel and follow for daily Python coding quizzes!",
                        "visual_direction": "Programmer celebrating at computer screen with Instagram follow bookmark icon",
                        "duration_sec": 3.5
                    }
                ])
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
            if is_quiz:
                return (
                    "🐍 Tricky Python Quiz Card of the Day!\n\n"
                    "Can you solve this before the timer runs out? Drop your answer (A, B, C, or D) in the comments! 👇\n\n"
                    "💡 Save this Reel to challenge your programmer friends.\n"
                    "🔔 Follow for daily Python coding quizzes and tricks!\n\n"
                    "#python #programming #coding #pythonquiz #developer #computerscience #learnpython #reels #viral #explorepage"
                )
            return (
                "🚨 The future is arriving faster than expected.\n\n"
                "Here are the 3 critical AI shifts reshaping tech in 2026. Bookmark this for later!\n\n"
                "👉 Save this Reel to stay ahead of the curve.\n"
                "💬 Which one are you trying first?\n\n"
                "#reels #viral #tech #ai #innovation #explorepage #futuretech #trending"
            )
        return "Insightful, high-impact Python quiz card breakdown designed for maximum Instagram Reels watch time and comments."
