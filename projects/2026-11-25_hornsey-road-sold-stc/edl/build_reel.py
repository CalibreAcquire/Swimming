"""479 Hornsey Road: "Sold subject to contract" reel (format: brand/formats/under_offer_reel.md).
Music-only, cuts on the beat of House 02 (744, 123 bpm, beat 0.4876 s; music starts on the beat at
15.929 s). 4-beat opening with the status and address, 2-beat shots, 4-beat close on the wordmark.
Footage: Kim's 28 Aug shoot (portrait edits p_*, gimbal DJI_*, phone IMG_*, photos DSC*).
Interior photos with tenants' belongings (bedrooms, living rooms) and shots with people are left out. Run from the project folder."""
import json

BEAT, FPS = 0.48762, 30
DARK = "eq=brightness=-0.09:contrast=0.94:saturation=0.95,vignette=angle=PI/3.2"
shots = [  # (file, in, beats, move, focus, zoom, grade)
    ("p_2.mp4", 0.6, 4, "push", [0.5, 0.45], 1.0, DARK),
    ("IMG_1553.MOV", 0.4, 2, "push", [0.42, 0.5], 1.0, None),
    ("p_2-2.mp4", 2.0, 2, "none", [0.5, 0.28], 1.6, None),          # white upper floors, detail
    ("DSC09756.jpg", 0, 2, "push", [0.5, 0.5], 1.0, None),           # shop interior
    ("DJI_20260828_124208_202_video.MP4", 3.0, 2, "none", [0.44, 0.5], 1.0, None),
    ("p_3.mp4", 3.0, 2, "none", [0.5, 0.62], 1.5, None),             # fascia detail
    ("DSC09781.jpg", 0, 2, "push", [0.45, 0.5], 1.0, None),          # kitchen
    ("p_1-1.mp4", 6.0, 2, "none", [0.5, 0.5], 1.0, None),            # low angle, tree
    ("DSC09774.jpg", 0, 2, "push", [0.45, 0.5], 1.0, None),          # bathroom
    ("DJI_20260828_123833_797_video.MP4", 3.0, 2, "none", [0.46, 0.5], 1.0, None),
    ("p_2-1.mp4", 2.0, 2, "none", [0.5, 0.25], 1.45, None),          # top floors and sky
    ("p_1-2.mp4", 2.0, 2, "none", [0.5, 0.5], 1.0, None),
    ("DJI_20260828_124117_877_video.MP4", 2.0, 2, "none", [0.53, 0.5], 1.0, None),
    ("p_2-3.mp4", 1.0, 4, "pull", [0.5, 0.4], 1.0, DARK),            # close on the wordmark
]
out, t = [], 0
for f, a, beats, move, focus, zoom, grade in shots:
    t0 = round(t * BEAT * FPS) / FPS
    t += beats
    t1 = round(t * BEAT * FPS) / FPS
    sh = {"file": f"../raw/{f}", "in": a, "dur": round(t1 - t0, 4), "move": move, "focus": focus, "zoom": zoom}
    if grade:
        sh["grade"] = grade
    out.append(sh)
total = sum(s["dur"] for s in out)
close = total - out[-1]["dur"]
edl = {
    "format": "9x16", "fps": 30, "shots": out, "audio": [],
    "music": {"track": 744, "start": 15.929, "bed": -27}, "music_led": True,
    "text": [{"from": 0.12, "to": out[0]["dur"] - 0.05, "y": 0.36,
              "text": r"{\fnMontserrat SemiBold\fs46\fsp10}SOLD SUBJECT TO CONTRACT\N"
                      r"{\fnCormorant Garamond Medium\fs132\fsp0}479 Hornsey Road"}],
    "logos": [{"from": close + 0.1, "to": total, "file": "wordmark-white.png", "width": 640, "y": 0.30}],
    "outro": True,
}
json.dump(edl, open("edl/reel.json", "w"), indent=1)
print(f"{len(out)} shots, {total:.2f} s + outro")
