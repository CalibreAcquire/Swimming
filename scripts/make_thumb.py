#!/usr/bin/env python3
"""YouTube thumbnail (1280x720): stacked text on the left, Jake on the right.

Lines are "style:text" as on covers: bold (Montserrat Black, white), italic (Cormorant
Garamond italic, white), key (Montserrat Black, #FFDE59). Optional small spaced label under
the text, and an optional photo (e.g. the building) behind the text panel instead of black.
Monogram bottom-left (YouTube's timestamp covers bottom-right).

Usage: make_thumb.py <video> <time_s> <jake_centre_x> <out.jpg> [--label TEXT] [--photo IMG]
                     "bold:SOLD IN" "italic:weeks" ...
"""
import argparse, os, subprocess, tempfile

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(REPO, "brand", "fonts")
W, H = 1280, 720
YELLOW = (255, 222, 89)
STYLES = {"bold": ("Montserrat-900.ttf", 84, "white"),
          "italic": ("CormorantGaramond-500-Italic.ttf", 150, "white"),
          "key": ("Montserrat-900.ttf", 84, YELLOW)}
GRADE = "eq=contrast=1.08:saturation=0.92:gamma=0.98,colorbalance=rh=-0.02:bh=0.02"
PANEL = 720  # width of the Jake panel on the right


def frame(video, t):
    out = tempfile.mktemp(suffix=".png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1",
                    "-vf", f"{GRADE},scale=-2:720:flags=lanczos", out], check=True)
    img = Image.open(out).convert("RGB")
    os.remove(out)
    return img


def thumb(video, t, cx, out, lines, label=None, photo=None):
    src = frame(video, t)
    cx = cx * src.height / 720 if src.height != 720 else cx
    # Jake: a 640-wide slice around him, pushed in slightly to fill the right-hand panel
    x0 = int(min(max(0, cx - 320), src.width - 640))
    jake = src.crop((x0, 0, x0 + 640, 720)).resize((PANEL, 810), Image.LANCZOS).crop((0, 30, PANEL, 750))

    if photo:
        bg = Image.open(photo).convert("RGB")
        s = max(W / bg.width, H / bg.height)
        bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1), Image.LANCZOS)
        bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
        bg = ImageEnhance.Brightness(bg).enhance(0.32)
        # fade the photo to black before Jake's panel so it never shows through him
        m = Image.new("L", (W, H), 0)
        dm = ImageDraw.Draw(m)
        for x in range(W):
            dm.line([(x, 0), (x, H)], fill=int(255 * min(1, max(0, (700 - x) / 260))))
        bg = Image.composite(bg, Image.new("RGB", (W, H), (0, 0, 0)), m)
    else:
        bg = Image.new("RGB", (W, H), (0, 0, 0))
    canvas = bg.copy()
    canvas.paste(jake, (W - PANEL, 0))
    # fade Jake into the panel
    fade = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(fade)
    xs = W - PANEL
    for x in range(xs, xs + 300):
        d.line([(x, 0), (x, H)], fill=int(255 * ((x - xs) / 300) ** 1.4))
    d.rectangle([xs + 300, 0, W, H], fill=255)
    canvas = Image.composite(canvas, bg, fade)

    d = ImageDraw.Draw(canvas)
    x = 70
    parsed = []
    for spec in lines:
        style, text = spec.split(":", 1)
        fname, size, colour = STYLES[style]
        font = ImageFont.truetype(os.path.join(F, fname), size)
        while font.getlength(text) > 640 and size > 40:  # keep clear of Jake's face
            size -= 4
            font = ImageFont.truetype(os.path.join(F, fname), size)
        b = font.getbbox(text, anchor="ls")
        parsed.append((text, font, colour, -b[1], b[3], style))
    gap = 14
    total = sum(a + b for _, _, _, a, b, _ in parsed) + gap * (len(parsed) - 1)
    y = (H - total) / 2 - (40 if label else 0)
    for text, font, colour, asc, desc, style in parsed:
        y += asc
        d.text((x - (4 if style == "italic" else 0), y), text, font=font, fill=colour, anchor="ls")
        y += desc + gap
    if label:
        lf = ImageFont.truetype(os.path.join(F, "Montserrat-600.ttf"), 22)
        ly, lx = y + 60, x
        for ch in label:
            d.text((lx, ly), ch, font=lf, fill=(200, 200, 200), anchor="ls")
            lx += lf.getlength(ch) + 5
        d.line([(x, ly + 25), (x + 60, ly + 25)], fill=(150, 150, 150), width=2)

    logo = Image.open(os.path.join(REPO, "brand", "logos", "monogram-white.png")).convert("RGBA")
    logo = logo.resize((52, 52), Image.LANCZOS)
    logo.putalpha(logo.split()[3].point(lambda v: int(v * 0.85)))
    canvas.paste(logo, (x, H - 52 - 50), logo)
    canvas.save(out, quality=95)
    print(f"thumbnail -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    ap.add_argument("video"); ap.add_argument("t", type=float); ap.add_argument("cx", type=float)
    ap.add_argument("out"); ap.add_argument("lines", nargs="+")
    ap.add_argument("--label"); ap.add_argument("--photo")
    a = ap.parse_args()
    thumb(a.video, a.t, a.cx, a.out, a.lines, a.label, a.photo)
