#!/usr/bin/env python3
"""Phrase-by-phrase transcription for take selection.

Splits the recording at pauses measured against the room's own noise floor (the fixed
-38 dB silence detector in find_retakes.py misses pauses in rooms with hum or mic hiss,
so whole takes run together), then transcribes each phrase on its own. Short phrases
keep false starts and repeats that whole-file transcription drops or merges.

Writes a transcript JSON in the format calibre_edit.py reads (segments with word
timings {w, s, e} in source seconds) and prints one line per phrase.

Usage: phrase_transcribe.py <video> <out.json> [--model large-v3] [--min-pause 0.35]
"""
import argparse, json, subprocess, sys

import numpy as np
from faster_whisper import WhisperModel

SR = 16000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def levels(x, hop=160, win=480):
    n = (len(x) - win) // hop
    db = np.empty(n, dtype=np.float32)
    for k in range(0, n, 20000):
        i = np.arange(k, min(n, k + 20000))
        idx = np.arange(win)[None, :] + hop * i[:, None]
        db[i] = 20 * np.log10(np.sqrt((x[idx] ** 2).mean(1)) + 1e-9)
    return db


def phrases(db, min_pause, thr):
    """Speech spans (seconds) separated by pauses of at least min_pause."""
    quiet = db < thr
    spans, start, run = [], None, 0
    for i, q in enumerate(quiet):
        if not q:
            if start is None:
                start = i
            run = 0
        elif start is not None:
            run += 1
            if run * 0.01 >= min_pause:
                spans.append([start * 0.01, (i - run + 1) * 0.01])
                start, run = None, 0
    if start is not None:
        spans.append([start * 0.01, len(db) * 0.01])
    spans = [s for s in spans if s[1] - s[0] >= 0.25]
    # merge very short bursts into the neighbour (a breath or click on its own is not a phrase)
    out = []
    for s in spans:
        if out and (s[1] - s[0] < 0.6 or out[-1][1] - out[-1][0] < 0.6) and s[0] - out[-1][1] < 0.8:
            out[-1][1] = s[1]
        else:
            out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--min-pause", type=float, default=0.35)
    a = ap.parse_args()
    x = load(a.video)
    db = levels(x)
    thr = float(np.clip(np.percentile(db, 10) + 12, -40, -28))
    spans = phrases(db, a.min_pause, thr)
    print(f"threshold {thr:.1f} dB, {len(spans)} phrases", file=sys.stderr)
    m = WhisperModel(a.model, device="cpu", compute_type="int8")
    segs = []
    for s, e in spans:
        a0, a1 = max(0, s - 0.15), min(len(x) / SR, e + 0.2)
        part = x[int(a0 * SR):int(a1 * SR)]
        res, _ = m.transcribe(part, language="en", word_timestamps=True,
                              condition_on_previous_text=False, vad_filter=False, beam_size=5)
        words = [dict(w=w.word.strip(), s=round(a0 + w.start, 2), e=round(a0 + w.end, 2))
                 for r in res for w in r.words if w.word.strip()]
        text = " ".join(w["w"] for w in words)
        segs.append(dict(start=round(a0, 2), end=round(a1, 2), text=text, words=words))
        print(f"{a0:8.2f}-{a1:8.2f}  {text}", flush=True)
    json.dump(dict(language="en", segments=segs), open(a.out, "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
