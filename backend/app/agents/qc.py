"""QCAgent: Strict Quality Control gate requiring score >= 90/100."""

import os
from typing import Dict, Any
from backend.app.agents.base import BaseAgent
from backend.app.core.ffmpeg_utils import probe_video_stream
from backend.app.models.video import QCReport


class QCAgent(BaseAgent):
    """Audits rendered Reels against Instagram resolution, audio, safe zones, and pacing."""

    MIN_PASSING_SCORE = 90.0

    def __init__(self):
        super().__init__("QCAgent")

    async def audit_video(
        self,
        video_path: str,
        min_duration: float = 15.0,
        max_duration: float = 65.0,
        subtitle_safe_zone_verified: bool = True
    ) -> QCReport:
        self.log(f"Auditing video: {video_path}")
        
        if not os.path.exists(video_path):
            return QCReport(passed=False, score=0.0, remediation_notes="Rendered video file does not exist on disk.")

        probe = probe_video_stream(video_path)
        score = 100.0
        deductions = []

        # 1. Resolution Check (Exact 1080x1920 required for Instagram Reels)
        w, h = probe.get("width", 0), probe.get("height", 0)
        if w != 1080 or h != 1920:
            score -= 15.0
            deductions.append(f"Resolution is {w}x{h}, expected 1080x1920.")

        # 2. Frame Rate Check (30 fps or 60 fps)
        fps = probe.get("fps", 0)
        if fps < 29.0:
            score -= 5.0
            deductions.append(f"Frame rate {fps} is below 30 fps.")

        # 3. Audio Stream Check
        has_audio = probe.get("has_audio", False)
        if not has_audio:
            score -= 25.0
            deductions.append("Video is missing audio stream.")

        # 4. Duration Check (15s - 65s)
        duration = probe.get("duration", 0.0)
        if duration < min_duration or duration > max_duration:
            score -= 8.0
            deductions.append(f"Duration {duration:.1f}s outside optimal window [{min_duration}s, {max_duration}s].")

        # 5. Subtitle Safe Zone Verification (65% - 75% height)
        if not subtitle_safe_zone_verified:
            score -= 10.0
            deductions.append("Subtitles encroach on Instagram UI overlays.")

        score = max(0.0, min(100.0, score))
        passed = score >= self.MIN_PASSING_SCORE

        remediation = "; ".join(deductions) if deductions else "All Instagram Reels quality benchmarks passed."
        self.log(f"QC Audit Result: Score {score:.1f}/100 - {'PASSED' if passed else 'FAILED'}")

        return QCReport(
            passed=passed,
            score=score,
            details=probe,
            remediation_notes=remediation
        )
