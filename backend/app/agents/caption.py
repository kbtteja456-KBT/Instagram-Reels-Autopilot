"""CaptionAgent: Word-level kinetic ASS subtitle generation within Instagram safe zones."""

import os
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from backend.app.agents.base import BaseAgent
from backend.app.config import settings
from backend.app.providers.stt.whisper_provider import WhisperSTTProvider


class CaptionAgent(BaseAgent):
    """Generates kinetic ASS subtitles placed strictly in the 65%-75% height safe zone."""

    def __init__(self, stt_provider: Optional[WhisperSTTProvider] = None):
        super().__init__("CaptionAgent")
        self.stt = stt_provider or WhisperSTTProvider()

    async def generate_captions(
        self,
        audio_filepath: str,
        job_id: str,
        script_text: Optional[str] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        self.log(f"Extracting word-level timestamps for job: {job_id}...")
        
        words = await self.stt.extract_word_timestamps(audio_filepath, script_text=script_text)

        captions_dir = settings.temp_path / job_id / "captions"
        captions_dir.mkdir(parents=True, exist_ok=True)
        ass_path = str(captions_dir / "kinetic_subtitles.ass")

        self._build_kinetic_ass_file(words, ass_path)
        self.log(f"Kinetic ASS subtitles generated: {ass_path}")

        return ass_path, words

    def _format_ass_time(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int(round((seconds - int(seconds)) * 100))
        if cs >= 100:
            cs = 99
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    def _build_kinetic_ass_file(self, words: List[Dict[str, Any]], out_path: str) -> None:
        """Create ASS file with typography calibrated for 1080x1920 Instagram Reels safe zone.
        MarginV is set to 550px from bottom -> subtitle center ~ 1370px down from top (71.3% height).
        """
        header = """[Script Info]
Title: AI Instagram Reels Kinetic Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: InstagramSafe,Arial Black,68,&H00FFFFFF,&H0000D4FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4.5,2,2,60,60,560,1
Style: HighlightWord,Arial Black,74,&H0000E5FF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,105,105,1,0,1,5.5,3,2,60,60,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        # Group words into short 3-4 word phrases for punchy reading velocity
        chunk_size = 3
        events = []

        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            if not chunk:
                continue
            chunk_start = chunk[0]["start"]
            chunk_end = chunk[-1]["end"]
            
            # Each word in chunk gets active kinetic focus
            for active_idx, w in enumerate(chunk):
                w_start = self._format_ass_time(w["start"])
                w_end = self._format_ass_time(w["end"])
                
                # Assemble phrase with active word highlighted in golden yellow (\c&H002BF7&)
                phrase_parts = []
                for j, item in enumerate(chunk):
                    w_upper = item["word"].upper()
                    if j == active_idx:
                        # Gold / Instagram neon highlight
                        phrase_parts.append(r"{\c&H00D4FF&\fscx112\fscy112}" + w_upper + r"{\r}")
                    else:
                        phrase_parts.append(r"{\c&H00FFFFFF}" + w_upper + r"{\r}")
                
                text_line = " ".join(phrase_parts)
                events.append(f"Dialogue: 0,{w_start},{w_end},InstagramSafe,,0,0,0,,{text_line}\n")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(header)
            f.writelines(events)
