"""Reel cover options for 64 High Street, Brentwood (Jake: "more attractive, and sleek").
Premium layout: a small spaced label, a fine rule, an elegant headline, a quiet subline, over a
soft gradient. White only, no bold. Text sits inside the 3:4 area Instagram shows on the grid.
Run from the project folder: python3 edl/make_covers.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = "../../brand/fonts/"
W, H = 1080, 1920


def font(name, size):
    return ImageFont.truetype(F + name, size)


def tracked(draw, xy_centre, text, fnt, tracking, fill):
    """Draw text centred on xy_centre with letter spacing (px)."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy_centre[0] - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, xy_centre[1]), ch, font=fnt, fill=fill, anchor="ls")
        x += w + tracking


def shade(img, kind):
    a = np.asarray(img).astype(float)
    y = (np.arange(H) / H)[:, None, None]
    x = (np.arange(W) / W)[None, :, None]
    if kind == "bottom":   # darker towards the bottom, where the text sits
        g = 1 - 0.62 * np.clip((y - 0.42) / 0.38, 0, 1) ** 1.3
    elif kind == "top":    # darker at the top
        g = 1 - 0.55 * np.clip((0.55 - y) / 0.4, 0, 1) ** 1.3
    else:                  # centre band
        g = 1 - 0.5 * np.exp(-((y - 0.5) / 0.13) ** 2)
    vignette = 1 - 0.22 * (((x - 0.5) / 0.5) ** 2 + ((y - 0.5) / 0.5) ** 2) / 2
    return Image.fromarray((a * g * vignette).clip(0, 255).astype("uint8"))


def cover(src, out, kind, y_label, title_font, title_size, title_lines, sub, label="BRENTWOOD  ·  ESSEX"):
    img = shade(Image.open(src).convert("RGB"), kind)
    d = ImageDraw.Draw(img)
    white = (255, 255, 255)
    soft = (255, 255, 255, 215)
    # label
    tracked(d, (W / 2, y_label), label, font("Montserrat-500.ttf", 30), 9, white)
    # fine rule
    ry = y_label + 34
    d.line([(W / 2 - 46, ry), (W / 2 + 46, ry)], fill=(255, 255, 255), width=2)
    # headline
    tf = font(title_font, title_size)
    ty = ry + 30 + title_size * 0.85
    for line in title_lines:
        d.text((W / 2, ty), line, font=tf, fill=white, anchor="ms")
        ty += title_size * 1.02
    # subline
    tracked(d, (W / 2, ty + 26), sub, font("Montserrat-400.ttf", 34), 2, white)
    img.save(out, quality=95)


os.makedirs("thumbnails", exist_ok=True)
P = "thumbnails/2026-10-27_64-high-street-brentwood_reel-cover-"
# A: golden hour walk-up, text low on the pavement shadows
cover("work/cov/c00.png", P + "A_v1.jpg", "bottom", 1180,
      "CormorantGaramond-500.ttf", 132, ["64 High Street"], "Freehold restaurant investment")
# B: Las Tapas interior, warm and moody, text in the centre band
cover("work/cov/c06.png", P + "B_v1.jpg", "centre", 840,
      "CormorantGaramond-500-Italic.ttf", 140, ["64 High Street"], "Three restaurants  ·  all let")
# C: the 64 High Street frontage, text in the sky above the gable
cover("work/cov/c09.png", P + "C_v1.jpg", "top", 300,
      "CormorantGaramond-500.ttf", 126, ["64 High Street"], "Freehold restaurant investment")
print("covers A, B, C written")
