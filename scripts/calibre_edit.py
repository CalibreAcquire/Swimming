#!/usr/bin/env python3
"""Calibre Acquire edit renderer.

Turns an edit file (JSON), the source footage and a word-level transcript
(tools/transcribe.py) into a finished video in the house style (VIDEO_STYLE.md):
pauses and retakes removed, zooms, stacked word-by-word captions, black/white
text cards, logo watermark, a light grade and loudness-normalised audio.

Usage:
  calibre_edit.py plan   <edit.json>                 print cuts, shots, captions, cards
  calibre_edit.py render <edit.json> <out.mp4> [--draft]
  calibre_edit.py cards  <edit.json> <outdir>         preview every card as a PNG
  calibre_edit.py srt    <edit.json> <out.srt>        subtitle file for YouTube
  calibre_edit.py stills <edit.json> <video> <outdir> <t> [<t> ...]

Edit file keys (times are SOURCE seconds unless noted):
  source, transcript         paths, relative to the edit file
  format                     "16x9" (1920x1080) or "9x16" (1080x1920)
  window                     [start, end] of the source to use
  cuts                       [[a, b], ...] source ranges to drop (retakes, fluffs)
  max_gap                    longest pause kept between words, seconds
  anchor                     [x, y] subject's face in source pixels; zooms centre on it
  zoom                       {"wide": 1.0, "tight": 1.3, "every": 5.0}  auto shot rhythm
  shots                      [{"at": t, "zoom": z, "move": "pop"|"push"|"pull", "to": z1}]
                             a shot change at t (splits the segment there: a punch-in cut)
  captions                   caption markup, see parse_markup()
  cards                      [{"from": t, "to": t, "style": "black"|"white", "text": markup}]
  title_card                 {"text": markup, "dur": s}  hook title over the opening (reels)
  broll                      [{"from": t, "to": t, "file": path, "start": s, "focus": [fx, fy],
                               "zoom": z, "move": "push"|"pull"|"pan"|"none", "dir": 1|-1}]  property footage / photos over the
                             talking head while he speaks (video: "start" into the clip; image:
                             slow push-in to "zoom")
  broll_shade                0-1: dark fade over the bottom half of B-roll so captions read on
                             bright photos (0.45 suits white interiors; off by default)
  grade                      ffmpeg filter string for the colour grade
  audio                      {"preset": "basic"|"clean"|"studio"|"deep"|"full", "pitch": semitones}
                             voice processing, see voice.py
  music                      {"track": id from brand/music/library.json, "start": s, "bed": LUFS, "duck": ratio}
  outro                      true (default) appends Jake's outro for the format (brand/outros: YouTube
                             outro on 16x9, reel/Short outro on 9x16); false leaves it off
"""
import json, math, os, re, subprocess, sys, difflib, shutil, tempfile, wave
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import ImageFont
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(REPO, "brand", "fonts")
LOGOS = os.path.join(REPO, "brand", "logos")
YELLOW = "&H59DEFF&"  # #FFDE59 in ASS BGR order
FPS = 25
SR = 48000

FORMATS = {
    "16x9": dict(W=1920, H=1080, cap_base=968, cap_maxw=0.62,
                 italic=96, bold=66, key=150, card_plain=70, card_italic=160, card_key=78, card_label=34,
                 wm=72, wm_margin=48),
    "9x16": dict(W=1080, H=1920, cap_base=1460, cap_maxw=0.86,
                 italic=134, bold=92, key=220, card_plain=84, card_italic=176, card_key=96, card_label=40,
                 wm=64, wm_margin=56),
}

# style -> (ASS family, ttf file, bold, italic)
FONT_STYLES = {
    "italic":      ("Cormorant Garamond Medium", "CormorantGaramond-500-Italic.ttf", 0, 1),
    "bold":        ("Montserrat ExtraBold", "Montserrat-800.ttf", 0, 0),
    "key":         ("Montserrat Black", "Montserrat-900.ttf", 0, 0),
    "card_plain":  ("Montserrat Medium", "Montserrat-500.ttf", 0, 0),
    "card_italic": ("Cormorant Garamond Medium", "CormorantGaramond-500-Italic.ttf", 0, 1),
    "card_key_black": ("Montserrat ExtraBold", "Montserrat-800.ttf", 0, 0),
    "card_key_white": ("Cormorant Garamond Medium", "CormorantGaramond-500-Italic.ttf", 0, 1),
    "card_label":  ("Montserrat SemiBold", "Montserrat-600.ttf", 0, 0),
}

# white balance only, measured on the office wall (Jake chose look 1, 26 Oct 2026; looks/README.md).
# Footage from another location needs its own measurement: set "grade" in that EDL.
DEFAULT_GRADE = "colorchannelmixer=rr=0.973:bb=1.028"

OUTROS = os.path.join(REPO, "brand", "outros")
OUTRO_LUFS = -14.0  # the outros arrive at about -8.6 LUFS, peaking at 0 dBFS


def outro_clip(fmt, fps=FPS):
    """Jake's outro for this format, scaled to the output size at FPS with its audio at
    OUTRO_LUFS (a plain gain, so the sting keeps its shape). Cached in brand/outros/cache."""
    info = json.load(open(os.path.join(OUTROS, "outros.json")))[fmt]
    src = os.path.join(OUTROS, info["file"])
    if not os.path.exists(src):
        run(["curl", "-sSL", "-o", src,
             f"https://drive.usercontent.google.com/download?id={info['drive_id']}&export=download&confirm=t"])
    F = FORMATS[fmt]
    out = os.path.join(OUTROS, "cache", f"{fmt}_{F['W']}x{F['H']}_{fps}.mp4")
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(src):
        return out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    meas = subprocess.run(["ffmpeg", "-i", src, "-af", "ebur128", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", meas)[-1])
    run(["ffmpeg", "-v", "error", "-y", "-i", src,
         "-vf", f"scale={F['W']}:{F['H']}:flags=lanczos,fps={fps},setsar=1,format=yuv420p",
         "-af", f"volume={OUTRO_LUFS - lufs:.2f}dB,aresample={SR},aformat=channel_layouts=stereo",
         "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-c:a", "pcm_s16le", out])
    return out


# ---------------------------------------------------------------- utilities

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"command failed: {' '.join(cmd[:6])}...\n{r.stderr[-3000:]}")
    return r


def snap(t, up=False):
    f = t * FPS
    return (math.ceil(f - 1e-6) if up else math.floor(f + 1e-6)) / FPS


def norm(w):
    return re.sub(r"[^a-z0-9£$%]", "", w.lower())


class Font:
    """Measures text the way libass will draw it."""
    _cache = {}

    def __init__(self, style):
        self.family, fname, self.b, self.i = FONT_STYLES[style]
        path = os.path.join(FONTS, fname)
        t = TTFont(path)
        os2 = t["OS/2"]
        self.upm = t["head"].unitsPerEm
        self.win = os2.usWinAscent + os2.usWinDescent
        self.win_desc = os2.usWinDescent
        self.path = path

    @classmethod
    def get(cls, style):
        if style not in cls._cache:
            cls._cache[style] = Font(style)
        return cls._cache[style]

    def em(self, size):  # libass size is the win ascent+descent height
        return size * self.upm / self.win

    def pil(self, size):
        return ImageFont.truetype(self.path, max(1, round(self.em(size))))

    def width(self, text, size):
        return self.pil(size).getlength(text)

    def extents(self, text, size):
        """(top above baseline, bottom below baseline) of the actual glyphs."""
        x0, y0, x1, y1 = self.pil(size).getbbox(text, anchor="ls")
        return -y0, max(0, y1)

    def box_below_baseline(self, size):
        return size * self.win_desc / self.win


# ---------------------------------------------------------------- edit model

class Edit:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.dir = os.path.dirname(self.path)
        self.cfg = json.load(open(path))
        c = self.cfg
        self.src = self._p(c["source"])
        self.fmt = c.get("format", "16x9")
        self.F = FORMATS[self.fmt]
        self.max_gap = c.get("max_gap", 0.45)
        self.words = [w for s in json.load(open(self._p(c["transcript"])))["segments"] for w in s["words"]]
        self.silences = self._silences()
        self.segments = self._build_segments()
        self._assign_shots()

    def _p(self, p):
        return p if os.path.isabs(p) else os.path.join(self.dir, p)

    # -- silences from the audio, cached next to the source
    def _silences(self):
        work = os.path.join(self.dir, "..", "work")  # raw/ is read-only: keep caches in work/
        mode = self.cfg.get("silence_db")
        tag = "" if mode is None else f".{mode}"
        cache = (os.path.join(work, os.path.basename(self.src) + f"{tag}.silences.json")
                 if os.path.isdir(work) else self.src + f"{tag}.silences.json")
        if os.path.exists(cache):
            return json.load(open(cache))
        if mode is not None:
            sil = self._silences_rms(mode)
            json.dump(sil, open(cache, "w"))
            return sil
        r = subprocess.run(["ffmpeg", "-v", "info", "-i", self.src, "-af",
                            "silencedetect=noise=-38dB:d=0.2", "-f", "null", "-"],
                           capture_output=True, text=True)
        st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
        en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
        sil = [[a, b] for a, b in zip(st, en)]
        json.dump(sil, open(cache, "w"))
        return sil

    def _levels(self, mode):
        """Speech level every 10 ms (30 ms frames) and the pause threshold, cached in work/.
        "auto" puts the threshold 12 dB above the quietest 10% of the recording; a number
        sets it in dBFS."""
        work = os.path.join(self.dir, "..", "work")
        cache = os.path.join(work if os.path.isdir(work) else os.path.dirname(self.src),
                             os.path.basename(self.src) + ".levels.npy")
        if os.path.exists(cache):
            db = np.load(cache)
        else:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", self.src, "-ac", "1", "-ar", "16000",
                                  "-f", "s16le", "-"], capture_output=True).stdout
            x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
            hop, win = 160, 480
            n = (len(x) - win) // hop
            db = np.empty(n, dtype=np.float32)
            for k in range(0, n, 20000):  # in blocks: an 11-minute file is 66k frames
                i = np.arange(k, min(n, k + 20000))
                idx = np.arange(win)[None, :] + hop * i[:, None]
                db[i] = 20 * np.log10(np.sqrt((x[idx] ** 2).mean(1)) + 1e-9)
            np.save(cache, db)
        thr = float(mode) if mode != "auto" else float(np.clip(np.percentile(db, 10) + 12, -40, -28))
        return db, thr

    def _silences_rms(self, mode):
        """Pauses from the speech level rather than a fixed -38 dB: rooms with a noise floor
        above that (office hum, wireless mic hiss) otherwise show no pauses at all, and a
        word whisper stretches over a pause keeps the whole pause."""
        db, thr = self._levels(mode)
        quiet = db < thr
        sil, start, loud = [], None, 0
        for i, q in enumerate(quiet):
            if q:
                start, loud = (i if start is None else start), 0
            elif start is not None:
                loud += 1
                if loud > 6:  # more than 60 ms of sound ends the pause
                    end = i - loud + 1
                    if (end - start) * 0.01 >= 0.2:
                        sil.append([round(start * 0.01 + 0.015, 3), round(end * 0.01 + 0.015, 3)])
                    start, loud = None, 0
        print(f"silences: threshold {thr:.1f} dB, {len(sil)} pauses", file=sys.stderr)
        return sil

    def _pause(self, a, b):
        """A gap between two words long enough to cut. Whisper's word times drift on spoken
        numbers ("thirty-six thousand three hundred and eighty"), leaving gaps that are really
        speech, so with measured levels a gap is kept only if speech-level sound (10 dB over
        the pause threshold) fills a good part of it. Room noise and shuffling between takes
        still count as a pause."""
        if b - a <= self.max_gap:
            return False
        mode = self.cfg.get("silence_db")
        if mode is None:
            return True
        db, thr = self._levels(mode)
        seg = db[max(0, int(a * 100)):int(b * 100)]
        return len(seg) == 0 or (seg > thr + 10).mean() < 0.35

    def _speech(self, a, b):
        """True when [a, b] holds speech-level sound (only with measured levels)."""
        mode = self.cfg.get("silence_db")
        if mode is None or b <= a:
            return False
        db, thr = self._levels(mode)
        seg = db[max(0, int(a * 100)):int(b * 100)]
        return len(seg) > 0 and (seg > thr + 14).sum() >= 8  # 80 ms above speech level

    def _in_silence(self, t):
        for a, b in self.silences:
            if a < t < b:
                return a, b
        return None

    # -- which source ranges survive
    def _build_segments(self):
        c = self.cfg
        lo, hi = c.get("window", [0, 1e9])
        cuts = c.get("cuts", [])
        pad_in, pad_out = c.get("pad", [0.06, 0.10])

        def cut(w):
            m = (w["s"] + w["e"]) / 2
            return not (lo <= m <= hi) or any(a <= m <= b for a, b in cuts)

        # a window end or cut start inside a word drops that word (it's judged by its midpoint)
        # and clips its sound: warn so the point can be moved to the word's end
        for t in [hi] + [a for a, b in cuts]:
            for w in self.words:
                if w["s"] + 0.03 < t < w["e"] - 0.03:
                    print(f"WARNING: cut at {t} is inside '{w['w']}' ({w['s']:.2f}-{w['e']:.2f})",
                          file=sys.stderr)
        kept = [w for w in self.words if not cut(w)]
        groups, cur = [], []
        for w in kept:
            if cur and (self._pause(cur[-1]["e"], w["s"]) or self._cut_between(cur[-1], w, cuts)):
                groups.append(cur)
                cur = []
            cur.append(w)
        if cur:
            groups.append(cur)

        ranges = []
        for g in groups:
            s, e = g[0]["s"], g[-1]["e"]
            sil = self._in_silence(s)
            if sil:
                s = sil[1]
            else:  # whisper often starts a word late: begin where the silence before it ends
                prev = [b for a, b in self.silences if b <= s and s - b < 0.35]
                if prev:
                    s = max(prev)
            sil = self._in_silence(e)
            if sil:
                e = sil[0]
            else:
                # whisper often ends a word early (the "-ber" of "November"): with measured
                # levels, run on to the next pause if it starts within half a second
                reach = 0.5 if c.get("silence_db") is not None else 0.3
                nxt = [a for a, b in self.silences if a >= e and a - e < reach]
                if nxt:
                    e = min(nxt)
            # breaths: a short burst, a pause, then a word whose timing swallows both
            # (whisper stretches the word over the breath). Start after the pause;
            # likewise drop a breath after the last word.
            # With measured levels, only trim what is quieter than speech: a dip inside a
            # word ("twenty | twenty-seven") or a short word on its own ("Fourth.") is not a breath.
            for a, b in self.silences:
                if s < a < s + 0.7 and b - a >= 0.12 and g[0]["e"] > b and not self._speech(s, a):
                    s = b
            for a, b in reversed(self.silences):
                if e - 0.7 < b < e and b - a >= 0.12 and g[-1]["s"] < a and not self._speech(b, e):
                    e = a
            # split on long silences inside the group (whisper sometimes stretches words over pauses)
            pieces, start = [], s
            for a, b in self.silences:
                if start < a and b < e and b - a > self.max_gap:
                    pieces.append([start, a])
                    start = b
            pieces.append([start, e])
            for a, b in pieces:
                a, b = a - pad_in, b + pad_out
                for ca, cb in cuts:  # never let padding reach into a removed take
                    if a < cb <= g[0]["s"]:
                        a = max(a, cb)
                    if g[-1]["e"] <= ca < b:
                        b = min(b, ca)
                ranges.append([a, b])

        out = []
        for a, b in ranges:
            a, b = snap(max(a, lo)), snap(min(b, hi), up=True)
            if out and a <= out[-1][1]:
                out[-1][1] = max(out[-1][1], b)
            elif b - a >= 0.2:
                out.append([a, b])
        self.kept_words = kept
        if c.get("silence_db") is not None:  # sound left out between kept ranges, outside cuts
            for (_, b0), (a1, _) in zip(out, out[1:]):
                gap = [(b0, a1)]
                for ca, cb in cuts:
                    gap = [p for x, y in gap for p in ((x, min(y, ca)), (max(x, cb), y)) if p[1] > p[0]]
                for x, y in gap:
                    loud = (y - x) - sum(max(0, min(y, q) - max(x, p)) for p, q in self.silences)
                    if loud > 0.15:
                        print(f"WARNING: {loud:.2f}s of sound dropped between {x:.2f} and {y:.2f}"
                              " (speech, or a breath?)", file=sys.stderr)
            # sound kept with no words on it: whisper leaves out a repeated line, so this is
            # usually a retake the transcript doesn't show
            for a, b in out:
                spans = [(a, b)]
                for w in kept:
                    spans = [p for x, y in spans for p in ((x, min(y, w["s"])), (max(x, w["e"]), y))
                             if p[1] > p[0]]
                for x, y in spans:
                    loud = (y - x) - sum(max(0, min(y, q) - max(x, p)) for p, q in self.silences)
                    if loud > 0.5:
                        print(f"WARNING: {loud:.2f}s of sound kept with no transcript words between"
                              f" {x:.2f} and {y:.2f} (a retake whisper left out?)", file=sys.stderr)
        return [dict(a=a, b=b) for a, b in out]

    @staticmethod
    def _cut_between(w1, w2, cuts):
        # any cut reaching into the gap: a cut may start inside the last kept word's tail
        return any(a < w2["s"] and b > w1["e"] for a, b in cuts)

    # -- zoom rhythm
    def _assign_shots(self):
        zc = dict(wide=1.0, tight=1.3, every=5.0)
        zc.update(self.cfg.get("zoom", {}))
        shots = sorted(self.cfg.get("shots", []), key=lambda s: s["at"])
        # split segments at manual shot times and, for long takes, at the widest word gap
        for sh in shots:
            t = snap(sh["at"])
            for i, sg in enumerate(self.segments):
                if sg["a"] < t < sg["b"] - 0.2 and t - sg["a"] > 0.2:
                    self.segments[i:i + 1] = [dict(a=sg["a"], b=t), dict(a=t, b=sg["b"])]
                    break
        changed = True
        while changed:
            changed = False
            for i, sg in enumerate(self.segments):
                if sg["b"] - sg["a"] > zc["every"] * 1.6:
                    t = self._best_split(sg["a"] + 1.2, sg["b"] - 1.2, (sg["a"] + sg["b"]) / 2)
                    if t:
                        self.segments[i:i + 1] = [dict(a=sg["a"], b=t), dict(a=t, b=sg["b"])]
                        changed = True
                        break
        manual = {snap(s["at"]): s for s in shots}
        tight = False
        for sg in self.segments:
            sh = manual.get(sg["a"])
            if sh:
                sg.update(zoom=sh.get("zoom", zc["tight"]), move=sh.get("move"), to=sh.get("to"))
                tight = sg["zoom"] > 1.05
            else:
                tight = not tight
                sg.update(zoom=zc["tight"] if tight else zc["wide"], move=None, to=None)

    def _best_split(self, lo, hi, mid):
        best, score = None, -1
        for w1, w2 in zip(self.kept_words, self.kept_words[1:]):
            t = (w1["e"] + w2["s"]) / 2
            if lo < t < hi:
                gap = w2["s"] - w1["e"]
                sc = gap + (0.4 if re.search(r"[.,?!]$", w1["w"].strip()) else 0) - abs(t - mid) * 0.05
                if sc > score:
                    best, score = snap(t), sc
        return best

    # -- timeline mapping
    def out_time(self, t):
        o = 0.0
        for sg in self.segments:
            if t < sg["a"]:
                return o
            if t <= sg["b"]:
                return o + t - sg["a"]
            o += sg["b"] - sg["a"]
        return o

    @property
    def duration(self):
        return sum(sg["b"] - sg["a"] for sg in self.segments)

    def in_kept(self, t):
        return any(sg["a"] <= t <= sg["b"] for sg in self.segments)


# ---------------------------------------------------------------- captions

def parse_markup(text):
    """Caption / card markup -> tokens.

      plain words      captions: bold white sans; cards: Montserrat Medium
      *words*          italic serif (Cormorant Garamond)
      [WORDS]          key words: captions big yellow caps; cards bold (black) or yellow serif (white)
      ~words~          cards only: small spaced-out label, e.g. ~Step 1~
      |                force a new caption chunk
      /                force a new line (only on its own, so URLs keep their slashes)
    """
    toks, chunk_br, line_br, group = [], False, False, 0
    for m in re.finditer(r"\[[^\]]+\]|\*[^*]+\*|~[^~]+~|\||(?<!\S)/(?!\S)|[^\s\[\]*~|]+", text):
        s = m.group(0)
        if s == "|":
            chunk_br = True
            continue
        if s == "/":
            line_br = True
            continue
        style, words = {"[": "key", "*": "italic", "~": "label"}.get(s[0], "bold"), None
        words = s[1:-1].split() if style != "bold" else [s]
        group += 1
        for j, w in enumerate(words):
            toks.append(dict(text=w, style=style, group=group,
                             chunk_br=chunk_br and j == 0, line_br=line_br and j == 0))
        chunk_br = line_br = False
    return toks


def align(tokens, words):
    """Give each markup token a time from the transcript (difflib alignment)."""
    a = [norm(t["text"]) for t in tokens]
    b = [norm(w["w"]) for w in words]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                tokens[i1 + k]["s"], tokens[i1 + k]["e"] = words[j1 + k]["s"], words[j1 + k]["e"]
                tokens[i1 + k]["heard"] = words[j1 + k]["w"]
        elif op == "replace":
            s, e = words[j1]["s"], words[j2 - 1]["e"]
            n = i2 - i1
            for k in range(n):
                tokens[i1 + k]["s"] = s + (e - s) * k / n
                tokens[i1 + k]["e"] = s + (e - s) * (k + 1) / n
    # tokens the transcript didn't have: place them between their matched neighbours,
    # or drop them when they sit outside the footage used (e.g. a reel cut from a longer edit)
    for i, t in enumerate(tokens):
        if "s" not in t:
            prev = next((tokens[j]["e"] for j in range(i - 1, -1, -1) if "s" in tokens[j] and not tokens[j].get("guess")), None)
            nxt = next((tokens[j]["s"] for j in range(i + 1, len(tokens)) if "s" in tokens[j]), None)
            if prev is not None and nxt is not None and nxt - prev < 2.0:
                t["s"] = t["e"] = prev
                t["guess"] = True
    return [t for t in tokens if "s" in t]


def chunk(tokens):
    """Split tokens into caption chunks. Hand-placed '|' breaks are respected; long
    unbroken runs are split automatically (sentence ends, key words, size, time)."""
    manual = any(t["chunk_br"] for t in tokens)
    max_words = 5 if manual else 3
    chunks, cur = [], []
    for i, t in enumerate(tokens):
        if cur:
            prev = cur[-1]
            words_in = len(cur)
            brk = (t["chunk_br"]
                   or re.search(r"[.?!:;]$", prev["text"])
                   or (not manual and re.search(r",$", prev["text"]) and words_in >= 2)
                   or (prev["style"] == "key" and t["style"] != "key")
                   or (words_in >= max_words and t["group"] != prev["group"] and t["style"] != "key")
                   or t["s"] - prev["e"] > 0.6
                   or t["e"] - cur[0]["s"] > 2.4)
            if brk:
                chunks.append(cur)
                cur = []
        cur.append(t)
    if cur:
        chunks.append(cur)
    return chunks


def display(text, style, card=False):
    if not card:
        text = re.sub(r"[.,;:]+$", "", text)
    return text.upper() if style in ("key", "card_label") and not (card and style == "key") else text


TRACKING = {"card_label": 8}


class Line:
    """One line of text made of runs; each run is consecutive tokens in one style."""

    def __init__(self, card=False):
        self.runs, self.card = [], card

    def add(self, tok, style, size):
        if not self.runs or self.runs[-1]["style"] != style:
            self.runs.append(dict(style=style, font=Font.get(style), size=size, toks=[]))
        self.runs[-1]["toks"].append(tok)

    @property
    def toks(self):
        return [t for r in self.runs for t in r["toks"]]

    def run_text(self, r):
        return " ".join(display(t["text"], r["style"], self.card) for t in r["toks"])

    def width(self):
        w = 0
        for i, r in enumerate(self.runs):
            txt = self.run_text(r) + (" " if i < len(self.runs) - 1 else "")
            w += r["font"].width(txt, r["size"]) + TRACKING.get(r["style"], 0) * len(txt)
        return w

    def extents(self):
        ex = [r["font"].extents(self.run_text(r) or "x", r["size"]) for r in self.runs]
        return max(e[0] for e in ex), max(e[1] for e in ex)

    def box_below(self):
        return max(r["font"].box_below_baseline(r["size"]) for r in self.runs)

    @property
    def size(self):
        return max(r["size"] for r in self.runs)


def layout_lines(tokens, styles, sizes, maxw, card=False):
    """Captions: a new line whenever the style changes (the stacked tiers).
    Cards: lines break only at '/', styles mix within a line. Over-wide lines are
    shrunk (key words) or wrapped."""
    lines = []
    for t in tokens:
        st = styles(t["style"])
        new_line = (not lines or t["line_br"]
                    or (not card and lines[-1].runs[-1]["style"] != st))
        if new_line:
            lines.append(Line(card))
        lines[-1].add(t, st, sizes[st])
    out = []
    for ln in lines:
        w = ln.width()
        if w <= maxw:
            out.append(ln)
        elif len(ln.runs) == 1 and ln.runs[0]["style"] == "key" and w * 0.6 <= maxw:
            ln.runs[0]["size"] *= maxw / w
            out.append(ln)
        else:  # wrap greedily
            cur = Line(card)
            for r in ln.runs:
                for t in r["toks"]:
                    trial = Line(card)
                    for rr in cur.runs:
                        for tt in rr["toks"]:
                            trial.add(tt, rr["style"], rr["size"])
                    trial.add(t, r["style"], r["size"])
                    if cur.runs and trial.width() > maxw:
                        out.append(cur)
                        cur = Line(card)
                    cur.add(t, r["style"], r["size"])
            out.append(cur)
    return out


def stack(lines, bottom_baseline, gap_ratio=0.16):
    """Baselines for lines stacked upwards from the bottom one."""
    y = bottom_baseline
    for ln in reversed(lines):
        top, desc = ln.extents()
        ln.baseline, ln.top, ln.desc = y, y - top, desc
        y = ln.top - ln.size * gap_ratio
    # make room for descenders of the line above
    for i in range(len(lines) - 1):
        upper, lower = lines[i], lines[i + 1]
        clash = upper.baseline + upper.desc - (lower.top - lower.size * 0.05)
        if clash > 0:
            for ln in lines[:i + 1]:
                ln.baseline -= clash
                ln.top -= clash
    return lines


def ass_time(t):
    t = max(0, t)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ass_header(W, H):
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat ExtraBold,80,&H00FFFFFF,&H00FFFFFF,&H70000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,2,0,0,0,1
Style: Card,Montserrat Medium,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def line_event(ln, x, revealed, new, start, end, layer, style, base_tags, colours):
    """One ASS event drawing a line; tokens past `revealed` are invisible (they keep
    their space so the layout doesn't shift), token `new` animates in."""
    parts, k = [], 0
    for r in ln.runs:
        f = r["font"]
        head = (rf"\fn{f.family}\fs{r['size']:.0f}\b{f.b}\i{f.i}"
                rf"\fsp{TRACKING.get(r['style'], 0)}{colours.get(r['style'], '')}")
        words = []
        for t in r["toks"]:
            word = display(t["text"], r["style"], ln.card)
            if k >= revealed:
                tags = r"\alpha&HFF&"
            elif k == new and r["style"] == "key":
                tags = r"\fscx88\fscy88\t(0,110,\fscx100\fscy100)"
            elif k == new:
                tags = r"\alpha&HFF&\t(0,70,\alpha&H00&)"
            else:
                tags = ""
            words.append(("{" + tags + "}" if tags else "") + word)
            k += 1
        parts.append("{" + head + "}" + " ".join(words))
    y = ln.baseline + ln.box_below()
    lead = rf"{{\an2\pos({x:.0f},{y:.0f}){base_tags}}}"
    return f"Dialogue: {layer},{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{lead}{' '.join(parts)}\n"


CAPTION_STYLES = {"bold": "bold", "italic": "italic", "key": "key", "label": "bold"}


def caption_events(edit, card_spans):
    F = edit.F
    W = F["W"]
    toks = align(parse_markup(edit.cfg.get("captions", "")), edit.kept_words)
    if not toks:
        return ""
    sizes = dict(italic=F["italic"], bold=F["bold"], key=F["key"])
    colours = dict(key=rf"\1c{YELLOW}")
    shadow = r"\bord3\3c&H000000&\3a&H90&\blur4"
    ev, timed = [], []
    for ch in chunk(toks):
        if any(edit.in_kept(t["s"]) or edit.in_kept(t["e"]) for t in ch):
            timed.append(ch)
    for n, ch in enumerate(timed):
        lines = stack(layout_lines(ch, CAPTION_STYLES.get, sizes, W * F["cap_maxw"]), F["cap_base"])
        order = [t for ln in lines for t in ln.toks]
        reveal_at = [edit.out_time(t["s"]) for t in order]
        start = reveal_at[0]
        nxt = edit.out_time(timed[n + 1][0]["s"]) if n + 1 < len(timed) else edit.out_time(ch[-1]["e"]) + 0.6
        # hold briefly after the last word, but never past the start of the next caption
        end = min(max(edit.out_time(ch[-1]["e"]) + 0.7, start + 0.35), nxt)
        for k in range(len(order)):
            s = max(start, reveal_at[k])
            e = reveal_at[k + 1] if k + 1 < len(order) else end
            e = max(min(e, end), s)
            for a, b in card_spans:  # no captions over cards
                if s < b and e > a:
                    if s >= a:
                        s = b
                    else:
                        e = a
            if e - s < 0.04:
                continue
            seen = 0
            for ln in lines:
                cnt = len(ln.toks)
                revealed = max(0, min(cnt, k + 1 - seen))
                new = k - seen if 0 <= k - seen < cnt else -1
                if revealed:
                    ev.append(line_event(ln, W / 2, revealed, new, s, e, 1, "Cap", shadow, colours))
                seen += cnt
    return "".join(ev)


def card_events(edit):
    F = edit.F
    W, H = F["W"], F["H"]
    ev, spans = [], []
    for c in edit.cfg.get("cards", []):
        a, b = edit.out_time(c["from"]), edit.out_time(c["to"])
        if b - a < 0.3:
            continue
        black = c.get("style", "black") == "black"
        spans.append((a, b, "black" if black else "white"))
        bg, fg = ("&H000000&", "&HFFFFFF&") if black else ("&HFFFFFF&", "&H000000&")
        ev.append(f"Dialogue: 5,{ass_time(a)},{ass_time(b)},Card,,0,0,0,,"
                  rf"{{\an7\pos(0,0)\p1\bord0\shad0\1c{bg}}}m 0 0 l {W} 0 {W} {H} 0 {H}{{\p0}}" "\n")
        key = "card_key_black" if black else "card_key_white"
        styles = {"bold": "card_plain", "italic": "card_italic", "key": key, "label": "card_label"}.get
        sizes = dict(card_plain=F["card_plain"], card_italic=F["card_italic"], card_label=F["card_label"],
                     card_key_black=F["card_key"], card_key_white=F["card_italic"] * 1.1)
        lines = stack(layout_lines(parse_markup(c["text"]), styles, sizes, W * 0.8, card=True), 0,
                      gap_ratio=0.24 if len(parse_markup(c["text"])) < 12 else 0.5)  # lists need air
        labelled = len(lines) > 1 and all(r["style"] == "card_label" for r in lines[0].runs)
        if labelled:  # breathing room for the hairline under the label
            lines[0].baseline -= F["card_label"] * 0.9
            lines[0].top -= F["card_label"] * 0.9
        top, bottom = lines[0].top, lines[-1].baseline + lines[-1].desc
        shift = H / 2 - (top + bottom) / 2 - H * 0.02
        for ln in lines:
            ln.baseline += shift
            ln.top += shift
        colours = {"card_key_white": rf"\1c{fg}",
                   "card_plain": rf"\1c{fg}", "card_italic": rf"\1c{fg}",
                   "card_key_black": rf"\1c{fg}", "card_label": rf"\1c{fg}\1a&H50&"}
        # a fine hairline between a label and the headline under it
        if labelled:
            y = (lines[0].baseline + lines[0].desc + lines[1].top) / 2
            rw = F["card_label"] * 1.6
            ev.append(f"Dialogue: 6,{ass_time(a)},{ass_time(b)},Card,,0,0,0,,"
                      rf"{{\an7\pos({W / 2 - rw / 2:.0f},{y:.0f})\p1\bord0\shad0\1c{fg}\1a&H70&}}"
                      f"m 0 0 l {rw:.0f} 0 {rw:.0f} 2 0 2{{\\p0}}\n")
        build = c.get("build", True)
        step = min(0.45, (b - a) * 0.5 / max(1, len(lines))) if build else 0
        for i, ln in enumerate(lines):
            tags = r"\bord0\shad0" + (r"\fad(140,0)" if i and build else "")
            ev.append(line_event(ln, W / 2, len(ln.toks), -1, a + i * step, b, 6, "Card", tags, colours))
    return "".join(ev), spans


def title_events(edit):
    """Hook title over the opening seconds: {"text": markup, "dur": seconds}.
    Write key words in capitals; titles keep the author's case."""
    ti = edit.cfg.get("title_card")
    if not ti:
        return ""
    F = edit.F
    W, H = F["W"], F["H"]
    styles = {"bold": "bold", "italic": "italic", "key": "key", "label": "card_label"}.get
    sizes = dict(bold=F["bold"], italic=F["italic"] * 1.05, key=F["key"] * 0.7, card_label=F["card_label"])
    # sits where the captions go; captions start once it's gone
    lines = stack(layout_lines(parse_markup(ti["text"]), styles, sizes, W * F["cap_maxw"], card=True),
                  F["cap_base"], gap_ratio=0.18)
    colours = dict(key=rf"\1c{YELLOW}")
    dur = ti.get("dur", 3.0)
    tags = r"\bord3\3c&H000000&\3a&H90&\blur4\fad(120,200)"
    return "".join(line_event(ln, W / 2, len(ln.toks), -1, 0, dur, 4, "Cap", tags, colours) for ln in lines)


# ---------------------------------------------------------------- render

def base_window(edit):
    sw, sh = probe_size(edit.src)
    if edit.fmt == "16x9":
        return 0, 0, sw, sh
    bw = sh * 9 / 16
    ax = edit.cfg.get("anchor", [sw / 2, sh / 3])[0]
    x0 = min(max(0, ax - bw / 2), sw - bw)
    return x0, 0, bw, sh


def probe_size(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height", "-of", "csv=p=0", path])
    w, h = r.stdout.strip().split(",")
    return int(w), int(h)


def segment_filter(edit, sg, draft):
    F = edit.F
    OW, OH = F["W"], F["H"]
    x0, y0, bw, bh = base_window(edit)
    sw, sh = probe_size(edit.src)
    anc = edit.cfg.get("anchor", [sw / 2, sh / 3])
    ax, ay = (anc[0] - x0) / bw, (anc[1] - y0) / bh
    grade = edit.cfg.get("grade", DEFAULT_GRADE)
    z0 = sg["zoom"]
    move = sg.get("move")
    sharpen = "unsharp=5:5:0.45:5:5:0" if not draft else "null"
    if not move:
        cw, chh = bw / z0, bh / z0
        cx, cy = x0 + ax * bw * (1 - 1 / z0), y0 + ay * bh * (1 - 1 / z0)
        return (f"{grade},crop={cw:.2f}:{chh:.2f}:{cx:.2f}:{cy:.2f},"
                f"scale={OW}:{OH}:flags=lanczos,{sharpen},setsar=1")
    z1 = sg.get("to") or (z0 + (0.06 if move == "push" else 0.25 if move == "pop" else -0.25))
    n = round((sg["b"] - sg["a"]) * FPS)
    span = n - 1 if move == "push" else max(1, round(0.4 * FPS))
    p = f"min(1,on/{span})"
    ease = f"({p})*({p})*(3-2*({p}))"
    z = f"{z0}+({z1}-{z0})*{ease}"
    pw, ph = OW * 2, OH * 2  # oversample so zoompan's integer offsets don't judder
    return (f"{grade},crop={bw:.2f}:{bh:.2f}:{x0:.2f}:{y0:.2f},scale={pw}:{ph}:flags=lanczos,"
            f"zoompan=z='{z}':x='{ax}*iw*(1-1/zoom)':y='{ay}*ih*(1-1/zoom)':d=1:s={OW}x{OH}:fps={FPS},"
            f"{sharpen},setsar=1")


def render_segment(edit, i, sg, tmp, draft):
    out = os.path.join(tmp, f"seg{i:04d}.mp4")
    n = round((sg["b"] - sg["a"]) * FPS)
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sg['a']:.3f}", "-i", edit.src, "-an",
         "-vf", segment_filter(edit, sg, draft), "-r", str(FPS), "-frames:v", str(n),
         "-c:v", "libx264", "-preset", "ultrafast" if draft else "veryfast", "-crf", "12",
         "-pix_fmt", "yuv420p", out])
    return out


def render_audio(edit, tmp):
    raw = os.path.join(tmp, "src.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", edit.src, "-vn", "-ac", "2", "-ar", str(SR), raw])
    with wave.open(raw) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32)
    fade = int(0.012 * SR)
    ramp = np.linspace(0, 1, fade, dtype=np.float32)[:, None]
    parts = []
    for sg in edit.segments:
        p = a[round(sg["a"] * SR):round(sg["b"] * SR)].copy()
        want = round((sg["b"] - sg["a"]) * SR)
        if len(p) < want:
            p = np.vstack([p, np.zeros((want - len(p), 2), np.float32)])
        p[:fade] *= ramp
        p[-fade:] *= ramp[::-1]
        parts.append(p)
    cut = os.path.join(tmp, "cut.wav")
    with wave.open(cut, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.clip(np.vstack(parts), -32768, 32767).astype(np.int16).tobytes())
    out = os.path.join(tmp, "audio.wav")
    a = edit.cfg.get("audio", {})
    voice.process(cut, out, a.get("preset", "clean"), a.get("pitch", 0))
    if edit.cfg.get("music"):
        mixed = os.path.join(tmp, "mix.wav")
        voice.mix_music(out, mixed, edit.cfg["music"])
        out = mixed
    return out


IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")


def broll_spans(edit):
    """B-roll inserts mapped to the output timeline: (out_start, duration, spec)."""
    spans = []
    for b in edit.cfg.get("broll", []):
        a, e = edit.out_time(b["from"]), edit.out_time(b["to"])
        if e - a >= 0.4:
            spans.append((snap(a), snap(e - a, up=True), b))
    return spans


def render_broll(edit, i, a, dur, b, tmp, draft):
    """One B-roll insert rendered at the output size and frame rate.
    Video: cropped to fill the frame ("focus": [fx, fy] picks the area, 0-1).
    Image: fills the frame with a slow push-in (or "move": "none")."""
    W, H = edit.F["W"], edit.F["H"]
    src = edit._p(b["file"])
    n = round(dur * FPS)
    fx, fy = b.get("focus", [0.5, 0.5])
    out = os.path.join(tmp, f"broll{i:03d}.mp4")
    cover = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase:flags=lanczos,"
             f"crop={W * 2}:{H * 2}:(iw-{W * 2})*{fx}:(ih-{H * 2})*{fy}")
    if src.lower().endswith(IMAGE_EXT):
        move = b.get("move", "push")
        z1 = 1.0 if move == "none" else b.get("zoom", 1.08)
        t = f"on/{max(1, n - 1)}"
        e = f"({t})*({t})*(3-2*({t}))"  # eased, so the move starts and settles gently
        if move == "pull":    # starts close, eases out to the full frame
            z, x = f"{z1}-({z1}-1)*{e}", "iw/2-(iw/zoom/2)"
        elif move == "pan":   # held slightly close, drifts left to right (or "dir": -1)
            d = b.get("dir", 1)
            z, x = f"{z1}", f"(iw-iw/zoom)*({'' if d > 0 else '1-'}{e})"
        else:                 # push: slow, steady push-in to "zoom" (as on earlier videos)
            z, x = f"1+({z1}-1)*{t}", "iw/2-(iw/zoom/2)"
        vf = (f"{cover},zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':"
              f"d={n}:s={W}x{H}:fps={FPS},setsar=1")
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", src]
    else:
        vf = f"{cover},scale={W}:{H}:flags=lanczos,fps={FPS},setsar=1"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(b.get("start", 0)), "-i", src, "-an"]
    shade = edit.cfg.get("broll_shade", 0)
    if shade:  # soft dark fade over the bottom of bright photos so white captions stay readable
        from PIL import Image
        grad = os.path.join(tmp, f"shade_{W}x{H}_{shade}.png")
        if not os.path.exists(grad):
            g = Image.new("RGBA", (W, H))
            top = int(H * 0.5)
            for y in range(top, H):
                t = (y - top) / (H - top)
                a = int(255 * shade * t * t * (3 - 2 * t))
                g.paste((0, 0, 0, a), (0, y, W, y + 1))
            g.save(grad)
        cmd += ["-i", grad]
        args = ["-filter_complex", f"[0:v]{vf}[v];[v][1:v]overlay=0:0:format=auto,format=yuv420p"]
    else:
        args = ["-vf", vf]
    run(cmd + args + ["-frames:v", str(n), "-c:v", "libx264", "-preset", "ultrafast" if draft else "veryfast",
               "-crf", "14", "-pix_fmt", "yuv420p", out])
    return out


def render(edit_path, out, draft=False):
    edit = Edit(edit_path)
    F = edit.F
    tmp = tempfile.mkdtemp(prefix="calibre_")
    try:
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
            segs = list(ex.map(lambda a: render_segment(edit, a[0], a[1], tmp, draft), enumerate(edit.segments)))
            audio_f = ex.submit(render_audio, edit, tmp)
            brolls = broll_spans(edit)
            broll_files = list(ex.map(lambda x: render_broll(edit, x[0], *x[1], tmp, draft), enumerate(brolls)))
            audio = audio_f.result()
        lst = os.path.join(tmp, "list.txt")
        open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
        base = os.path.join(tmp, "base.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])

        cards, spans = card_events(edit)
        ass = os.path.join(tmp, "subs.ass")
        ti = edit.cfg.get("title_card")
        hide = [(a, b) for a, b, _ in spans] + ([(0, ti.get("dur", 3.0))] if ti else [])
        open(ass, "w").write(ass_header(F["W"], F["H"]) + caption_events(edit, hide) + cards + title_events(edit))
        shutil.copy(ass, os.path.splitext(out)[0] + ".ass")

        def when(style=None):
            sel = [(a, b) for a, b, s in spans if style is None or s == style]
            return "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in sel) or "0"

        W, H = F["W"], F["H"]
        wm, m = F["wm"], F["wm_margin"]
        # B-roll goes over the talking head, under captions, cards and logos
        fc, prev = "", "0:v"
        for k, (a, dur, _) in enumerate(brolls):
            fc += (f"[{5 + k}:v]setpts=PTS-STARTPTS+{a:.3f}/TB[br{k}];"
                   f"[{prev}][br{k}]overlay=0:0:eof_action=pass:enable='between(t,{a:.3f},{a + dur - 0.001:.3f})'[bv{k}];")
            prev = f"bv{k}"
        fc += (f"[{prev}]subtitles={ass}:fontsdir={FONTS}[s];"
              f"[2:v]scale={wm}:-1,format=rgba,colorchannelmixer=aa=0.6[wm];"
              f"[3:v]scale={round(wm * 0.8)}:-1[cw];[4:v]scale={round(wm * 0.8)}:-1[cb];"
              f"[s][wm]overlay={W - wm - m}:{m}:enable='eq(0,{when()})'[a];"
              f"[a][cw]overlay=(W-w)/2:H-h-{m + 20}:enable='{when('black')}'[b];"
              f"[b][cb]overlay=(W-w)/2:H-h-{m + 20}:enable='{when('white')}'[v]")
        maps, outro_in = ["-map", "[v]", "-map", "1:a"], []
        if edit.cfg.get("outro", True):
            o = 5 + len(broll_files)
            D = edit.duration
            fc += (f";[v]trim=duration={D:.3f},setpts=PTS-STARTPTS[vm];"
                   f"[1:a]atrim=duration={D:.3f},asetpts=PTS-STARTPTS[am];"
                   f"[vm][am][{o}:v][{o}:a]concat=n=2:v=1:a=1[vo][ao]")
            maps, outro_in = ["-map", "[vo]", "-map", "[ao]"], ["-i", outro_clip(edit.fmt)]
        run(["ffmpeg", "-v", "error", "-y", "-i", base, "-i", audio,
             "-i", os.path.join(LOGOS, "monogram-white.png"),
             "-i", os.path.join(LOGOS, "monogram-white.png"),
             "-i", os.path.join(LOGOS, "monogram-black.png"),
             *[x for f in broll_files for x in ("-i", f)], *outro_in,
             "-filter_complex", fc, *maps,
             "-c:v", "libx264", "-preset", "veryfast" if draft else "slow", "-crf", "20" if draft else "17",
             "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
             "-movflags", "+faststart", "-shortest", out])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"rendered {out}  {edit.duration:.1f}s  {len(edit.segments)} segments"
          + ("  + outro" if edit.cfg.get("outro", True) else ""))


# ---------------------------------------------------------------- plan / stills

def plan(edit_path):
    edit = Edit(edit_path)
    print(f"source {edit.src}\nformat {edit.fmt}  output {edit.duration:.1f}s  "
          f"({len(edit.segments)} shots)\n")
    print("SHOTS  out_start  src_in-src_out  zoom")
    o = 0
    for sg in edit.segments:
        mv = f" {sg['move']}->{sg.get('to') or ''}" if sg.get("move") else ""
        print(f"  {o:7.2f}  {sg['a']:7.2f}-{sg['b']:7.2f}  {sg['zoom']:.2f}{mv}")
        o += sg["b"] - sg["a"]
    toks = align(parse_markup(edit.cfg.get("captions", "")), edit.kept_words)
    if toks:
        print("\nCAPTIONS (out time)")
        for ch in chunk(toks):
            txt = " / ".join(f"{t['text']}" if t["style"] == "bold" else
                             f"*{t['text']}*" if t["style"] == "italic" else t["text"].upper() for t in ch)
            print(f"  {edit.out_time(ch[0]['s']):7.2f}  {txt}")
    print("\nCARDS")
    for c in edit.cfg.get("cards", []):
        print(f"  {edit.out_time(c['from']):7.2f}-{edit.out_time(c['to']):7.2f}  {c.get('style', 'black'):5}  {c['text']}")


def card_stills(edit_path, outdir):
    """Render every card as a PNG for approval, without rendering the video."""
    edit = Edit(edit_path)
    F = edit.F
    os.makedirs(outdir, exist_ok=True)
    cards, spans = card_events(edit)
    ass = os.path.join(outdir, "cards.ass")
    open(ass, "w").write(ass_header(F["W"], F["H"]) + cards)
    for i, (a, b, style) in enumerate(spans):
        logo = os.path.join(LOGOS, "monogram-white.png" if style == "black" else "monogram-black.png")
        wm, m = F["wm"], F["wm_margin"]
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={F['W']}x{F['H']}:d={b + 1}",
             "-i", logo, "-filter_complex",
             f"[0]subtitles={ass}:fontsdir={FONTS}[s];[1]scale={round(wm * 0.8)}:-1[l];"
             f"[s][l]overlay=(W-w)/2:H-h-{m + 20}", "-ss", f"{b - 0.05:.2f}", "-frames:v", "1",
             os.path.join(outdir, f"card{i + 1:02d}.png")])
    print(f"{len(spans)} cards -> {outdir}")


ACRONYMS = {"HMO", "UK", "VAT", "SDLT", "ROI", "LTV", "GDV", "BTL", "EPC"}
# capitalised words from brand/glossary.txt (names, places), keyed by lower case
_GLOSSARY = [l.strip() for l in open(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "brand", "glossary.txt")) if l.strip() and not l.startswith("#")]
# single words ("Brompton", "HMOs") set a word's case anywhere; multi-word terms ("Fabian House",
# "Commercial Road") only where the whole phrase appears, so "commercial lender" stays lower case
GLOSSARY_CASE = {w.lower().strip(".,"): w.strip(".,") for w in _GLOSSARY
                 if " " not in w and any(c.isupper() for c in w)}
GLOSSARY_PHRASES = [w.split() for w in _GLOSSARY if " " in w and any(c.isupper() for c in w)]


def _phrase_case(words, phrases=GLOSSARY_PHRASES):
    """Apply multi-word glossary terms to a list of {"text": ...} words, in place."""
    bare = [re.sub(r"[^\w'-]", "", w["text"]).lower() for w in words]
    for ph in phrases:
        low = [p.lower() for p in ph]
        for i in range(len(words) - len(ph) + 1):
            if bare[i:i + len(ph)] == low:
                for k, form in enumerate(ph):
                    t = words[i + k]["text"]
                    words[i + k]["text"] = re.sub(re.escape(bare[i + k]), form, t, count=1, flags=re.I)


def srt(edit_path, out):
    """Subtitle file (.srt) for upload to YouTube, from the caption text and word timings.
    Key words are written in capitals for the on-screen style; subtitles use the
    spelling as spoken. One sentence per subtitle, long ones split evenly."""
    edit = Edit(edit_path)
    toks = align(parse_markup(edit.cfg.get("captions", "")), edit.kept_words)
    words = []
    for t in toks:
        if not any(sg["a"] < t["e"] and sg["b"] > t["s"] for sg in edit.segments):
            continue
        text = t["text"]
        if t["style"] == "key" and text.isupper():
            # key words are capitals on screen; subtitles take names and acronyms from the
            # glossary and lower-case the rest (whisper's own capitals are unreliable,
            # e.g. "The Vendors Motivation.")
            punct = re.sub(r"^.*?([.,?!;:]*)$", r"\1", text)
            core = text[:len(text) - len(punct)]
            text = (core if core in ACRONYMS else GLOSSARY_CASE.get(core.lower(), core.lower())) + punct
        if not words or re.search(r"[.?!]$", words[-1]["text"]):  # sentence start
            text = text[:1].upper() + text[1:]
        words.append(dict(text=text, s=edit.out_time(t["s"]), e=edit.out_time(t["e"])))
    _phrase_case(words)
    # per-video terms cased anywhere in the subtitles, e.g. "srt_terms": ["Budget", "Section 24"]
    _phrase_case(words, [t.split() for t in edit.cfg.get("srt_terms", [])])

    sentences, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[.?!]$", w["text"]):
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)
    cues = []
    for snt in sentences:
        n = max(1, math.ceil(len(" ".join(w["text"] for w in snt)) / 80))
        size = len(snt) / n
        for k in range(n):
            part = snt[round(k * size):round((k + 1) * size)]
            if part:
                cues.append(part)

    def ts(t):
        ms = int(round(max(0, t) * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, c in enumerate(cues):
        text = " ".join(x["text"] for x in c)
        if len(text) > 42:  # two balanced lines
            ws = text.split()
            best = min(range(1, len(ws)), key=lambda k: abs(len(" ".join(ws[:k])) - len(text) / 2))
            text = " ".join(ws[:best]) + "\n" + " ".join(ws[best:])
        end = min(c[-1]["e"] + 0.4, cues[i + 1][0]["s"]) if i + 1 < len(cues) else c[-1]["e"] + 0.4
        lines.append(f"{i + 1}\n{ts(c[0]['s'])} --> {ts(max(end, c[0]['s'] + 0.8))}\n{text}\n")
    open(out, "w").write("\n".join(lines))
    print(f"{len(cues)} subtitles -> {out}")


def stills(video, outdir, times):
    os.makedirs(outdir, exist_ok=True)
    for t in times:
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1",
             os.path.join(outdir, f"still_{float(t):07.2f}.png")])


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "plan":
        plan(sys.argv[2])
    elif cmd == "render":
        render(sys.argv[2], sys.argv[3], draft="--draft" in sys.argv)
    elif cmd == "srt":
        srt(sys.argv[2], sys.argv[3])
    elif cmd == "cards":
        card_stills(sys.argv[2], sys.argv[3])
    elif cmd == "stills":
        stills(sys.argv[3], sys.argv[4], sys.argv[5:])
    else:
        sys.exit(__doc__)
