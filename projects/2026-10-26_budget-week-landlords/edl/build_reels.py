"""Reel EDLs for the Budget video, cut from the same takes as the YouTube edit."""
import json
yt = json.load(open("edl/youtube.json"))
words = [w for s in json.load(open("transcript/phrases_large.json"))["segments"] for w in s["words"]]

def t_of(word, near, which="s"):
    w = min((w for w in words if w["w"].strip(".,").lower() == word.lower()), key=lambda w: abs(w["s"] - near))
    return w[which]

REELS = {
    "reel-1-already-law": dict(
        keep=[(83.45, 91.25), (91.55, 99.65), (183.80, 202.35)],
        title="The biggest landlord tax change / [WON'T BE IN] / [THE BUDGET]", music=10),
    "reel-2-the-real-rate": dict(
        keep=[(t_of("Take", 347.0) - 0.08, 366.45), (367.25, 390.70), (398.20, 404.70), (413.38, 419.92), (428.50, 441.65)],
        title="April 2027: £360 more tax. / [THE REAL RATE] / [IS 55%]", music=40),
    "reel-3-exchange-not-completion": dict(
        keep=[(853.40, 865.05), (877.80, 883.80), (884.15, 901.40)],
        title="Selling before the Budget? / [WHEN A SALE] / [COUNTS FOR TAX]", music=70),
    "reel-4-capital-gains": dict(
        keep=[(682.66, 692.70), (694.75, 702.30), (713.07, 728.90)],
        title="Capital gains tax at 40%? / [THE REAL] / [NUMBERS]", music=55),
    "reel-5-making-tax-digital": dict(
        keep=[(248.60, 270.30)],
        title="Making Tax Digital / [FROM APRIL 2027:] / [OVER £30,000]", music=15),
}
for name, r in REELS.items():
    keep = r["keep"]
    e = {
        "source": yt["source"], "transcript": yt["transcript"], "captions": yt["captions"],
        "format": "9x16", "max_gap": 0.3, "anchor": yt["anchor"],
        "zoom": {"wide": 1.0, "tight": 1.15, "every": 2.6}, "audio": {"preset": "full"},
        "cards": [], "broll": [],
        "window": [round(keep[0][0], 2), keep[-1][1]],
        "cuts": [[a[1], b[0]] for a, b in zip(keep, keep[1:]) if b[0] - a[1] > 0.02],
        "shots": [], "title_card": {"text": r["title"], "dur": 2.8},
        "music": {"track": 744, "start": r["music"], "bed": -27},
        "silence_db": "auto",  # no "grade": the default white balance (Jake, 26 Oct)
    }
    json.dump(e, open(f"edl/{name}.json", "w"), indent=2, ensure_ascii=False)
    open(f"edl/{name}.json", "a").write("\n")
    print(name, e["window"], len(e["cuts"]), "cuts")
