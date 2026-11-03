"""Builds edl/teaser.json: a music-led teaser from Jake's Dubai ghost visit (Binghatti tower and
show apartment, iPhone, portrait, no speech). Same look as the Brentwood teaser
(scripts/listing_edit.py): short clips, slow push-ins, plain white centred text, the outro.
Facts on screen come from the Binghatti one-page summary (22 Oct 2026). Dubai campaign CTA: comment DUBAI.
Run from the project folder: python3 edl/build_teaser.py
"""
import json, os, re, subprocess

R = "../raw/"
shots, audio, text = [], [], []
t = 0.0


def shot(file, src_in, dur, **kw):
    global t
    # the room/street sound, low under the music (the clips also carry spatial audio: map 0:a:0)
    r = subprocess.run(["ffmpeg", "-ss", str(src_in), "-t", str(dur), "-i", os.path.join("edl", R + file),
                        "-map", "0:a:0", "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True)
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])
    audio.append(dict(file=R + file, a=src_in, b=src_in + dur, at=round(t, 3), gain=round(-40 - lufs, 2)))
    shots.append(dict(file=R + file, **{"in": src_in}, dur=dur, move=kw.pop("move", "push"), **kw))
    t += dur


def line(a, b, s, **kw):
    text.append(dict(**{"from": round(a, 2), "to": round(b, 2)}, text=s, **kw))


# the walk up to the tower
shot("IMG_0084.MOV", 1.2, 2.0, focus=[0.5, 0.5])
a = t
shot("IMG_0084.MOV", 7.0, 2.8, focus=[0.5, 0.35])
line(0.25, t - 0.1, "Dubai\\NA private viewing")
# inside the show apartment
shot("IMG_0059.MOV", 0.2, 2.5)
a = t
shot("IMG_0066.MOV", 0.3, 1.8)
shot("IMG_0066.MOV", 3.0, 2.4, focus=[0.5, 0.4])
line(a + 0.2, t - 0.1, "Six projects\\NAl Jaddaf and JVC")
# Jake at the window: the call to action
a = t
shot("IMG_0069.MOV", 0.2, 3.4, focus=[0.45, 0.5])
line(a + 0.2, t, "Comment DUBAI\\Nfor prices and availability", y=0.37)  # above Jake's head

edl = dict(format="9x16", fps=30, shots=shots, audio=audio, text=text,
           music={"track": 744, "start": 30, "bed": -27}, music_led=True, outro=True)
json.dump(edl, open("edl/teaser.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(shots)} shots, {t:.1f}s + outro")
