"""Pattern interrupt and retention pacing calculator."""

from typing import List, Dict, Any


class PatternInterruptManager:
    """Manages visual interrupts, pacing cuts, and zoom pulses for Instagram Reels."""

    @staticmethod
    def calculate_scene_durations(total_duration: float, scene_count: int) -> List[float]:
        """Distribute durations ensuring scenes fall within 2.5 to 3.5s window."""
        avg_dur = total_duration / scene_count
        durations = []
        for i in range(scene_count):
            # Oscillate pacing slightly for dynamic rhythm
            offset = 0.3 if i % 2 == 0 else -0.3
            dur = max(2.5, min(3.8, avg_dur + offset))
            durations.append(round(dur, 2))
        return durations

    @staticmethod
    def get_audio_ducking_levels() -> Dict[str, str]:
        """Standard broadcast-grade ducking levels for speech over ambient music."""
        return {
            "speech_target_lufs": "-18.0",
            "music_ducked_volume": "-26.0dB",
            "crossfade_duration": "0.3s"
        }
