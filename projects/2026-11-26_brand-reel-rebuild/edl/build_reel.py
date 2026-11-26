"""Brand reel rebuild (Jake's boosted reel, 172K views): past deals, then the pitch.
Rebuilt from the original footage (no Instagram screen, no old text):
  Loughton (110 High Road, shop & uppers) and Whitechapel (339-343 Commercial Road, mixed-use freehold)
  and the Commercial Road street aerial: 'Pinned Instagram Post.mp4' 172-192 s (Mark Steele's drone,
  outlines already drawn); Bow (611-613 Roman Road, development): '611-613 Roman Road.mp4' 5-8 s;
  City skyline: '611-613 Roman Road.mp4' 9-11 s (the Fieldgate Street skyline is blown out).
"Stop using Rightmove" becomes "Stop scrolling the portals" (no portal names in public content).
Cuts on the beat of House 02 (744, 123 bpm) from 15.929 s. Warm look (STYLE_WARM.md): DM Sans,
dark grid cards, cream headline. Run from the project folder."""
import json

B, FPS = 0.48762, 30
WARM = "colortemperature=temperature=5200:mix=0.6,eq=contrast=1.03:saturation=1.04"
PIN, RR, FG = "../raw/Pinned Instagram Post.mp4", "../raw/611-613 Roman Road.mp4", "../raw/Fieldgate Road Drone video.mov"
FIT = {"bg": "../graphics/dark_grid.png", "width": 1000, "y": 0.53, "radius": 26}
CARD = "../graphics/dark_grid.png"
plan = [  # (file, in, beats, move, focus, extra)
    (PIN, 179.0, 5, "push", [0.5, 0.5], {"fit": FIT, "grade": WARM}),          # Loughton
    (PIN, 182.4, 6, "push", [0.5, 0.5], {"fit": FIT, "grade": WARM}),          # Whitechapel
    (RR, 5.0, 6, "push", [0.5, 0.55], {"grade": WARM}),                        # Bow
    (CARD, 0, 6, "none", [0.5, 0.5], {}),                                       # stop scrolling
    (RR, 9.2, 5, "push", [0.5, 0.45], {"grade": WARM}),                        # skyline
    (CARD, 0, 8, "none", [0.5, 0.5], {}),                                       # what we buy
    (PIN, 190.25, 4, "push", [0.5, 0.5], {"grade": WARM + ",eq=brightness=-0.06,vignette=angle=PI/3.5"}),  # street aerial
    (CARD, 0, 5, "none", [0.5, 0.5], {}),                                       # end
]
shots, starts, t = [], [], 0
for f, a, beats, move, focus, extra in plan:
    t0 = round(t * B * FPS) / FPS
    t += beats
    t1 = round(t * B * FPS) / FPS
    starts.append(t0)
    shots.append(dict({"file": f, "in": a, "dur": round(t1 - t0, 4), "move": move, "focus": focus}, **extra))
total = sum(s["dur"] for s in shots)
end = [s0 + s["dur"] for s0, s in zip(starts, shots)]

LBL = r"{\fnDM Sans SemiBold\fs46\fsp10}"
PLACE = r"{\fnDM Sans Medium\fs132\fsp0}"
HEAD = r"{\fnDM Sans Medium\fs120\fsp0\c&HD8E6EF&}"
SUB = r"{\fnDM Sans SemiBold\fs44\fsp10\c&H7A8A99&}"
ITEM = r"{\fnDM Sans Medium\fs88\fsp0}"
KEY = r"{\fnDM Sans SemiBold\fs120\fsp0\c&HD8E6EF&}"
text = [
    {"from": starts[0] + 0.1, "to": end[0] - 0.05, "y": 0.27, "text": LBL + r"SHOP & UPPERS\N" + PLACE + "Loughton"},
    {"from": starts[1] + 0.1, "to": end[1] - 0.05, "y": 0.27, "text": LBL + r"MIXED-USE FREEHOLD\N" + PLACE + "Whitechapel"},
    {"from": starts[2] + 0.1, "to": end[2] - 0.05, "y": 0.16, "text": LBL + r"DEVELOPMENT\N" + PLACE + "Bow"},
    {"from": starts[3] + 0.1, "to": end[3] - 0.05, "y": 0.44, "text": HEAD + r"Stop scrolling\Nthe portals"},
    {"from": starts[3] + 2 * B, "to": end[3] - 0.05, "y": 0.56, "text": SUB + "AS A PROPERTY INVESTOR"},
    {"from": starts[4] + 0.1, "to": end[4] - 0.05, "y": 0.20, "text": PLACE + r"Start investing\N" + r"{\fs96}with purpose"},
    {"from": starts[5] + 0.1, "to": end[5] - 0.05, "y": 0.34, "text": ITEM + "Mixed-use"},
    {"from": starts[5] + 2 * B, "to": end[5] - 0.05, "y": 0.42, "text": ITEM + "Unbroken residential"},
    {"from": starts[5] + 4 * B, "to": end[5] - 0.05, "y": 0.50, "text": ITEM + "Commercial"},
    {"from": starts[5] + 6 * B, "to": end[5] - 0.05, "y": 0.62, "text": SUB + r"ALWAYS\N" + KEY + "Freehold"},
    {"from": starts[6] + 0.1, "to": end[6] - 0.05, "y": 0.20, "text": LBL + r"SECURE\N" + PLACE + r"{\fs104}off-market property"},
    {"from": starts[7] + 0.5, "to": end[7] - 0.05, "y": 0.555, "text": r"{\fnDM Sans Medium\fs44\alpha&H30&}calibreacquire.co.uk/register"},
]
edl = {"format": "9x16", "fps": 30, "shots": shots, "audio": [], "text": text,
       "logos": [{"from": starts[7] + 0.15, "to": total, "file": "wordmark-white.png", "width": 600, "y": 0.47}],
       "music": {"track": 744, "start": 15.929, "bed": -27}, "music_led": True, "outro": True}
json.dump(edl, open("edl/reel.json", "w"), indent=1)
print(f"{len(shots)} shots, {total:.2f} s + outro")
