"""Master LeetCode 2D Stickman Visual Explainer Engine.

Pedagogy:
- Designed for students and coding interview preparation.
- Stickman stands beside the IDE, points at each code line.
- Text callout speech bubbles explain WHAT each line does and WHY.
- Closes with Emerald Green Accepted output, 3.5s YAAAYYY celebration, and 5.0s Takeaways.
"""

import os
import sys
import math
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings
from backend.app.core.ffmpeg_utils import get_ffmpeg_binary

FPS = 30
WIDTH = 1080
HEIGHT = 1920

ASSETS_DIR = BASE_DIR / "media_storage" / "assets"
SFX_DIR = ASSETS_DIR / "sfx"
TEMP_DIR = Path(settings.temp_path)
RENDERED_DIR = Path(settings.reels_output_path)
THUMBNAILS_DIR = Path(settings.media_storage_dir) / "thumbnails"

RENDERED_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Theme Palette (LeetCode Dark)
BG_COLOR = (13, 17, 23)
CARD_BG = (22, 27, 34)
CARD_BORDER = (48, 54, 61)
TERMINAL_BG = (10, 14, 20)
TERMINAL_BORDER = (33, 38, 45)
STICK_YELLOW = (255, 215, 0)
CYAN_KEYWORD = (88, 166, 255)
AMBER_NUMBER = (255, 166, 87)
PURPLE_OP = (210, 168, 255)
GREEN_STRING = (126, 231, 135)
WHITE_VAR = (240, 246, 252)
MUTED_TEXT = (139, 148, 158)
SUCCESS_GREEN = (63, 185, 80)
GOLD_BORDER = (245, 158, 11)
CALLOUT_BG = (30, 41, 59)
CALLOUT_BORDER = (56, 189, 248)


def load_font(font_names: List[str], size: int) -> ImageFont.ImageFont:
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
            matches = list(d.rglob(name))
            if matches:
                try:
                    return ImageFont.truetype(str(matches[0]), size)
                except Exception:
                    pass
    return ImageFont.load_default()


FONT_CODE = load_font(["consola.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"], 30)
FONT_CODE_BOLD = load_font(["consolab.ttf", "LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"], 30)
FONT_HEADER = load_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 38)
FONT_SUBTITLE = load_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 22)
FONT_CALLOUT = load_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 23)
FONT_TERM = load_font(["consola.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"], 26)
FONT_TERM_BOLD = load_font(["consolab.ttf", "LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"], 28)
FONT_ALERT = load_font(["arialbd.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], 26)
FONT_TAKEAWAY = load_font(["consola.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"], 24)
FONT_TAKEAWAY_BOLD = load_font(["consolab.ttf", "LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"], 24)


def draw_vector_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, r_outer: int = 12, r_inner: int = 5, fill: Tuple[int, int, int] = GOLD_BORDER):
    pts = []
    for i in range(10):
        r = r_outer if i % 2 == 0 else r_inner
        ang = i * math.pi / 5 - math.pi / 2
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def draw_fitted_line(draw: ImageDraw.ImageDraw, x: int, y: int, max_w: int, text: str, fill: Tuple[int, int, int], bold: bool = False):
    font_names = ["consolab.ttf", "LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"] if bold else ["consola.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"]
    for sz in range(24, 15, -1):
        f = load_font(font_names, sz)
        w = draw.textlength(text, font=f)
        if w <= max_w:
            draw.text((x, y), text, fill=fill, font=f)
            return
    f = load_font(font_names, 16)
    clipped = text
    while len(clipped) > 8 and draw.textlength(clipped + "...", font=f) > max_w:
        clipped = clipped[:-1]
    draw.text((x, y), clipped + "...", fill=fill, font=f)


def draw_standing_stickman(draw: ImageDraw.ImageDraw, x: int = 190, y_floor: int = 1450, point_y: int = 600, t: float = 0.0):
    """Draws stickman standing beside IDE, pointing his right arm and hand toward active code line."""
    color = STICK_YELLOW
    head_r = 22
    head_cy = y_floor - 200
    torso_top = head_cy + head_r
    torso_bot = y_floor - 90

    # Head
    draw.ellipse([x - head_r, head_cy - head_r, x + head_r, head_cy + head_r], outline=color, width=4)
    # Smile / eye looking at code
    draw.ellipse([x + 6, head_cy - 6, x + 10, head_cy - 2], fill=color)

    # Torso
    draw.line([(x, torso_top), (x, torso_bot)], fill=color, width=5)

    # Left arm resting on hip
    draw.line([(x, torso_top + 18), (x - 28, torso_top + 45)], fill=color, width=4)
    draw.line([(x - 28, torso_top + 45), (x - 6, torso_top + 65)], fill=color, width=4)

    # Right arm pointing up/right at target code line!
    elbow_x = x + 35
    elbow_y = torso_top + 25
    target_hand_x = 360
    target_hand_y = max(450, min(point_y, 1100))
    draw.line([(x, torso_top + 18), (elbow_x, elbow_y)], fill=color, width=4)
    draw.line([(elbow_x, elbow_y), (target_hand_x, target_hand_y)], fill=color, width=4)
    # Pointing finger
    draw.ellipse([target_hand_x - 4, target_hand_y - 4, target_hand_x + 4, target_hand_y + 4], fill=color)

    # Legs
    draw.line([(x, torso_bot), (x - 20, y_floor)], fill=color, width=5)
    draw.line([(x, torso_bot), (x + 20, y_floor)], fill=color, width=5)


def draw_callout_box(draw: ImageDraw.ImageDraw, x: int, y: int, text: str):
    """Draws a modern high-contrast speech/callout box pointing to the code."""
    padding_x = 24
    padding_y = 14
    f = FONT_CALLOUT
    text_w = draw.textlength(text, font=f)
    box_w = int(text_w + padding_x * 2)
    box_h = 56

    bx0 = max(240, min(x, 1000 - box_w))
    by0 = y - box_h - 12
    bx1 = bx0 + box_w
    by1 = by0 + box_h

    # Speech Bubble
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=14, fill=CALLOUT_BG, outline=CALLOUT_BORDER, width=2)
    # Pointer triangle pointing down/left toward stickman hand
    draw.polygon([(bx0 + 30, by1), (bx0 + 44, by1 + 10), (bx0 + 58, by1)], fill=CALLOUT_BG)
    draw.line([(bx0 + 30, by1), (bx0 + 44, by1 + 10)], fill=CALLOUT_BORDER, width=2)
    draw.line([(bx0 + 44, by1 + 10), (bx0 + 58, by1)], fill=CALLOUT_BORDER, width=2)

    draw.text((bx0 + padding_x, by0 + padding_y), text, fill=(255, 255, 255), font=f)


def render_leetcode_episode(prob_data: Dict[str, Any]) -> str:
    """Renders 31.0s LeetCode visual explainer Reel with line-by-line speech callouts."""
    prob_id = prob_data.get("problem_id", 1)
    title = prob_data.get("title", f"LeetCode #{prob_id}")
    filename = prob_data.get("filename", f"solution_{prob_id}.py")
    steps = prob_data.get("solution_steps", [])
    output_text = prob_data.get("terminal_output", "[Accepted] Runtime: 38ms")
    t1 = prob_data.get("takeaway_l1", "1. Optimal O(N) Algorithm")
    t2 = prob_data.get("takeaway_l2", "2. Clean single pass execution")
    teaser = prob_data.get("next_teaser", f"LeetCode #{prob_id + 1}")

    file_prefix = f"leetcode_ep{prob_id}"
    final_video = RENDERED_DIR / f"{file_prefix}.mp4"
    final_thumb = THUMBNAILS_DIR / f"{file_prefix}.jpg"
    ep_frames_dir = TEMP_DIR / f"frames_{file_prefix}"
    shutil.rmtree(ep_frames_dir, ignore_errors=True)
    ep_frames_dir.mkdir(parents=True, exist_ok=True)

    TOTAL_SECONDS = 31.0
    TOTAL_FRAMES = int(TOTAL_SECONDS * FPS)

    # Timeline Allocation:
    # 0.0s - 2.5s: Problem statement intro & Stickman walks in
    # 2.5s - 21.0s: Line-by-line typing + stickman points + callout box appears
    # 21.0s - 22.5s: Code execution -> Emerald Green Accepted
    # 22.5s - 26.0s: 3.5s "YAAAYYY!" Victory Jump
    # 26.0s - 31.0s: 5.0s Key Takeaways Box

    num_steps = len(steps)
    step_duration = (21.0 - 2.5) / max(num_steps, 1)

    print(f"🎬 Generating LeetCode Reel: {title} ({num_steps} steps, {TOTAL_SECONDS}s @ {FPS}fps)...")

    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / FPS
        im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(im)

        # Header Badge
        draw.rounded_rectangle([80, 240, 1000, 330], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)
        draw_vector_star(draw, 125, 285, r_outer=14, r_inner=6, fill=(255, 184, 0))
        draw.text((155, 260), title, fill=(255, 255, 255), font=FONT_HEADER)

        # Main Code Window (Y=350 to Y=1120)
        ed_x0, ed_y0, ed_x1, ed_y1 = 80, 350, 1000, 1120
        draw.rounded_rectangle([ed_x0, ed_y0, ed_x1, ed_y1], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)
        # Window bar
        draw.rounded_rectangle([ed_x0, ed_y0, ed_x1, ed_y0 + 44], radius=16, fill=(33, 38, 45))
        draw.rectangle([ed_x0, ed_y0 + 30, ed_x1, ed_y0 + 44], fill=(33, 38, 45))
        draw.ellipse([ed_x0 + 16, ed_y0 + 15, ed_x0 + 28, ed_y0 + 27], fill=(239, 68, 68))
        draw.ellipse([ed_x0 + 36, ed_y0 + 15, ed_x0 + 48, ed_y0 + 27], fill=(245, 158, 11))
        draw.ellipse([ed_x0 + 56, ed_y0 + 15, ed_x0 + 68, ed_y0 + 27], fill=(34, 197, 94))
        draw.text((ed_x0 + 80, ed_y0 + 11), filename, fill=(203, 213, 225), font=FONT_SUBTITLE)

        # Terminal Box (Y=1140 to Y=1310)
        tm_x0, tm_y0, tm_x1, tm_y1 = 80, 1140, 1000, 1310
        draw.rounded_rectangle([tm_x0, tm_y0, tm_x1, tm_y1], radius=16, fill=TERMINAL_BG, outline=TERMINAL_BORDER, width=2)
        draw.rounded_rectangle([tm_x0, tm_y0, tm_x1, tm_y0 + 44], radius=16, fill=(22, 27, 34))
        draw.rectangle([tm_x0, tm_y0 + 30, tm_x1, tm_y0 + 44], fill=(22, 27, 34))
        draw.text((tm_x0 + 30, tm_y0 + 11), "terminal - python", fill=(148, 163, 184), font=FONT_SUBTITLE)

        if t < 2.5:
            # Intro: walk-in
            walk_progress = min(1.0, t / 2.2)
            cur_x = int(50 + walk_progress * 140)
            # Walk-in stickman
            draw_standing_stickman(draw, x=cur_x, y_floor=1450, point_y=500, t=t)
            draw.text((ed_x0 + 35, ed_y0 + 75), "# Solving LeetCode with Python", fill=MUTED_TEXT, font=FONT_CODE)
            draw.text((ed_x0 + 35, ed_y0 + 125), "# Watch line-by-line explanation:", fill=CYAN_KEYWORD, font=FONT_CODE)

        elif t < 21.0:
            # Active step calculation
            elapsed_steps = t - 2.5
            active_step_idx = min(num_steps - 1, int(elapsed_steps / step_duration))
            active_line_y = ed_y0 + 75 + active_step_idx * 55

            # Stickman standing and pointing at active line
            draw_standing_stickman(draw, x=190, y_floor=1450, point_y=active_line_y, t=t)

            # Draw lines up to active step
            for idx in range(active_step_idx + 1):
                code_line, explanation = steps[idx]
                line_y = ed_y0 + 75 + idx * 55
                draw.text((ed_x0 + 30, line_y), str(idx + 1), fill=MUTED_TEXT, font=FONT_CODE)
                # Code text
                is_active = (idx == active_step_idx)
                c_fill = (255, 255, 255) if is_active else (180, 190, 205)
                draw.text((ed_x0 + 80, line_y), code_line, fill=c_fill, font=FONT_CODE_BOLD if is_active else FONT_CODE)

            # Speech Callout Box for active line
            current_explanation = steps[active_step_idx][1]
            draw_callout_box(draw, x=380, y=active_line_y, text=current_explanation)

            # Terminal shows running
            draw.text((tm_x0 + 35, tm_y0 + 65), f"$ python {filename}", fill=MUTED_TEXT, font=FONT_TERM)

        elif t < 22.5:
            # Green Output Appears
            draw_standing_stickman(draw, x=190, y_floor=1450, point_y=600, t=t)
            for idx, (code_line, _) in enumerate(steps):
                line_y = ed_y0 + 75 + idx * 55
                draw.text((ed_x0 + 30, line_y), str(idx + 1), fill=MUTED_TEXT, font=FONT_CODE)
                draw.text((ed_x0 + 80, line_y), code_line, fill=(255, 255, 255), font=FONT_CODE)

            draw.text((tm_x0 + 35, tm_y0 + 65), output_text, fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)
            draw.text((tm_x0 + 35, tm_y0 + 110), "[Execution completed with exit code 0]", fill=MUTED_TEXT, font=FONT_TERM)

        elif t < 26.0:
            # 3.5s "YAAAYYY!" Victory Jump in Center!
            jump_t = (t - 22.5) / 3.5
            bounce = abs(math.sin(jump_t * math.pi * 5)) * 60
            hero_x = 540
            hero_y = int(1400 - bounce)

            # Draw Victory Stickman
            draw.ellipse([hero_x - 26, hero_y - 200, hero_x + 26, hero_y - 148], outline=STICK_YELLOW, width=5)
            draw.line([(hero_x, hero_y - 148), (hero_x, hero_y - 70)], fill=STICK_YELLOW, width=6)
            # Pumping both arms high in the air
            draw.line([(hero_x, hero_y - 130), (hero_x - 55, hero_y - 210)], fill=STICK_YELLOW, width=5)
            draw.line([(hero_x, hero_y - 130), (hero_x + 55, hero_y - 210)], fill=STICK_YELLOW, width=5)
            # Jumping legs
            draw.line([(hero_x, hero_y - 70), (hero_x - 40, hero_y)], fill=STICK_YELLOW, width=6)
            draw.line([(hero_x, hero_y - 70), (hero_x + 40, hero_y)], fill=STICK_YELLOW, width=6)

            # Comic "YAAAYYY!" Speech Bubble
            draw.rounded_rectangle([hero_x - 110, hero_y - 300, hero_x + 110, hero_y - 230], radius=18, fill=(255, 255, 255))
            draw.polygon([(hero_x - 15, hero_y - 230), (hero_x, hero_y - 210), (hero_x + 15, hero_y - 230)], fill=(255, 255, 255))
            draw.text((hero_x - 85, hero_y - 290), "YAAAYYY!", fill=(225, 29, 72), font=FONT_HEADER)

            # Sparkle Golden Stars
            for ang in [0.5, 1.2, 2.1, 3.8, 4.9]:
                sx = int(hero_x + 160 * math.cos(ang + t * 4))
                sy = int(hero_y - 150 + 80 * math.sin(ang + t * 4))
                draw_vector_star(draw, sx, sy, r_outer=14, r_inner=6, fill=GOLD_BORDER)

            # Code and Green Output
            for idx, (code_line, _) in enumerate(steps[:6]):
                line_y = ed_y0 + 75 + idx * 55
                draw.text((ed_x0 + 80, line_y), code_line, fill=(200, 210, 225), font=FONT_CODE)
            draw.text((tm_x0 + 35, tm_y0 + 65), output_text, fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)

        else:
            # 5.0s Key Takeaways Box
            for idx, (code_line, _) in enumerate(steps[:6]):
                line_y = ed_y0 + 75 + idx * 55
                draw.text((ed_x0 + 80, line_y), code_line, fill=(200, 210, 225), font=FONT_CODE)
            draw.text((tm_x0 + 35, tm_y0 + 65), output_text, fill=SUCCESS_GREEN, font=FONT_TERM_BOLD)

            # Standing stickman with thumbs up
            draw_standing_stickman(draw, x=190, y_floor=1450, point_y=600, t=t)

            # Framed Golden Takeaways Box
            box_y0, box_y1 = 1140, 1310
            draw.rounded_rectangle([ed_x0, box_y0, ed_x1, box_y1], radius=16, fill=(28, 22, 10), outline=GOLD_BORDER, width=3)
            draw_vector_star(draw, ed_x0 + 36, box_y0 + 27, r_outer=11, r_inner=5, fill=GOLD_BORDER)
            draw.text((ed_x0 + 58, box_y0 + 15), "KEY TAKEAWAYS:", fill=GOLD_BORDER, font=FONT_ALERT)
            max_w = (ed_x1 - ed_x0) - 60
            draw_fitted_line(draw, ed_x0 + 30, box_y0 + 58, max_w, t1, WHITE_VAR, bold=True)
            draw_fitted_line(draw, ed_x0 + 30, box_y0 + 104, max_w, t2, GREEN_STRING, bold=False)

        # Instagram Safe Zone CTA (Centered at Y=1720)
        draw.rounded_rectangle([200, 1700, 880, 1775], radius=38, fill=(225, 29, 72))
        follow_text = f"▶ FOLLOW FOR {teaser.upper()}!"
        draw.text((230, 1722), follow_text, fill=(255, 255, 255), font=FONT_ALERT)

        im.save(ep_frames_dir / f"f_{frame_idx:05d}.png")

    # Victory thumbnail
    thumb_idx = int(24.5 * FPS)
    thumb_frame = Image.open(ep_frames_dir / f"f_{thumb_idx:05d}.png")
    thumb_frame.save(final_thumb, quality=95)
    print(f"📸 LeetCode Thumbnail saved: {final_thumb}")

    # FFmpeg Encoding with Foley SFX
    sfx_ambient = SFX_DIR / "ambient_coding_pad.wav"
    sfx_keyboard = SFX_DIR / "keyboard.wav"
    sfx_ding = SFX_DIR / "success_ding.wav"
    sfx_chime = SFX_DIR / "chime.wav"

    filter_complex = (
        "[1:a]volume=0.18[amb];"
        "[2:a]adelay=2500|2500,volume=0.45[k1];"
        "[2:a]adelay=6000|6000,volume=0.45[k2];"
        "[2:a]adelay=10000|10000,volume=0.45[k3];"
        "[2:a]adelay=14000|14000,volume=0.45[k4];"
        "[2:a]adelay=18000|18000,volume=0.45[k5];"
        "[3:a]adelay=21000|21000,volume=0.85[ding];"
        "[4:a]adelay=22500|22500,volume=0.75[chime];"
        "[amb][k1][k2][k3][k4][k5][ding][chime]"
        "amix=inputs=8:duration=longest,volume=2.2,alimiter=limit=-1.5dB[aout]"
    )

    cmd = [
        get_ffmpeg_binary(), "-y",
        "-r", str(FPS),
        "-i", str(ep_frames_dir / "f_%05d.png"),
        "-i", str(sfx_ambient),
        "-i", str(sfx_keyboard),
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
    print(f"🎉 LEETCODE REEL SAVED: {final_video}")
    return str(final_video)
