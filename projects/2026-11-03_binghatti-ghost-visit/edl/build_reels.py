"""Builds the Binghatti Ghost reel set (edl/reel1.json ... reel4.json) from Jake's ghost visit
(iPhone, portrait, no speech). Same look as the Brentwood teaser (scripts/listing_edit.py):
short clips, slow push-ins, plain white centred text, music, the outro. Each reel opens on a
different shot and uses a different track so the set doesn't repeat.

Facts on screen, from Drive (Binghatti – Investor Data, 22 Oct 2026, and the Al Jaddaf market report):
Binghatti Ghost, Al Jaddaf; completed (developer handover 30 Apr 2026, ready resales registered in Oct);
entry unit AED 1,162,500 for 436 sq ft (about £236,000 at 4.9217). Binghatti signed off co-branding (Jake, 3 Nov).
Dubai campaign CTA: comment DUBAI.
Run from the project folder: python3 edl/build_reels.py
"""
import json, os, re, subprocess

R = "../raw/"


class Reel:
    def __init__(self):
        self.shots, self.audio, self.text, self.t = [], [], [], 0.0

    def shot(self, file, src_in, dur, **kw):
        # room/street sound low under the music (the clips also carry spatial audio: map 0:a:0)
        r = subprocess.run(["ffmpeg", "-ss", str(src_in), "-t", str(dur), "-i", os.path.join("edl", R + file),
                            "-map", "0:a:0", "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                           capture_output=True, text=True)
        lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])
        self.audio.append(dict(file=R + file, a=src_in, b=src_in + dur, at=round(self.t, 3), gain=round(-40 - lufs, 2)))
        self.shots.append(dict(file=R + file, **{"in": src_in}, dur=dur, move=kw.pop("move", "push"), **kw))
        self.t += dur
        return self

    def line(self, a, b, s, **kw):
        self.text.append(dict(**{"from": round(a, 2), "to": round(b, 2)}, text=s, **kw))

    def save(self, name, track, start):
        edl = dict(format="9x16", fps=30, shots=self.shots, audio=self.audio, text=self.text,
                   music={"track": track, "start": start, "bed": -27}, music_led=True, outro=True)
        json.dump(edl, open(f"edl/{name}.json", "w"), indent=1, ensure_ascii=False)
        print(f"{name}: {len(self.shots)} shots, {self.t:.1f}s + outro")


CTA = "Comment DUBAI\\Nfor prices and availability"

# 1. The teaser: arrive, step inside, the view, Jake at the window
r = Reel()
r.shot("IMG_0084.MOV", 1.2, 2.0, focus=[0.5, 0.5]).shot("IMG_0084.MOV", 7.0, 2.8, focus=[0.5, 0.35])
r.line(0.25, r.t - 0.1, "Binghatti Ghost\\NAl Jaddaf, Dubai")
a = r.t
r.shot("IMG_0059.MOV", 0.2, 2.5).shot("IMG_0066.MOV", 0.3, 1.8).shot("IMG_0066.MOV", 3.0, 2.4, focus=[0.5, 0.4])
r.line(a + 0.2, r.t - 0.1, "Completed\\NReady now")
a = r.t
r.shot("IMG_0069.MOV", 0.2, 3.4, focus=[0.45, 0.5])
r.line(a + 0.2, r.t, CTA, y=0.37)  # above Jake's head
r.save("reel1", 744, 30)

# 2. The view: opens on the window, ends on the tower
r = Reel()
r.shot("IMG_0066.MOV", 2.8, 2.6, focus=[0.5, 0.4])
r.line(0.2, r.t - 0.1, "The view from\\NBinghatti Ghost")
a = r.t
r.shot("IMG_0069.MOV", 0.3, 3.2, focus=[0.45, 0.5])
r.line(a + 0.2, r.t - 0.1, "Al Jaddaf, Dubai", y=0.37)
r.shot("IMG_0066.MOV", 0.2, 1.6).shot("IMG_0059.MOV", 0.4, 2.2)
a = r.t
r.shot("IMG_0084.MOV", 7.2, 2.8, focus=[0.5, 0.35], move="pull")
r.line(a + 0.15, r.t, CTA)
r.save("reel2", 609, 20)

# 3. Walkthrough: longer, unhurried shots, the visit in order
r = Reel()
r.shot("IMG_0084.MOV", 0.6, 3.0, focus=[0.5, 0.5])
r.line(0.25, 2.9, "Walk through\\NBinghatti Ghost")
r.shot("IMG_0084.MOV", 6.4, 3.4, focus=[0.5, 0.35])
r.shot("IMG_0059.MOV", 0.1, 2.9)
r.shot("IMG_0066.MOV", 0.2, 5.1, focus=[0.5, 0.45])
a = r.t
r.shot("IMG_0069.MOV", 0.1, 3.6, focus=[0.45, 0.5])
r.line(a + 0.2, r.t, CTA, y=0.37)
r.save("reel3", 770, 45)

# 4. The numbers: entry price (check it against Binghatti's live feed before posting)
r = Reel()
r.shot("IMG_0059.MOV", 0.2, 2.6)
r.line(0.2, r.t - 0.1, "Binghatti Ghost\\NAl Jaddaf, Dubai")
a = r.t
r.shot("IMG_0066.MOV", 0.3, 1.9).shot("IMG_0066.MOV", 3.1, 2.2, focus=[0.5, 0.4])
r.line(a + 0.2, r.t - 0.1, "Completed 2026\\NFrom 436 sq ft")
a = r.t
r.shot("IMG_0084.MOV", 7.0, 2.8, focus=[0.5, 0.35])
r.line(a + 0.15, r.t - 0.1, "From AED 1,162,500\\Nabout £236,000")
a = r.t
r.shot("IMG_0069.MOV", 0.2, 3.4, focus=[0.45, 0.5])
r.line(a + 0.2, r.t, CTA, y=0.37)
r.save("reel4", 175, 10)
