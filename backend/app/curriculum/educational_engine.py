"""Production Master Animation Studio: Educational Engine (Alan Becker Style) for Instagram Reels.
Generates high-retention live-coding 2D stickman programming Reels (Ep 1 to 10,000+).

Core Design Rules (100% User Specified):
1. ZERO VOICE NARRATION: Pure international visual storytelling + punchy Foley SFX.
2. NO GHOST STICKMAN: Desk & Chair is 100% EMPTY when stickman walks in from left (t=0.0s to 2.5s)!
3. LAPTOP OPPOSITE STICKMAN: Laptop screen tilted toward stickman's eyes and hands.
4. PROGRESSIVE TYPING: Characters type with mechanical keyboard clacking sound effects.
5. 2 ERRORS WITH IMMEDIATE ROAMING:
   - Error 1: Hits Enter -> Red crash + buzzer -> Stickman IMMEDIATELY leaps up and roams left-to-right (? ?).
   - Error 2: Hits Enter -> Red crash + buzzer -> Stickman IMMEDIATELY leaps up and roams left-to-right (? ?).
6. SNAPPY SOLUTION TYPING (NO DEAD LAG):
   - Types working code at natural pace, finishing right when Enter is struck.
7. IMMEDIATE "YAAAYYY!" VICTORY (STRICTLY 3.5 SECONDS):
   - Terminal succeeds in bright Emerald Green -> ding SFX -> Stickman IMMEDIATELY launches into YAAAYYY jumping with stars & chime!
8. IMMEDIATE KEY TAKEAWAYS (STRICTLY 5.0 SECONDS):
   - Framed Golden Key Takeaway box with vector gold star and zero overflow.
   - Follow CTA explicitly announces the next topic: "▶ FOLLOW FOR EPISODE N+1: [NEXT CONCEPT]!"
9. INSTAGRAM SAFE ZONE COMPLIANCE:
   - Avoids top 220px, bottom 320px, and right 140px.
   - Follow CTA placed safely at Y=1720.
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
TEMP_DIR = settings.temp_path / "educational_studio"
RENDERED_DIR = settings.reels_output_path
THUMBNAILS_DIR = STORAGE / "thumbnails"
SFX_DIR = STORAGE / "assets" / "sfx"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
RENDERED_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

# 1080x1920 9:16 Instagram Reels Standard (31.0 seconds total)
WIDTH = 1080
HEIGHT = 1920
FPS = 30
TOTAL_SECONDS = 31.0
TOTAL_FRAMES = int(FPS * TOTAL_SECONDS)  # 930 frames

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


def draw_vector_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, r_outer: int = 12, r_inner: int = 5, fill: Tuple[int, int, int] = GOLD_BORDER):
    """Draw crisp 5-point vector star without relying on emoji font glyphs."""
    pts = []
    for i in range(10):
        r = r_outer if i % 2 == 0 else r_inner
        ang = i * math.pi / 5 - math.pi / 2
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def draw_fitted_takeaway_line(draw: ImageDraw.ImageDraw, x: int, y: int, max_w: int, text: str, fill: Tuple[int, int, int], bold: bool = False):
    """Draw takeaway text guaranteeing it never spills out of the bounding box."""
    font_names = ["consolab.ttf", "LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"] if bold else ["consola.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"]
    # Progressively test font sizes from 25 down to 16 until text fits cleanly
    for sz in range(25, 15, -1):
        f = load_cross_platform_font(font_names, sz)
        w = draw.textlength(text, font=f)
        if w <= max_w:
            draw.text((x, y), text, fill=fill, font=f)
            return
    # If still too long at size 16, clip with ellipsis
    f = load_cross_platform_font(font_names, 16)
    clipped = text
    while len(clipped) > 8 and draw.textlength(clipped + "...", font=f) > max_w:
        clipped = clipped[:-1]
    draw.text((x, y), clipped + "...", fill=fill, font=f)


def draw_python_logo(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 36):
    """Draw crisp Python dual-color snake logo."""
    draw.rounded_rectangle([cx - size, cy - size, cx, cy], radius=size // 4, fill=(56, 114, 164))
    draw.ellipse([cx - size * 0.7, cy - size * 0.7, cx - size * 0.4, cy - size * 0.4], fill=(255, 255, 255))
    draw.rounded_rectangle([cx, cy, cx + size, cy + size], radius=size // 4, fill=(255, 212, 59))
    draw.ellipse([cx + size * 0.4, cy + size * 0.4, cx + size * 0.7, cy + size * 0.7], fill=(11, 14, 20))


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


def render_educational_episode(ep_data: Dict[str, Any]) -> str:
    """Master production generator for any Python programming episode (Ep 1 to 10,000+).
    Pacing: 3.5s YAAAYYY victory jump -> 5.0s Key Takeaways with zero overflow and Next Topic CTA.
    """
    ep_num = ep_data.get("actual_episode_number") or ep_data.get("episode", 1)
    title = ep_data.get("title", f"Python Lesson {ep_num}")

    channel_name = "Python Mastery Series"
    file_prefix = f"educational_python_ep{ep_num}"
    final_video = RENDERED_DIR / f"{file_prefix}.mp4"
    final_thumb = THUMBNAILS_DIR / f"{file_prefix}.jpg"

    # Curriculum items
    filename = ep_data.get("filename", f"lesson_{ep_num}.py")
    err1_code = ep_data.get("err1_code", "print(Hello World)")
    err1_msg = ep_data.get("err1_msg", "SyntaxError: invalid syntax")
    err1_note = ep_data.get("err1_note", "# Mistake: Text must always be enclosed in quotes!")

    err2_code = ep_data.get("err2_code", 'Print("Hello World")')
    err2_msg = ep_data.get("err2_msg", "NameError: name 'Print' is not defined")
    err2_note = ep_data.get("err2_note", "# Mistake: Python is case-sensitive! Use lowercase print()")

    sol_lines = ep_data.get("solution_lines", ['print("Hello, World!")'])
    sol_output = ep_data.get("solution_output", "Hello, World!")

    takeaway_l1 = ep_data.get("takeaway_l1", "1. Always use lowercase print() (case-sensitive)")
    takeaway_l2 = ep_data.get("takeaway_l2", "2. Text strings must be enclosed in quotes: \"...\"")

    # Next topic teaser
    next_teaser = ep_data.get("next_teaser")
    if not next_teaser:
        next_teaser = f"Episode {ep_num + 1}: Next Python Topic!"
    follow_text = f"▶ FOLLOW FOR {next_teaser.upper()}!"

    print("\n" + "=" * 65)
    print(f"🎬 RENDERING MASTER EPISODE {ep_num}: {title.upper()} (31s Snappy Pacing)")
    print(f"Duration: {TOTAL_SECONDS}s | Standard: 1080x1920 @ {FPS}fps (2-Error Flow)")
    print("=" * 65)

    ep_frames_dir = TEMP_DIR / f"frames_ep{ep_num}"
    if ep_frames_dir.exists():
        shutil.rmtree(ep_frames_dir)
    ep_frames_dir.mkdir(parents=True, exist_ok=True)

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

        # Header with Logo
        draw_python_logo(draw, 140, 120, size=36)
        draw.text((200, 85), channel_name, fill=CYAN_KEYWORD, font=FONT_SUBTITLE)
        draw.text((200, 115), f"EPISODE {ep_num}: {title[:30]}", fill=WHITE_VAR, font=FONT_HEADER)

        # Base IDE Windows
        draw_window_frame(draw, ed_x0, ed_y0, ed_x1, ed_y1, title=filename, is_terminal=False)
        draw_window_frame(draw, tm_x0, tm_y0, tm_x1, tm_y1, title=f"TERMINAL - python3 {filename}", is_terminal=True)

        # Desk & Chair
        draw_empty_desk_and_chair(draw, dx=540, dy=1460)

        # Snappy Choreography (Strict 3.5s YAAAYYY -> 5.0s Key Takeaways)
        if t < 2.5:
            # Walk-in
            walk_prog = t / 2.5
            walk_x = int(80 + walk_prog * (700 - 80))
            draw_stickman_actor(draw, action="walk_in", walk_x=walk_x, t=t)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            draw.rectangle([ed_x0 + 90, ed_y0 + 75, ed_x0 + 92, ed_y0 + 115], fill=WHITE_VAR)

        elif t < 5.8:
            # Sits & types Error 1
            draw_stickman_actor(draw, action="sitting_typing", t=t)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            chars_to_show = max(1, min(len(err1_code), int((t - 2.6) * 6))) if t >= 2.6 else 1
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(err1_code[:chars_to_show]))

        elif t < 6.2:
            # Enter -> Error 1 Crash!
            draw_stickman_actor(draw, action="sitting_enter", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 70, ed_x1 - 20, ed_y0 + 125], radius=8, fill=(45, 16, 16), outline=ERROR_RED, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(err1_code))

            draw.text((tm_x0 + 35, tm_y0 + 65), f">>> python3 {filename}", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), err1_msg, fill=ERROR_RED, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), err1_note, fill=AMBER_NUMBER, font=FONT_TERM)

        elif t < 9.5:
            # IMMEDIATELY leaps up & roams left-to-right! (? ?)
            draw_stickman_actor(draw, action="pacing_thinking", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 70, ed_x1 - 20, ed_y0 + 125], radius=8, fill=(45, 16, 16), outline=ERROR_RED, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(err1_code))

            draw.text((tm_x0 + 35, tm_y0 + 65), f">>> python3 {filename}", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), err1_msg, fill=ERROR_RED, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), err1_note, fill=AMBER_NUMBER, font=FONT_TERM)

        elif t < 13.5:
            # Sits & types Error 2
            draw_stickman_actor(draw, action="sitting_typing", t=t)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            chars_to_show = max(1, min(len(err2_code), int((t - 9.6) * 6))) if t >= 9.6 else 1
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(err2_code[:chars_to_show]))

        elif t < 14.0:
            # Enter -> Error 2 Crash!
            draw_stickman_actor(draw, action="sitting_enter", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 70, ed_x1 - 20, ed_y0 + 125], radius=8, fill=(45, 16, 16), outline=ERROR_RED, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(err2_code))

            draw.text((tm_x0 + 35, tm_y0 + 65), f">>> python3 {filename}", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), err2_msg, fill=ERROR_RED, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), err2_note, fill=AMBER_NUMBER, font=FONT_TERM)

        elif t < 17.5:
            # IMMEDIATELY leaps up & roams left-to-right! (? ?)
            draw_stickman_actor(draw, action="pacing_thinking", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 70, ed_x1 - 20, ed_y0 + 125], radius=8, fill=(45, 16, 16), outline=ERROR_RED, width=2)
            draw.text((ed_x0 + 35, ed_y0 + 75), "1", fill=MUTED_TEXT, font=FONT_CODE)
            render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75, tokenize_code(err2_code))

            draw.text((tm_x0 + 35, tm_y0 + 65), f">>> python3 {filename}", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), err2_msg, fill=ERROR_RED, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), err2_note, fill=AMBER_NUMBER, font=FONT_TERM)

        elif t < 21.8:
            # Sits & types working code (finishes right at 21.6s)
            draw_stickman_actor(draw, action="sitting_typing", t=t)
            for idx, s_line in enumerate(sol_lines):
                draw.text((ed_x0 + 35, ed_y0 + 75 + idx * 55), str(idx + 1), fill=MUTED_TEXT, font=FONT_CODE)
                sub_s = max(1, min(len(s_line), int((t - 17.6) * 6.0))) if t >= 17.6 else 1
                render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75 + idx * 55, tokenize_code(s_line[:sub_s]))

            draw.text((tm_x0 + 35, tm_y0 + 65), f">>> python3 {filename}", fill=MUTED_TEXT, font=FONT_TERM)

        elif t < 22.5:
            # Enter -> Bright Green Terminal Success!
            draw_stickman_actor(draw, action="sitting_enter", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 65, ed_x1 - 20, ed_y0 + 135], radius=8, fill=(16, 35, 24), outline=SUCCESS_GREEN, width=2)
            for idx, s_line in enumerate(sol_lines):
                draw.text((ed_x0 + 35, ed_y0 + 75 + idx * 55), str(idx + 1), fill=MUTED_TEXT, font=FONT_CODE)
                render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75 + idx * 55, tokenize_code(s_line))

            draw.text((tm_x0 + 35, tm_y0 + 65), f">>> python3 {filename}", fill=MUTED_TEXT, font=FONT_TERM)
            draw.text((tm_x0 + 35, tm_y0 + 115), sol_output, fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 165), "[Program finished with exit code 0]", fill=WHITE_VAR, font=FONT_TERM)

        elif t < 26.0:
            # STRICTLY 3.5s "YAAAYYY!" victory jump! (NO LAG!)
            draw_stickman_actor(draw, action="yaay_celebrate", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 65, ed_x1 - 20, ed_y0 + 135], radius=8, fill=(16, 35, 24), outline=SUCCESS_GREEN, width=2)
            for idx, s_line in enumerate(sol_lines):
                draw.text((ed_x0 + 35, ed_y0 + 75 + idx * 55), str(idx + 1), fill=MUTED_TEXT, font=FONT_CODE)
                render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75 + idx * 55, tokenize_code(s_line))

            draw.text((tm_x0 + 35, tm_y0 + 65), sol_output, fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 115), "[Program finished with exit code 0]", fill=MUTED_TEXT, font=FONT_TERM)

        else:
            # STRICTLY 5.0s Key Takeaways (Y=1140 to Y=1310) with ZERO OVERFLOW + Follow CTA
            draw_stickman_actor(draw, action="thumbs_up", t=t)
            draw.rounded_rectangle([ed_x0 + 20, ed_y0 + 65, ed_x1 - 20, ed_y0 + 135], radius=8, fill=(16, 35, 24), outline=SUCCESS_GREEN, width=2)
            for idx, s_line in enumerate(sol_lines):
                draw.text((ed_x0 + 35, ed_y0 + 75 + idx * 55), str(idx + 1), fill=MUTED_TEXT, font=FONT_CODE)
                render_code_tokens(draw, ed_x0 + 90, ed_y0 + 75 + idx * 55, tokenize_code(s_line))

            draw.text((tm_x0 + 35, tm_y0 + 65), sol_output, fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 115), "[Program finished with exit code 0]", fill=MUTED_TEXT, font=FONT_TERM)

            box_y0, box_y1 = 1140, 1310
            draw.rounded_rectangle([ed_x0, box_y0, ed_x1, box_y1], radius=16, fill=(28, 22, 10), outline=GOLD_BORDER, width=3)
            draw_vector_star(draw, ed_x0 + 36, box_y0 + 27, r_outer=11, r_inner=5, fill=GOLD_BORDER)
            draw.text((ed_x0 + 58, box_y0 + 15), "KEY TAKEAWAYS:", fill=GOLD_BORDER, font=FONT_ALERT)
            max_takeaway_w = (ed_x1 - ed_x0) - 60  # 920 - 60 = 860px max width inside the card
            draw_fitted_takeaway_line(draw, ed_x0 + 30, box_y0 + 58, max_takeaway_w, takeaway_l1, WHITE_VAR, bold=True)
            draw_fitted_takeaway_line(draw, ed_x0 + 30, box_y0 + 104, max_takeaway_w, takeaway_l2, GREEN_STRING, bold=False)

        # Instagram Safe Zone CTA (Centered at Y=1720)
        draw.rounded_rectangle([200, 1700, 880, 1775], radius=38, fill=(225, 29, 72))
        draw.text((230, 1722), follow_text, fill=(255, 255, 255), font=FONT_ALERT)

        im.save(ep_frames_dir / f"f_{frame_idx:05d}.png")

    # High-impact thumbnail at victory moment
    thumb_idx = int(24.5 * FPS)
    thumb_frame = Image.open(ep_frames_dir / f"f_{thumb_idx:05d}.png")
    thumb_frame.save(final_thumb, quality=95)
    print(f"📸 Thumbnail saved: {final_thumb}")

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
        "[4:a]adelay=2700|2700,volume=0.45[k_err1_a];"
        "[4:a]adelay=4300|4300,volume=0.45[k_err1_b];"
        "[5:a]adelay=5900|5900,volume=0.75[buzz1];"
        "[2:a]adelay=6500|6500,volume=0.40[roam1_a];"
        "[2:a]adelay=8000|8000,volume=0.40[roam1_b];"
        "[3:a]adelay=9500|9500,volume=0.40[sit2];"
        "[4:a]adelay=9800|9800,volume=0.45[k_err2_a];"
        "[4:a]adelay=11800|11800,volume=0.45[k_err2_b];"
        "[5:a]adelay=13600|13600,volume=0.75[buzz2];"
        "[2:a]adelay=14300|14300,volume=0.40[roam2_a];"
        "[2:a]adelay=15800|15800,volume=0.40[roam2_b];"
        "[3:a]adelay=17500|17500,volume=0.40[sit3];"
        "[4:a]adelay=17800|17800,volume=0.45[k_sol_a];"
        "[4:a]adelay=19800|19800,volume=0.45[k_sol_b];"
        "[6:a]adelay=22100|22100,volume=0.85[ding];"
        "[7:a]adelay=22600|22600,volume=0.75[chime];"
        "[amb][walk_in1][walk_in2][sit1][k_err1_a][k_err1_b][buzz1][roam1_a][roam1_b][sit2][k_err2_a][k_err2_b][buzz2][roam2_a][roam2_b][sit3][k_sol_a][k_sol_b][ding][chime]"
        "amix=inputs=20:duration=longest,volume=2.2,alimiter=limit=-1.5dB[aout]"
    )

    cmd = [
        FFMPEG, "-y",
        "-r", str(FPS),
        "-i", str(ep_frames_dir / "f_%05d.png"),
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
        str(final_video)
    ]

    subprocess.run(cmd, check=True)
    shutil.rmtree(ep_frames_dir, ignore_errors=True)
    print(f"🎉 Master Educational Video saved: {final_video}")
    return str(final_video)
