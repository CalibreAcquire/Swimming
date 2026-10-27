"""Builds edl/reel.json (9:16 listing video) for 64 High Street, Brentwood.

Picture: walk-ups, then the Q&A clips with Kim's footage of each restaurant cut in as Lee
names it (Spanish = Las Tapas, 64 High Street; Italian = first floor, 119 South Street;
Indian = ground floor, 119 South Street, the blue paint), then the deal and the register line.
Sound: the Q&A clips back to back, walk-up ambience low, music bed (voice.mix_music).
Captions: phrase by phrase from the clip transcripts, plain and centred.
"""
import json, os, re, subprocess, sys

sys.path.insert(0, "../../scripts")
import voice  # noqa: E402

J = "../raw/jake/"
K = "../raw/kim/"
words = json.load(open("transcript/jake_clips.json"))

KIM = {  # contact-sheet numbers (work/kim_clips.png)
    0: "exterior_shop1_DJI_20261020_120054_890_video.MP4", 1: "exterior_shop1_stable1.mp4",
    2: "exterior_shop1_stable2.mp4", 3: "exterior_shop2_DJI_20261020_120247_467_video.MP4",
    4: "exterior_shop2_DJI_20261020_120305_618_video.MP4", 5: "exterior_shop2_static1.mp4",
    6: "exterior_shop3_static1.mp4", 7: "exterior_shop3_static2.mp4",
    8: "internal_shop1_IMG_3524.MOV", 9: "internal_shop1_IMG_3529.MOV", 10: "internal_shop1_IMG_3531.MOV",
    11: "internal_shop2_DJI_20261020_110152_513_video.MP4", 12: "internal_shop2_DJI_20261020_110235_323_video.MP4",
    13: "internal_shop2_DJI_20261020_110254_689_video.MP4", 14: "internal_shop3_1.MP4",
    15: "internal_shop3_DJI_20261020_112220_135_video.MP4", 16: "internal_shop3_DJI_20261020_112259_153_video.MP4",
    17: "internal_shop3_IMG_3549.MOV", 18: "internal_shop3_IMG_3551.MOV", 19: "internal_shop3_IMG_3552.MOV",
}

# spoken words whisper got wrong, keyed by (clip, word start): checked against medium and a
# prompted pass ("three-hole" = freehold, "60,000 people" = £60,000 p.a.)
FIX = {("IMG_6636.MOV", 0.46): "freehold", ("IMG_6636.MOV", 0.64): None,
       ("IMG_6636.MOV", 4.76): "£60,000", ("IMG_6636.MOV", 5.1): None, ("IMG_6636.MOV", 5.46): "p.a."}

shots, audio, text = [], [], []
t = 0.0


def shot(file, src_in, dur, **kw):
    global t
    shots.append(dict(file=file, **{"in": round(src_in, 3)}, dur=round(dur, 3), **kw))
    t += dur


def title(a, b, s, **kw):
    text.append(dict(**{"from": round(a, 2), "to": round(b, 2)}, text=s, **kw))


def ambience(file, src_in, dur, at):
    # -map 0:a:0: the walk-ups also carry Apple spatial audio (apac), which ffmpeg can't decode
    r = subprocess.run(["ffmpeg", "-ss", str(src_in), "-t", str(dur), "-i", os.path.join("edl", file),
                        "-map", "0:a:0", "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True)
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])
    audio.append(dict(file=file, a=round(src_in, 3), b=round(src_in + dur, 3), at=round(at, 3),
                      gain=round(-36 - lufs, 2)))


def captions(clip, a, b, at):
    """Phrase captions for the words of `clip` between source a and b, placed at output `at`.
    A phrase runs to the next comma or full stop; long ones are split in two near the middle.
    Only a sentence's first word gets a capital."""
    ws = []
    for w in words[clip]["words"]:
        if w["s"] < a - 0.05 or w["e"] > b + 0.05:
            continue
        key = (clip, w["s"])
        txt = FIX[key] if key in FIX else w["w"]
        if txt is None:
            ws[-1]["e"] = w["e"]
            continue
        ws.append(dict(w=txt, s=w["s"], e=w["e"]))
    # phrase breaks set by hand ("|"); the text must have the same words as the clip
    parts = [p.split() for p in BREAKS[clip].split("|")]
    assert sum(map(len, parts)) == len(ws), (clip, [w["w"] for w in ws])
    out, k = [], 0
    for p in parts:
        out.append((" ".join(p), ws[k:k + len(p)]))
        k += len(p)
    for i, (txt, ph) in enumerate(out):
        nxt = out[i + 1][1] if i + 1 < len(out) else None
        start = at + ph[0]["s"] - a
        stop = at + (nxt[0]["s"] - a if nxt else ph[-1]["e"] - a + 0.35)
        title(start, min(stop, at + b - a), re.sub(r"(?<!p\.a)[.,]$", "", txt))


BREAKS = {
    "IMG_6633.MOV": "So tell me what this one's all about?",
    "IMG_6636.MOV": "We've got a freehold building | it comprises three restaurants | "
                    "bringing in just under £60,000 p.a.",
    "IMG_6638.MOV": "So what's the layout of the building?",
    "IMG_6639.MOV": "Well, what we've got then | is at the front, | the frontage on High Street | "
                    "is the Spanish restaurant. | The Italian occupies the first floor. | "
                    "And then the Indian restaurant | is all of the ground floor | "
                    "up to where the blue paint finishes.",
    "IMG_6645.MOV": "What's the condition of the building | and what does a buyer need to think about? | "
                    "Yeah, they're all well established restaurants, | they're all in good condition. | "
                    "Nothing really for the buyer to worry about, | "
                    "they're all fully repairing | and insuring leases. | No residential elements, | "
                    "very little management, | a good sound investment.",
}


def dialogue(clip, a, b, cuts):
    """Clip's sound from a to b. Picture: the clip itself, with cutaways
    cuts = [(from, to, kim_number, kim_in, kw)] in clip seconds."""
    at = t
    audio.append(dict(file=J + clip, a=a, b=b, at=round(at, 3)))
    captions(clip, a, b, at)
    pos = a
    for c0, c1, k, k_in, kw in cuts + [(b, b, None, 0, {})]:
        if c0 > pos:  # the speakers themselves
            shot(J + clip, pos, c0 - pos, move="push", zoom=1.0, focus=[0.5, 0.3])
        if k is not None:
            shot(K + KIM[k], k_in, c1 - c0, **kw)
        pos = c1


# ---- opening: the walk up, titles over it
title(0.4, 3.0, "64 High Street\\NBrentwood")
for f, s_in, d in [("IMG_6648.MOV", 0.6, 1.5), ("IMG_6653.MOV", 2.2, 1.4), ("IMG_6655.MOV", 0.8, 1.5)]:
    ambience(J + f, s_in, d, t)
    shot(J + f, s_in, d, move="push")
title(4.5, 6.3, "Freehold\\NThree restaurants, all let")
shot(K + KIM[6], 2.0, 1.9, move="push", focus=[0.5, 0.6])

# ---- Q1: what is it
dialogue("IMG_6633.MOV", 0.0, 2.25, [])
dialogue("IMG_6636.MOV", 0.0, 5.78, [
    (1.25, 2.1, 16, 1.0, dict(move="push")),
    (2.1, 2.95, 11, 2.0, dict(move="push")),
])
# ---- Q2: the layout
dialogue("IMG_6638.MOV", 0.0, 1.85, [])
dialogue("IMG_6639.MOV", 0.0, 14.62, [
    (1.7, 3.3, 7, 1.0, dict(move="push", focus=[0.5, 0.6])),      # the frontage on High Street
    (3.3, 5.5, 14, 2.0, dict(move="push")),                        # the Spanish restaurant
    (5.5, 7.0, 4, 1.5, dict(move="push")),                         # the Italian
    (7.0, 8.6, 12, 1.0, dict(move="push")),                        # first floor
    (9.9, 11.3, 1, 2.0, dict(move="push")),                        # the Indian restaurant
    (11.3, 12.6, 10, 1.0, dict(move="push")),                      # ground floor
    (12.6, 14.62, 2, 3.0, dict(move="push", focus=[0.5, 0.6])),   # where the blue paint finishes
])
# ---- Q3: condition (IMG_6641 was a false start)
dialogue("IMG_6645.MOV", 0.0, 17.05, [
    (4.6, 6.0, 17, 1.0, dict(move="push")),                        # good condition
    (6.0, 7.3, 9, 2.0, dict(move="push")),
    (9.4, 11.0, 3, 2.0, dict(move="push")),                        # full repairing and insuring
    (11.0, 12.7, 0, 2.0, dict(move="push")),                       # no residential
    (12.7, 14.3, 18, 1.0, dict(move="push")),                      # very little management
])
# ---- close: the deal, then where to register
a = t
ambience(J + "IMG_6655.MOV", 3.8, 2.4, t)
shot(J + "IMG_6655.MOV", 3.8, 2.4, move="push")
title(a + 0.2, a + 2.4, "Guide price £700,000\\N£57,400 a year  ·  8.20% gross yield")
a = t
shot(K + KIM[7], 5.0, 2.6, move="push", focus=[0.5, 0.6])
title(a + 0.1, a + 2.6, "Now available for sale\\Ncalibreacquire.co.uk/register")

edl = dict(format="9x16", fps=30, shots=shots, audio=audio, text=text,
           music={"track": 770, "start": 20, "bed": -27}, outro=True)
json.dump(edl, open("edl/reel.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(shots)} shots, {t:.1f}s + outro, {len(text)} text events")
