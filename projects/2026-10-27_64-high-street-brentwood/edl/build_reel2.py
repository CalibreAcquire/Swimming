"""Builds edl/reel2.json: a second, shorter listing reel for 64 High Street, Brentwood.
A music-led teaser (no Q&A): the golden-hour walk-up, then each restaurant inside and out, a few
plain centred lines, ending on the comment prompt. Same look as reel 1 (scripts/listing_edit.py).
Run from the project folder: python3 edl/build_reel2.py
"""
import json, os, re, subprocess

J = "../raw/jake/"
K = "../raw/kim/"
KIM = {1: "exterior_shop1_stable1.mp4", 4: "exterior_shop2_DJI_20261020_120305_618_video.MP4",
       6: "exterior_shop3_static1.mp4", 7: "exterior_shop3_static2.mp4", 10: "internal_shop1_IMG_3531.MOV",
       11: "internal_shop2_DJI_20261020_110152_513_video.MP4", 14: "internal_shop3_1.MP4",
       15: "internal_shop3_DJI_20261020_112220_135_video.MP4", 17: "internal_shop3_IMG_3549.MOV"}

shots, audio, text = [], [], []
t = 0.0


def shot(file, src_in, dur, ambience=False, **kw):
    global t
    if ambience:  # street sound under the music, low (the walk-ups also carry spatial audio: map 0:a:0)
        r = subprocess.run(["ffmpeg", "-ss", str(src_in), "-t", str(dur), "-i", os.path.join("edl", file),
                            "-map", "0:a:0", "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                           capture_output=True, text=True)
        lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])
        audio.append(dict(file=file, a=src_in, b=src_in + dur, at=round(t, 3), gain=round(-38 - lufs, 2)))
    shots.append(dict(file=file, **{"in": src_in}, dur=dur, move=kw.pop("move", "push"), **kw))
    t += dur


def line(a, b, s):
    text.append(dict(**{"from": round(a, 2), "to": round(b, 2)}, text=s))


# the walk-up at golden hour
line(0.3, 2.1, "64 High Street\\NBrentwood")
shot(J + "IMG_6655.MOV", 0.5, 2.2, ambience=True)
shot(J + "IMG_6648.MOV", 0.8, 1.4, ambience=True)
shot(K + KIM[6], 2.0, 1.5, focus=[0.5, 0.6])
# Las Tapas, 64 High Street
a = t
shot(K + KIM[14], 2.0, 1.5)
shot(K + KIM[15], 3.0, 1.4)
line(a + 0.2, t - 0.1, "A freehold restaurant investment")
# the Italian, first floor
a = t
shot(K + KIM[4], 1.5, 1.4)
shot(K + KIM[11], 2.0, 1.4)
line(a + 0.2, t - 0.1, "Three restaurants")
# the Indian, ground floor
a = t
shot(K + KIM[1], 2.0, 1.4)
shot(K + KIM[10], 1.0, 1.4)
line(a + 0.2, t - 0.1, "All let")
shot(K + KIM[17], 1.0, 1.4)
# back on the street
a = t
# (not IMG_6653: it passes another business's shopfront, which would sit under "for sale")
shot(J + "IMG_6655.MOV", 4.0, 2.6, ambience=True)
line(a + 0.3, t - 0.1, "Now available for sale")
a = t
shot(K + KIM[7], 5.0, 3.0, focus=[0.5, 0.6])
line(a + 0.2, t, "Comment BRENTWOOD\\Nfor the full pack")

edl = dict(format="9x16", fps=30, shots=shots, audio=audio, text=text,
           music={"track": 770, "start": 20, "bed": -27}, music_led=True, outro=True)
json.dump(edl, open("edl/reel2.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(shots)} shots, {t:.1f}s + outro")
