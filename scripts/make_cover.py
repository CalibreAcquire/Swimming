#!/usr/bin/env python3
"""Reel / Short cover (1080x1920) in the caption style: a 9:16 frame of Jake with a
stacked headline over his chest.

Lines are "style:text", styles as in the captions: bold (Montserrat ExtraBold, white),
italic (Cormorant Garamond italic, white), key (Montserrat Black caps, #FFDE59).
Text stays inside the 3:4 area Instagram shows on the profile grid.

Usage: make_cover.py <video> <time_s> <crop_centre_x> <out.jpg> "bold:Are you" "key:OVERPAYING?"
"""
import os, subprocess, sys, tempfile

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(REPO, "brand", "fonts")
W, H = 1080, 1920
YELLOW = (255, 222, 89)
STYLES = {"bold": ("Montserrat-800.ttf", 104, "white"),
          "italic": ("CormorantGaramond-500-Italic.ttf", 150, "white"),
          "key": ("Montserrat-900.ttf", 150, YELLOW)}
GRADE = "eq=contrast=1.06:saturation=0.94:gamma=0.98,colorbalance=rh=-0.02:bh=0.02"


def frame(video, t, cx):
    """9:16 crop of the source frame around x=cx, scaled to 1080x1920."""
    out = tempfile.mktemp(suffix=".png")
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height", "-of", "csv=p=0", video], capture_output=True, text=True)
    sw, sh = map(int, probe.stdout.strip().split(","))
    cw = sh * 9 / 16
    x0 = min(max(0, cx - cw / 2), sw - cw)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", "-vf",
                    f"{GRADE},crop={cw:.0f}:{sh}:{x0:.0f}:0,scale={W}:{H}:flags=lanczos,unsharp=5:5:0.5",
                    out], check=True)
    img = Image.open(out).convert("RGB")
    os.remove(out)
    return img


def cover(video, t, cx, out, lines, centre_y=1120):
    img = frame(video, t, cx)
    # soft darkening behind the text for legibility
    shade = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(shade)
    for y in range(H):
        dist = abs(y - centre_y) / 520
        d.line([(0, y), (W, y)], fill=int(150 * max(0, 1 - dist) ** 1.5))
    img = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, shade)

    d = ImageDraw.Draw(img)
    parsed = []
    for spec in lines:
        style, text = spec.split(":", 1)
        fname, size, colour = STYLES[style]
        font = ImageFont.truetype(os.path.join(F, fname), size)
        while font.getlength(text) > W * 0.86 and size > 40:  # fit width
            size -= 4
            font = ImageFont.truetype(os.path.join(F, fname), size)
        top, bottom = font.getbbox(text, anchor="ls")[1], font.getbbox(text, anchor="ls")[3]
        parsed.append((text, font, colour, -top, bottom, size))
    gap = 18
    total = sum(a + b for _, _, _, a, b, _ in parsed) + gap * (len(parsed) - 1)
    y = centre_y - total / 2
    for text, font, colour, asc, desc, size in parsed:
        y += asc
        d.text((W / 2 + 3, y + 4), text, font=font, fill=(0, 0, 0), anchor="ms")  # subtle drop shadow
        d.text((W / 2, y), text, font=font, fill=colour, anchor="ms")
        y += desc + gap
    assert 240 < centre_y - total / 2 and centre_y + total / 2 < 1680, "text outside the profile-grid area"

    logo = Image.open(os.path.join(REPO, "brand", "logos", "monogram-black.png")).convert("RGBA").resize((56, 56), Image.LANCZOS)
    logo.putalpha(logo.split()[3].point(lambda v: int(v * 0.6)))
    img.paste(logo, (W - 56 - 60, 290), logo)
    img.save(out, quality=94)
    print(f"cover -> {out}")


if __name__ == "__main__":
    if len(sys.argv) < 6:
        sys.exit(__doc__)
    cover(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5:])
