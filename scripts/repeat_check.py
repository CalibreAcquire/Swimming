#!/usr/bin/env python3
"""QA on a finished render: transcribe it in overlapping 20 s chunks and list any run of
four or more words said twice within 30 seconds (a retake left in).

Whole-file transcription of a render skips repeated lines (whisper treats the second one as
an echo), and the phrase-by-phrase retake finder sees no pauses under a music bed, so this
works on short chunks instead.

Usage: repeat_check.py <render.mp4> [--model medium]
"""
import argparse, re, subprocess

import numpy as np
from faster_whisper import WhisperModel

CHUNK, STEP = 20.0, 15.0


def audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def norm(w):
    return re.sub(r"[^a-z0-9%£]", "", w.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--model", default="medium")
    a = ap.parse_args()
    x = audio(a.video)
    dur = len(x) / 16000
    m = WhisperModel(a.model, device="cpu", compute_type="int8")
    words = {}  # rounded time -> word, chunks overlap so keep one per position
    t = 0.0
    while t < dur:
        seg = x[int(t * 16000):int(min(dur, t + CHUNK) * 16000)]
        segs, _ = m.transcribe(seg, word_timestamps=True, language="en",
                               condition_on_previous_text=False)
        for s in segs:
            for w in s.words:
                st = t + w.start
                if t > 0 and w.start < (CHUNK - STEP) / 2:
                    continue  # belongs to the previous chunk
                if st < t + CHUNK - (CHUNK - STEP) / 2 or t + CHUNK >= dur:
                    if norm(w.word):
                        words[round(st, 1)] = norm(w.word)
        t += STEP
    seq = sorted(words.items())
    hits = []
    for i in range(len(seq) - 3):
        gram = tuple(w for _, w in seq[i:i + 4])
        for j in range(i + 4, len(seq) - 3):
            if seq[j][0] - seq[i][0] > 30:
                break
            if tuple(w for _, w in seq[j:j + 4]) == gram:
                hits.append((seq[i][0], seq[j][0], " ".join(gram)))
    print(f"{a.video}: {len(seq)} words")
    last = -99
    for t1, t2, g in hits:
        if t1 - last > 2:
            print(f"  REPEAT {t1:7.1f}s and {t2:7.1f}s: {g}")
        last = t1
    if not hits:
        print("  no repeats")


if __name__ == "__main__":
    main()
