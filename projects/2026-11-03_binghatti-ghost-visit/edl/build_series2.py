"""Dubai series, second pass (Jake, 3 Nov: lots of residential footage is fine, but the emphasis and
information should be on the shops and offices as an investment; use all the clips in Drive; include how
many towers, flats and residents, with the shops directly below).

  2 the view (teaser, v2)   more of the visit: entrance, lobby, lifts, the apartment, the view
  3 retail                  Spectre: 2 towers, 712 apartments, 235 offices, ~1,500 residents, 19 shops below
  4 offices                 Spectre offices: sizes, 128 of 230 sold, from AED 1,864,999, handover Dec 2028
  5 residences              Binghatti in Al Jaddaf (10 developments with stock on 22 Oct): studio to 3 bed,
                             ready now or handover by 2028, from AED 799,999 (Starfall and Wraith entry units)
  6 al jaddaf               shop rents up 17-20%, AED 173 per sq ft; sales more than tripled; price per sq ft +22%
  7 costs                   what a buyer pays on top

Sources (Drive › Binghatti – Investor Data): Spectre Project Facts (towers and unit counts), the one-page
summary and live feed (22 Oct 2026), the Al Jaddaf and JVC market report (26 Oct 2026), the 2026 DLD extract.
Residents: an estimate from the unit mix (1.5 per studio, 2 per 1 bed, 3 per 2 bed, 4 per 3 bed = 1,472).
Run from the project folder: python3 edl/build_series2.py
"""
import json, os, re, subprocess

R, W = "../raw/", "../work/"
STILL = (".png", ".jpg", ".JPG")


class Reel:
    def __init__(self):
        self.shots, self.audio, self.text, self.t = [], [], [], 0.0

    def shot(self, file, src_in, dur, **kw):
        still = file.endswith(STILL)
        path = (W if file.startswith("spectre") or file.endswith(".jpg") else R) + file  # renders and converted photos live in work/
        if not still:  # room/street sound low under the music (map 0:a:0: spatial audio)
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

    def say(self, s, *shots, y=None):
        """Shots back to back with one line across them."""
        a = self.t
        for sh in shots:
            self.shot(*sh[:3], **(sh[3] if len(sh) > 3 else {}))
        self.line(a + 0.2, self.t - 0.1, s, **({"y": y} if y else {}))
        return self

    def save(self, name, track, start):
        edl = dict(format="9x16", fps=30, shots=self.shots, audio=self.audio, text=self.text,
                   music={"track": track, "start": start, "bed": -27}, music_led=True, outro=True)
        json.dump(edl, open(f"edl/{name}.json", "w"), indent=1, ensure_ascii=False)
        print(f"{name}: {len(self.shots)} shots, {self.t:.1f}s + outro")


CTA = "Comment DUBAI\\Nfor prices and availability"
F = {"focus": [0.5, 0.4]}
TOWER = {"focus": [0.5, 0.35]}
NIGHT, SUNSET, BURJ = "spectre_render_night.png", "spectre_render_sunset.png", "spectre_render_burj.png"


def end(r, s=CTA):
    """Jake walking out of the development: from behind through the lobby doors (0076), cut on the
    doorway to the head-on shot (0080) of him stepping out and walking to camera (Jake, 3 Nov)."""
    r.shot("IMG_0076.MOV", 5.4, 1.2, move="none")  # cut sooner, as he reaches the doors (Jake, 4 Nov)
    a = r.t
    r.shot("IMG_0080.MOV", 10.0, 5.8, focus=[0.5, 0.5])  # a second shorter at the end (Jake, 4 Nov)
    r.line(a + 1.0, r.t, s, y=0.3)


# Jake, 4 Nov: more footage in Drive with better views (4K: skyline, balcony, living room, kitchen,
# corridor, lift lobby, the district from the street; photos of the empty ground-floor shopfronts).
# IMG_6716 (lift lobby) is out: Jake turns and looks back at the camera (Jake, 4 Nov).
# 1. Teaser (v2, 4 Nov): re-cut with the new footage, smooth zoom and the walk-out ending to match the series
r = Reel()
r.say("Binghatti\\NAl Jaddaf, Dubai", ("IMG_6727.MOV", 0.5, 2.6, {"focus": [0.5, 0.5]}), ("IMG_6726.MOV", 0.5, 2.0))
r.shot("IMG_0074.MOV", 0.2, 1.8).shot("IMG_0073.MOV", 5.0, 1.8)
r.say("A private viewing", ("IMG_6717.MOV", 0.2, 2.4), ("IMG_6720.MOV", 0.2, 2.4), y=0.37)
end(r)
r.save("s1_teaser", 744, 30)

# 2. The view (teaser)
r = Reel()
r.say("The view\\NBinghatti, Al Jaddaf", ("IMG_6720.MOV", 0.2, 2.6), ("IMG_6719.MOV", 2.2, 2.8))
r.shot("IMG_6715.MOV", 0.2, 2.2).shot("IMG_0072.MOV", 4.8, 1.7)
r.say("10 Binghatti developments\\Nin Al Jaddaf", ("IMG_6717.MOV", 0.2, 2.6), ("IMG_6727.MOV", 3.0, 3.0, {"focus": [0.5, 0.5]}), y=0.37)
end(r)
r.save("s2_view", 609, 35)

# 3. Retail: shops below two towers
r = Reel()
r.say("Binghatti Spectre\\NAl Jaddaf, Dubai", (NIGHT, 0, 2.6, {"focus": [0.62, 0.5]}))
r.say("Two towers\\N712 apartments, 235 offices", (SUNSET, 0, 2.6, {"focus": [0.82, 0.5]}), ("IMG_6726.MOV", 0.5, 2.2))
r.say("Around 1,500 residents\\Nonce complete", ("IMG_6715.MOV", 0.2, 2.3), ("IMG_0072.MOV", 4.8, 1.7))
r.say("19 shops on the ground floor\\Ndirectly below", ("IMG_6731.jpg", 0, 2.2), ("IMG_6734.jpg", 0, 2.2))
r.say("7 shops left\\NFrom AED 8,922,999", (NIGHT, 0, 2.6, {"zoom": 1.12, "focus": [0.6, 0.5]}))
end(r)
r.save("s3_retail", 770, 20)

# 4. Offices
r = Reel()
r.say("The offices at\\NBinghatti Spectre", (NIGHT, 0, 2.6, {"zoom": 1.1, "focus": [0.6, 0.45]}))
r.say("705 to 4,018 sq ft", ("IMG_6715.MOV", 0.3, 2.2), ("IMG_0072.MOV", 4.6, 2.0))
r.say("128 sold\\Nsince the September launch", (SUNSET, 0, 2.6, {"focus": [0.82, 0.5]}), ("IMG_0073.MOV", 5.0, 1.7))
r.say("From AED 1,864,999\\Nabout £379,000", ("IMG_6726.MOV", 0.5, 2.2), ("IMG_0074.MOV", 0.2, 2.0))  # communal areas, not a flat
r.say("Handover\\NDecember 2028", (BURJ, 0, 2.6, {"focus": [0.66, 0.5]}))
end(r)
r.save("s4_offices", 744, 75)

# 5. Residences across the area: plenty of the apartment
r = Reel()
r.say("Binghatti in Al Jaddaf\\NThe residences", ("IMG_6713.MOV", 0.3, 2.2), ("IMG_6727.MOV", 3.0, 2.4, {"focus": [0.5, 0.5]}))
r.say("Studio to\\Nthree-bedroom apartments", ("IMG_6717.MOV", 0.2, 2.4), ("IMG_6718.MOV", 0.2, 2.2))
r.say("Freehold\\NReady now or handover by 2028", ("IMG_0060.MOV", 3.0, 2.0), ("IMG_0063.MOV", 0.2, 1.8), ("IMG_6719.MOV", 2.0, 2.4))
r.say("From AED 799,999\\Nabout £162,500", ("IMG_6720.MOV", 0.2, 2.6), ("IMG_0054.MOV", 0.4, 2.2))
end(r)
r.save("s5_residences", 175, 10)

# 6. Al Jaddaf in numbers (12 months to late October 2026), shops first
r = Reel()
r.say("Al Jaddaf, Dubai\\NThe last 12 months", ("IMG_6727.MOV", 0.5, 3.2, {"focus": [0.5, 0.5]}))
r.say("Shop rents\\Nup 17% to 20%", ("IMG_6733.jpg", 0, 2.6))
r.say("Shops let at about\\NAED 173 per sq ft a year", ("IMG_6736.jpg", 0, 2.6))
r.say("Apartment sales\\Nmore than tripled", ("IMG_6712.MOV", 0.3, 2.8))
r.say("Price per sq ft\\Nup 22%", ("IMG_6720.MOV", 0.2, 2.4))
end(r)
r.save("s6_al_jaddaf", 132, 30)

# 7. The costs on top (built to be saved)
r = Reel()
r.say("Buying in Dubai\\NThe costs on top", ("IMG_6717.MOV", 0.2, 2.4), ("IMG_0061.MOV", 0.2, 1.4))
r.say("4% Dubai Land\\NDepartment registration", ("IMG_6718.MOV", 0.2, 2.4))
r.say("About AED 4,800 in\\Nregistration and admin fees", ("IMG_0056.MOV", 0.3, 2.6))
r.say("5% VAT on\\Ncommercial units", ("IMG_6732.jpg", 0, 2.6))
end(r, "Comment DUBAI\\Nfor the full cost breakdown")
r.save("s7_costs", 609, 80)
