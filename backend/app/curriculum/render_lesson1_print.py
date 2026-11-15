"""Master Production Animation Studio: Lesson 1 - The print() Function (Zero-Lag Snappy Pacing).

Fixes applied per user feedback:
1. ZERO LAG: Eliminated the 6-second dead pause after typing at 23s.
2. IMMEDIATE ROAMING: As soon as an error occurs, stickman IMMEDIATELY leaps up and roams left-to-right thinking with ? ?.
3. IMMEDIATE YAAAYYY: As soon as the terminal turns green with exit code 0, stickman IMMEDIATELY launches into the YAAAYYY victory jump!
4. ZERO TEXT OVERFLOW: Takeaway box has vector star and strict padding with >150px safety margin.
5. ONE CONCEPT ONLY: 100% focused on print() without mixing other topics.
6. 100% FOLEY SFX: Rapid mechanical typing on every letter, footsteps on roaming, buzzers on error, bright ding on green, celebration chime on YAAAYYY.
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
TEMP_DIR = settings.temp_path / "lesson1_studio"
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
TOTAL_SECONDS = 38.0
TOTAL_FRAMES = int(FPS * TOTAL_SECONDS)  # 1140 frames

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
GOLD_BORDER = (250, 204, 21)


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


FONT_CODE = load_cross_platform_font(["consola.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"], 34)
FONT_CODE_BOLD = load_cross_platform_font(["consolab.ttf", "LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"], 34)
FONT_TAKEAWAY = load_cross_platform_font(["consola.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"], 25)
FONT_TAKEAWAY_BOLD = load_cross_platform_font(["consolab.ttf", "LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"], 25)
FONT_HEADER = load_cross_platform_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 42)
FONT_SUBTITLE = load_cross_platform_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 22)
FONT_TERM = load_cross_platform_font(["consola.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"], 26)
FONT_TERM_BOLD = load_cross_platform_font(["consolab.ttf", "LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"], 28)
FONT_ALERT = load_cross_platform_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 26)
FONT_COMIC = load_cross_platform_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 36)


def tokenize_code(line: str) -> List[Tuple[str, Tuple[int, int, int]]]:
    """Tokenize Python source line into colored syntax tokens."""
    keywords_py = {
        'def', 'return', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'in',
        'class', 'print', 'str', 'int', 'float', 'bool', 'True', 'False', 'None'
    }

    pattern = re.compile(r'(\".*?\"|\'.*?\'|\#.*|\b\d+\b|\b[a-zA-Z_]\w*\b|[^\s\w]|\s+)')
    tokens = []
    for match in pattern.finditer(line):
        token = match.group()
        if token.startswith('#'):
            tokens.append((token, MUTED_TEXT))
        elif (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
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


def draw_vector_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, r_outer: int = 12, r_inner: int = 5, fill: Tuple[int, int, int] = GOLD_BORDER):
    """Draw crisp 5-point vector star without relying on emoji font glyphs."""
    pts = []
    for i in range(10):
        r = r_outer if i % 2 == 0 else r_inner
        ang = i * math.pi / 5 - math.pi / 2
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def draw_window_frame(draw: ImageDraw.ImageDraw, x0: int, y0: int, x1: int, y1: int, title: str = "main.py", is_terminal: bool = False):
    """Draw modern dark IDE window frame with macOS-style window controls."""
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
    """Draw ONLY furniture & laptop. Chair is empty (NO ghost stickman!)."""
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

    elif action in ("sitting_typing", "sitting_enter", "sitting_idle"):
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
        else:
            draw.line([shoulder, (655, 1450)], fill=color, width=6)
            draw.line([(655, 1450), (595, 1460)], fill=color, width=6)

    elif action == "pacing_thinking":
        # Out of chair! Walking back and forth between x=620 and x=320, hand on chin thinking
        pace_x = int(470 + math.sin(t * 3.5) * 150)
        hx = pace_x
        hy = 1400
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill=color)
        neck = (hx, hy + head_r)
        hip = (hx, hy + head_r + 80)
        draw.line([neck, hip], fill=color, width=7)

        # Walking legs
        leg_p = math.sin(t * 12.0) * 22.0
        draw.line([hip, (hip[0] + leg_p, 1550)], fill=color, width=6)
        draw.line([hip, (hip[0] - leg_p, 1550)], fill=color, width=6)

        # Right hand on chin thinking, left arm folded
        shoulder = (neck[0], neck[1] + 12)
        draw.line([shoulder, (hx - 15, hy + 50)], fill=color, width=6)
        draw.line([shoulder, (hx + 18, hy + 30)], fill=color, width=6)
        draw.line([(hx + 18, hy + 30), (hx + 4, hy + 18)], fill=color, width=6)

        # Animated floating question marks
        q_wiggle = math.sin(t * 7.0) * 6
        draw.text((hx - 35, hy - 65 + q_wiggle), "?", fill=ERROR_RED, font=FONT_HEADER)
        draw.text((hx + 28, hy - 75 - q_wiggle), "?", fill=AMBER_NUMBER, font=FONT_HEADER)

    elif action == "yaay_celebrate":
        # LEAPED OUT OF CHAIR! Jumping in the air in center floor with YAAAYYY!
        jump_y = int(math.sin(t * 9.0) * 38)
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
            s_wiggle = 5 + int(3 * math.sin(t * 14.0))
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


def render_lesson1_snappy() -> Tuple[str, str]:
    """Render Lesson 1 Reel with snappy zero-lag pacing and instant roaming on error."""
    output_mp4 = RENDERED_DIR / "educational_python_ep1_print.mp4"
    output_thumb = THUMBNAILS_DIR / "educational_python_ep1_print.jpg"

    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 65)
    print("🎬 RENDERING LESSON 1: THE print() FUNCTION (SNAPPY ZERO-LAG)")
    print(f"Resolution: {WIDTH}x{HEIGHT} | FPS: {FPS} | Total: {TOTAL_SECONDS}s ({TOTAL_FRAMES} frames)")
    print("=" * 65)

    ed_x0, ed_y0, ed_x1, ed_y1 = 80, 240, 1000, 720
    tm_x0, tm_y0, tm_x1, tm_y1 = 80, 760, 1000, 1080

    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / FPS
        im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(im)

        # Background grid
        for gy in range(0, HEIGHT, 100):
            draw.line([(0, gy), (WIDTH, gy)], fill=(16, 20, 28), width=1)
        for gx in range(0, WIDTH, 100):
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(16, 20, 28), width=1)

        # Header with Python Logo
        draw_python_logo(draw, 140, 120, size=36)
        draw.text((200, 85), "Python Mastery Series", fill=CYAN_KEYWORD, font=FONT_SUBTITLE)
        draw.text((200, 115), "EPISODE 1: The print() Function", fill=WHITE_VAR, font=FONT_HEADER)

        # Base IDE Windows
        draw_window_frame(draw, ed_x0, ed_y0, ed_x1, ed_y1, title="lesson_1.py", is_terminal=False)
        draw_window_frame(draw, tm_x0, tm_y0, tm_x1, tm_y1, title="TERMINAL - python3 lesson_1.py", is_terminal=True)

        # Furniture (Desk, Laptop, Chair)
        draw_empty_desk_and_chair(draw, dx=540, dy=1460)

        # -------------------------------------------------------------
        # SNAPPY ZERO-LAG CHOREOGRAPHY STATE MACHINE
        # -------------------------------------------------------------

        if t < 2.5:
            # ACT 0: Empty chair! Walking in from left with leg/arm swing
            walk_prog = t / 2.5
            walk_x = int(80 + walk_prog * (700 - 80))
            draw_stickman_actor(draw, action="walk_in", walk_x=walk_x, t=t)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            draw.rectangle([ed_x0 + 90, ed_y0 + 75, ed_x0 + 92, ed_y0 + 115], fill=WHITE_VAR)

        elif t < 6.0:
            # ACT 1: Sits down -> Types ERROR 1: print(Hello World) without quotes!
            draw_stickman_actor(draw, action="sitting_typing", t=t)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            full_line_err1 = "print(Hello World)"
            chars_to_show = max(1, min(len(full_line_err1), int((t - 2.6) * 6))) if t >= 2.6 else 1
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(full_line_err1[:chars_to_show]))

        elif t < 6.5:
            # ACT 2: Hits Enter at 6.0s -> ERROR 1 CRASH!
            draw_stickman_actor(draw, action="sitting_enter", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 70, ed_x1 - 20, ed_y0 + 125], radius=8, fill=(45, 16, 16), outline=ERROR_RED, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code("print(Hello World)"))

            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> python3 lesson_1.py", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), "SyntaxError: invalid syntax", fill=ERROR_RED, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), "# Mistake: Text must always be enclosed in quotes!", fill=AMBER_NUMBER, font=FONT_TERM)

        elif t < 10.5:
            # ACT 3: IMMEDIATELY LEAPS UP AND ROAMS LEFT-TO-RIGHT! (? ?)
            draw_stickman_actor(draw, action="pacing_thinking", t=t)
            # Editor keeps error highlighted
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 70, ed_x1 - 20, ed_y0 + 125], radius=8, fill=(45, 16, 16), outline=ERROR_RED, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code("print(Hello World)"))

            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> python3 lesson_1.py", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), "SyntaxError: invalid syntax", fill=ERROR_RED, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), "# Mistake: Text must always be enclosed in quotes!", fill=AMBER_NUMBER, font=FONT_TERM)

        elif t < 14.5:
            # ACT 4: Sits back down -> Types ERROR 2: Print("Hello World") with Capital P!
            draw_stickman_actor(draw, action="sitting_typing", t=t)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            full_line_err2 = 'Print("Hello World")'
            chars_to_show = max(1, min(len(full_line_err2), int((t - 10.6) * 6))) if t >= 10.6 else 1
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(full_line_err2[:chars_to_show]))

        elif t < 15.0:
            # ACT 5: Hits Enter at 14.5s -> ERROR 2 CRASH!
            draw_stickman_actor(draw, action="sitting_enter", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 70, ed_x1 - 20, ed_y0 + 125], radius=8, fill=(45, 16, 16), outline=ERROR_RED, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code('Print("Hello World")'))

            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> python3 lesson_1.py", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), "NameError: name 'Print' is not defined", fill=ERROR_RED, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), "# Mistake: Python is case-sensitive! Use lowercase print()", fill=AMBER_NUMBER, font=FONT_TERM)

        elif t < 19.5:
            # ACT 6: IMMEDIATELY LEAPS UP AND ROAMS LEFT-TO-RIGHT! (? ?)
            draw_stickman_actor(draw, action="pacing_thinking", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 70, ed_x1 - 20, ed_y0 + 125], radius=8, fill=(45, 16, 16), outline=ERROR_RED, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code('Print("Hello World")'))

            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> python3 lesson_1.py", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), "NameError: name 'Print' is not defined", fill=ERROR_RED, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), "# Mistake: Python is case-sensitive! Use lowercase print()", fill=AMBER_NUMBER, font=FONT_TERM)

        elif t < 24.0:
            # ACT 7: Sits down -> Types working code: print("Hello, World!") at natural speed
            draw_stickman_actor(draw, action="sitting_typing", t=t)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            working_code = 'print("Hello, World!")'
            # Paced so typing finishes right at 23.8s with ZERO dead lag
            sub_len = max(1, min(len(working_code), int((t - 19.6) * 5.5))) if t >= 19.6 else 1
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(working_code[:sub_len]))

            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> python3 lesson_1.py", fill=MUTED_TEXT, font=FONT_TERM)

        elif t < 25.0:
            # ACT 8: Strikes Enter at 24.0s -> GREEN SUCCESS OUTPUT!
            draw_stickman_actor(draw, action="sitting_enter", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 65, ed_x1 - 20, ed_y0 + 135], radius=8, fill=(16, 35, 24), outline=SUCCESS_GREEN, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code('print("Hello, World!")'))

            draw.text((tm_x0 + 35, tm_y0 + 65), ">>> python3 lesson_1.py", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), "Hello, World!", fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), "[Program finished with exit code 0]", fill=WHITE_VAR, font=FONT_TERM)

        elif t < 32.5:
            # ACT 9: IMMEDIATELY LEAPS OUT OF CHAIR! JUMPING WITH "YAAAYYY!" (NO LAG!)
            draw_stickman_actor(draw, action="yaay_celebrate", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 65, ed_x1 - 20, ed_y0 + 135], radius=8, fill=(16, 35, 24), outline=SUCCESS_GREEN, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code('print("Hello, World!")'))

            draw.text((tm_x0 + 35, tm_y0 + 65), "Hello, World!", fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 115), "[Program finished with exit code 0]", fill=MUTED_TEXT, font=FONT_TERM)

        else:
            # ACT 10: Thumbs Up & Framed Golden Key Takeaway Box (ZERO OVERFLOW)
            draw_stickman_actor(draw, action="thumbs_up", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 65, ed_x1 - 20, ed_y0 + 135], radius=8, fill=(16, 35, 24), outline=SUCCESS_GREEN, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code('print("Hello, World!")'))

            draw.text((tm_x0 + 35, tm_y0 + 65), "Hello, World!", fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 115), "[Program finished with exit code 0]", fill=MUTED_TEXT, font=FONT_TERM)

            # Framed Golden Key Takeaway Box
            box_y0, box_y1 = 1140, 1310
            draw.rounded_rectangle([ed_x0, box_y0, ed_x1, box_y1], radius=16, fill=(28, 22, 10), outline=GOLD_BORDER, width=3)
            draw_vector_star(draw, ed_x0 + 36, box_y0 + 27, r_outer=11, r_inner=5, fill=GOLD_BORDER)
            draw.text((ed_x0 + 58, box_y0 + 15), "KEY TAKEAWAYS:", fill=GOLD_BORDER, font=FONT_ALERT)

            takeaway_1 = "1. Always use lowercase print() (case-sensitive)"
            takeaway_2 = "2. Text strings must be enclosed in quotes: \"...\""
            draw.text((ed_x0 + 30, box_y0 + 58), takeaway_1, fill=WHITE_VAR, font=FONT_TAKEAWAY_BOLD)
            draw.text((ed_x0 + 30, box_y0 + 104), takeaway_2, fill=GREEN_STRING, font=FONT_TAKEAWAY)

        # Instagram Safe Zone CTA (Centered at Y=1720)
        draw.rounded_rectangle([250, 1700, 830, 1775], radius=38, fill=(225, 29, 72))
        draw.text((290, 1722), "▶ FOLLOW FOR EPISODE 2: COMMENTS!", fill=(255, 255, 255), font=FONT_ALERT)

        im.save(FRAMES_DIR / f"f_{frame_idx:05d}.png")
        if frame_idx % 250 == 0:
            print(f"  Rendered {frame_idx}/{TOTAL_FRAMES} frames ({t:.1f}s / {TOTAL_SECONDS}s)")

    # High-impact thumbnail
    thumb_idx = int(28.0 * FPS)
    thumb_frame = Image.open(FRAMES_DIR / f"f_{thumb_idx:05d}.png")
    thumb_frame.save(output_thumb, quality=95)
    print(f"📸 Thumbnail saved: {output_thumb}")

    # Snappy Foley Audio Mix with exact delays
    sfx_ambient = SFX_DIR / "ambient_coding_pad.wav"
    sfx_footsteps = SFX_DIR / "footsteps.wav"
    sfx_pop = SFX_DIR / "pop.wav"
    sfx_keyboard = SFX_DIR / "keyboard.wav"
    sfx_buzzer = SFX_DIR / "buzzer.wav"
    sfx_ding = SFX_DIR / "success_ding.wav"
    sfx_chime = SFX_DIR / "chime.wav"

    filter_complex = (
        "[1:a]volume=0.20[amb];"
        "[2:a]adelay=300|300,volume=0.45[walk_in1];"
        "[2:a]adelay=1400|1400,volume=0.45[walk_in2];"
        "[3:a]adelay=2500|2500,volume=0.40[sit1];"
        "[4:a]adelay=2800|2800,volume=0.45[k_err1_a];"
        "[4:a]adelay=4400|4400,volume=0.45[k_err1_b];"
        "[5:a]adelay=6000|6000,volume=0.75[buzz1];"
        "[2:a]adelay=6700|6700,volume=0.40[roam1_a];"
        "[2:a]adelay=8500|8500,volume=0.40[roam1_b];"
        "[3:a]adelay=10500|10500,volume=0.40[sit2];"
        "[4:a]adelay=10800|10800,volume=0.45[k_err2_a];"
        "[4:a]adelay=12600|12600,volume=0.45[k_err2_b];"
        "[5:a]adelay=14500|14500,volume=0.75[buzz2];"
        "[2:a]adelay=15200|15200,volume=0.40[roam2_a];"
        "[2:a]adelay=17200|17200,volume=0.40[roam2_b];"
        "[3:a]adelay=19500|19500,volume=0.40[sit3];"
        "[4:a]adelay=19800|19800,volume=0.45[k_sol_a];"
        "[4:a]adelay=21800|21800,volume=0.45[k_sol_b];"
        "[6:a]adelay=24100|24100,volume=0.85[ding];"
        "[7:a]adelay=25100|25100,volume=0.75[chime];"
        "[amb][walk_in1][walk_in2][sit1][k_err1_a][k_err1_b][buzz1][roam1_a][roam1_b][sit2][k_err2_a][k_err2_b][buzz2][roam2_a][roam2_b][sit3][k_sol_a][k_sol_b][ding][chime]"
        "amix=inputs=20:duration=longest,volume=2.2,alimiter=limit=-1.5dB[aout]"
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
    print(f"🎉 SNAPPY LESSON 1 REEL SAVED: {output_mp4}")
    return str(output_mp4), str(output_thumb)


if __name__ == "__main__":
    mp4, thumb = render_lesson1_snappy()
    print(f"\nCompleted successfully!\nMP4: {mp4}\nThumbnail: {thumb}")
