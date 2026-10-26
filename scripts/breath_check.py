#!/usr/bin/env python3
"""Pauses and breaths kept in an edit, found with a voice-activity detector (Silero, bundled with
faster-whisper), which treats breaths as non-speech. Whisper often stretches the first word of a
take back over the breath before it ("Bank" from 794.54 when the voice starts at 795.82), so the
renderer's word-based pause trimming keeps the breath. Run before every render.

Usage: breath_check.py <edl.json> [--min 0.55] [--loud 0.15]

Prints, in output time:
  PAUSE   non-speech stretches of --min seconds or more (merged across cuts)
  BREATH  non-speech stretches with --loud seconds or more of loud sound (12 dB over the room)
  WORD    kept words whose span starts 0.3 s or more before the voice (fix the word start and
          start the take just before the voice; check by re-transcribing from the new start)
The VAD's onset is often 0.1-0.2 s late: a short BREATH right before a word is usually the word.
"""
import argparse, json, os, subprocess, sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calibre_edit as ce


def vad(src, work):
    cache = os.path.join(work, os.path.basename(src) + ".vad.json")
    if os.path.exists(cache):
        return json.load(open(cache))
    from faster_whisper.vad import get_speech_timestamps, VadOptions
    wav = os.path.join(work, os.path.basename(src) + ".16k.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", "16000", wav], check=True)
    x, sr = sf.read(wav, dtype="float32")
    ts = get_speech_timestamps(x, VadOptions(threshold=0.5, min_silence_duration_ms=150,
                                             speech_pad_ms=30, min_speech_duration_ms=100))
    sp = [(t["start"] / sr, t["end"] / sr) for t in ts]
    json.dump(sp, open(cache, "w"))
    os.remove(wav)
    return sp


def fmt(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:05.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edl")
    ap.add_argument("--min", type=float, default=0.55)
    ap.add_argument("--loud", type=float, default=0.15)
    a = ap.parse_args()
    e = ce.Edit(a.edl)
    work = os.path.join(e.dir, "..", "work")
    db, thr = e._levels("auto")
    sp = vad(e.src, work)
    st = np.array([s for s, _ in sp]); en = np.array([b for _, b in sp])

    def speech(t):
        k = np.searchsorted(st, t, side="right") - 1
        return k >= 0 and t < en[k]

    track = []
    for s in e.segments:
        for i in range(int(round(s["a"] * 100)), int(round(s["b"] * 100))):
            track.append((i / 100, speech(i / 100)))
    i = 0
    while i < len(track):
        if track[i][1]:
            i += 1
            continue
        j = i
        while j < len(track) and not track[j][1]:
            j += 1
        d = (j - i) / 100
        lv = np.array([db[min(int(round(t * 100)), len(db) - 1)] for t, _ in track[i:j]])
        loud = (lv > thr + 12).sum() / 100
        where = f"src {track[i][0]:.2f}-{track[j - 1][0] + 0.01:.2f}"
        if d >= a.min:
            print(f"PAUSE   {fmt(i / 100)}  {d:.2f}s ({loud:.2f}s loud)  {where}")
        elif loud >= a.loud:
            print(f"BREATH  {fmt(i / 100)}  {d:.2f}s ({loud:.2f}s loud)  {where}")
        i = j
    for w in e.kept_words:
        seg = next((s for s in e.segments if s["a"] <= w["s"] < s["b"]), None)
        if not seg:
            continue
        k = np.searchsorted(st, w["s"], side="left")
        if k < len(st) and st[k] < w["e"] and st[k] - max(w["s"], seg["a"]) >= 0.3 and not speech(w["s"]):
            print(f"WORD    {fmt(e.out_time(w['s']))}  '{w['w']}' starts {w['s']:.2f}, voice at "
                  f"{st[k]:.2f} (take starts {seg['a']:.2f})")


if __name__ == "__main__":
    main()
