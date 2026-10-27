#!/usr/bin/env python3
"""Listing video renderer: many short clips on one timeline, in the premium listing style
(Jake, 27 Oct 2026): hard cuts every 1-3 s, slow push-ins, plain white Montserrat text
centred on screen (no bold, no colour), a music bed, the logo watermark and the outro.

calibre_edit.py is built around one talking-head source; listings mix the Q&A clips,
walk-ups and Kim's property footage, so they use this instead.

Usage: listing_edit.py <edl.json> <out.mp4> [--draft]

EDL keys (times in OUTPUT seconds unless noted; paths relative to the EDL):
  format        "9x16" (1080x1920) or "16x9" (1920x1080)
  fps           output frame rate (default 30)
  shots         [{"file", "in": source s, "dur": s, "move": "push"|"pull"|"none",
                  "zoom": start zoom (1.0), "focus": [fx, fy] 0-1 point to zoom into}]
                  played back to back; their total is the video length (before the outro)
  audio         [{"file", "a": source s, "b": source s, "at": output s, "gain": dB}]  speech
                  and ambience laid on the timeline; speech clips are levelled to each other
  text          [{"from", "to", "text", "size": px (default 50), "y": 0-1 (default 0.5)}]
                  "\\N" breaks a line; captions and titles both use this
  music         {"track", "start", "bed", "duck"}  as voice.mix_music
  grade         ffmpeg filter for colour (default none: location footage keeps its own colour)
  outro         true (default): Jake's outro for the format, from brand/outros
"""
import json, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice  # noqa: E402
import calibre_edit as ce  # noqa: E402

SR = 48000
SIZES = {"9x16": (1080, 1920), "16x9": (1920, 1080)}


def run(cmd):
    subprocess.run(cmd, check=True)


def ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def text_ass(edl, W, H):
    """Plain white Montserrat, centred, soft shadow; a gentle fade in and out."""
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: T,Montserrat Medium,50,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,0,2,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for t in edl.get("text", []):
        size = t.get("size", 54 if W < H else 50)
        y = t.get("y", 0.5) * H
        pos = rf"\an5\pos({W / 2:.0f},{y:.0f})\fs{size}\fad(120,120)"
        # a soft dark halo under the text (no box), so it reads on white walls and bright sky
        halo = rf"{{{pos}\bord6\3c&H000000&\3a&H88&\1a&HFF&\shad0\blur10}}"
        ev.append(f"Dialogue: 0,{ass_time(t['from'])},{ass_time(t['to'])},T,,0,0,0,,{halo}{t['text']}\n")
        tags = rf"{{{pos}\bord0\shad1\4a&HA0&\blur0.4}}"
        ev.append(f"Dialogue: 1,{ass_time(t['from'])},{ass_time(t['to'])},T,,0,0,0,,{tags}{t['text']}\n")
    return head + "".join(ev)


def render_shot(edl, i, s, base, tmp, W, H, fps, draft):
    out = os.path.join(tmp, f"shot{i:03d}.mp4")
    src = os.path.join(base, s["file"])
    dur = s["dur"]
    z0 = s.get("zoom", 1.0)
    move = s.get("move", "push")
    z1 = z0 + (0.05 if move == "push" else -0.05 if move == "pull" else 0)
    if move == "pull":
        z0, z1 = z0 + 0.05, z0
    fx, fy = s.get("focus", [0.5, 0.45])
    grade = edl.get("grade") or "null"
    # cover the frame, then a time-varying zoom (eval=frame) and a crop around the focus point
    zoom = f"({z0}+({z1}-{z0})*min(t/{dur},1))"
    vf = (f"fps={fps},{grade},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
          f"crop={W}:{H},scale=w='ceil({W}*{zoom}/2)*2':h=-2:eval=frame:flags=bicubic,"
          f"crop={W}:{H}:x='(iw-{W})*{fx}':y='(ih-{H})*{fy}',setsar=1,format=yuv420p")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['in']:.3f}", "-i", src, "-t", f"{dur:.3f}", "-an",
         "-vf", vf, "-frames:v", str(round(dur * fps)), "-r", str(fps),
         "-c:v", "libx264", "-preset", "ultrafast" if draft else "medium", "-crf", "14", out])
    return out


def render_audio(edl, base, tmp, total):
    """Each clip cleaned (high-pass, light denoise), speech levelled to -20 LUFS, laid on the
    timeline with short fades, then the music bed and the -14 LUFS master (voice.py)."""
    parts = []
    for i, a in enumerate(edl.get("audio", [])):
        raw = os.path.join(tmp, f"a{i:02d}.wav")
        d = a["b"] - a["a"]
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a['a']:.3f}", "-t", f"{d:.3f}",
             "-i", os.path.join(base, a["file"]), "-map", "0:a:0", "-ac", "2", "-ar", str(SR),
             "-af", "highpass=f=90,afftdn=nf=-28", raw])
        if a.get("gain") is None:  # speech: level each clip so Jake and Lee match
            g = -20 - voice.integrated_lufs(raw)
        else:
            g = a["gain"]
        fade = min(0.03, d / 4)
        parts.append((raw, a["at"], g, d, fade))
    if not parts:
        silent = os.path.join(tmp, "voice.wav")
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo",
             "-t", f"{total:.3f}", silent])
        return silent
    ins, fc = [], []
    for k, (raw, at, g, d, fade) in enumerate(parts):
        ins += ["-i", raw]
        fc.append(f"[{k}:a]volume={g:.2f}dB,afade=t=in:d={fade},afade=t=out:st={d - fade:.3f}:d={fade},"
                  f"adelay={int(at * 1000)}|{int(at * 1000)}[p{k}]")
    fc.append("".join(f"[p{k}]" for k in range(len(parts))) +
              f"amix=inputs={len(parts)}:normalize=0:duration=longest,apad,atrim=0:{total:.3f}[m]")
    lay = os.path.join(tmp, "laid.wav")
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[m]",
         "-ar", str(SR), lay])
    vo = os.path.join(tmp, "voice.wav")
    voice.loudnorm(lay, vo, "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=160:makeup=2")
    if edl.get("music"):
        mixed = os.path.join(tmp, "mix.wav")
        voice.mix_music(vo, mixed, edl["music"])
        return mixed
    return vo


def render(edl_path, out, draft=False):
    edl = json.load(open(edl_path))
    base = os.path.dirname(os.path.abspath(edl_path))
    fmt = edl.get("format", "9x16")
    W, H = SIZES[fmt]
    fps = edl.get("fps", 30)
    shots = edl["shots"]
    total = sum(s["dur"] for s in shots)
    tmp = tempfile.mkdtemp(prefix="listing_")
    try:
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
            files = list(ex.map(lambda x: render_shot(edl, x[0], x[1], base, tmp, W, H, fps, draft),
                                enumerate(shots)))
            audio = ex.submit(render_audio, edl, base, tmp, total).result()
        lst = os.path.join(tmp, "list.txt")
        open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
        video = os.path.join(tmp, "video.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
        ass = os.path.join(tmp, "text.ass")
        open(ass, "w").write(text_ass(edl, W, H))
        shutil.copy(ass, os.path.splitext(out)[0] + ".ass")
        wm = 64 if fmt == "9x16" else 72
        m = 56 if fmt == "9x16" else 48
        fc = (f"[0:v]subtitles={ass}:fontsdir={ce.FONTS}[s];"
              f"[2:v]scale={wm}:-1,format=rgba,colorchannelmixer=aa=0.6[wm];"
              f"[s][wm]overlay={W - wm - m}:{m}[v0];"
              f"[v0]trim=duration={total:.3f},setpts=PTS-STARTPTS[v];"
              f"[1:a]atrim=duration={total:.3f},asetpts=PTS-STARTPTS[a]")
        ins = ["-i", video, "-i", audio, "-i", os.path.join(ce.LOGOS, "monogram-white.png")]
        if edl.get("outro", True):
            ins += ["-i", ce.outro_clip(fmt, fps)]
            fc += ";[v][a][3:v][3:a]concat=n=2:v=1:a=1[vo][ao]"
            maps = ["-map", "[vo]", "-map", "[ao]"]
        else:
            maps = ["-map", "[v]", "-map", "[a]"]
        run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, *maps,
             "-c:v", "libx264", "-preset", "veryfast" if draft else "slow", "-crf", "20" if draft else "17",
             "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(fps),
             "-c:a", "aac", "-b:a", "320k", "-ar", str(SR), "-movflags", "+faststart", out])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"rendered {out}  {total:.1f}s + outro" if edl.get("outro", True) else f"rendered {out}  {total:.1f}s")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    render(a[0], a[1], draft="--draft" in sys.argv)
