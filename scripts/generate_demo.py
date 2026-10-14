from __future__ import annotations

from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont

CANVAS_WIDTH = 900
CANVAS_HEIGHT = 620
TERM_X = 20
TERM_Y = 20
TERM_WIDTH = CANVAS_WIDTH - (TERM_X * 2)
TERM_HEIGHT = CANVAS_HEIGHT - (TERM_Y * 2)

CANVAS_BG = (13, 17, 23)
TERM_BG = (22, 27, 34)
HEADER_BG = (30, 36, 46)
BORDER_COLOR = (48, 54, 61)

FG_TEXT = (230, 237, 243)
MUTED_TEXT = (139, 148, 158)
CYAN_ACCENT = (56, 189, 248)
GREEN_ACCENT = (52, 211, 153)
YELLOW_ACCENT = (251, 191, 36)

RED_BTN = (255, 95, 86)
YELLOW_BTN = (255, 189, 46)
GREEN_BTN = (39, 201, 63)


def load_fonts() -> tuple[ImageFont.ImageFont, ImageFont.ImageFont, ImageFont.ImageFont]:
    font = ImageFont.truetype("C:/Windows/Fonts/CascadiaCode.ttf", 16)
    bold_font = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 16)
    title_font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 13)
    return font, bold_font, title_font


def create_base_terminal(title_font: ImageFont.ImageFont) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), CANVAS_BG)
    draw = ImageDraw.Draw(img)

    # Window body
    draw.rounded_rectangle(
        [(TERM_X, TERM_Y), (TERM_X + TERM_WIDTH, TERM_Y + TERM_HEIGHT)],
        radius=10,
        fill=TERM_BG,
        outline=BORDER_COLOR,
        width=1,
    )

    # Window header
    header_h = 38
    draw.rounded_rectangle(
        [(TERM_X, TERM_Y), (TERM_X + TERM_WIDTH, TERM_Y + header_h)],
        radius=10,
        fill=HEADER_BG,
    )
    draw.rectangle(
        [(TERM_X, TERM_Y + header_h - 10), (TERM_X + TERM_WIDTH, TERM_Y + header_h)],
        fill=HEADER_BG,
    )
    draw.line(
        [(TERM_X, TERM_Y + header_h), (TERM_X + TERM_WIDTH, TERM_Y + header_h)],
        fill=BORDER_COLOR,
        width=1,
    )

    # Traffic light buttons
    for bx, c in [(TERM_X + 18, RED_BTN), (TERM_X + 38, YELLOW_BTN), (TERM_X + 58, GREEN_BTN)]:
        draw.ellipse([(bx - 6, TERM_Y + 14 - 6), (bx + 6, TERM_Y + 14 + 6)], fill=c)

    # Window title centered
    title = "user@workstation: ~/dailybrief"
    tw = title_font.getbbox(title)[2] - title_font.getbbox(title)[0]
    draw.text((TERM_X + (TERM_WIDTH - tw) // 2, TERM_Y + 11), title, font=title_font, fill=MUTED_TEXT)

    return img, draw


def render_typing_frame(
    typed_text: str,
    cursor: bool,
    fonts: tuple[ImageFont.ImageFont, ImageFont.ImageFont, ImageFont.ImageFont],
) -> Image.Image:
    font, bold_font, title_font = fonts
    img, draw = create_base_terminal(title_font)

    cur_y = TERM_Y + 52
    draw.text((TERM_X + 24, cur_y), "$ ", font=bold_font, fill=GREEN_ACCENT)
    pw = bold_font.getbbox("$ ")[2] - bold_font.getbbox("$ ")[0]
    draw.text((TERM_X + 24 + pw, cur_y), typed_text, font=font, fill=FG_TEXT)

    if cursor:
        tw = font.getbbox(typed_text)[2] - font.getbbox(typed_text)[0] if typed_text else 0
        draw.text((TERM_X + 24 + pw + tw, cur_y), "█", font=font, fill=CYAN_ACCENT)

    return img


def render_spinner_frame(
    command: str,
    spinner_char: str,
    message: str,
    fonts: tuple[ImageFont.ImageFont, ImageFont.ImageFont, ImageFont.ImageFont],
) -> Image.Image:
    font, bold_font, title_font = fonts
    img, draw = create_base_terminal(title_font)

    cur_y = TERM_Y + 52
    draw.text((TERM_X + 24, cur_y), "$ ", font=bold_font, fill=GREEN_ACCENT)
    pw = bold_font.getbbox("$ ")[2] - bold_font.getbbox("$ ")[0]
    draw.text((TERM_X + 24 + pw, cur_y), command, font=font, fill=FG_TEXT)

    cur_y += 32
    draw.text((TERM_X + 24, cur_y), f"{spinner_char} {message}", font=font, fill=CYAN_ACCENT)

    return img


def render_full_output(
    command: str,
    show_cursor: bool,
    fonts: tuple[ImageFont.ImageFont, ImageFont.ImageFont, ImageFont.ImageFont],
) -> Image.Image:
    font, bold_font, title_font = fonts
    img, draw = create_base_terminal(title_font)

    # Prompt
    cur_y = TERM_Y + 52
    draw.text((TERM_X + 24, cur_y), "$ ", font=bold_font, fill=GREEN_ACCENT)
    pw = bold_font.getbbox("$ ")[2] - bold_font.getbbox("$ ")[0]
    draw.text((TERM_X + 24 + pw, cur_y), command, font=font, fill=FG_TEXT)

    # Header panel (Cyan)
    cur_y += 36
    panel_x = TERM_X + 24
    panel_w = TERM_WIDTH - 48
    header_panel_h = 60
    draw.rounded_rectangle([(panel_x, cur_y), (panel_x + panel_w, cur_y + header_panel_h)], radius=6, outline=CYAN_ACCENT, width=1)

    t1 = "DailyBrief"
    t1_w = bold_font.getbbox(t1)[2] - bold_font.getbbox(t1)[0]
    draw.text((panel_x + (panel_w - t1_w) // 2, cur_y + 10), t1, font=bold_font, fill=CYAN_ACCENT)

    t2 = "Date: 2026-10-15"
    t2_w = font.getbbox(t2)[2] - font.getbbox(t2)[0]
    draw.text((panel_x + (panel_w - t2_w) // 2, cur_y + 32), t2, font=font, fill=MUTED_TEXT)

    # Content panel (Green)
    cur_y += header_panel_h + 18
    brief_panel_h = 240
    draw.rounded_rectangle([(panel_x, cur_y), (panel_x + panel_w, cur_y + brief_panel_h)], radius=6, outline=GREEN_ACCENT, width=1)

    btitle = " Daily Brief "
    btw = bold_font.getbbox(btitle)[2] - bold_font.getbbox(btitle)[0]
    draw.rectangle([(panel_x + 18, cur_y - 2), (panel_x + 18 + btw, cur_y + 2)], fill=TERM_BG)
    draw.text((panel_x + 18, cur_y - 10), btitle, font=bold_font, fill=GREEN_ACCENT)

    cy = cur_y + 20
    cx = panel_x + 24
    draw.text((cx, cy), "Key Priorities for Today", font=bold_font, fill=YELLOW_ACCENT)
    cy += 26
    draw.text((cx, cy), "1. Fix login session timeout bug before noon release", font=font, fill=FG_TEXT)
    cy += 24
    draw.text((cx, cy), "2. Finalize & publish v0.2.0 changelog to GitHub", font=font, fill=FG_TEXT)
    cy += 24
    draw.text((cx, cy), "3. Align with design team on onboarding copy adjustments", font=font, fill=FG_TEXT)

    cy += 32
    draw.text((cx, cy), "Things Not to Forget / Follow-ups", font=bold_font, fill=CYAN_ACCENT)
    cy += 26
    draw.text((cx, cy), "- Standup status update at 10:30 AM (5-min prep)", font=font, fill=FG_TEXT)
    cy += 24
    draw.text((cx, cy), "- Review analytics funnel conversion report at 16:00", font=font, fill=FG_TEXT)
    cy += 24
    draw.text((cx, cy), "- Triage incoming customer feedback into repo issues", font=font, fill=FG_TEXT)

    # Footer
    cur_y += brief_panel_h + 12
    draw.text((panel_x, cur_y), "Compiled from 3 file(s)", font=font, fill=MUTED_TEXT)

    # Return prompt
    cur_y += 30
    draw.text((panel_x, cur_y), "$ ", font=bold_font, fill=GREEN_ACCENT)
    if show_cursor:
        draw.text((panel_x + pw, cur_y), "█", font=font, fill=CYAN_ACCENT)

    return img


def main() -> None:
    fonts = load_fonts()
    frames: list[Image.Image] = []
    durations: list[int] = []

    command = "dailybrief --source ./notes"

    # 1. Start with cursor blink
    frames.append(render_typing_frame("", True, fonts))
    durations.append(450)
    frames.append(render_typing_frame("", False, fonts))
    durations.append(300)

    # 2. Typing keystrokes
    for i in range(1, len(command) + 1):
        typed = command[:i]
        cursor = (i % 2 == 0 or i == len(command))
        frames.append(render_typing_frame(typed, cursor, fonts))
        delay = 80 if command[i - 1] == " " else random.randint(35, 60)
        durations.append(delay)

    # 3. Short pause after enter
    frames.append(render_typing_frame(command, False, fonts))
    durations.append(250)

    # 4. Spinner frames
    spinners = [
        ("*", "Scanning ./notes (3 files found)..."),
        ("*", "Analyzing notes with Claude Sonnet..."),
        ("*", "Generating daily briefing..."),
    ]
    for sp_char, sp_msg in spinners:
        frames.append(render_spinner_frame(command, sp_char, sp_msg, fonts))
        durations.append(220)

    # 5. Full output with reading pause
    full_with_cursor = render_full_output(command, True, fonts)
    frames.append(full_with_cursor)
    durations.append(4200)

    # Final frame cursor blink before loop
    full_no_cursor = render_full_output(command, False, fonts)
    frames.append(full_no_cursor)
    durations.append(600)

    output_path = Path(__file__).resolve().parents[1] / "demo.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"Generated clean demo GIF: {output_path} ({len(frames)} frames)")


if __name__ == "__main__":
    main()