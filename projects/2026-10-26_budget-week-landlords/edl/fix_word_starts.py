"""Whisper stretched some take-opening words back over the breath before them (e.g. "Bank" at
794.54 when the voice starts at 795.82), which hid deep breaths inside the word. Move those word
starts to the real onset (Silero VAD + level check, verified by re-transcribing from the new
take start). Writes transcript/phrases_large_fixed.json, which the EDLs use."""
import json
ONSETS = {  # word: (whisper start, real start)
    "On": (82.83, 83.47), "And": (282.91, 283.50), "if": (316.98, 317.50), "So": (412.9, 413.40),
    "It": (628.22, 628.74), "Then": (682.15, 682.68), "To": (712.45, 713.09),
    "bank": (794.54, 795.82), "first": (842.22, 842.30), "Some": (499.47, 499.92),
    "some": (739.19, 740.27),
}
d = json.load(open("transcript/phrases_large.json"))
n = 0
for s in d["segments"]:
    for w in s["words"]:
        fix = ONSETS.get(w["w"].strip(".,"))
        if fix and abs(w["s"] - fix[0]) < 0.005:
            w["s"] = fix[1]; n += 1
            # whisper's end can now sit before the new start ("On" 83.43): give the word a
            # minimum length and push the following words of the phrase along behind it
            ws = s["words"]; k = ws.index(w)
            w["e"] = max(w["e"], round(w["s"] + 0.15, 2))
            for prev, nxt in zip(ws[k:], ws[k + 1:]):
                if nxt["s"] >= prev["e"]:
                    break
                nxt["s"] = prev["e"]
                nxt["e"] = max(nxt["e"], round(nxt["s"] + 0.12, 2))
assert n == len(ONSETS), n
json.dump(d, open("transcript/phrases_large_fixed.json", "w"), ensure_ascii=False)
print(n, "word starts moved")
