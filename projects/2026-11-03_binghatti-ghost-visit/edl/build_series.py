"""Builds the information reels of the Dubai series (Jake, 3 Nov: start with teasers, then each
video gives more information). Reels 1 and 2 (teaser, the view) come from build_reels.py; these follow:

  3 residences   Binghatti Ghost homes: studios to 3 bedrooms, freehold, ready; studios from AED 1,162,500
  4 commercial   Binghatti Spectre offices and retail, Al Jaddaf (Binghatti's renders from the office brochure)
  5 costs        what a buyer pays on top in Dubai
  6 al-jaddaf    the area in numbers

Sources (Drive › Binghatti – Investor Data): live unit feed and one-page summary (22 Oct 2026),
the Al Jaddaf and JVC market report (26 Oct 2026, 12 months to late Oct), and the 2026 DLD extract
(Ghost sales: studio, 1, 2 and 3 bed flats, freehold; ready resales from October). £1 = AED 4.9217.
Run from the project folder: python3 edl/build_series.py
"""
import json, os, re, subprocess

R = "../raw/"
W = "../work/"
STILL = (".png", ".jpg")


class Reel:
    def __init__(self):
        self.shots, self.audio, self.text, self.t = [], [], [], 0.0

    def shot(self, file, src_in, dur, **kw):
        path = (W if file.endswith(STILL) else R) + file
        if not file.endswith(STILL):  # room/street sound low under the music (map 0:a:0: spatial audio)
            r = subprocess.run(["ffmpeg", "-ss", str(src_in), "-t", str(dur), "-i", os.path.join("edl", path),
                                "-map", "0:a:0", "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                               capture_output=True, text=True)
            lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])
            self.audio.append(dict(file=path, a=src_in, b=src_in + dur, at=round(self.t, 3), gain=round(-40 - lufs, 2)))
        self.shots.append(dict(file=path, **{"in": src_in}, dur=dur, move=kw.pop("move", "push"), **kw))
        self.t += dur
        return self

    def line(self, a, b, s, **kw):
        self.text.append(dict(**{"from": round(a, 2), "to": round(b, 2)}, text=s, **kw))

    def card(self, dur, s, **shot):
        """One shot with one line over it, timed to the shot."""
        a = self.t
        self.shot(**shot, dur=dur)
        self.line(a + 0.2, self.t - 0.1, s, **({"y": shot.pop("y")} if "y" in shot else {}))
        return self

    def save(self, name, track, start):
        edl = dict(format="9x16", fps=30, shots=self.shots, audio=self.audio, text=self.text,
                   music={"track": track, "start": start, "bed": -27}, music_led=True, outro=True)
        json.dump(edl, open(f"edl/{name}.json", "w"), indent=1, ensure_ascii=False)
        print(f"{name}: {len(self.shots)} shots, {self.t:.1f}s + outro")


CTA = "Comment DUBAI\\Nfor prices and availability"


def cta(r, s=CTA):
    a = r.t
    r.shot("IMG_0069.MOV", 0.2, 3.4, focus=[0.45, 0.5])
    r.line(a + 0.2, r.t, s, y=0.37)  # above Jake's head


# 3. The residences at Binghatti Ghost
r = Reel()
a = r.t
r.shot("IMG_0084.MOV", 7.0, 2.6, focus=[0.5, 0.35])
r.line(0.2, r.t - 0.1, "Binghatti Ghost\\NThe residences")
a = r.t
r.shot("IMG_0059.MOV", 0.2, 2.6)
r.line(a + 0.2, r.t - 0.1, "Studios to\\Nthree bedrooms")
a = r.t
r.shot("IMG_0066.MOV", 0.3, 2.0).shot("IMG_0066.MOV", 3.0, 2.2, focus=[0.5, 0.4])
r.line(a + 0.2, r.t - 0.1, "Freehold\\NCompleted and ready now")
a = r.t
r.shot("IMG_0084.MOV", 1.2, 2.4, focus=[0.5, 0.5])
r.line(a + 0.15, r.t - 0.1, "Studios from AED 1,162,500\\Nabout £236,000")
cta(r)
r.save("reel3b", 744, 50)

# 4. Commercial: offices and retail at Binghatti Spectre
r = Reel()
r.shot("spectre_render_night.png", 0, 2.8, focus=[0.62, 0.5])
r.line(0.2, r.t - 0.1, "Offices and retail\\NBinghatti Spectre, Al Jaddaf")
a = r.t
r.shot("spectre_render_sunset.png", 0, 2.8, focus=[0.82, 0.5])
r.line(a + 0.2, r.t - 0.1, "Offices from 705 to 4,018 sq ft\\NFrom AED 1,864,999, about £379,000")
a = r.t
r.shot("spectre_render_burj.png", 0, 2.8, focus=[0.66, 0.5], move="pull")  # brochure p4, right half
r.line(a + 0.2, r.t - 0.1, "Ground-floor retail\\NFrom AED 8,922,999")
a = r.t
r.shot("spectre_render_night.png", 0, 2.4, zoom=1.15, focus=[0.6, 0.45])
r.line(a + 0.2, r.t - 0.1, "Handover\\NDecember 2028")
cta(r)
r.save("reel4b", 770, 60)

# 5. The costs on top (built to be saved)
r = Reel()
r.card(2.6, "Buying in Dubai\\NThe costs on top", file="IMG_0059.MOV", src_in=0.2)
r.card(2.6, "4% Dubai Land\\NDepartment registration", file="IMG_0066.MOV", src_in=0.3)
r.card(2.6, "About AED 4,800 in\\Nregistration and admin fees", file="IMG_0066.MOV", src_in=2.9, focus=[0.5, 0.4])
r.card(2.6, "5% VAT on\\Ncommercial units", file="IMG_0084.MOV", src_in=7.0, focus=[0.5, 0.35])
cta(r, "Comment DUBAI\\Nfor the full cost breakdown")
r.save("reel5", 609, 70)

# 6. Al Jaddaf in numbers (12 months to late October 2026)
r = Reel()
r.card(2.6, "Al Jaddaf, Dubai\\NThe last 12 months", file="spectre_render_sunset.png", src_in=0, focus=[0.82, 0.5])
r.card(2.8, "Apartment sales\\Nmore than tripled", file="IMG_0084.MOV", src_in=1.2, focus=[0.5, 0.5])
r.card(2.6, "Price per sq ft\\Nup 22%", file="IMG_0084.MOV", src_in=7.0, focus=[0.5, 0.35])
r.card(2.8, "Studios let for about\\NAED 48,700 a year", file="IMG_0066.MOV", src_in=3.0, focus=[0.5, 0.4])
cta(r)
r.save("reel6", 175, 40)
