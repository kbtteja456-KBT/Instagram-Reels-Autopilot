"""High-fidelity Quiz Card Reel video renderer replicating viral Python quiz aesthetic."""

import math
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pygments.lexers import PythonLexer
from pygments import token

from backend.app.config import settings
from backend.app.core.ffmpeg_utils import get_ffmpeg_binary
from backend.app.core.logging import logger


def get_token_color(ttype) -> Tuple[int, int, int]:
    """Map Pygments token types to modern dark theme syntax colors."""
    if ttype in token.Keyword or ttype in token.Keyword.Constant:
        return (244, 114, 182)  # Pink/Magenta (def, for, in, return)
    elif ttype in token.Name.Builtin or ttype in token.Name.Class:
        return (192, 132, 252)  # Purple (print, len, sorted, list, range)
    elif ttype in token.Name.Function:
        return (56, 189, 248)   # Bright Blue/Cyan
    elif ttype in token.Literal.Number:
        return (56, 189, 248)   # Sky Blue
    elif ttype in token.Literal.String:
        return (134, 239, 172)  # Light Green
    elif ttype in token.Operator:
        return (147, 197, 253)  # Soft Blue (=, +, ==, %)
    elif ttype in token.Comment:
        return (100, 116, 139)  # Slate Gray
    elif ttype in token.Punctuation:
        return (200, 210, 225)  # Soft Silver (brackets, colons, parens)
    else:
        return (245, 248, 255)  # Crisp White (variable names, text)


class QuizCardRenderer:
    """Renders 1080x1920 30fps vertical reels matching the reference quiz card design."""

    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.ffmpeg_bin = get_ffmpeg_binary()

        # Load fonts
        self.font_title = self._load_font("C:/Windows/Fonts/segoeuib.ttf", 52)
        self.font_header_badge = self._load_font("C:/Windows/Fonts/segoeuib.ttf", 36)
        self.font_code = self._load_font("C:/Windows/Fonts/consolab.ttf", 36, is_mono=True)
        self.font_code_tab = self._load_font("C:/Windows/Fonts/segoeui.ttf", 30)
        self.font_badge = self._load_font("C:/Windows/Fonts/segoeuib.ttf", 32)
        self.font_option_letter = self._load_font("C:/Windows/Fonts/segoeuib.ttf", 38)
        self.font_option_text = self._load_font("C:/Windows/Fonts/consolab.ttf", 38, is_mono=True)
        self.font_explain = self._load_font("C:/Windows/Fonts/segoeuib.ttf", 34)
        self.font_explain_sub = self._load_font("C:/Windows/Fonts/segoeui.ttf", 28)

        # Pre-render background gradient template for maximum performance
        self._bg_template = Image.new("RGB", (self.width, self.height), (247, 249, 252))
        draw_bg = ImageDraw.Draw(self._bg_template)
        for i in range(0, self.height, 4):
            blend = i / self.height
            r = int(252 * (1 - blend) + 243 * blend)
            g = int(253 * (1 - blend) + 246 * blend)
            b = int(255 * (1 - blend) + 250 * blend)
            draw_bg.line([(0, i), (self.width, i + 3)], fill=(r, g, b), width=4)

    def _load_font(self, font_path: str, size: int, is_mono: bool = False) -> ImageFont.FreeTypeFont:
        candidates = [
            font_path,
            f"C:/Windows/Fonts/{os.path.basename(font_path)}",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if is_mono else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf" if is_mono else "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf" if is_mono else "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "arial.ttf"
        ]
        for c in candidates:
            try:
                if os.path.exists(c) or not os.path.isabs(c):
                    return ImageFont.truetype(c, size)
            except Exception:
                continue
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()

    def _draw_python_logo(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int = 54):
        """Draw iconic Python two-tone yellow/blue icon."""
        blue = (55, 118, 171)
        yellow = (255, 212, 59)
        s = size // 2
        
        # Upper blue curve
        draw.rounded_rectangle([x, y, x + s + 10, y + s + 6], radius=8, fill=blue)
        draw.ellipse([x + 6, y + 4, x + 14, y + 12], fill=(255, 255, 255))
        
        # Lower yellow curve
        draw.rounded_rectangle([x + 12, y + 16, x + size, y + size], radius=8, fill=yellow)
        draw.ellipse([x + size - 14, y + size - 12, x + size - 6, y + size - 4], fill=(255, 255, 255))

    def _draw_bulb_icon(self, draw: ImageDraw.ImageDraw, x: int, y: int):
        """Draw small clean lightbulb icon."""
        draw.ellipse([x, y, x + 22, y + 22], fill=(245, 158, 11))
        draw.rectangle([x + 6, y + 20, x + 16, y + 26], fill=(180, 110, 8))

    def _draw_checkmark(self, draw: ImageDraw.ImageDraw, x: int, y: int):
        """Draw crisp white checkmark."""
        draw.line([(x, y + 12), (x + 8, y + 20)], fill=(255, 255, 255), width=4)
        draw.line([(x + 8, y + 20), (x + 22, y + 4)], fill=(255, 255, 255), width=4)

    def _tokenize_code(self, code_str: str) -> List[List[Tuple[str, Tuple[int, int, int]]]]:
        """Tokenize code into lines with syntax highlighting colors."""
        lines = code_str.split("\n")
        lexer = PythonLexer()
        tokenized_lines = []
        for line in lines:
            line_tokens = []
            for ttype, val in lexer.get_tokens(line):
                val_clean = val.replace("\n", "").replace("\r", "")
                if val_clean:
                    color = get_token_color(ttype)
                    line_tokens.append((val_clean, color))
            tokenized_lines.append(line_tokens)
        return tokenized_lines

    def render_quiz_frame(
        self,
        t: float,
        quiz_data: Dict[str, Any],
        total_duration: float,
        options_start_t: float = 6.5,
        countdown_start_t: float = 11.0,
        countdown_end_t: float = 16.5,
        reveal_start_t: float = 16.5
    ) -> Image.Image:
        """Render a single 1080x1920 frame at time t (seconds)."""
        img = self._bg_template.copy()
        draw = ImageDraw.Draw(img)

        # 1. Top Header
        header_y = 120
        self._draw_python_logo(draw, 90, header_y - 8, size=54)
        draw.text((160, header_y), "PYTHON QUIZ", font=self.font_header_badge, fill=(71, 85, 105))

        # Main Question
        q_y = header_y + 70
        question_text = quiz_data.get("question", "What is the output of this code?")
        draw.text((90, q_y), question_text, font=self.font_title, fill=(15, 23, 42))

        # 2. macOS Dark Code Window
        box_x = 90
        box_y = q_y + 100
        box_w = 900
        
        # Calculate height based on lines of code
        code_str = quiz_data.get("code", "")
        code_lines = self._tokenize_code(code_str)
        line_height = 54
        box_h = max(460, 120 + len(code_lines) * line_height)
        box_r = 28

        # Code box drop shadow
        shadow_rect = [box_x + 4, box_y + 12, box_x + box_w + 4, box_y + box_h + 12]
        draw.rounded_rectangle(shadow_rect, radius=box_r, fill=(215, 222, 232))

        # Dark editor body
        draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=box_r, fill=(28, 33, 43))

        # macOS traffic dots
        dot_y = box_y + 36
        draw.ellipse([box_x + 36, dot_y, box_x + 56, dot_y + 20], fill=(255, 95, 86))
        draw.ellipse([box_x + 68, dot_y, box_x + 88, dot_y + 20], fill=(255, 189, 46))
        draw.ellipse([box_x + 100, dot_y, box_x + 120, dot_y + 20], fill=(39, 201, 63))

        # Tab name
        tab_name = quiz_data.get("file_tab", "main.py")
        draw.text((box_x + 150, box_y + 30), tab_name, font=self.font_code_tab, fill=(130, 145, 165))

        # Draw Code lines
        code_start_y = box_y + 100
        for i, line_tokens in enumerate(code_lines):
            ly = code_start_y + i * line_height
            line_num_str = f"{i + 1} |"
            draw.text((box_x + 36, ly), line_num_str, font=self.font_code, fill=(80, 95, 115))
            cx = box_x + 105
            for text, color in line_tokens:
                draw.text((cx, ly), text, font=self.font_code, fill=color)
                cx += int(draw.textlength(text, font=self.font_code))

        # 3. Badges (Timer Pill on Left, "Think carefully!" Pill on Right)
        badge_y = box_y + box_h + 26
        badge_h = 56

        # Left: Interactive 15-second countdown timer badge
        timer_w = 260
        timer_x = box_x
        if t < countdown_end_t:
            rem_sec = max(1, int(countdown_end_t - t) + 1)
            is_urgent = rem_sec <= 4
            t_bg = (254, 226, 226) if is_urgent else (224, 242, 254)
            t_border = (239, 68, 68) if is_urgent else (2, 132, 199)
            t_text_color = (185, 28, 28) if is_urgent else (3, 105, 161)
            t_label = f"Time: {rem_sec}s"
        else:
            t_bg = (209, 250, 229)
            t_border = (16, 185, 129)
            t_text_color = (4, 120, 87)
            t_label = "TIME'S UP!"

        draw.rounded_rectangle(
            [timer_x, badge_y, timer_x + timer_w, badge_y + badge_h],
            radius=18,
            fill=t_bg,
            outline=t_border,
            width=2
        )
        # Clock circle icon
        clock_cx = timer_x + 32
        clock_cy = badge_y + badge_h // 2
        draw.ellipse([clock_cx - 14, clock_cy - 14, clock_cx + 14, clock_cy + 14], fill=t_border)
        draw.line([(clock_cx, clock_cy), (clock_cx, clock_cy - 8)], fill=(255, 255, 255), width=2)
        draw.line([(clock_cx, clock_cy), (clock_cx + 6, clock_cy)], fill=(255, 255, 255), width=2)
        draw.text((timer_x + 60, badge_y + 10), t_label, font=self.font_badge, fill=t_text_color)

        # Right: "Think carefully!" Badge
        think_w = 340
        think_x = box_x + box_w - think_w
        badge_text = quiz_data.get("badge_text", "Think carefully!")
        draw.rounded_rectangle(
            [think_x, badge_y, think_x + think_w, badge_y + badge_h],
            radius=18,
            fill=(254, 243, 199),
            outline=(245, 158, 11),
            width=2
        )
        self._draw_bulb_icon(draw, think_x + 22, badge_y + 14)
        draw.text((think_x + 56, badge_y + 10), badge_text, font=self.font_badge, fill=(146, 64, 14))

        # 4. Animated 15-Second Progress Bar
        bar_y = badge_y + badge_h + 16
        draw.rounded_rectangle([box_x, bar_y, box_x + box_w, bar_y + 12], radius=6, fill=(226, 232, 240))
        if t <= countdown_end_t:
            cd_progress = max(0.0, min(1.0, (t - countdown_start_t) / max(0.1, countdown_end_t - countdown_start_t)))
            bar_w = int(box_w * (1.0 - cd_progress))
            if bar_w > 0:
                bar_color = (239, 68, 68) if cd_progress > 0.7 else (2, 132, 199)
                draw.rounded_rectangle([box_x, bar_y, box_x + bar_w, bar_y + 12], radius=6, fill=bar_color)
        else:
            # Full green bar on reveal
            draw.rounded_rectangle([box_x, bar_y, box_x + box_w, bar_y + 12], radius=6, fill=(16, 185, 129))

        # 5. Four Option Cards (Visible right from t=0 so viewers can solve!)
        options_start_y = bar_y + 30
        card_h = 108
        card_spacing = 22

        color_palette = [
            ((239, 68, 68), (254, 242, 242), (252, 165, 165)),    # A: Red
            ((59, 130, 246), (239, 246, 255), (147, 197, 253)),   # B: Blue
            ((245, 158, 11), (255, 251, 235), (252, 211, 77)),    # C: Amber
            ((168, 85, 247), (250, 245, 255), (216, 180, 254))    # D: Purple
        ]

        options_data = quiz_data.get("options", [])
        correct_idx = quiz_data.get("correct_idx", 0)
        is_revealed = t >= reveal_start_t

        for idx, opt in enumerate(options_data):
            letter = opt.get("letter", chr(65 + idx))
            opt_text = opt.get("text", "")
            color_primary, color_bg, color_border = color_palette[idx % 4]

            oy = options_start_y + idx * (card_h + card_spacing)

            # Reveal styling
            if is_revealed:
                if idx == correct_idx:
                    bg_fill = (220, 252, 231)  # Emerald light
                    border_fill = (16, 185, 129)  # Emerald green
                    border_w = 4
                    badge_color = (16, 185, 129)
                    text_color = (6, 95, 70)
                else:
                    bg_fill = (248, 250, 252)
                    border_fill = (226, 232, 240)
                    border_w = 2
                    badge_color = (148, 163, 184)
                    text_color = (148, 163, 184)
            else:
                bg_fill = color_bg
                border_fill = color_border
                border_w = 2
                badge_color = color_primary
                text_color = (30, 41, 59)

            # Draw card rounded container
            draw.rounded_rectangle(
                [box_x, oy, box_x + box_w, oy + card_h],
                radius=30,
                fill=bg_fill,
                outline=border_fill,
                width=border_w
            )

            # Circular letter badge
            circle_cx = box_x + 56
            circle_cy = oy + card_h // 2
            circle_rad = 34
            draw.ellipse(
                [circle_cx - circle_rad, circle_cy - circle_rad, circle_cx + circle_rad, circle_cy + circle_rad],
                fill=badge_color
            )
            # Letter text
            lw = draw.textlength(letter, font=self.font_option_letter)
            draw.text((circle_cx - lw // 2, circle_cy - 22), letter, font=self.font_option_letter, fill=(255, 255, 255))

            # Option code text
            draw.text((box_x + 125, oy + 32), opt_text, font=self.font_option_text, fill=text_color)

            # Add "CORRECT [check]" tag if revealed
            if is_revealed and idx == correct_idx:
                tag_x = box_x + box_w - 235
                draw.rounded_rectangle(
                    [tag_x, oy + 26, tag_x + 195, oy + card_h - 26],
                    radius=16,
                    fill=(16, 185, 129)
                )
                self._draw_checkmark(draw, tag_x + 16, oy + 30)
                draw.text((tag_x + 48, oy + 30), "CORRECT", font=self.font_badge, fill=(255, 255, 255))

        # 6. Explanation Card (Slides up on reveal)
        if is_revealed:
            exp_y = options_start_y + 4 * (card_h + card_spacing) + 10
            exp_h = 240
            draw.rounded_rectangle(
                [box_x, exp_y, box_x + box_w, exp_y + exp_h],
                radius=26,
                fill=(240, 253, 244),
                outline=(16, 185, 129),
                width=3
            )
            # Title
            draw.text((box_x + 36, exp_y + 24), "Explanation & Answer:", font=self.font_explain, fill=(6, 95, 70))
            
            explanation_lines = quiz_data.get("explanation_lines", [])
            for li, line_text in enumerate(explanation_lines[:2]):
                draw.text(
                    (box_x + 36, exp_y + 75 + li * 45),
                    line_text,
                    font=self.font_explain_sub,
                    fill=(21, 128, 61)
                )

            # CTA
            draw.text(
                (box_x + 36, exp_y + 175),
                "Save this Reel & follow for daily Python quizzes!",
                font=self.font_explain,
                fill=(15, 23, 42)
            )

        return img

    def render_quiz_video(
        self,
        output_video_path: str,
        quiz_data: Dict[str, Any],
        total_duration_sec: float = 20.0,
        options_start_t: float = 0.0,
        countdown_start_t: float = 0.0,
        countdown_end_t: float = 15.0,
        reveal_start_t: float = 15.0,
        fps: int = 30
    ) -> str:
        """Render frame sequence directly to MP4 vertical video via FFmpeg pipe."""
        Path(output_video_path).parent.mkdir(parents=True, exist_ok=True)
        total_frames = int(total_duration_sec * fps)

        # Low-memory FFmpeg configuration for cloud instances (Render 512MB RAM limit)
        # Using -threads 1, small buffer size, and direct raw rgb24 piping avoids multi-thread bloat
        cmd = [
            self.ffmpeg_bin, "-y",
            "-loglevel", "error",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "rgb24",
            "-r", str(fps),
            "-i", "-",
            "-threads", "1",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-bufsize", "3000k",
            "-maxrate", "5000k",
            "-pix_fmt", "yuv420p",
            output_video_path
        ]

        logger.info(f"[QuizCardRenderer] Rendering {total_frames} frames ({total_duration_sec:.1f}s) to {output_video_path} [Low-Memory Mode]...")
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

        import gc
        for f in range(total_frames):
            t = f / fps
            frame_img = self.render_quiz_frame(
                t=t,
                quiz_data=quiz_data,
                total_duration=total_duration_sec,
                options_start_t=options_start_t,
                countdown_start_t=countdown_start_t,
                countdown_end_t=countdown_end_t,
                reveal_start_t=reveal_start_t
            )
            # Write raw RGB bytes directly from PIL (zero cv2/numpy allocation overhead)
            proc.stdin.write(frame_img.tobytes())
            del frame_img

            # Periodic garbage collection every 60 frames to keep RAM rock steady
            if f % 60 == 0:
                gc.collect()

        proc.stdin.close()
        proc.wait()

        if proc.returncode != 0 or not os.path.exists(output_video_path):
            raise RuntimeError(f"FFmpeg rawvideo pipe render failed with return code {proc.returncode}")

        logger.info(f"[QuizCardRenderer] Video track successfully rendered: {output_video_path}")
        return output_video_path

    def assemble_final_reel(
        self,
        video_track_path: str,
        audio_track_path: str,
        output_mp4_path: str
    ) -> str:
        """Mux video track and mixed audio track into Instagram-ready MP4 with low memory footprint."""
        Path(output_mp4_path).parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.ffmpeg_bin, "-y",
            "-threads", "1",
            "-i", video_track_path,
            "-i", audio_track_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-shortest",
            output_mp4_path
        ]
        logger.info(f"[QuizCardRenderer] Muxing video and audio into final Reel: {output_mp4_path}...")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0 or not os.path.exists(output_mp4_path):
            raise RuntimeError(f"Failed muxing final Reel: {proc.stderr}")
        return output_mp4_path
