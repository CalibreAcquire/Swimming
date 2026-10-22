#!/usr/bin/env python3
"""QA a rendered video: loudness, true peak, voice vs music, caption overlaps.

Usage: qa.py <video.mp4> [<video.mp4> ...]
The captions file is the .ass written next to each render. Retakes are checked
separately with find_retakes.py (slow).
"""
import os, re, subprocess, sys

import numpy as np


def loudness(path):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af", "ebur128=framelog=quiet:peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    i = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])
    tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)[-1])
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    n = 1600
    db = 20 * np.log10(np.sqrt((x[:len(x) // n * n].reshape(-1, n) ** 2).mean(1)) + 1e-9)
    return i, tp, np.percentile(db, 80) - np.percentile(db, 8)


def caption_overlaps(ass):
    def t(s):
        h, m, x = s.split(":")
        return int(h) * 3600 + int(m) * 60 + float(x)
    states = sorted({(t(a), t(b)) for a, b in re.findall(r"Dialogue: 1,([^,]+),([^,]+),Cap,", open(ass).read())})
    return [(a1, a2) for (a1, b1), (a2, _) in zip(states, states[1:]) if a2 < b1 - 0.011]


if __name__ == "__main__":
    for v in sys.argv[1:]:
        i, tp, gap = loudness(v)
        ok = abs(i + 14) <= 0.5 and tp <= -1.0
        line = f"{os.path.basename(v)}: {i:.1f} LUFS, {tp:.1f} dBTP, music {gap:.1f} dB under voice [{'ok' if ok else 'CHECK'}]"
        ass = os.path.splitext(v)[0] + ".ass"
        if os.path.exists(ass):
            ov = caption_overlaps(ass)
            line += f", caption overlaps: {len(ov)}" + (f" at {[round(a, 2) for a, _ in ov[:5]]}" if ov else "")
        print(line)
