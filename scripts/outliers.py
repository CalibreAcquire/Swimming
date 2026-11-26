#!/usr/bin/env python3
"""Find outlier videos (views far above their channel's norm) for the monthly ideas list.

The YouTube playbook (brand/youtube_playbook.md) says: study videos doing 3x or more their channel's
average, in our niche and adjacent ones, and build ideas from them.

    outliers.py discover "commercial property uk" "hmo uk" ... [--per 40] > channels.json
        Searches YouTube and lists the channels that come up most, with their subscriber counts.
    outliers.py scan channels.json|@handle ... [--last 60] [--min 3] [--out outliers.json]
        Reads each channel's latest long-form videos, scores each video as views / channel median
        and lists everything at --min x or more (default 3x), best first.

Needs yt-dlp (pip install yt-dlp). Uses public listing pages only (no downloads, no API key).
The median is used rather than the mean so one viral video doesn't hide the others; the score is
still read the same way (3x worth a look, 30x+ a hit).
"""
import argparse
import collections
import json
import statistics
import subprocess
import sys


def ytdlp_json(url, extra=()):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--no-warnings", *extra, url],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not r.stdout.strip():
        print(f"  skip {url}: {r.stderr.strip()[:200]}", file=sys.stderr)
        return None
    return json.loads(r.stdout)


def discover(queries, per):
    seen = collections.Counter()
    names = {}
    for q in queries:
        d = ytdlp_json(f"ytsearch{per}:{q}")
        for e in (d or {}).get("entries", []) or []:
            cid = e.get("channel_id")
            if not cid:
                continue
            seen[cid] += 1
            names[cid] = e.get("channel") or e.get("uploader") or cid
        print(f"  searched: {q}", file=sys.stderr)
    out = [{"channel_id": c, "name": names[c], "hits": n} for c, n in seen.most_common()]
    json.dump(out, sys.stdout, indent=1, ensure_ascii=False)


def channel_videos(ref, last):
    url = ref if ref.startswith("http") else (
        f"https://www.youtube.com/{ref}" if ref.startswith("@") else f"https://www.youtube.com/channel/{ref}")
    d = ytdlp_json(url + "/videos", ["--playlist-end", str(last)])
    if not d:
        return None, []
    vids = [e for e in d.get("entries", []) or [] if e.get("view_count")]
    return d, vids


def scan(refs, last, minx):
    chans = []
    for r in refs:
        if r.endswith(".json"):
            chans += [c["channel_id"] for c in json.load(open(r))]
        else:
            chans.append(r)
    rows = []
    for ref in chans:
        d, vids = channel_videos(ref, last)
        if len(vids) < 8:
            continue
        med = statistics.median(v["view_count"] for v in vids)
        mean = statistics.mean(v["view_count"] for v in vids)
        name = d.get("channel") or d.get("uploader") or ref
        subs = d.get("channel_follower_count")
        print(f"  {name}: {len(vids)} videos, median {med:,.0f}, subs {subs}", file=sys.stderr)
        for v in vids:
            score = v["view_count"] / max(med, 1)
            if score >= minx:
                rows.append({"score": round(score, 1), "views": v["view_count"], "median": int(med),
                             "mean": int(mean), "subs": subs, "channel": name, "title": v.get("title"),
                             "duration": v.get("duration"), "url": f"https://www.youtube.com/watch?v={v['id']}"})
    rows.sort(key=lambda r: -r["score"])
    return rows


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("discover"); a.add_argument("queries", nargs="+"); a.add_argument("--per", type=int, default=40)
    b = sub.add_parser("scan"); b.add_argument("refs", nargs="+"); b.add_argument("--last", type=int, default=60)
    b.add_argument("--min", type=float, default=3.0); b.add_argument("--out")
    args = ap.parse_args()
    if args.cmd == "discover":
        discover(args.queries, args.per)
    else:
        rows = scan(args.refs, args.last, args.min)
        if args.out:
            json.dump(rows, open(args.out, "w"), indent=1, ensure_ascii=False)
        for r in rows:
            print(f"{r['score']:6.1f}x {r['views']:>10,}  {r['channel'][:28]:28}  {r['title']}")


if __name__ == "__main__":
    main()
