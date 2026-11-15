"""Master Trial Video Generator: Lesson 1 - Python Variables Done Right!
Inspired by the reference video (educational_python_ep2.mp4).

Key Principles:
1. ZERO boring memory allocation / memory slot jargon (strictly relatable for beginners).
2. Explains the topic cleanly.
3. Demonstrates 2 common beginner mistakes / errors first (NameError & SyntaxError).
4. At last, types the right code, strikes Enter, and terminal outputs success in bright Emerald Green.
5. High-energy articulated yellow stickman with animated expressions, walking, laptop typing, pacing, and YAAAYYY celebration!
6. Synchronized with natural energetic neural narration (Edge-TTS) and punchy Foley SFX.
7. 100% Instagram Reels safe zone compliant.
"""

import os
import sys
import math
import shutil
import asyncio
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings
from backend.app.core.ffmpeg_utils import get_ffmpeg_binary
from backend.app.core.logging import logger

FFMPEG = get_ffmpeg_binary()
STORAGE = Path(settings.media_storage_dir)
TEMP_DIR = settings.temp_path / "trial_lesson1"
FRAMES_DIR = TEMP_DIR / "frames"
RENDERED_DIR = settings.reels_output_path
THUMBNAILS_DIR = STORAGE / "thumbnails"
SFX_DIR = STORAGE / "assets" / "sfx"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
FRAMES_DIR.mkdir(parents=True, exist_ok=True)
RENDERED_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920
FPS = 30
TOTAL_SECONDS = 48.0
TOTAL_FRAMES = int(FPS * TOTAL_SECONDS)  # 1440 frames

# Palette matching the reference video
BG_DARK = (10, 12, 16)
STICK_YELLOW = (255, 215, 0)
STICK_OUTLINE = (235, 195, 0)
CYAN_ACCENT = (56, 189, 248)
EMERALD_GREEN = (34, 197, 94)
GOLD_VAL = (250, 204, 21)
PURPLE_KEYWORD = (168, 85, 247)
WHITE = (255, 255, 255)
MUTED_GRAY = (148, 163, 184)
PANEL_BG = (18, 22, 30)
PANEL_BORDER = (40, 48, 65)
ERROR_RED = (239, 68, 68)
ERROR_BG = (45, 16, 16)
LAPTOP_SILVER = (190, 200, 215)
DESK_COLOR = (28, 34, 46)


def get_font(family: str, size: int):
    candidates = []
    if family == "mono":
        candidates = ["consola.ttf", "consolab.ttf", "cour.ttf", "courbd.ttf", "LiberationMono-Bold.ttf"]
    elif family == "bold":
        candidates = ["segoepb.ttf", "arialbd.ttf", "calibrib.ttf", "tahomabd.ttf", "LiberationSans-Bold.ttf"]
    else:
        candidates = ["segoeui.ttf", "arial.ttf", "calibri.ttf", "tahoma.ttf", "LiberationSans-Regular.ttf"]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    return ImageFont.load_default()


font_header = get_font("bold", 42)
font_sub = get_font("bold", 26)
font_code = get_font("mono", 38)
font_term = get_font("mono", 36)
font_callout = get_font("bold", 32)
font_comic = get_font("bold", 44)


# -------------------------------------------------------------
# ARTICULATED YELLOW STICKMAN (MATCHING REFERENCE VIDEO)
# -------------------------------------------------------------
def draw_yellow_stickman(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    action: str = "idle",
    param: float = 0.0,
    face: str = "smile",
    scale: float = 1.65
):
    lw = max(6, int(8 * scale))
    r_head = int(28 * scale)
    h_torso = int(68 * scale)
    l_arm = int(52 * scale)
    l_thigh = int(55 * scale)
    l_calf = int(52 * scale)

    head_x = x
    head_y = y - h_torso - r_head
    torso_top = (x, y - h_torso)
    torso_bot = (x, y)

    # Head (Solid Vibrant Yellow)
    draw.ellipse(
        [head_x - r_head, head_y - r_head, head_x + r_head, head_y + r_head],
        fill=STICK_YELLOW,
        outline=STICK_OUTLINE,
        width=3
    )

    # Eyes & Expressions
    ew, eh = 4, 6
    if face == "blink":
        draw.line([(head_x - 14, head_y), (head_x - 4, head_y)], fill=(20, 20, 20), width=3)
        draw.line([(head_x + 4, head_y), (head_x + 14, head_y)], fill=(20, 20, 20), width=3)
    elif face == "happy":
        draw.arc([head_x - 16, head_y - 6, head_x - 2, head_y + 8], 180, 360, fill=(20, 20, 20), width=3)
        draw.arc([head_x + 2, head_y - 6, head_x + 16, head_y + 8], 180, 360, fill=(20, 20, 20), width=3)
        draw.arc([head_x - 10, head_y + 6, head_x + 10, head_y + 20], 0, 180, fill=(20, 20, 20), width=3)
    elif face == "curious":
        draw.ellipse([head_x - 14, head_y - 6, head_x - 4, head_y + 6], fill=(20, 20, 20))
        draw.ellipse([head_x + 4, head_y - 10, head_x + 16, head_y + 6], fill=(20, 20, 20))
        draw.arc([head_x - 6, head_y + 8, head_x + 8, head_y + 18], 0, 180, fill=(20, 20, 20), width=2)
    elif face == "shocked":
        # Wide eyes, open mouth
        draw.ellipse([head_x - 14, head_y - 8, head_x - 4, head_y + 4], fill=(20, 20, 20))
        draw.ellipse([head_x + 4, head_y - 8, head_x + 14, head_y + 4], fill=(20, 20, 20))
        draw.ellipse([head_x - 6, head_y + 8, head_x + 6, head_y + 20], fill=(20, 20, 20))
    else:  # smile
        draw.ellipse([head_x - 12 - ew, head_y - eh, head_x - 12 + ew, head_y + eh], fill=(20, 20, 20))
        draw.ellipse([head_x + 12 - ew, head_y - eh, head_x + 12 + ew, head_y + eh], fill=(20, 20, 20))
        draw.arc([head_x - 8, head_y + 6, head_x + 8, head_y + 18], 0, 180, fill=(20, 20, 20), width=3)

    # Torso
    draw.line([torso_top, torso_bot], fill=STICK_YELLOW, width=lw)

    # Limbs based on action
    if action == "walk":
        cycle = param * math.pi * 4
        a1, a2 = math.sin(cycle) * 35, -math.sin(cycle) * 35
        draw.line([torso_top, (x + a1, y - h_torso * 0.4)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + a1, y - h_torso * 0.4), (x + a1 * 1.3, y - 5)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_top, (x + a2, y - h_torso * 0.4)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + a2, y - h_torso * 0.4), (x + a2 * 1.3, y - 5)], fill=STICK_YELLOW, width=lw)
        l1, l2 = math.sin(cycle) * 45, -math.sin(cycle) * 45
        draw.line([torso_bot, (x + l1, y + l_thigh)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + l1, y + l_thigh), (x + l1 * 1.2, y + l_thigh + l_calf)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_bot, (x + l2, y + l_thigh)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + l2, y + l_thigh), (x + l2 * 1.2, y + l_thigh + l_calf)], fill=STICK_YELLOW, width=lw)

    elif action == "typing_at_laptop":
        t_off = math.sin(param * 18) * 4
        draw.line([torso_top, (x - 35, y - h_torso * 0.5)], fill=STICK_YELLOW, width=lw)
        draw.line([(x - 35, y - h_torso * 0.5), (x - 70, y - h_torso * 0.3 + t_off)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_top, (x - 20, y - h_torso * 0.4)], fill=STICK_YELLOW, width=lw)
        draw.line([(x - 20, y - h_torso * 0.4), (x - 55, y - h_torso * 0.2 - t_off)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_bot, (x - 45, y + 25)], fill=STICK_YELLOW, width=lw)
        draw.line([(x - 45, y + 25), (x - 50, y + 105)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_bot, (x - 25, y + 35)], fill=STICK_YELLOW, width=lw)
        draw.line([(x - 25, y + 35), (x - 30, y + 115)], fill=STICK_YELLOW, width=lw)

    elif action == "point_right":
        draw.line([torso_top, (x - 25, y - h_torso * 0.5)], fill=STICK_YELLOW, width=lw)
        draw.line([(x - 25, y - h_torso * 0.5), (x - 25, y - 5)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_top, (x + 50, y - h_torso * 0.8)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + 50, y - h_torso * 0.8), (x + 120, y - h_torso * 0.9)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_bot, (x - 25, y + l_thigh)], fill=STICK_YELLOW, width=lw)
        draw.line([(x - 25, y + l_thigh), (x - 28, y + l_thigh + l_calf)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_bot, (x + 25, y + l_thigh)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + 25, y + l_thigh), (x + 28, y + l_thigh + l_calf)], fill=STICK_YELLOW, width=lw)

    elif action == "pacing_thinking":
        # Out of chair, pacing back and forth with hand on chin
        cycle = param * math.pi * 3
        l1, l2 = math.sin(cycle) * 35, -math.sin(cycle) * 35
        draw.line([torso_bot, (x + l1, y + l_thigh)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + l1, y + l_thigh), (x + l1 * 1.2, y + l_thigh + l_calf)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_bot, (x + l2, y + l_thigh)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + l2, y + l_thigh), (x + l2 * 1.2, y + l_thigh + l_calf)], fill=STICK_YELLOW, width=lw)

        # Right hand on chin, left arm folded
        shoulder = (torso_top[0], torso_top[1] + 10)
        draw.line([shoulder, (x - 25, y - h_torso * 0.4)], fill=STICK_YELLOW, width=lw)
        draw.line([(x - 25, y - h_torso * 0.4), (x + 10, y - h_torso * 0.4)], fill=STICK_YELLOW, width=lw)
        draw.line([shoulder, (x + 25, y - h_torso * 0.6)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + 25, y - h_torso * 0.6), (head_x + 6, head_y + 16)], fill=STICK_YELLOW, width=lw)

        # Floating animated question marks
        q_wiggle = math.sin(param * 6.0) * 8
        draw.text((head_x - 45, head_y - 70 + q_wiggle), "?", fill=ERROR_RED, font=font_comic)
        draw.text((head_x + 35, head_y - 80 - q_wiggle), "?", fill=GOLD_VAL, font=font_comic)

    elif action == "yaay_celebrate":
        # Jumping in center with arms pumping and speech bubble
        jump_y = int(math.sin(param * 8.0) * 35)
        head_y -= abs(jump_y)
        torso_top = (torso_top[0], torso_top[1] - abs(jump_y))
        torso_bot = (torso_bot[0], torso_bot[1] - abs(jump_y))

        # Legs spread in jump
        draw.line([torso_bot, (x - 35, y + l_thigh + l_calf - abs(jump_y) + 10)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_bot, (x + 35, y + l_thigh + l_calf - abs(jump_y) + 10)], fill=STICK_YELLOW, width=lw)

        # Both arms raised high pumping fists
        shoulder = (torso_top[0], torso_top[1] + 10)
        draw.line([shoulder, (shoulder[0] - 45, shoulder[1] - 40)], fill=STICK_YELLOW, width=lw)
        draw.line([(shoulder[0] - 45, shoulder[1] - 40), (shoulder[0] - 70, shoulder[1] - 75)], fill=STICK_YELLOW, width=lw)
        draw.line([shoulder, (shoulder[0] + 45, shoulder[1] - 40)], fill=STICK_YELLOW, width=lw)
        draw.line([(shoulder[0] + 45, shoulder[1] - 40), (shoulder[0] + 70, shoulder[1] - 75)], fill=STICK_YELLOW, width=lw)

        # Comic Speech Bubble shouting "YAAAYYY!"
        draw.rounded_rectangle([head_x - 100, head_y - 110, head_x + 100, head_y - 45], radius=16, fill=GOLD_VAL, outline=WHITE, width=3)
        draw.text((head_x - 85, head_y - 102), "YAAAYYY!", fill=(11, 14, 20), font=font_comic)

        # Golden sparkle stars
        for sx, sy in [(head_x - 145, head_y - 45), (head_x + 135, head_y - 35), (head_x - 95, head_y + 55), (head_x + 105, head_y + 65)]:
            s_wiggle = 6 + int(3 * math.sin(param * 12.0))
            draw.line([(sx - s_wiggle, sy), (sx + s_wiggle, sy)], fill=GOLD_VAL, width=3)
            draw.line([(sx, sy - s_wiggle), (sx, sy + s_wiggle)], fill=GOLD_VAL, width=3)

    elif action == "thumbs_up":
        draw.line([torso_top, (x - 35, y - h_torso * 0.5)], fill=STICK_YELLOW, width=lw)
        draw.line([(x - 35, y - h_torso * 0.5), (x - 15, y - 5)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_top, (x + 45, y - h_torso * 0.6)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + 45, y - h_torso * 0.6), (x + 55, y - h_torso - 25)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + 55, y - h_torso - 25), (x + 55, y - h_torso - 45)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_bot, (x - 25, y + l_thigh)], fill=STICK_YELLOW, width=lw)
        draw.line([(x - 25, y + l_thigh), (x - 28, y + l_thigh + l_calf)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_bot, (x + 25, y + l_thigh)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + 25, y + l_thigh), (x + 28, y + l_thigh + l_calf)], fill=STICK_YELLOW, width=lw)

    else:  # standing idle
        draw.line([torso_top, (x - 25, y - h_torso * 0.5)], fill=STICK_YELLOW, width=lw)
        draw.line([(x - 25, y - h_torso * 0.5), (x - 28, y - 10)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_top, (x + 25, y - h_torso * 0.5)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + 25, y - h_torso * 0.5), (x + 28, y - 10)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_bot, (x - 25, y + l_thigh)], fill=STICK_YELLOW, width=lw)
        draw.line([(x - 25, y + l_thigh), (x - 28, y + l_thigh + l_calf)], fill=STICK_YELLOW, width=lw)
        draw.line([torso_bot, (x + 25, y + l_thigh)], fill=STICK_YELLOW, width=lw)
        draw.line([(x + 25, y + l_thigh), (x + 28, y + l_thigh + l_calf)], fill=STICK_YELLOW, width=lw)


def draw_desk_and_laptop(draw: ImageDraw.ImageDraw, desk_x: float, desk_y: float, laptop_open: float = 1.0):
    draw.rounded_rectangle([desk_x, desk_y, desk_x + 360, desk_y + 24], radius=6, fill=DESK_COLOR)
    draw.rectangle([desk_x + 30, desk_y + 24, desk_x + 44, desk_y + 260], fill=(22, 28, 38))
    draw.rectangle([desk_x + 316, desk_y + 24, desk_x + 330, desk_y + 260], fill=(22, 28, 38))

    lap_x, lap_y = desk_x + 80, desk_y - 12
    draw.rounded_rectangle([lap_x, lap_y, lap_x + 180, lap_y + 12], radius=4, fill=LAPTOP_SILVER)

    angle = 1.25 * laptop_open
    lid_len = 120
    screen_top_x = lap_x + 40 - int(math.cos(angle) * lid_len)
    screen_top_y = lap_y - int(math.sin(angle) * lid_len)
    draw.line([(lap_x + 40, lap_y), (screen_top_x, screen_top_y)], fill=LAPTOP_SILVER, width=8)

    if laptop_open > 0.3:
        draw.polygon(
            [(lap_x + 40, lap_y), (screen_top_x, screen_top_y), (lap_x + 140, screen_top_y - 20), (lap_x + 120, lap_y)],
            fill=(40, 60, 90)
        )


def draw_floating_code_editor(draw: ImageDraw.ImageDraw, lines: list, highlights: list, is_error: bool = False):
    x0, y0 = 60, 220
    x1, y1 = WIDTH - 60, 560
    border_col = ERROR_RED if is_error else PANEL_BORDER
    draw.rounded_rectangle([x0, y0, x1, y1], radius=20, fill=PANEL_BG, outline=border_col, width=3)
    draw.rounded_rectangle([x0, y0, x1, y0 + 55], radius=20, fill=(24, 30, 42))
    draw.rectangle([x0, y0 + 35, x1, y0 + 55], fill=(24, 30, 42))
    draw.ellipse([x0 + 25, y0 + 18, x0 + 43, y0 + 36], fill=(239, 68, 68))
    draw.ellipse([x0 + 55, y0 + 18, x0 + 73, y0 + 36], fill=(250, 204, 21))
    draw.ellipse([x0 + 85, y0 + 18, x0 + 103, y0 + 36], fill=(34, 197, 94))
    draw.text((x0 + (x1 - x0) // 2, y0 + 28), "main.py — Python", fill=MUTED_GRAY, font=font_sub, anchor="mm")

    cy = y0 + 80
    for idx, (code_text, is_hl) in enumerate(zip(lines, highlights)):
        line_num = f"{idx + 1:2d}  "
        draw.text((x0 + 30, cy), line_num, fill=(80, 95, 120), font=font_code)

        if is_hl:
            hl_fill = ERROR_BG if is_error else (38, 52, 75)
            hl_border = ERROR_RED if is_error else CYAN_ACCENT
            draw.rounded_rectangle([x0 + 95, cy - 6, x1 - 30, cy + 46], radius=8, fill=hl_fill, outline=hl_border, width=2)

        # Syntax colorization
        if "print" in code_text:
            draw.text((x0 + 110, cy), "print", fill=PURPLE_KEYWORD, font=font_code)
            rest = code_text[5:]
            draw.text((x0 + 110 + draw.textlength("print", font=font_code), cy), rest, fill=WHITE, font=font_code)
        elif "=" in code_text:
            var_name, val = code_text.split("=", 1)
            var_col = ERROR_RED if is_error else CYAN_ACCENT
            draw.text((x0 + 110, cy), var_name, fill=var_col, font=font_code)
            w_var = draw.textlength(var_name, font=font_code)
            draw.text((x0 + 110 + w_var, cy), "=", fill=WHITE, font=font_code)
            w_eq = draw.textlength("=", font=font_code)
            val_col = GOLD_VAL if val.strip().isdigit() else EMERALD_GREEN
            draw.text((x0 + 110 + w_var + w_eq, cy), val, fill=val_col, font=font_code)
        else:
            draw.text((x0 + 110, cy), code_text, fill=WHITE, font=font_code)

        cy += 54


def draw_terminal_output(draw: ImageDraw.ImageDraw, output_lines: list, is_error: bool = False):
    x0, y0 = 60, 590
    x1, y1 = WIDTH - 60, 770
    border_col = ERROR_RED if is_error else PANEL_BORDER
    bg_col = (20, 12, 14) if is_error else (14, 18, 24)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=bg_col, outline=border_col, width=2)
    draw.text((x0 + 30, y0 + 26), "Terminal Output (Python 3.14)", fill=MUTED_GRAY, font=get_font("bold", 22), anchor="lm")
    draw.line([(x0, y0 + 44), (x1, y0 + 44)], fill=(30, 38, 50), width=1)

    cy = y0 + 68
    for l in output_lines:
        draw.text((x0 + 30, cy), ">>> ", fill=(100, 115, 140), font=font_term)
        col = ERROR_RED if is_error else EMERALD_GREEN
        draw.text((x0 + 110, cy), l, fill=col, font=font_term)
        cy += 44


def draw_nametag_visual(draw: ImageDraw.ImageDraw, var_name: str, var_val: str, x: float = 720, y: float = 1100):
    """Draws a clean, intuitive Name Tag visual showing how variables label data."""
    w, h = 300, 220
    draw.rounded_rectangle([x - w // 2, y - h // 2, x + w // 2, y + h // 2], radius=16, fill=PANEL_BG, outline=CYAN_ACCENT, width=3)
    # Header ribbon: "HELLO, MY NAME IS"
    draw.rounded_rectangle([x - w // 2, y - h // 2, x + w // 2, y - h // 2 + 50], radius=14, fill=CYAN_ACCENT)
    draw.rectangle([x - w // 2, y - h // 2 + 35, x + w // 2, y - h // 2 + 50], fill=CYAN_ACCENT)
    draw.text((x, y - h // 2 + 25), "PYTHON NAME TAG", fill=(10, 15, 25), font=get_font("bold", 22), anchor="mm")

    # Name tag label
    draw.text((x, y - 5), var_name, fill=GOLD_VAL, font=get_font("bold", 44), anchor="mm")
    draw.line([(x - 90, y + 25), (x + 90, y + 25)], fill=(40, 50, 70), width=2)
    draw.text((x, y + 55), f'holds: {var_val}', fill=WHITE, font=get_font("mono", 30), anchor="mm")


def draw_callout_banner(draw: ImageDraw.ImageDraw, badge_text: str, line1: str, line2: str = "", is_error: bool = False):
    by = 1600
    border_col = ERROR_RED if is_error else CYAN_ACCENT
    draw.rounded_rectangle([50, by, WIDTH - 50, by + 230], radius=22, fill=PANEL_BG, outline=border_col, width=3)
    badge_bg = (60, 20, 25) if is_error else (30, 48, 75)
    badge_fg = ERROR_RED if is_error else GOLD_VAL
    draw.rounded_rectangle([80, by + 18, 560, by + 68], radius=12, fill=badge_bg)
    draw.text((95, by + 43), badge_text, fill=badge_fg, font=font_sub, anchor="lm")
    draw.text((80, by + 105), line1[:44], fill=WHITE, font=font_callout)
    if line2:
        draw.text((80, by + 155), line2[:50], fill=MUTED_GRAY, font=font_sub)


# -------------------------------------------------------------
# MAIN RENDER FUNCTION
# -------------------------------------------------------------
def render_trial_video():
    final_video = RENDERED_DIR / "trial_python_lesson1_variables.mp4"
    final_thumb = THUMBNAILS_DIR / "trial_python_lesson1_variables.jpg"
    narration_audio = TEMP_DIR / "narration.mp3"

    print(f"\n==================================================================")
    print(f"🎬 RENDERING MASTER TRIAL VIDEO: PYTHON VARIABLES (LESSON 1)")
    print(f"Goal: High Retention, 2 Errors -> Right Code, Zero Memory Jargon!")
    print(f"Canvas: {WIDTH}x{HEIGHT} @ {FPS} FPS | Duration: {TOTAL_SECONDS}s ({TOTAL_FRAMES} frames)")
    print(f"==================================================================")

    # 1. Synthesize Narration Audio with Edge-TTS
    print("\n[1/3] Generating crystal clear neural narration via Edge-TTS...")
    script = (
        "Welcome to Python Lesson 1! What is a variable? Think of it simply as a labeled name tag for your data. "
        "Mistake 1: Using a variable before creating it! If you print score, Python crashes with NameError because score does not exist yet! "
        "Mistake 2: Starting a name with a number! In Python, variable names cannot start with digits or spaces. Writing 1st_score causes an instant SyntaxError! "
        "Here is the right way! First assign player equals Alex, and score equals 100. Now when we print, Python outputs: Alex scored 100 with zero errors! "
        "Two simple rules: define before use, and start with letters. Follow for Lesson 2: Python Data Types!"
    )

    async def _gen_tts():
        import edge_tts
        tts = edge_tts.Communicate(script, "en-US-ChristopherNeural", rate="+8%")
        await tts.save(str(narration_audio))

    asyncio.run(_gen_tts())
    print(f"✅ Narration saved: {narration_audio}")

    # 2. Render all 1440 frames
    print("\n[2/3] Rendering progressive animation frames...")
    desk_x, desk_y = 100, 1380

    for frame in range(TOTAL_FRAMES):
        t = frame / FPS

        img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(img)

        # Subtle dark blueprint grid
        for gy in range(0, HEIGHT, 100):
            draw.line([(0, gy), (WIDTH, gy)], fill=(16, 20, 28), width=1)
        for gx in range(0, WIDTH, 100):
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(16, 20, 28), width=1)

        # Floor line
        draw.line([(0, 1580), (WIDTH, 1580)], fill=(35, 45, 60), width=4)

        # Top Header Pill (Safe Zone Y=45 to 175)
        draw.rounded_rectangle([60, 45, WIDTH - 60, 175], radius=20, fill=PANEL_BG, outline=PANEL_BORDER, width=2)
        draw.text((WIDTH // 2, 85), "PYTHON MASTERCLASS • LESSON 1", fill=STICK_YELLOW, font=font_header, anchor="mm")
        draw.text((WIDTH // 2, 135), "Variables Explained (And The 2 Critical Mistakes!)", fill=WHITE, font=font_sub, anchor="mm")

        # -------------------------------------------------------------
        # SYNCHRONIZED TIMELINE (48.0s Total)
        # -------------------------------------------------------------

        # --- BEAT 1: 0.0s - 7.0s (Intro: What is a Variable?) ---
        if t < 7.0:
            lines = ["# What is a Variable in Python?", 'player = "Alex"']
            draw_floating_code_editor(draw, lines, [False, False])
            draw_nametag_visual(draw, var_name="player", var_val='"Alex"')

            if t < 2.5:
                # Walk in from left
                walk_p = t / 2.5
                sm_x = int(-100 + (desk_x + 280 + 100) * walk_p)
                draw_desk_and_laptop(draw, desk_x, desk_y, laptop_open=0.0)
                draw_yellow_stickman(draw, sm_x, 1540, action="walk", param=walk_p, face="smile")
            else:
                # Sits and opens laptop
                open_p = min(1.0, (t - 2.5) / 1.5)
                draw_desk_and_laptop(draw, desk_x, desk_y, laptop_open=open_p)
                draw_yellow_stickman(draw, desk_x + 280, 1420, action="typing_at_laptop", param=t, face="happy")

            draw_callout_banner(
                draw,
                badge_text="STEP 1: THE CONCEPT",
                line1="A variable is a labeled name tag for your data!",
                line2="It lets Python store values so your program can use them later."
            )

        # --- BEAT 2: 7.0s - 17.0s (Mistake 1: Using Variable Before Assigning) ---
        elif t < 17.0:
            lines = [
                "print(score)  # score was never created!"
            ]
            is_err_now = (t >= 9.5)
            draw_floating_code_editor(draw, lines, [True], is_error=is_err_now)

            if is_err_now:
                draw_terminal_output(draw, ["NameError: name 'score' is not defined"], is_error=True)
                draw_desk_and_laptop(draw, desk_x, desk_y, laptop_open=1.0)
                # Leaps up in shock with ? ?
                draw_yellow_stickman(draw, desk_x + 360, 1540, action="pacing_thinking", param=t, face="shocked")
            else:
                draw_desk_and_laptop(draw, desk_x, desk_y, laptop_open=1.0)
                draw_yellow_stickman(draw, desk_x + 280, 1420, action="typing_at_laptop", param=t, face="curious")

            draw_callout_banner(
                draw,
                badge_text="MISTAKE 1: NameError",
                line1="Never print or use a variable before assigning it!",
                line2="Python reads top-to-bottom: assign score first, then use it.",
                is_error=True
            )

        # --- BEAT 3: 17.0s - 27.0s (Mistake 2: Starting Name with a Number) ---
        elif t < 27.0:
            lines = [
                "1st_score = 100  # Starts with digit 1!"
            ]
            is_err_now = (t >= 19.5)
            draw_floating_code_editor(draw, lines, [True], is_error=is_err_now)

            if is_err_now:
                draw_terminal_output(draw, ["SyntaxError: invalid decimal literal"], is_error=True)
                draw_desk_and_laptop(draw, desk_x, desk_y, laptop_open=1.0)
                draw_yellow_stickman(draw, desk_x + 360, 1540, action="pacing_thinking", param=t, face="shocked")
            else:
                draw_desk_and_laptop(draw, desk_x, desk_y, laptop_open=1.0)
                draw_yellow_stickman(draw, desk_x + 280, 1420, action="typing_at_laptop", param=t, face="curious")

            draw_callout_banner(
                draw,
                badge_text="MISTAKE 2: SyntaxError",
                line1="Variable names can NEVER start with a number!",
                line2="Use score_1 or first_score. Letters & underscores only!",
                is_error=True
            )

        # --- BEAT 4: 27.0s - 38.0s (The Right Way: Live Typing Working Code) ---
        elif t < 38.0:
            lines = [
                'player = "Alex"',
                "score = 100",
                'print(player, "scored", score)'
            ]
            has_executed = (t >= 32.5)
            draw_floating_code_editor(draw, lines, [False, False, True], is_error=False)

            if has_executed:
                draw_terminal_output(draw, [
                    "Alex scored 100",
                    "[Program finished with exit code 0]"
                ], is_error=False)
                draw_desk_and_laptop(draw, desk_x, desk_y, laptop_open=1.0)
                # Pointing happily to success output
                draw_yellow_stickman(draw, desk_x + 360, 1540, action="point_right", face="happy")
            else:
                draw_desk_and_laptop(draw, desk_x, desk_y, laptop_open=1.0)
                draw_yellow_stickman(draw, desk_x + 280, 1420, action="typing_at_laptop", param=t, face="smile")

            draw_callout_banner(
                draw,
                badge_text="THE RIGHT WAY: SUCCESS!",
                line1='player = "Alex"; score = 100; print(...)',
                line2="Define first, follow naming rules -> clean, flawless execution!"
            )

        # --- BEAT 5: 38.0s - 48.0s (Victory Celebration & Follow CTA) ---
        else:
            lines = [
                'player = "Alex"',
                "score = 100",
                'print(player, "scored", score)'
            ]
            draw_floating_code_editor(draw, lines, [False, False, False], is_error=False)
            draw_terminal_output(draw, [
                "Alex scored 100",
                "[Program finished with exit code 0]"
            ], is_error=False)

            draw_desk_and_laptop(draw, desk_x, desk_y, laptop_open=1.0)

            if t < 43.5:
                # Jumping YAAAYYY! with golden stars!
                draw_yellow_stickman(draw, 540, 1540, action="yaay_celebrate", param=t, face="happy")
            else:
                # Proud thumbs up
                draw_yellow_stickman(draw, 520, 1540, action="thumbs_up", face="happy")

            # Next Episode Follow Banner (Safe Zone Y=1450 to 1565)
            draw.rounded_rectangle([60, 1450, WIDTH - 60, 1565], radius=18, fill=STICK_YELLOW)
            draw.text((WIDTH // 2, 1507), "FOLLOW FOR LESSON 2: DATA TYPES! 🚀", fill=(20, 20, 20), font=get_font("bold", 34), anchor="mm")

            draw_callout_banner(
                draw,
                badge_text="LESSON 1 MASTERED!",
                line1="Rule 1: Define before using! Rule 2: Start with letters!",
                line2="Next Episode: The 4 Core Data Types (int, float, str, bool)!"
            )

        frame_path = FRAMES_DIR / f"frame_{frame:04d}.png"
        img.save(frame_path, format="PNG")

        if frame % 250 == 0:
            print(f"  Rendered Frame {frame}/{TOTAL_FRAMES} ({t:.1f}s / {TOTAL_SECONDS:.1f}s)")

    print(f"✅ All {TOTAL_FRAMES} frames successfully rendered!")

    # 3. Foley SFX & Audio Mix with FFmpeg
    print("\n[3/3] Mixing neural narration and Foley sound effects via FFmpeg...")
    sfx_whoosh = SFX_DIR / "whoosh.wav"
    sfx_pop = SFX_DIR / "pop.wav"
    sfx_keyboard = SFX_DIR / "keyboard.wav"
    sfx_buzzer = SFX_DIR / "buzzer.wav"
    sfx_ding = SFX_DIR / "success_ding.wav"
    sfx_chime = SFX_DIR / "chime.wav"
    sfx_footsteps = SFX_DIR / "footsteps.wav"
    sfx_ambient = SFX_DIR / "ambient_coding_pad.wav"

    filter_complex = (
        "[0:v]fps=30,format=yuv420p[v];"
        "[1:a]volume=1.0[narr];"
        "[2:a]adelay=2500|2500,volume=0.35[s_whoosh];"
        "[3:a]adelay=7200|7200,volume=0.30[s_key1];"
        "[4:a]adelay=9600|9600,volume=0.55[s_buzz1];"
        "[5:a]adelay=11500|11500,volume=0.35[s_walk1];"
        "[3:a]adelay=17200|17200,volume=0.30[s_key2];"
        "[4:a]adelay=19600|19600,volume=0.55[s_buzz2];"
        "[5:a]adelay=21500|21500,volume=0.35[s_walk2];"
        "[3:a]adelay=27500|27500,volume=0.30[s_key3];"
        "[6:a]adelay=32800|32800,volume=0.60[s_ding];"
        "[7:a]adelay=38200|38200,volume=0.50[s_chime];"
        "[8:a]volume=0.15[s_amb];"
        "[narr][s_whoosh][s_key1][s_buzz1][s_walk1][s_key2][s_buzz2][s_walk2][s_key3][s_ding][s_chime][s_amb]amix=inputs=12:duration=first:dropout_transition=0,alimiter=limit=-1.5dB[a]"
    )

    cmd = [
        FFMPEG, "-y",
        "-framerate", str(FPS),
        "-i", str(FRAMES_DIR / "frame_%04d.png"),
        "-i", str(narration_audio),
        "-i", str(sfx_whoosh),
        "-i", str(sfx_keyboard),
        "-i", str(sfx_buzzer),
        "-i", str(sfx_footsteps),
        "-i", str(sfx_ding),
        "-i", str(sfx_chime),
        "-i", str(sfx_ambient),
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(TOTAL_SECONDS),
        str(final_video)
    ]

    subprocess.run(cmd, check=True)
    file_size_mb = os.path.getsize(final_video) / (1024 * 1024)
    print(f"\n🎉 MASTER TRIAL VIDEO GENERATED: {final_video} ({file_size_mb:.2f} MB)")

    # High CTR Thumbnail
    thumb_frame = FRAMES_DIR / f"frame_{int(39.0 * FPS):04d}.png"
    if thumb_frame.exists():
        im_thumb = Image.open(thumb_frame)
        im_thumb.save(final_thumb, "JPEG", quality=95)
        print(f"📸 Thumbnail saved: {final_thumb}")

    # Clean temporary frame files
    shutil.rmtree(FRAMES_DIR, ignore_errors=True)
    return str(final_video)


if __name__ == "__main__":
    render_trial_video()
