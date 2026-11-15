"""Master Production Animation Studio: Educational Engine (Alan Becker Style).
Generates the definitive 2-Error live-coding 2D stickman programming Reel.

Core Design Rules:
1. ZERO VOICE NARRATION: Pure international visual comedy + punchy Foley SFX.
2. NO GHOST STICKMAN: Desk & chair is 100% EMPTY when stickman walks in from left (t=0.0s to 2.8s)!
3. LAPTOP OPPOSITE STICKMAN: Laptop screen tilted rightward toward stickman's eyes and hands.
4. PROGRESSIVE TYPING: Characters type letter-by-letter with mechanical keyboard clacking SFX.
5. 2 BEGINNER ERRORS DEMONSTRATED FIRST:
   - Error 1: Using unassigned variable -> NameError: name 'score' is not defined + buzzer SFX!
   - Error 2: Starting variable name with a number -> SyntaxError: invalid decimal literal + buzzer SFX!
6. 5-SECOND PACING & THINKING PHASE: Leaps out of chair, walks back and forth scratching chin (? ?).
7. BACKSPACE & LIVE FIX: Returns to chair, clears mistakes, types clean working code.
8. GREEN SUCCESS & "YAAAYYY!" VICTORY:
   - Strikes Enter -> Emerald Green terminal output [Program finished with exit code 0] + ding SFX!
   - Leaps into center floor jumping and pumping fists shouting "YAAAYYY!" + golden stars + chime SFX!
9. ZERO-OVERFLOW TAKEAWAY BOX: Framed Golden Key Takeaway box with exact padding.
10. INSTAGRAM SAFE ZONE COMPLIANCE:
    - Avoids top 220px and bottom 320px.
    - Follow CTA at Y=1720: "▶ FOLLOW FOR EPISODE 2!"
"""

import os
import sys
import math
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings
from backend.app.core.ffmpeg_utils import get_ffmpeg_binary
from backend.app.core.logging import logger

FFMPEG = get_ffmpeg_binary()
STORAGE = Path(settings.media_storage_dir)
TEMP_DIR = settings.temp_path / "master_trial_studio"
FRAMES_DIR = TEMP_DIR / "frames"
RENDERED_DIR = settings.reels_output_path
THUMBNAILS_DIR = STORAGE / "thumbnails"
SFX_DIR = STORAGE / "assets" / "sfx"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
FRAMES_DIR.mkdir(parents=True, exist_ok=True)
RENDERED_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

# 1080x1920 9:16 Instagram Reels Standard
WIDTH = 1080
HEIGHT = 1920
FPS = 30
TOTAL_SECONDS = 42.0
TOTAL_FRAMES = int(FPS * TOTAL_SECONDS)  # 1260 frames

# Palette
BG_COLOR = (11, 14, 20)
STICK_YELLOW = (255, 215, 0)
CYAN_KEYWORD = (56, 189, 248)
AMBER_NUMBER = (251, 146, 60)
PURPLE_OP = (192, 132, 252)
GREEN_STRING = (52, 211, 153)
WHITE_VAR = (241, 245, 249)
MUTED_TEXT = (100, 116, 139)
CARD_BG = (17, 24, 39)
CARD_BORDER = (31, 41, 55)
TERMINAL_BG = (10, 15, 26)
TERMINAL_BORDER = (30, 41, 59)
ERROR_RED = (239, 68, 68)
SUCCESS_GREEN = (34, 197, 94)
LAPTOP_SILVER = (190, 200, 215)


def load_cross_platform_font(font_names: List[str], size: int) -> ImageFont.ImageFont:
    """Search Windows and Linux font directories for matching fonts."""
    search_dirs = [
        Path("C:/Windows/Fonts"),
        Path("/usr/share/fonts/truetype"),
        Path("/usr/share/fonts/truetype/liberation"),
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts"),
        Path.home() / ".fonts",
    ]
    for name in font_names:
        p = Path(name)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
        for d in search_dirs:
            if not d.exists():
                continue
            candidate = d / name
            if candidate.exists():
                try:
                    return ImageFont.truetype(str(candidate), size)
                except Exception:
                    pass
            matches = list(d.rglob(name))
            if matches:
                try:
                    return ImageFont.truetype(str(matches[0]), size)
                except Exception:
                    pass
    return ImageFont.load_default()


FONT_CODE = load_cross_platform_font(["consola.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"], 32)
FONT_CODE_BOLD = load_cross_platform_font(["consolab.ttf", "LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"], 32)
FONT_HEADER = load_cross_platform_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 42)
FONT_SUBTITLE = load_cross_platform_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 22)
FONT_TERM = load_cross_platform_font(["consola.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"], 26)
FONT_TERM_BOLD = load_cross_platform_font(["consolab.ttf", "LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"], 28)
FONT_ALERT = load_cross_platform_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 28)
FONT_COMIC = load_cross_platform_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 36)


def tokenize_code(line: str) -> List[Tuple[str, Tuple[int, int, int]]]:
    """Tokenize Python source line into colored syntax tokens."""
    keywords_py = {
        'def', 'return', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'in',
        'class', 'print', 'str', 'int', 'float', 'bool', 'True', 'False', 'None'
    }

    pattern = re.compile(r'(f\".*?\"|f\'.*?\'|\".*?\"|\'.*?\'|\#.*|\b\d+\b|\b[a-zA-Z_]\w*\b|[^\s\w]|\s+)')
    tokens = []
    for match in pattern.finditer(line):
        token = match.group()
        if token.startswith('#'):
            tokens.append((token, MUTED_TEXT))
        elif (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
            tokens.append((token, GREEN_STRING))
        elif token.startswith('f"') or token.startswith("f'"):
            tokens.append((token, GREEN_STRING))
        elif token.isdigit():
            tokens.append((token, AMBER_NUMBER))
        elif token in keywords_py:
            tokens.append((token, CYAN_KEYWORD))
        elif token in '+-*/=<>!&|^%:':
            tokens.append((token, PURPLE_OP))
        else:
            tokens.append((token, WHITE_VAR))
    return tokens


def draw_python_logo(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 36):
    """Draw Python dual-color snake logo."""
    draw.rounded_rectangle([cx - size, cy - size, cx, cy], radius=size // 4, fill=(56, 114, 164))
    draw.ellipse([cx - size * 0.7, cy - size * 0.7, cx - size * 0.4, cy - size * 0.4], fill=(255, 255, 255))
    draw.rounded_rectangle([cx, cy, cx + size, cy + size], radius=size // 4, fill=(255, 212, 59))
    draw.ellipse([cx + size * 0.4, cy + size * 0.4, cx + size * 0.7, cy + size * 0.7], fill=(11, 14, 20))


def draw_window_frame(draw: ImageDraw.ImageDraw, x0: int, y0: int, x1: int, y1: int, title: str = "main.py", is_terminal: bool = False):
    """Draw modern IDE window frame with macOS buttons."""
    bg = TERMINAL_BG if is_terminal else CARD_BG
    border = TERMINAL_BORDER if is_terminal else CARD_BORDER
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=bg, outline=border, width=2)
    draw.rounded_rectangle([x0, y0, x1, y0 + 44], radius=16, fill=(22, 30, 46) if is_terminal else (26, 36, 54))
    draw.rectangle([x0, y0 + 30, x1, y0 + 44], fill=(22, 30, 46) if is_terminal else (26, 36, 54))
    draw.ellipse([x0 + 16, y0 + 15, x0 + 28, y0 + 27], fill=(239, 68, 68))
    draw.ellipse([x0 + 36, y0 + 15, x0 + 48, y0 + 27], fill=(245, 158, 11))
    draw.ellipse([x0 + 56, y0 + 15, x0 + 68, y0 + 27], fill=(34, 197, 94))
    t_color = (148, 163, 184) if is_terminal else (203, 213, 225)
    draw.text((x0 + 80, y0 + 11), title, fill=t_color, font=FONT_SUBTITLE)


def draw_empty_desk_and_chair(draw: ImageDraw.ImageDraw, dx: int = 540, dy: int = 1460):
    """Draw ONLY the furniture & laptop. Chair is empty (no ghost stickman!)."""
    # Desk
    dw, dh = 300, 14
    dx0, dx1 = dx - dw // 2, dx + dw // 2
    draw.rounded_rectangle([dx0, dy, dx1, dy + dh], radius=6, fill=(45, 55, 75), outline=(70, 85, 115), width=2)
    draw.line([(dx0 + 25, dy + dh), (dx0 + 25, 1560)], fill=(70, 85, 115), width=4)
    draw.line([(dx1 - 25, dy + dh), (dx1 - 25, 1560)], fill=(70, 85, 115), width=4)

    # Empty Chair at x=710
    cx, cy = 710, dy + 25
    draw.rounded_rectangle([cx - 30, cy, cx + 30, cy + 10], radius=4, fill=(55, 65, 88))
    draw.line([(cx + 25, cy - 85), (cx + 25, cy + 10)], fill=(55, 65, 88), width=5)
    draw.line([(cx, cy + 10), (cx, 1560)], fill=(40, 50, 70), width=4)
    draw.line([(cx - 25, 1560), (cx + 25, 1560)], fill=(40, 50, 70), width=3)

    # Laptop on desk facing stickman (screen tilted right toward stickman's eyes)
    lx_left, lx_right = 510, 625
    draw.polygon([
        (lx_left, dy),
        (lx_right, dy),
        (lx_right - 8, dy + 8),
        (lx_left + 8, dy + 8)
    ], fill=LAPTOP_SILVER, outline=(160, 175, 195))
    draw.rectangle([560, dy + 2, 585, dy + 6], fill=(180, 190, 205))

    sx_hinge = lx_left + 5
    sy_hinge = dy
    sx_top = sx_hinge - 28
    sy_top = dy - 68
    draw.polygon([(sx_hinge - 4, sy_hinge), (sx_hinge, sy_hinge), (sx_top, sy_top), (sx_top - 4, sy_top)], fill=(160, 175, 195))
    draw.polygon([(sx_hinge, sy_hinge), (sx_hinge + 45, sy_hinge - 15), (sx_top + 45, sy_top), (sx_top, sy_top)], fill=(45, 95, 155), outline=(56, 189, 248), width=1)


def draw_stickman_actor(draw: ImageDraw.ImageDraw, action: str = "walk_in", walk_x: int = 100, t: float = 0.0):
    """Single master stickman actor function. Ensures EXACTLY ONE stickman exists at any time."""
    color = STICK_YELLOW
    head_r = 24

    if action == "walk_in":
        # Walking from left to right toward chair
        hx = walk_x
        hy = 1400
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill=color)
        neck = (hx, hy + head_r)
        hip = (hx, hy + head_r + 80)
        draw.line([neck, hip], fill=color, width=7)
        leg_p = math.sin(t * 14.0) * 28.0
        draw.line([hip, (hip[0] + leg_p, 1550)], fill=color, width=6)
        draw.line([hip, (hip[0] - leg_p, 1550)], fill=color, width=6)
        arm_p = math.sin(t * 14.0) * 22.0
        draw.line([neck, (neck[0] - arm_p, neck[1] + 45)], fill=color, width=6)
        draw.line([neck, (neck[0] + arm_p, neck[1] + 45)], fill=color, width=6)

    elif action in ("sitting_typing", "sitting_enter", "sitting_idle", "sitting_shocked"):
        # Sitting on chair at x=700, hands on keyboard
        hx = 700
        hy = 1390
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill=color)
        neck = (hx - 4, hy + head_r)
        hip = (705, 1485)
        draw.line([neck, hip], fill=color, width=7)
        knee = (640, 1495)
        foot = (630, 1550)
        draw.line([hip, knee], fill=color, width=6)
        draw.line([knee, foot], fill=color, width=6)

        shoulder = (neck[0] - 2, neck[1] + 12)
        if action == "sitting_typing":
            t_wave = math.sin(t * 28.0) * 6.0
            draw.line([shoulder, (650, 1445)], fill=color, width=6)
            draw.line([(650, 1445), (585, 1460 + t_wave)], fill=color, width=6)
        elif action == "sitting_enter":
            draw.line([shoulder, (640, 1435)], fill=color, width=6)
            draw.line([(640, 1435), (580, 1452)], fill=color, width=6)
        elif action == "sitting_shocked":
            # Throws hands up in disbelief!
            draw.line([shoulder, (shoulder[0] - 30, shoulder[1] - 40)], fill=color, width=6)
            draw.line([shoulder, (shoulder[0] + 25, shoulder[1] - 40)], fill=color, width=6)
            # Comic shock exclamation mark above head
            draw.text((hx - 6, hy - 60), "!", fill=ERROR_RED, font=FONT_HEADER)
        else:
            draw.line([shoulder, (655, 1450)], fill=color, width=6)
            draw.line([(655, 1450), (595, 1460)], fill=color, width=6)

    elif action == "pacing_thinking":
        # Out of chair! Walking back and forth between x=620 and x=320, hand on chin thinking
        pace_x = int(470 + math.sin(t * 2.8) * 150)
        hx = pace_x
        hy = 1400
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill=color)
        neck = (hx, hy + head_r)
        hip = (hx, hy + head_r + 80)
        draw.line([neck, hip], fill=color, width=7)

        # Walking legs
        leg_p = math.sin(t * 10.0) * 22.0
        draw.line([hip, (hip[0] + leg_p, 1550)], fill=color, width=6)
        draw.line([hip, (hip[0] - leg_p, 1550)], fill=color, width=6)

        # Right hand on chin thinking, left arm folded
        shoulder = (neck[0], neck[1] + 12)
        draw.line([shoulder, (hx - 15, hy + 50)], fill=color, width=6)
        draw.line([shoulder, (hx + 18, hy + 30)], fill=color, width=6)
        draw.line([(hx + 18, hy + 30), (hx + 4, hy + 18)], fill=color, width=6)

        # Animated floating question marks
        q_wiggle = math.sin(t * 6.0) * 6
        draw.text((hx - 35, hy - 65 + q_wiggle), "?", fill=ERROR_RED, font=FONT_HEADER)
        draw.text((hx + 28, hy - 75 - q_wiggle), "?", fill=AMBER_NUMBER, font=FONT_HEADER)

    elif action == "yaay_celebrate":
        # LEAPED OUT OF CHAIR! Jumping in the air in center floor with YAAAYYY!
        jump_y = int(math.sin(t * 8.0) * 35)
        hx = 450
        hy = 1380 - abs(jump_y)
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill=color)
        neck = (hx, hy + head_r)
        hip = (hx, hy + head_r + 80)
        draw.line([neck, hip], fill=color, width=7)

        # Jumping legs spread wide
        draw.line([hip, (hip[0] - 35, 1550 - abs(jump_y) + 10)], fill=color, width=6)
        draw.line([hip, (hip[0] + 35, 1550 - abs(jump_y) + 10)], fill=color, width=6)

        # Both arms pumping the air in victory!
        shoulder = (neck[0], neck[1] + 10)
        draw.line([shoulder, (shoulder[0] - 40, shoulder[1] - 35)], fill=color, width=6)
        draw.line([(shoulder[0] - 40, shoulder[1] - 35), (shoulder[0] - 65, shoulder[1] - 65)], fill=color, width=6)
        draw.line([shoulder, (shoulder[0] + 40, shoulder[1] - 35)], fill=color, width=6)
        draw.line([(shoulder[0] + 40, shoulder[1] - 35), (shoulder[0] + 65, shoulder[1] - 65)], fill=color, width=6)

        # Big Comic Speech Bubble: YAAAYYY!
        draw.rounded_rectangle([hx - 95, hy - 110, hx + 95, hy - 50], radius=16, fill=(250, 204, 21), outline=(255, 255, 255), width=3)
        draw.text((hx - 80, hy - 102), "YAAAYYY!", fill=(11, 14, 20), font=FONT_COMIC)

        # Sparkle celebration stars
        for sx, sy in [(hx - 140, hy - 40), (hx + 130, hy - 30), (hx - 90, hy + 50), (hx + 100, hy + 60)]:
            s_wiggle = 5 + int(3 * math.sin(t * 12.0))
            draw.line([(sx - s_wiggle, sy), (sx + s_wiggle, sy)], fill=(255, 215, 0), width=3)
            draw.line([(sx, sy - s_wiggle), (sx, sy + s_wiggle)], fill=(255, 215, 0), width=3)

    elif action == "thumbs_up":
        # Standing proudly next to desk, giving big thumbs up!
        hx = 480
        hy = 1400
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill=color)
        neck = (hx, hy + head_r)
        hip = (hx, hy + head_r + 80)
        draw.line([neck, hip], fill=color, width=7)
        draw.line([hip, (hip[0] - 18, 1550)], fill=color, width=6)
        draw.line([hip, (hip[0] + 18, 1550)], fill=color, width=6)
        shoulder = (neck[0], neck[1] + 12)
        draw.line([shoulder, (shoulder[0] - 25, shoulder[1] + 45)], fill=color, width=6)
        draw.line([shoulder, (shoulder[0] + 35, shoulder[1] - 10)], fill=color, width=6)
        draw.line([(shoulder[0] + 35, shoulder[1] - 10), (shoulder[0] + 55, shoulder[1] - 25)], fill=color, width=6)
        draw.line([(shoulder[0] + 55, shoulder[1] - 25), (shoulder[0] + 55, shoulder[1] - 40)], fill=color, width=7)


def render_code_tokens(draw: ImageDraw.ImageDraw, x_start: int, y: int, tokens: List[Tuple[str, Tuple[int, int, int]]]) -> int:
    """Render syntax highlighted tokens horizontally."""
    cur_x = x_start
    for text, col in tokens:
        draw.text((cur_x, y), text, fill=col, font=FONT_CODE)
        bbox = FONT_CODE.getbbox(text)
        cur_x += (bbox[2] - bbox[0])
    return cur_x


def render_master_trial_video() -> Tuple[str, str]:
    """Render the master trial video demonstrating 2 beginner mistakes + working code."""
    output_mp4 = RENDERED_DIR / "trial_python_master_preview.mp4"
    output_thumb = THUMBNAILS_DIR / "trial_python_master_preview.jpg"

    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 65)
    print("🎬 RENDERING MASTER TRIAL VIDEO: PYTHON VARIABLES (2-ERROR FLOW)")
    print(f"Resolution: {WIDTH}x{HEIGHT} | FPS: {FPS} | Total: {TOTAL_SECONDS}s ({TOTAL_FRAMES} frames)")
    print("=" * 65)

    ed_x0, ed_y0, ed_x1, ed_y1 = 80, 240, 1000, 720
    tm_x0, tm_y0, tm_x1, tm_y1 = 80, 760, 1000, 1080

    # 1. Render all 1,260 frames
    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / FPS
        im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(im)

        # Subtle background grid
        for gy in range(0, HEIGHT, 100):
            draw.line([(0, gy), (WIDTH, gy)], fill=(16, 20, 28), width=1)
        for gx in range(0, WIDTH, 100):
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(16, 20, 28), width=1)

        # Header with Python Logo (within safe zone Y=80 to Y=220)
        draw_python_logo(draw, 140, 120, size=36)
        draw.text((200, 85), "Python Mastery Series", fill=CYAN_KEYWORD, font=FONT_SUBTITLE)
        draw.text((200, 115), "EPISODE 1: Variables & Names", fill=WHITE_VAR, font=FONT_HEADER)

        # Base IDE Windows
        draw_window_frame(draw, ed_x0, ed_y0, ed_x1, ed_y1, title="variables.py", is_terminal=False)
        draw_window_frame(draw, tm_x0, tm_y0, tm_x1, tm_y1, title="TERMINAL - python3 variables.py", is_terminal=True)

        # Furniture (Desk, Laptop, Chair)
        draw_empty_desk_and_chair(draw, dx=540, dy=1460)

        # -------------------------------------------------------------
        # 11-ACT MASTER CHOREOGRAPHY STATE MACHINE
        # -------------------------------------------------------------

        if t < 2.8:
            # ACT 0: Empty chair! Walking in from left with leg/arm swing
            walk_prog = t / 2.8
            walk_x = int(80 + walk_prog * (700 - 80))
            draw_stickman_actor(draw, action="walk_in", walk_x=walk_x, t=t)
            # Empty cursor in editor
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            draw.rectangle([ed_x0 + 90, ed_y0 + 75, ed_x0 + 92, ed_y0 + 115], fill=WHITE_VAR)

        elif t < 6.8:
            # ACT 1: Sits down -> Types ERROR 1: print(score)
            draw_stickman_actor(draw, action="sitting_typing", t=t)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            full_line = "print(score)"
            # Progressive typing
            chars_to_show = max(1, min(len(full_line), int((t - 3.2) * 4))) if t >= 3.2 else 1
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(full_line[:chars_to_show]))

        elif t < 10.0:
            # ACT 2: Hits Enter -> ERROR 1 CRASH! NameError
            draw_stickman_actor(draw, action="sitting_shocked", t=t)
            # Red highlight box under line 1
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 70, ed_x1 - 20, ed_y0 + 125], radius=8, fill=(45, 16, 16), outline=ERROR_RED, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code("print(score)"))

            # Terminal error output
            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> python3 variables.py", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), "NameError: name 'score' is not defined", fill=ERROR_RED, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), "# Mistake: Using a variable before creating it!", fill=AMBER_NUMBER, font=FONT_TERM)

        elif t < 12.5:
            # ACT 3: Backspaces line 1 and types ERROR 2: 1st_score = 100
            draw_stickman_actor(draw, action="sitting_typing", t=t)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            full_line_err2 = "1st_score = 100"
            chars_to_show = max(1, min(len(full_line_err2), int((t - 10.0) * 7)))
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(full_line_err2[:chars_to_show]))

        elif t < 15.5:
            # ACT 4: Hits Enter -> ERROR 2 CRASH! SyntaxError
            draw_stickman_actor(draw, action="sitting_shocked", t=t)
            # Red highlight box under line 1
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 70, ed_x1 - 20, ed_y0 + 125], radius=8, fill=(45, 16, 16), outline=ERROR_RED, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code("1st_score = 100"))

            # Terminal error output
            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> python3 variables.py", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), "SyntaxError: invalid decimal literal", fill=ERROR_RED, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), "# Mistake: Variable names cannot start with a digit!", fill=AMBER_NUMBER, font=FONT_TERM)

        elif t < 21.0:
            # ACT 5: 5-Second Pacing & Thinking Phase! (? ?)
            draw_stickman_actor(draw, action="pacing_thinking", t=t)
            # Keep error visible in IDE
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 70, ed_x1 - 20, ed_y0 + 125], radius=8, fill=(45, 16, 16), outline=ERROR_RED, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code("1st_score = 100"))

            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> python3 variables.py", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), "SyntaxError: invalid decimal literal", fill=ERROR_RED, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), "# Mistake: Variable names cannot start with a digit!", fill=AMBER_NUMBER, font=FONT_TERM)

        elif t < 29.5:
            # ACT 6: Sits back down -> Types clean working 3-line code!
            draw_stickman_actor(draw, action="sitting_typing", t=t)

            # Line 1: player = "Alex"
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            l1_target = 'player = "Alex"'
            if t < 23.5:
                sub_l1 = max(1, min(len(l1_target), int((t - 21.0) * 7)))
                render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(l1_target[:sub_l1]))
            else:
                render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(l1_target))

            # Line 2: score = 100
            if t >= 23.5:
                draw.text((ed_x0 + 35, ed_y0 + 130), "2", fill=MUTED_TEXT, font=FONT_CODE)
                l2_target = 'score = 100'
                if t < 26.0:
                    sub_l2 = max(1, min(len(l2_target), int((t - 23.5) * 6)))
                    render_code_tokens(draw, ed_x0 + 90, ed_y0 + 130, tokenize_code(l2_target[:sub_l2]))
                else:
                    render_code_tokens(draw, ed_x0 + 90, ed_y0 + 130, tokenize_code(l2_target))

            # Line 3: print(f"{player}: {score} pts")
            if t >= 26.0:
                draw.text((ed_x0 + 35, ed_y0 + 185), "3", fill=MUTED_TEXT, font=FONT_CODE)
                l3_target = 'print(f"{player}: {score} pts")'
                sub_l3 = max(1, min(len(l3_target), int((t - 26.0) * 10)))
                render_code_tokens(draw, ed_x0 + 90, ed_y0 + 185, tokenize_code(l3_target[:sub_l3]))

            # Terminal shows ready
            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> python3 variables.py", fill=MUTED_TEXT, font=FONT_TERM)

        elif t < 33.5:
            # ACT 7: Strikes Enter -> Bright Green Terminal Success!
            draw_stickman_actor(draw, action="sitting_enter", t=t)
            # Subtle green border on code editor
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 65, ed_x1 - 20, ed_y0 + 245], radius=8, fill=(16, 35, 24), outline=SUCCESS_GREEN, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code('player = "Alex"'))
            draw.text((ed_x0 + 35, ed_y0 + 130), "2", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 130, tokenize_code('score = 100'))
            draw.text((ed_x0 + 35, ed_y0 + 185), "3", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 185, tokenize_code('print(f"{player}: {score} pts")'))

            # Terminal green output
            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> python3 variables.py", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), ">>> Alex: 100 pts", fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), "[Program finished with exit code 0]", fill=WHITE_VAR, font=FONT_TERM)

        elif t < 38.0:
            # ACT 8: LEAPED OUT OF CHAIR! Jumping with YAAAYYY! + Golden Sparkles!
            draw_stickman_actor(draw, action="yaay_celebrate", t=t)
            # Keep green editor state
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 65, ed_x1 - 20, ed_y0 + 245], radius=8, fill=(16, 35, 24), outline=SUCCESS_GREEN, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code('player = "Alex"'))
            draw.text((ed_x0 + 35, ed_y0 + 130), "2", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 130, tokenize_code('score = 100'))
            draw.text((ed_x0 + 35, ed_y0 + 185), "3", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 185, tokenize_code('print(f"{player}: {score} pts")'))

            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> Alex: 100 pts", fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 115), "[Program finished with exit code 0]", fill=MUTED_TEXT, font=FONT_TERM)

        else:
            # ACT 9: Thumbs Up & Framed Golden Key Takeaway Box (Zero Overflow!)
            draw_stickman_actor(draw, action="thumbs_up", t=t)
            # Keep green editor state
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 65, ed_x1 - 20, ed_y0 + 245], radius=8, fill=(16, 35, 24), outline=SUCCESS_GREEN, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code('player = "Alex"'))
            draw.text((ed_x0 + 35, ed_y0 + 130), "2", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 130, tokenize_code('score = 100'))
            draw.text((ed_x0 + 35, ed_y0 + 185), "3", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 185, tokenize_code('print(f"{player}: {score} pts")'))

            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> Alex: 100 pts", fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 115), "[Program finished with exit code 0]", fill=MUTED_TEXT, font=FONT_TERM)

            # Framed Golden Key Takeaway Box (Y=1160 to Y=1320)
            box_y0, box_y1 = 1140, 1310
            draw.rounded_rectangle([ed_x0, box_y0, ed_x1, box_y1], radius=16, fill=(28, 22, 10), outline=(250, 204, 21), width=3)
            draw.text((ed_x0 + 30, box_y0 + 16), "⭐ KEY TAKEAWAYS:", fill=(250, 204, 21), font=FONT_ALERT)
            draw.text((ed_x0 + 30, box_y0 + 58), "1. Define variables before printing them (avoids NameError)", fill=WHITE_VAR, font=FONT_CODE_BOLD)
            draw.text((ed_x0 + 30, box_y0 + 104), "2. Variable names must start with a letter, never digits!", fill=GREEN_STRING, font=FONT_CODE)

        # Instagram Reels Safe Zone Call To Action (Centered at Y=1720)
        draw.rounded_rectangle([260, 1700, 820, 1775], radius=38, fill=(225, 29, 72))
        draw.text((315, 1722), "▶ FOLLOW FOR EPISODE 2!", fill=(255, 255, 255), font=FONT_ALERT)

        im.save(FRAMES_DIR / f"f_{frame_idx:05d}.png")
        if frame_idx % 250 == 0:
            print(f"  Rendered {frame_idx}/{TOTAL_FRAMES} frames ({t:.1f}s / {TOTAL_SECONDS}s)")

    # 2. Save high-impact thumbnail from victory moment (t=35.0s)
    thumb_idx = int(35.0 * FPS)
    thumb_frame = Image.open(FRAMES_DIR / f"f_{thumb_idx:05d}.png")
    thumb_frame.save(output_thumb, quality=95)
    print(f"📸 Thumbnail saved: {output_thumb}")

    # 3. Audio Engineering: Foley SFX Multi-Layer Mix (Zero Voiceover!)
    sfx_ambient = SFX_DIR / "ambient_coding_pad.wav"
    sfx_footsteps = SFX_DIR / "footsteps.wav"
    sfx_pop = SFX_DIR / "pop.wav"
    sfx_keyboard = SFX_DIR / "keyboard.wav"
    sfx_buzzer = SFX_DIR / "buzzer.wav"
    sfx_ding = SFX_DIR / "success_ding.wav"
    sfx_chime = SFX_DIR / "chime.wav"

    filter_complex = (
        "[1:a]volume=0.20[amb];"
        "[2:a]adelay=400|400,volume=0.45[walk1];"
        "[2:a]adelay=1600|1600,volume=0.45[walk2];"
        "[3:a]adelay=2800|2800,volume=0.40[sit];"
        "[4:a]adelay=3300|3300,volume=0.45[k_err1];"
        "[5:a]adelay=6900|6900,volume=0.70[buzz1];"
        "[4:a]adelay=10100|10100,volume=0.45[k_err2];"
        "[5:a]adelay=12600|12600,volume=0.70[buzz2];"
        "[2:a]adelay=16000|16000,volume=0.35[pace1];"
        "[2:a]adelay=18500|18500,volume=0.35[pace2];"
        "[4:a]adelay=21200|21200,volume=0.45[k_sol1];"
        "[4:a]adelay=23800|23800,volume=0.45[k_sol2];"
        "[4:a]adelay=26200|26200,volume=0.45[k_sol3];"
        "[6:a]adelay=29700|29700,volume=0.80[ding];"
        "[7:a]adelay=33700|33700,volume=0.70[chime];"
        "[amb][walk1][walk2][sit][k_err1][buzz1][k_err2][buzz2][pace1][pace2][k_sol1][k_sol2][k_sol3][ding][chime]"
        "amix=inputs=15:duration=longest,volume=2.2,alimiter=limit=-1.5dB[aout]"
    )

    cmd = [
        FFMPEG, "-y",
        "-r", str(FPS),
        "-i", str(FRAMES_DIR / "f_%05d.png"),
        "-i", str(sfx_ambient),
        "-i", str(sfx_footsteps),
        "-i", str(sfx_pop),
        "-i", str(sfx_keyboard),
        "-i", str(sfx_buzzer),
        "-i", str(sfx_ding),
        "-i", str(sfx_chime),
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(TOTAL_SECONDS),
        str(output_mp4)
    ]

    print("\n🔊 Encoding with FFmpeg...")
    subprocess.run(cmd, check=True)
    shutil.rmtree(FRAMES_DIR, ignore_errors=True)
    print(f"🎉 MASTER TRIAL VIDEO SAVED: {output_mp4}")
    return str(output_mp4), str(output_thumb)


if __name__ == "__main__":
    mp4, thumb = render_master_trial_video()
    print(f"\nCompleted successfully!\nMP4: {mp4}\nThumbnail: {thumb}")
