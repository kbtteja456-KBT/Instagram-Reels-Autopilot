import re
from typing import Dict, Any, List, Optional
from backend.app.agents.base import BaseAgent
from backend.app.agents.script import ReelScript
from backend.app.providers.ai.openrouter import OpenRouterAIProvider


class CaptionWriterAgent(BaseAgent):
    """Crafts captivating Instagram captions and curated hashtags."""

    def __init__(self, ai_provider: Optional[OpenRouterAIProvider] = None):
        super().__init__("CaptionWriterAgent")
        self.ai = ai_provider or OpenRouterAIProvider()

    async def generate_caption(self, script: ReelScript, niche: str = "Technology & AI") -> Dict[str, Any]:
        self.log(f"Writing viral caption and hashtags for '{script.title}'...")

        prompt = f"""You are a viral Instagram growth strategist.
Write a high-converting Instagram caption for this Reel:
Title: "{script.title}"
Niche: "{niche}"
Opening Hook: "{script.hook}"
Summary Narration: "{script.full_narration_text[:200]}..."

Structure:
1. First line: A bold emoji hook repeating or amplifying the opening statement.
2. 2-3 short bullet points summarizing the practical value.
3. Strong call-to-action (Save this Reel & share your thoughts).
4. Exactly 8-12 relevant, viral hashtags (e.g. #reels #viral #explorepage #tech...).

Return ONLY the caption text directly. Do not include introductory or closing remarks."""

        try:
            caption_text = await self.ai.generate_text(prompt)
            caption_text = caption_text.strip()
            # Extract hashtags
            hashtags = re.findall(r"#\w+", caption_text)
            if not hashtags:
                clean_niche = re.sub(r"[^\w]", "", niche.lower())
                hashtags = ["#reels", "#viral", "#explorepage", f"#{clean_niche}"]
            
            return {
                "caption": caption_text,
                "hashtags": hashtags
            }
        except Exception as e:
            self.log(f"Dynamic caption error: {e}. Utilizing fallback caption.")

        default_caption = (
            f"⚡ {script.hook}\n\n"
            f"Here is what you need to know about {script.title}.\n\n"
            "👉 Save this Reel so you don't lose it.\n"
            "💬 Drop your thoughts below — are you ready for this?\n\n"
            "#reels #viral #explorepage #tech #productivity"
        )
        return {
            "caption": default_caption,
            "hashtags": ["#reels", "#viral", "#explorepage", "#tech", "#productivity"]
        }
