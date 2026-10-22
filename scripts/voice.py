"""Voice processing for talking-head audio recorded on a camera mic.

Presets (chosen per edit with "audio": {"preset": ...}):
  basic   — high-pass, gentle compression, loudness normalise (the original chain)
  clean   — + light dereverb (WPE), EQ: less boxiness, more presence and air,
            de-essing, smoother compression
  studio  — + stronger dereverb, a touch of warmth, firmer compression and a soft
            expander that shortens the room tail between phrases
  deep    — studio's cleanup with a deeper, fuller tone: more chest and body,
            softer top, denser compression
Optional "pitch": semitones (e.g. -1) lowers the voice, formants preserved.

Everything ends with two-pass loudness normalisation to -14 LUFS / -1.5 dBTP.
"""
import json, re, subprocess

import numpy as np
import soundfile as sf

EQ_CLEAN = ("highpass=f=80:poles=2,"
            "equalizer=f=300:t=q:w=1.1:g=-3,"      # boxy room/low-mid build-up
            "equalizer=f=4000:t=q:w=1.0:g=2.5,"    # presence / intelligibility
            "highshelf=f=10000:g=1.5,"             # air
            "deesser=i=0.35")
EQ_STUDIO = EQ_CLEAN + ",lowshelf=f=140:g=1.5"     # a little chest warmth
EQ_DEEP = ("highpass=f=70:poles=2,"
           "lowshelf=f=170:g=3.5,"                  # weight and chest
           "equalizer=f=230:t=q:w=0.9:g=1.5,"      # body
           "equalizer=f=380:t=q:w=1.2:g=-2.5,"     # keep the boxiness out above the body
           "equalizer=f=3500:t=q:w=1.0:g=1.5,"     # enough presence to stay clear
           "highshelf=f=8000:g=-1,"                # softer top end
           "deesser=i=0.35")

PRESETS = {
    "basic":  dict(wpe=None, chain="highpass=f=70,acompressor=threshold=-21dB:ratio=2.5:attack=8:release=160:makeup=2"),
    "clean":  dict(wpe=(20, 3), chain=EQ_CLEAN + ",acompressor=threshold=-24dB:ratio=3:attack=6:release=140:knee=4:makeup=3"),
    "studio": dict(wpe=(30, 2), chain=EQ_STUDIO + ",acompressor=threshold=-26dB:ratio=4:attack=5:release=120:knee=4:makeup=4,"
                                       "agate=threshold=0.012:ratio=1.8:range=0.35:attack=8:release=250:knee=4"),
    "deep":   dict(wpe=(30, 2), chain=EQ_DEEP + ",acompressor=threshold=-27dB:ratio=4:attack=6:release=140:knee=4:makeup=4,"
                                     "agate=threshold=0.012:ratio=1.8:range=0.35:attack=8:release=250:knee=4"),
}


def pitch_filter(semitones):
    """Lower/raise pitch without changing timing; formants are kept so it still sounds like you."""
    if not semitones:
        return ""
    return f"rubberband=pitch={2 ** (semitones / 12):.5f}:formant=preserved:pitchq=quality,"


def dereverb(path_in, path_out, taps, delay, block=20.0, overlap=1.0):
    """Weighted Prediction Error dereverberation (nara_wpe).

    Runs on the mono voice in overlapping ~20 s blocks (whole-file WPE needs many GB
    of memory) and crossfades the blocks back together.
    """
    from nara_wpe.wpe import wpe
    from nara_wpe.utils import stft, istft
    x, sr = sf.read(path_in, always_2d=True)
    mono = x.mean(axis=1)
    size, shift = 1536, 384  # 32 ms / 8 ms at 48 kHz
    hop, ov = int(block * sr), int(overlap * sr)
    out, weight = np.zeros_like(mono), np.zeros_like(mono)
    for start in range(0, len(mono), hop):
        a, b = max(0, start - ov), min(len(mono), start + hop + ov)
        seg = mono[a:b]
        Y = stft(seg[None], size=size, shift=shift)
        Z = wpe(Y.transpose(2, 0, 1), taps=taps, delay=delay, iterations=3,
                statistics_mode="full").transpose(1, 2, 0)
        z = istft(Z, size=size, shift=shift)[0][:len(seg)]
        w = np.ones(len(seg))
        if a > 0:
            w[:2 * ov] = np.linspace(0, 1, 2 * ov)
        if b < len(mono):
            w[-2 * ov:] = np.linspace(1, 0, 2 * ov)
        out[a:a + len(z)] += z * w[:len(z)]
        weight[a:a + len(z)] += w[:len(z)]
    out /= np.maximum(weight, 1e-6)
    sf.write(path_out, np.repeat(out[:, None], x.shape[1], axis=1), sr, subtype="PCM_24")


def loudnorm(path_in, path_out, chain, sr=48000):
    """Apply chain, then two-pass loudnorm so the level is exact without pumping."""
    target = "I=-14:TP=-1.5:LRA=9"
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path_in, "-af", f"{chain},loudnorm={target}:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)[-1])
    second = (f"{chain},loudnorm={target}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path_in, "-af", second, "-ar", str(sr), path_out], check=True)


def process(path_in, path_out, preset="clean", pitch=0):
    p = PRESETS[preset]
    src = path_in
    if p["wpe"]:
        src = path_out + ".wpe.wav"
        dereverb(path_in, src, *p["wpe"])
    loudnorm(src, path_out, pitch_filter(pitch) + p["chain"])


# ---------------------------------------------------------------- music bed

REPO = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))


def music_file(track_id):
    """Path to a library track, downloading it into music/cache/ the first time."""
    import os
    lib = json.load(open(os.path.join(REPO, "brand", "music", "library.json")))["tracks"]
    t = next(x for x in lib if x["id"] == int(track_id))
    path = os.path.join(REPO, "brand", "music", "cache", f"{t['id']}.mp3")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["curl", "-sS", "-L", "-o", path, t["url"]], check=True)
    return path


def integrated_lufs(path, start=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "info", "-ss", str(start)] + (["-t", str(dur)] if dur else []) + \
          ["-i", path, "-af", "ebur128=framelog=quiet", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def mix_music(voice_wav, out_wav, music):
    """Lay a music bed under the processed voice.

    music = {"track": <library id>, "start": seconds into the track,
             "bed": LUFS of the bed before ducking (default -30), "duck": dB-ish strength}
    The bed dips under speech (sidechain compression), fades in/out, and the
    finished mix is normalised to -14 LUFS.
    """
    dur = sf.info(voice_wav).duration
    src = music_file(music["track"])
    start = music.get("start", 0.0)
    gain = music.get("bed", -30.0) - integrated_lufs(src, start, min(dur, 120))
    fade_out = min(3.0, dur / 4)
    premix = out_wav + ".premix.wav"
    fc = (f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{dur:.3f},asetpts=N/SR/TB,"
          f"volume={gain:.2f}dB,afade=t=in:d=0.8,afade=t=out:st={dur - fade_out:.3f}:d={fade_out:.3f}[m];"
          f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[v][sc];"
          f"[m][sc]sidechaincompress=threshold=0.1:ratio={music.get('duck', 2.5)}:attack=50:release=600:knee=4[md];"
          f"[v][md]amix=inputs=2:normalize=0:duration=first")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice_wav, "-stream_loop", "-1", "-ss", str(start), "-i", src,
                    "-filter_complex", fc, "-ar", "48000", premix], check=True)
    loudnorm(premix, out_wav, "anull")
