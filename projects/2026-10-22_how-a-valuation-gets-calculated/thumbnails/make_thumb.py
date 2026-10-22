"""YouTube thumbnail (1280x720): text on a black panel left, Jake on the right.

Frame: ffmpeg -ss 45.6 -i ../src/raw.mp4 -frames:v 1 \
         -vf "eq=contrast=1.08:saturation=0.92:gamma=0.98,colorbalance=rh=-0.02:bh=0.02" frame.png
Then run from this folder: python3 make_thumb.py
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = "/home/user/Swimming/brand/fonts/"
W, H = 1280, 720
YELLOW = (255, 222, 89)

def thumb(out, accent):
    bg = Image.new("RGB", (W, H), (0, 0, 0))
    # photo: Jake on the right, slight push-in
    src = Image.open("frame.png")
    crop = src.crop((250, 0, 250 + 640, 720)).resize((720, 810), Image.LANCZOS).crop((0, 30, 720, 750))
    bg.paste(crop, (W - 720, 0))
    # fade the photo into the black panel, plus a soft vignette at the top/bottom edges
    fade = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(fade)
    x0 = W - 720
    for x in range(x0, x0 + 300):
        d.line([(x, 0), (x, H)], fill=int(255 * ((x - x0) / 300) ** 1.4))
    d.rectangle([x0 + 300, 0, W, H], fill=255)
    black = Image.new("RGB", (W, H), (0, 0, 0))
    bg = Image.composite(bg, black, fade)
    # text
    d = ImageDraw.Draw(bg)
    mont_black = ImageFont.truetype(F + "Montserrat-900.ttf", 76)
    corm = ImageFont.truetype(F + "CormorantGaramond-500-Italic.ttf", 150)
    label = ImageFont.truetype(F + "Montserrat-600.ttf", 22)
    x = 70
    d.text((x, 168), "SAME BUILDING.", font=mont_black, fill="white", anchor="ls")
    d.text((x - 4, 320), "Different", font=corm, fill="white", anchor="ls")
    d.text((x, 420), "PRICE.", font=mont_black, fill=YELLOW if accent else "white", anchor="ls")
    # small spaced label + hairline, like the cards
    lab = "HOW A VALUATION ACTUALLY WORKS"
    cx = x
    for ch in lab:
        d.text((cx, 520), ch, font=label, fill=(200, 200, 200), anchor="ls")
        cx += label.getlength(ch) + 5
    d.line([(x, 545), (x + 60, 545)], fill=(150, 150, 150), width=2)
    # monogram, bottom-left (bottom-right is covered by YouTube's timestamp)
    logo = Image.open("/home/user/Swimming/brand/logos/monogram-white.png").convert("RGBA")
    logo = logo.resize((56, 56), Image.LANCZOS)
    a = logo.split()[3].point(lambda v: int(v * 0.85))
    logo.putalpha(a)
    bg.paste(logo, (x, 615), logo)
    bg.save(out, quality=95)

thumb("thumb-A-monochrome.jpg", accent=False)
thumb("thumb-B-yellow-accent.jpg", accent=True)
