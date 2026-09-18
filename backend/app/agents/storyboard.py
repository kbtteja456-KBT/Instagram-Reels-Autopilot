"""StoryboardAgent: Visual prompts and pacing layout."""

from typing import List, Optional
from backend.app.agents.base import BaseAgent
from backend.app.agents.script import ReelScript
from backend.app.models.video import Storyboard, Scene


class StoryboardAgent(BaseAgent):
    """Plans cinematic visual prompts and pacing structure for the Reel."""

    def __init__(self):
        super().__init__("StoryboardAgent")

    async def create_storyboard(self, script: ReelScript) -> Storyboard:
        self.log(f"Assembling storyboard with {len(script.scenes)} visual scenes...")
        return Storyboard(
            scenes=script.scenes,
            total_duration_sec=script.target_duration_sec
        )
