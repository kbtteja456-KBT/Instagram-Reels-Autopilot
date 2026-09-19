import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.agents.base import BaseAgent
from backend.app.agents.research import ResearchResult
from backend.app.models.video import Scene
from backend.app.providers.ai.openrouter import OpenRouterAIProvider


class ReelScript(BaseModel):
    title: str
    hook: str
    target_duration_sec: float = 45.0
    scenes: List[Scene] = Field(default_factory=list)
    full_narration_text: str = ""


class ScriptAgent(BaseAgent):
    """Produces pacing-optimized Reel scripts with 2.5–3.5s scene beats."""

    def __init__(self, ai_provider: Optional[OpenRouterAIProvider] = None):
        super().__init__("ScriptAgent")
        self.ai = ai_provider or OpenRouterAIProvider()

    async def generate_script(
        self,
        topic: str,
        hook: str,
        research: ResearchResult,
        target_duration_sec: float = 40.0
    ) -> ReelScript:
        self.log(f"Composing dynamic Reel script for '{topic}' ({target_duration_sec}s target)...")

        is_quiz = any(k in topic.lower() for k in ["quiz", "python", "code", "card"]) or any(k in research.niche.lower() for k in ["quiz", "python", "code", "card"])

        if is_quiz:
            prompt = f"""You are a master viral Instagram Reels coding educator.
Write a high-retention 30-40 second Python Quiz Card Reel script on: "{topic}".
Opening Hook: "{hook}"
Key Insight/Answer: "{research.key_takeaway}"

Return ONLY a JSON array with exactly 5 scenes following this viral Quiz Card format:
[
  {{
    "scene_number": 1,
    "narration_chunk": "{hook}",
    "visual_direction": "Glowing Python terminal with dark mode syntax highlighting code editor",
    "duration_sec": 3.5
  }},
  {{
    "scene_number": 2,
    "narration_chunk": "Look at this snippet. What does it print? Option A, B, C, or D?",
    "visual_direction": "Clean Python code card with multiple choice options A B C D",
    "duration_sec": 4.0
  }},
  {{
    "scene_number": 3,
    "narration_chunk": "Pause the video and drop your answer in the comments. 3, 2, 1...",
    "visual_direction": "Neon digital stopwatch timer countdown on programming workstation",
    "duration_sec": 3.0
  }},
  {{
    "scene_number": 4,
    "narration_chunk": "The correct answer is Option B! In Python, list multiplication replicates the pointers without cloning the inner elements.",
    "visual_direction": "Terminal executing python code showing output in green font",
    "duration_sec": 4.5
  }},
  {{
    "scene_number": 5,
    "narration_chunk": "Did you get it right? Save this Reel and follow for daily Python coding quizzes!",
    "visual_direction": "Programmer celebrating at computer screen with Instagram follow bookmark icon",
    "duration_sec": 3.5
  }}
]
Rules:
1. Scene 1 MUST use the opening hook.
2. Scene 3 MUST have a pause/countdown challenge.
3. Scene 4 MUST clearly explain the answer and why Python evaluates it that way.
4. Return ONLY valid JSON array. No markdown, no commentary."""
        else:
            prompt = f"""You are a master viral Instagram Reels scriptwriter.
Write a high-retention script for a 30-45 second Reel on the topic: "{topic}".
Opening Hook: "{hook}"
Key Takeaway: "{research.key_takeaway}"

Return ONLY a JSON array with 5 to 6 sequential scenes. Every scene must cut every 2.5 to 3.5 seconds.
Format:
[
  {{
    "scene_number": 1,
    "narration_chunk": "{hook}",
    "visual_direction": "Dramatic fast cinematic visual for opening hook",
    "duration_sec": 3.2
  }},
  {{
    "scene_number": 2,
    "narration_chunk": "Short, punchy sentence explaining the problem or surprising insight.",
    "visual_direction": "high quality stock b-roll visual description",
    "duration_sec": 3.0
  }}
]
Rules:
1. Scene 1 MUST use the opening hook.
2. Scene narration should be conversational, punchy, and sound natural when spoken aloud.
3. The final scene should have a clear call-to-action to follow or save.
4. Return ONLY valid JSON array. No markdown formatting, no commentary."""

        scenes: List[Scene] = []
        try:
            raw_text = await self.ai.generate_text(prompt)
            # Clean possible markdown wrapping like ```json ... ```
            cleaned = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.IGNORECASE)
            cleaned = re.sub(r"```$", "", cleaned.strip()).strip()

            # Find array brackets
            start_idx = cleaned.find("[")
            end_idx = cleaned.rfind("]")
            if start_idx != -1 and end_idx != -1:
                json_str = cleaned[start_idx:end_idx + 1]
                data = json.loads(json_str)
                for idx, item in enumerate(data, start=1):
                    scenes.append(Scene(
                        scene_number=idx,
                        narration_chunk=item.get("narration_chunk", "").strip(),
                        visual_direction=item.get("visual_direction", topic).strip(),
                        duration_sec=float(item.get("duration_sec", 3.0))
                    ))
        except Exception as e:
            self.log(f"Dynamic script parsing note: {e}. Utilizing structured fallback.")

        # Fallback if AI returned empty or invalid
        if not scenes:
            if is_quiz:
                scenes = [
                    Scene(scene_number=1, narration_chunk=hook, visual_direction="Glowing Python terminal with dark mode syntax highlighting", duration_sec=3.5),
                    Scene(scene_number=2, narration_chunk="Look at this snippet. What is the output? Option A, B, C, or D?", visual_direction="Python code card showing multiple choice options", duration_sec=4.0),
                    Scene(scene_number=3, narration_chunk="Pause the video and test your Python skills. 3, 2, 1, what did you guess?", visual_direction="Neon timer countdown on developer workstation", duration_sec=3.0),
                    Scene(scene_number=4, narration_chunk=research.key_takeaway or "The correct answer is Option B. List multiplication repeats references rather than deep copies.", visual_direction="Terminal executing Python code showing green output", duration_sec=4.5),
                    Scene(scene_number=5, narration_chunk="Did you get it right? Comment below, save this Reel, and follow for daily Python quizzes!", visual_direction="Programmer workstation with save and follow bookmark icon", duration_sec=3.5),
                ]
            else:
                scenes = [
                    Scene(scene_number=1, narration_chunk=hook, visual_direction=f"{topic} cinematic dramatic", duration_sec=3.5),
                    Scene(scene_number=2, narration_chunk=f"Most people have no idea this shift in {topic} is already here.", visual_direction="person surprised looking at smartphone screen", duration_sec=3.2),
                    Scene(scene_number=3, narration_chunk=research.key_takeaway or f"The secret comes down to automating the execution before everyone else.", visual_direction="futuristic technology glowing circuit data streams", duration_sec=3.5),
                    Scene(scene_number=4, narration_chunk="Those who leverage smart systems right now will dominate the next year.", visual_direction="successful entrepreneur smiling in modern office", duration_sec=3.3),
                    Scene(scene_number=5, narration_chunk="Save this Reel right now and follow for daily actionable breakthroughs.", visual_direction="glowing smartphone screen with save and follow bookmark", duration_sec=3.0),
                ]

        full_text = " ".join([s.narration_chunk for s in scenes])

        return ReelScript(
            title=topic,
            hook=hook,
            target_duration_sec=round(sum(s.duration_sec for s in scenes), 1),
            scenes=scenes,
            full_narration_text=full_text
        )
