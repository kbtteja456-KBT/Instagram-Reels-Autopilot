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

    async def generate_ideas(self, niche: str = "python program quiz card reels", count: int = 3) -> List[Dict[str, Any]]:
        self.log(f"Brainstorming {count} viral Reel ideas for niche: {niche}")
        
        is_quiz = any(k in niche.lower() for k in ["quiz", "python", "card", "code", "coding"])

        if is_quiz:
            prompt = (
                f"Generate {count} viral Instagram Reels Python Programming Quiz Card concepts.\n"
                "Each quiz card Reel must have:\n"
                "- A 3-second scroll-stopping question hook (e.g. 'Can you guess what this tricky Python code prints?')\n"
                "- A concrete Python snippet problem with tricky output (e.g. mutable default args, list multiplication, is vs ==, string slicing, tuple mutation)\n"
                "- Multiple choice options (A, B, C, D)\n"
                "- High retention and comments appeal\n"
                "Format as JSON array with keys: 'topic', 'hook', 'angle'."
            )
        else:
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
            start = resp.find("[")
            end = resp.rfind("]") + 1
            if start != -1 and end != 0:
                return json.loads(resp[start:end])
        except Exception as e:
            self.log(f"Parsing AI ideas failed: {e}. Using curated viral ideas.")

        if is_quiz:
            return [
                {
                    "topic": "Python Quiz: What is the output of print([1, 2] * 2)?",
                    "hook": "Only 10% of Python developers get this quiz question right on the first try.",
                    "angle": "Tricky Python list multiplication and memory reference quiz card"
                },
                {
                    "topic": "Python Quiz: The Mutable Default Argument Trap",
                    "hook": "Stop writing Python functions like this before it breaks your production code.",
                    "angle": "Classic Python def foo(x=[]) gotcha quiz card"
                },
                {
                    "topic": "Python Quiz: Difference between 'is' and '=='",
                    "hook": "Do you know the subtle difference between 'is' and '==' in Python?",
                    "angle": "Python object identity vs equality comparison quiz"
                }
            ]

        # General Fallback viral ideas
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
