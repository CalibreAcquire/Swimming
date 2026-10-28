#!/usr/bin/env python3
"""Adds Jake's outro to an already finished export, for videos rendered before outros existed
(27 Oct 2026). The video itself is kept as delivered (no re-render, so its grade and edit stay
the same); the outro for its format is appended and the result written as the next version.

Usage: add_outro.py <export.mp4> [...]   writes <name>_v(N+1).mp4 next to each file
       add_outro.py --check <export.mp4> [...]   only reports whether each one already ends on the outro
"""
import json, os, re, subprocess, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calibre_edit as ce  # noqa: E402

OUTRO_LEN = 4.6


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                       capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    num, den = map(int, v["r_frame_rate"].split("/"))
    return int(v["width"]), int(v["height"]), round(num / den, 3), float(d["format"]["duration"])


def frame(path, t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1",
                        "-vf", "scale=64:64,format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).astype(float)


def has_outro(path, fmt, fps):
    """True when the last seconds of `path` match the outro (mean grey-level difference)."""
    _, _, _, dur = probe(path)
    out = ce.outro_clip(fmt, fps)
    diffs = [np.abs(frame(path, dur - OUTRO_LEN + t) - frame(out, t)).mean() for t in (0.5, 1.0, 2.0, 3.0, 4.0)]
    return max(diffs) < 0.5  # a true match is ~0; dark end cards can sit near 1-2


def next_version(path):
    m = re.match(r"(.*_v)(\d+)\.mp4$", path)
    if not m:
        sys.exit(f"no _vN in {path}")
    return f"{m.group(1)}{int(m.group(2)) + 1}.mp4"


def add(path):
    W, H, fps, dur = probe(path)
    fmt = "16x9" if W > H else "9x16"
    fps_i = int(round(fps))
    if has_outro(path, fmt, fps_i):
        print(f"already ends on the outro: {path}")
        return None
    out = next_version(path)
    if os.path.exists(out):
        sys.exit(f"{out} exists; not overwriting")
    outro = ce.outro_clip(fmt, fps_i)
    fc = (f"[1:v]scale={W}:{H}:flags=lanczos,fps={fps_i},setsar=1,format=yuv420p[ov];"
          f"[0:v]setsar=1,format=yuv420p[mv];[0:a]aresample=48000,aformat=channel_layouts=stereo[ma];"
          f"[1:a]aresample=48000,aformat=channel_layouts=stereo[oa];"
          f"[mv][ma][ov][oa]concat=n=2:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-i", outro, "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                    "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(fps_i),
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
    print(f"{out}  {probe(out)[3]:.1f}s (was {dur:.1f}s)")
    return out


if __name__ == "__main__":
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    for f in files:
        if "--check" in sys.argv:
            W, H, fps, _ = probe(f)
            print(("OUTRO   " if has_outro(f, "16x9" if W > H else "9x16", int(round(fps))) else "none    ") + f)
        else:
            add(f)
