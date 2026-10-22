#!/usr/bin/env python3
"""Instagram Story announcing a YouTube video (1080x1920).

Black background, monogram, spaced "NEW ON YOUTUBE" label with a hairline, the
title in Cormorant Garamond italic, the video thumbnail, and a clear band for the
link sticker. Everything sits inside Instagram's Story safe area (the top ~250 px
and bottom ~340 px are covered by the app).

Usage: make_story.py <thumbnail.jpg> <out.png> "Title line 1" ["Title line 2" ...]
"""
import os, sys

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(REPO, "brand", "fonts")
W, H = 1080, 1920


def spaced(d, xy, text, font, fill, tracking):
    """Draw centred text with extra letter spacing."""
    width = sum(font.getlength(c) for c in text) + tracking * (len(text) - 1)
    x, y = xy[0] - width / 2, xy[1]
    for c in text:
        d.text((x, y), c, font=font, fill=fill, anchor="ls")
        x += font.getlength(c) + tracking


def story(thumb, out, title_lines):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)

    logo = Image.open(os.path.join(REPO, "brand", "logos", "monogram-white.png")).convert("RGBA")
    logo = logo.resize((64, 64), Image.LANCZOS)
    img.paste(logo, ((W - 64) // 2, 280), logo)

    label = ImageFont.truetype(os.path.join(F, "Montserrat-600.ttf"), 30)
    spaced(d, (W / 2, 410), "NEW ON YOUTUBE", label, (190, 190, 190), 9)
    d.line([(W / 2 - 40, 442), (W / 2 + 40, 442)], fill=(120, 120, 120), width=2)

    serif = ImageFont.truetype(os.path.join(F, "CormorantGaramond-500-Italic.ttf"), 104)
    y = 530
    for line in title_lines:
        d.text((W / 2, y), line, font=serif, fill="white", anchor="ms")
        y += 98

    t = Image.open(thumb).convert("RGB").resize((940, 529), Image.LANCZOS)
    top = y - 30  # y is one line below the last baseline
    img.paste(t, ((W - 940) // 2, top))
    d.rectangle([(W - 940) // 2 - 1, top - 1, (W + 940) // 2, top + 529], outline=(70, 70, 70), width=1)

    small = ImageFont.truetype(os.path.join(F, "Montserrat-500.ttf"), 34)
    d.text((W / 2, top + 529 + 70), "Tap the link below to watch", font=small, fill=(200, 200, 200), anchor="ms")
    # the band below this line is left empty for the link sticker
    band = (top + 529 + 100, top + 529 + 240)
    assert band[1] <= H - 340, "link sticker band would sit under the Instagram reply bar"
    img.save(out)
    print(f"story -> {out}  (link sticker band: y {band[0]}-{band[1]})")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    story(sys.argv[1], sys.argv[2], sys.argv[3:])
