"""Reel cover options for the Dubai ghost-visit teaser, in the Brentwood premium layout.
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
P = "thumbnails/2026-11-03_binghatti-ghost-visit_reel-cover-"
# A: Jake at the window, text in the ceiling/window band above him
cover("work/cov/window.png", P + "A_v1.jpg", "top", 360,
      "CormorantGaramond-500-Italic.ttf", 132, ["A private viewing"], "Comment DUBAI", label="DUBAI  ·  UAE")
# B: the tower from the garden path, text low over the planting
cover("work/cov/tower.png", P + "B_v1.jpg", "bottom", 1180,
      "CormorantGaramond-500-Italic.ttf", 132, ["A private viewing"], "Comment DUBAI", label="DUBAI  ·  UAE")
# one cover per reel, each on a different picture (Jake, 3 Nov: covers mustn't repeat on the grid)
cover("work/cov/view.png", P + "C_v1.jpg", "centre", 840,
      "CormorantGaramond-500-Italic.ttf", 140, ["The view"], "Binghatti Ghost", label="AL JADDAF  ·  DUBAI")
cover("work/cov/tower.png", P + "D_v1.jpg", "bottom", 1180,
      "CormorantGaramond-500.ttf", 128, ["Binghatti Ghost"], "The walkthrough", label="AL JADDAF  ·  DUBAI")
cover("work/cov/hall.png", P + "E_v1.jpg", "centre", 840,
      "CormorantGaramond-500.ttf", 128, ["Binghatti Ghost"], "From AED 1,162,500", label="AL JADDAF  ·  DUBAI")
# the information reels (3 Nov, later): E is reel 3 (residences); F to H below
cover("work/cov/burj.png", P + "F_v1.jpg", "bottom", 1180,
      "CormorantGaramond-500.ttf", 128, ["Binghatti Spectre"], "Offices and retail", label="AL JADDAF  ·  DUBAI")
cover("work/cov/bed.png", P + "G_v1.jpg", "centre", 840,
      "CormorantGaramond-500-Italic.ttf", 132, ["The costs on top"], "Buying in Dubai", label="DUBAI  ·  UAE")
cover("work/cov/sunset.png", P + "H_v1.jpg", "top", 360,
      "CormorantGaramond-500.ttf", 132, ["Al Jaddaf"], "The last 12 months in numbers", label="DUBAI  ·  UAE")
# second pass (commercial emphasis): I retail, J offices
cover("work/cov/burj.png", P + "I_v1.jpg", "bottom", 1180,
      "CormorantGaramond-500.ttf", 128, ["Binghatti Spectre"], "19 shops below 712 apartments", label="AL JADDAF  ·  DUBAI")
cover("work/cov/night.png", P + "J_v1.jpg", "bottom", 1180,
      "CormorantGaramond-500-Italic.ttf", 140, ["The offices"], "Binghatti Spectre, from AED 1,864,999", label="AL JADDAF  ·  DUBAI")
# area-wide versions (Jake, 3 Nov: not Ghost specifically, the Binghatti developments in Al Jaddaf)
cover("work/cov/view.png", P + "C_v2.jpg", "centre", 840,
      "CormorantGaramond-500-Italic.ttf", 140, ["The view"], "Binghatti, Al Jaddaf", label="AL JADDAF  ·  DUBAI")
cover("work/cov/hall.png", P + "E_v2.jpg", "centre", 840,
      "CormorantGaramond-500-Italic.ttf", 136, ["The residences"], "From AED 799,999", label="AL JADDAF  ·  DUBAI")
print("covers written")
