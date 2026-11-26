#!/usr/bin/env python3
"""Check a script, transcript or title list against the YouTube playbook and the content rules.

    script_check.py <script.txt|.md|.pdf|transcript.json|.srt> [--title "..."] [--listing] [--instagram]
    script_check.py --titles titles.txt

Flags (each with the line or timestamp):
  * PROMISE  the title's key words are not shown or said in the first 10 seconds (about 25 words)
  * INTRO    the intro runs past 45 seconds before the main content starts; topic-list openings
             ("in today's video we'll cover…"); a self-introduction inside the first 10 seconds
  * EARLIER  references to earlier videos ("as you saw last week") that lose new viewers
  * ENDING   ending language before the last 15% ("at the end of the day", "to wrap up")
  * JARGON   terms half the audience may not know (fine when the video is for experienced investors)
  * RULE     content rules from CLAUDE.md section 8 (portals, "land value", fees, "off-market" in a
             listing video, the £30m line on Instagram)
Title lists: length (about 60 characters), all capitals, jargon, title case.

Transcripts are read as faster-whisper JSON ({"segments":[{"start","end","text"}]} or a list of
words with "start"/"word"), or .srt. Plain scripts are timed at 2.6 words a second (Jake's pace).
"""
import argparse
import json
import re
import subprocess
import sys

WPS = 2.6  # Jake's speaking rate, words per second

EARLIER = [r"\b(my|our|the) (last|previous) (video|episode)", r"\blast week'?s? video", r"\bas (you|we) saw\b",
           r"\bas i (said|mentioned) (in|last)", r"\bin (my|our) (last|previous|other) video", r"\bif you watched\b",
           r"\bcheck out (my|our) (last|previous)", r"\bpart (one|two|1|2)\b"]
ENDING = [r"\bat the end of the day\b", r"\bto wrap (this )?up\b", r"\bin conclusion\b", r"\bto sum (it )?up\b",
          r"\bthat'?s (it|all) for\b", r"\bbefore (i|we) go\b", r"\bone last thing\b", r"\bto finish\b",
          r"\bthanks for watching\b", r"\bso there you have it\b"]
TOPIC_LIST = [r"\bin (today'?s|this) video\b", r"\bi'?ll show you\b", r"\bwe'?(ll| will) (cover|look at|go through|talk about)\b",
              r"\bi'?m going to (cover|go through|talk about)\b", r"\bwe'?re going to (cover|go through)\b"]
SELF_INTRO = [r"\bmy name is\b", r"\bi'?m jake\b", r"\bfounder of calibre\b"]
JARGON = ["HMO", "SDLT", "GDV", "EBITDA", "BRR", "BRRR", "BTL", "LTV", "ICR", "NOI", "cap rate", "FRI", "IRI",
          "Section 24", "CGT", "ROCE", "SPV", "PRS", "EPC", "title split", "permitted development", "Class MA",
          "AST", "covenant", "yield compression", "MVL", "BADR", "s24", "ERV", "WAULT", "vacant possession"]
RULES = [(r"\b(rightmove|zoopla|onthemarket|land registry|loopnet|realla|costar|savills|knight frank)\b",
          "names a portal, company or data source (use 'all major property platforms')"),
         (r"\bland value\b", "'land value' for an existing building (use 'site value')"),
         (r"\b(registration|joining|membership) fee\b|\bpaid (strategy )?call\b", "fee or paid call"),
         (r"\bon the market now\b|\bavailable to buy now\b", "banned listing wording")]


def load(path):
    """Return a list of (seconds, text) units: sentences for scripts, segments for transcripts."""
    if path.endswith(".json"):
        d = json.load(open(path))
        segs = d.get("segments", d) if isinstance(d, dict) else d
        if segs and segs[0].get("words"):
            segs = [{"start": w.get("start", w.get("s")), "word": w.get("word", w.get("w", ""))}
                    for s in segs for w in s["words"]]
        if segs and "word" in segs[0]:
            text, units, t0 = [], [], segs[0]["start"]
            for w in segs:
                text.append(w["word"].strip())
                if re.search(r"[.?!]$", w["word"].strip()):
                    units.append((t0, " ".join(text))); text = []; t0 = None
                elif t0 is None:
                    t0 = w["start"]
            if text:
                units.append((t0 or segs[-1]["start"], " ".join(text)))
            return units, True
        return [(s["start"], s["text"].strip()) for s in segs], True
    if path.endswith(".srt"):
        units = []
        for block in re.split(r"\n\s*\n", open(path, encoding="utf-8").read().strip()):
            lines = block.strip().splitlines()
            m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)", lines[1]) if len(lines) > 2 else None
            if m:
                h, mi, s, ms = map(int, m.groups())
                units.append((h * 3600 + mi * 60 + s + ms / 1000, " ".join(lines[2:])))
        return units, True
    if path.endswith(".pdf"):
        raw = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True).stdout
    else:
        raw = open(path, encoding="utf-8").read()
    sents = [s.strip() for s in re.split(r"(?<=[.?!])\s+|\n{2,}", raw) if s.strip()]
    units, words = [], 0
    for s in sents:
        units.append((words / WPS, s))
        words += len(s.split())
    return units, False


def fmt(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def check_script(path, title, listing, instagram):
    units, timed = load(path)
    end = units[-1][0] if units else 0
    out = []

    def flag(kind, t, text, why):
        text = " ".join(text.split())
        out.append((t, kind, why, text if len(text) < 140 else text[:137] + "..."))

    for t, text in units:
        low = text.lower()
        if any(re.search(p, low) for p in EARLIER):
                flag("EARLIER", t, text, "refers to an earlier video; new viewers won't have seen it")
        if t < end * 0.85 and any(re.search(p, low) for p in ENDING):
                flag("ENDING", t, text, "ending language mid-video makes people leave")
        if t < 60 and any(re.search(p, low) for p in TOPIC_LIST):
                flag("INTRO", t, text, "topic list in the intro; open a curiosity gap instead")
        if t < 10 and any(re.search(p, low) for p in SELF_INTRO):
                flag("INTRO", t, text, "self-introduction inside the first 10 s; prove the promise first")
        for j in JARGON:
            if re.search(r"\b" + re.escape(j) + r"\b", text, 0 if j.isupper() else re.I):
                flag("JARGON", t, text, f"'{j}': explain it or keep it for an investor-only video")
        for p, why in RULES:
            if re.search(p, low):
                flag("RULE", t, text, why)
        if listing and re.search(r"\boff[- ]market\b", low):
            flag("RULE", t, text, "'off-market' in a listing video (use 'now available for sale')")
        if instagram and re.search(r"£\s?30\s?(million|m)\b", low):
            flag("RULE", t, text, "the £30m line is YouTube only")

    # Intro length: main content starts after the last intro marker in the first 2 minutes.
    markers = [t for t, text in units if t < 120 and any(re.search(p, text.lower()) for p in
               TOPIC_LIST + SELF_INTRO + [r"\bwelcome back\b", r"\bsubscribe\b", r"\bcalculator"])]
    if markers and max(markers) > 45:
        nxt = [t for t, _ in units if t > max(markers)]
        flag("INTRO", nxt[0] if nxt else max(markers), "",
             f"intro markers run to {fmt(max(markers))}; aim for the content to start before 0:45")

    if title:
        stop = set("a an the and or of to in on for with is are was it this that how why what i we you my our "
                   "your from at by be".split())
        keys = [w for w in re.findall(r"[a-z0-9£%,.]+", title.lower()) if w.strip(",.") not in stop]
        keys = [k.strip(",.") for k in keys if k.strip(",.")]
        first = " ".join(text for t, text in units if t < 10).lower()
        hit = [k for k in keys if k in first]
        if len(hit) < max(1, len(keys) // 2):
            flag("PROMISE", 0, first[:120], f"first 10 s say {len(hit)}/{len(keys)} of the title's key words "
                 f"({', '.join(k for k in keys if k not in hit)} missing); show or say the promise early")

    out.sort()
    for t, kind, why, text in out:
        print(f"{fmt(t):>6} {kind:8} {why}" + (f"\n{'':16}\"{text}\"" if text else ""))
    print(f"\n{len(out)} flags ({'timed' if timed else 'script timed at %.1f words/s' % WPS}; "
          f"running time about {fmt(end)})")


def check_titles(path):
    for line in open(path, encoding="utf-8"):
        t = re.sub(r"^\s*(\d+[.)]|[-*])\s*", "", line.strip()).strip("`")
        if not t or t.startswith("#"):
            continue
        notes = []
        if len(t) > 60:
            notes.append(f"{len(t)} chars")
        if [w for w in re.findall(r"\b[A-Z][A-Z'’]{2,}\b", t) if w not in ("HMO", "SDLT", "VAT", "CGT", "UAE", "STC", "GDV")]:
            notes.append("all-caps word")
        for j in JARGON:
            if re.search(r"\b" + re.escape(j) + r"\b", t, 0 if j.isupper() else re.I):
                notes.append(f"jargon '{j}'")
        small = set("a an and as at but by for in of on or the to vs with from".split())
        words = re.findall(r"[A-Za-z][\w'’-]*", t)
        if any(w[0].islower() and w.lower() not in small for w in words[1:]):
            notes.append("not title case")
        print(f"{len(t):3}  {t}" + (f"   <- {'; '.join(notes)}" if notes else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--title")
    ap.add_argument("--titles")
    ap.add_argument("--listing", action="store_true")
    ap.add_argument("--instagram", action="store_true")
    a = ap.parse_args()
    if a.titles:
        check_titles(a.titles)
    elif a.path:
        check_script(a.path, a.title, a.listing, a.instagram)
    else:
        ap.error("give a script/transcript or --titles")


if __name__ == "__main__":
    main()
