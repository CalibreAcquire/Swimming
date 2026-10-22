#!/usr/bin/env python3
"""Find restarts and retakes that a whole-file transcript can hide.

Whisper tends to merge a false start into the take that follows it ("I'm Jake,
found—  I'm Jake, the founder of…" comes out as one sentence). This splits the
audio at its pauses, transcribes every phrase on its own, and flags phrases that
start the same way as one shortly after them.

Usage: find_retakes.py <video> [--json transcript.json]
Prints candidate retakes as source time ranges to consider for "cuts". With --json
it also writes the phrase-by-phrase transcript in the same format as
transcribe.py; it is usually the more accurate of the two, so use it for editing.
"""
import json, re, subprocess, sys

import numpy as np
from faster_whisper import WhisperModel

SR = 16000
# phrases whisper invents over silence or room noise
HALLUCINATIONS = {"thanksforwatching", "yeah", "thankyou", "you"}


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def silences(src):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", src, "-af", "silencedetect=noise=-38dB:d=0.25",
                        "-f", "null", "-"], capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return list(zip(st, en))


def main():
    src = sys.argv[1]
    out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
    total = len(audio) / SR

    sil = silences(src)
    edges = [0.0] + [x for a, b in sil for x in (a, b)] + [total]
    spans = [(edges[i], edges[i + 1]) for i in range(0, len(edges) - 1, 2) if edges[i + 1] - edges[i] > 0.25]

    model = WhisperModel("medium", device="cpu", compute_type="int8")
    phrases = []
    for a, b in spans:
        clip = audio[int(max(0, a - 0.1) * SR):int(min(total, b + 0.1) * SR)]
        segs, _ = model.transcribe(clip, word_timestamps=True, condition_on_previous_text=False, language="en")
        words = [dict(w=w.word.strip(), s=round(a - 0.1 + w.start, 2), e=round(a - 0.1 + w.end, 2))
                 for s in segs for w in s.words]
        if words and norm("".join(w["w"] for w in words)) not in HALLUCINATIONS:
            phrases.append(dict(s=a, e=b, words=words, text=" ".join(w["w"] for w in words)))
            print(f"{a:7.2f}-{b:7.2f}  {phrases[-1]['text']}", file=sys.stderr)

    print("\nCANDIDATE RETAKES (earlier attempt -> restart)")
    found = 0
    for i, p in enumerate(phrases):
        head = [norm(w["w"]) for w in p["words"][:3]]
        for q in phrases[i + 1:i + 4]:
            if q["s"] - p["s"] > 25:
                break
            qh = [norm(w["w"]) for w in q["words"][:3]]
            k = 2 if len(head) >= 2 and len(qh) >= 2 else 1
            if head[:k] == qh[:k] and head[:k] != [""] * k:
                found += 1
                print(f"  {p['s']:7.2f}-{q['s']:7.2f}  \"{p['text']}\"  ->  \"{q['text']}\"")
                break
    if not found:
        print("  none")
    if out_json:
        segs = [dict(start=p["s"], end=p["e"], text=p["text"], words=p["words"]) for p in phrases]
        json.dump(dict(language="en", segments=segs), open(out_json, "w"), indent=1)


if __name__ == "__main__":
    main()
