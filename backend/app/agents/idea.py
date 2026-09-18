"""IdeaAgent: Brainstorm viral concepts optimized for Instagram Reels."""

import json
from typing import List, Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.providers.ai.openrouter import OpenRouterAIProvider


class IdeaAgent(BaseAgent):
    """Brainstorms high-retention concepts tailored for Instagram Reels format."""

    TOP_NICHES = [
        "Technology & AI",
        "Wealth & Financial Freedom",
        "Productivity & High Performance",
        "Science & Future",
        "Psychology & Human Behavior"
    ]

    def __init__(self, ai_provider: Optional[OpenRouterAIProvider] = None):
        super().__init__("IdeaAgent")
        self.ai = ai_provider or OpenRouterAIProvider()

    async def generate_ideas(self, niche: str = "Technology & AI", count: int = 3) -> List[Dict[str, Any]]:
        self.log(f"Brainstorming {count} viral Reel ideas for niche: {niche}")
        
        prompt = (
            f"Generate {count} viral Instagram Reels concepts for the niche '{niche}'.\n"
            "Each Reel must have:\n"
            "- A 3-second scroll-stopping hook\n"
            "- A compelling core topic\n"
            "- High save/share appeal\n"
            "Format as JSON array with keys: 'topic', 'hook', 'angle'."
        )

        try:
            resp = await self.ai.generate_text(prompt)
            # Find json in response if wrapped
            start = resp.find("[")
            end = resp.rfind("]") + 1
            if start != -1 and end != 0:
                return json.loads(resp[start:end])
        except Exception as e:
            self.log(f"Parsing AI ideas failed: {e}. Using curated viral ideas.")

        # Fallback viral ideas
        return [
            {
                "topic": "3 AI Workflows That Make Coding 10x Faster",
                "hook": "If you're still writing boilerplate by hand in 2026, stop immediately.",
                "angle": "Actionable developer productivity hack"
            },
            {
                "topic": "How Quantum Chips Actually Work in 45 Seconds",
                "hook": "This microscopic chip is colder than outer space.",
                "angle": "Mind-blowing science breakdown"
            },
            {
                "topic": "The 1% Rule of Digital Asset Growth",
                "hook": "Most people get poor waiting for the right moment.",
                "angle": "Contrarian wealth mindset"
            }
        ]
