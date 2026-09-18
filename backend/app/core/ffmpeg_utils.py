"""FFmpeg path resolution and media probing utilities."""

import os
import shutil
import subprocess
import json
from typing import Dict, Any, Optional
from backend.app.core.logging import logger


def get_ffmpeg_binary() -> str:
    """Resolve FFmpeg binary path from environment, system PATH, or imageio-ffmpeg."""
    # 1. System PATH
    which_ffmpeg = shutil.which("ffmpeg")
    if which_ffmpeg:
        return which_ffmpeg

    # 2. Try imageio_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass

    # 3. Default fallback
    return "ffmpeg"


def get_ffprobe_binary() -> str:
    """Resolve FFprobe binary path."""
    which_ffprobe = shutil.which("ffprobe")
    if which_ffprobe:
        return which_ffprobe
    return "ffprobe"


def probe_video_stream(video_path: str) -> Dict[str, Any]:
    """Inspect video container and return stream metadata (resolution, fps, duration)."""
    ffprobe_bin = get_ffprobe_binary()
    cmd = [
        ffprobe_bin,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        
        v_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
        a_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})
        
        width = int(v_stream.get("width", 0))
        height = int(v_stream.get("height", 0))
        
        # Calculate fps
        r_frame_rate = v_stream.get("r_frame_rate", "30/1")
        if "/" in r_frame_rate:
            num, den = map(float, r_frame_rate.split("/"))
            fps = num / den if den != 0 else 30.0
        else:
            fps = float(r_frame_rate) if r_frame_rate else 30.0
            
        duration = float(data.get("format", {}).get("duration", v_stream.get("duration", 0.0)))
        
        return {
            "width": width,
            "height": height,
            "fps": round(fps, 2),
            "duration": round(duration, 2),
            "has_audio": bool(a_stream),
            "video_codec": v_stream.get("codec_name", ""),
            "audio_codec": a_stream.get("codec_name", "")
        }
    except Exception as e:
        # Fallback to OpenCV VideoCapture when ffprobe is not available on Windows
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = round(frame_count / fps, 2) if fps > 0 else 40.0
                cap.release()
                return {
                    "width": width or 1080,
                    "height": height or 1920,
                    "fps": round(fps, 2),
                    "duration": duration,
                    "has_audio": True,
                    "video_codec": "h264",
                    "audio_codec": "aac"
                }
        except Exception:
            pass

        logger.warning(f"[FFprobe] Probe failed for {video_path}: {e}")
        return {
            "width": 1080,
            "height": 1920,
            "fps": 30.0,
            "duration": 45.0,
            "has_audio": True,
            "video_codec": "h264",
            "audio_codec": "aac"
        }
