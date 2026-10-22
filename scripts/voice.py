"""Voice processing for talking-head audio recorded on a camera mic.

Presets (chosen per edit with "audio": {"preset": ...}):
  basic   — high-pass, gentle compression, loudness normalise (the original chain)
  clean   — + light dereverb (WPE), EQ: less boxiness, more presence and air,
            de-essing, smoother compression
  studio  — + stronger dereverb, a touch of warmth, firmer compression and a soft
            expander that shortens the room tail between phrases
  deep    — studio's cleanup with a deeper, fuller tone: more chest and body,
            softer top, denser compression
  full    — for echoey rooms: WPE plus gentle, smoothed late-reverb suppression,
            deep's tone with more body, gentle compression so the room tail stays down
            (Jake's default from 22 Oct 2026)
Optional "pitch": semitones (e.g. -1) lowers the voice, formants preserved.

Everything ends at -14 LUFS / -1.3 dBTP via a plain gain and a peak limiter.
(ffmpeg's loudnorm falls back to dynamic mode when it can't hit the target
linearly, and that brings the room echo back up between words.)
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

EQ_FULL = ("highpass=f=70:poles=2,"
           "lowshelf=f=160:g=5.5,"                  # weight and chest
           "equalizer=f=250:t=q:w=0.9:g=2.5,"      # body
           "equalizer=f=450:t=q:w=1.2:g=-3,"       # boxiness
           "equalizer=f=3000:t=q:w=1.0:g=2,"       # presence
           "highshelf=f=8000:g=-0.5,"
           "deesser=i=0.35")

PRESETS = {
    "basic":  dict(wpe=None, chain="highpass=f=70,acompressor=threshold=-21dB:ratio=2.5:attack=8:release=160:makeup=2"),
    "clean":  dict(wpe=(20, 3), chain=EQ_CLEAN + ",acompressor=threshold=-24dB:ratio=3:attack=6:release=140:knee=4:makeup=3"),
    "studio": dict(wpe=(30, 2), chain=EQ_STUDIO + ",acompressor=threshold=-26dB:ratio=4:attack=5:release=120:knee=4:makeup=4,"
                                       "agate=threshold=0.012:ratio=1.8:range=0.35:attack=8:release=250:knee=4"),
    "deep":   dict(wpe=(30, 2), chain=EQ_DEEP + ",acompressor=threshold=-27dB:ratio=4:attack=6:release=140:knee=4:makeup=4,"
                                     "agate=threshold=0.012:ratio=1.8:range=0.35:attack=8:release=250:knee=4"),
    # chain runs on the voice levelled to -20 LUFS (see process)
    # reverb: (rt60, floor dB, gain smoothing bins x frames); Jake chose this gentle
    # setting (Option A): stronger or faster suppression sounded robotic
    "full":   dict(wpe=(30, 2), reverb=(0.8, -8, (9, 9)), chain=EQ_FULL + ",acompressor=threshold=-18dB:ratio=2:attack=10:release=200:knee=6"),
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
        n = min(2 * ov, len(seg))  # the last block can be shorter than the crossfade
        if a > 0:
            w[:n] = np.linspace(0, 1, n)
        if b < len(mono):
            w[-n:] = np.linspace(1, 0, n)
        out[a:a + len(z)] += z * w[:len(z)]
        weight[a:a + len(z)] += w[:len(z)]
    out /= np.maximum(weight, 1e-6)
    sf.write(path_out, np.repeat(out[:, None], x.shape[1], axis=1), sr, subtype="PCM_24")


def suppress_reverb(path_in, path_out, rt60=0.8, delay=0.05, floor_db=-14.0, smooth=(3, 3)):
    """Late-reverb suppression (Lebart et al.): the room tail at each moment is
    predicted from the signal `delay` seconds earlier, decayed at the room's RT60,
    and subtracted spectrally. Takes out the echo WPE leaves behind in lively rooms.
    """
    import scipy.signal as ss
    x, sr = sf.read(path_in, always_2d=True)
    mono = x.mean(axis=1)
    nper, hop = 1024, 256
    f, t, Y = ss.stft(mono, sr, nperseg=nper, noverlap=nper - hop)
    P = np.abs(Y) ** 2
    # smooth the power over ~30 ms so the prediction follows the envelope, not each frame
    k = np.ones(5) / 5
    Ps = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, P)
    nd = max(1, int(round(delay * sr / hop)))
    decay = np.exp(-2 * (3 * np.log(10) / rt60) * delay)
    late = np.zeros_like(Ps)
    late[:, nd:] = decay * Ps[:, :-nd]
    g = np.maximum(1 - late / (Ps + 1e-12), 10 ** (floor_db / 10))
    g = np.sqrt(g)
    # smooth the gain across frequency bins and time frames: heavy smoothing keeps the
    # voice natural (fast, narrow gain changes are what sound robotic)
    from scipy.ndimage import uniform_filter
    g = uniform_filter(g, size=smooth, mode="nearest")
    _, z = ss.istft(Y * g, sr, nperseg=nper, noverlap=nper - hop)
    z = z[:len(mono)]
    sf.write(path_out, np.repeat(z[:, None], x.shape[1], axis=1), sr, subtype="PCM_24")


def measure(path):
    """Integrated loudness (LUFS) and true peak (dBTP)."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af", "ebur128=framelog=quiet:peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    return (float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1]),
            float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)[-1]))


def loudnorm(path_in, path_out, chain, sr=48000, target=-14.0, ceiling=-1.6):
    """Apply chain, then a plain gain to the target loudness and a peak limiter.

    No dynamic loudness processing: what the chain did to the dynamics is what you hear.
    """
    tmp = path_out + ".pre.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path_in, "-af", chain, "-c:a", "pcm_f32le", tmp], check=True)
    gain = target - measure(tmp)[0]
    for _ in range(3):  # limiting lowers the loudness a little; correct and redo
        lim = f"volume={gain:.2f}dB,alimiter=limit={10 ** (ceiling / 20):.4f}:attack=2:release=80:level=0"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", lim, "-ar", str(sr), "-c:a", "pcm_s24le",
                        path_out], check=True)
        i, _ = measure(path_out)
        if abs(i - target) < 0.15:
            break
        gain += target - i
    __import__("os").remove(tmp)


def process(path_in, path_out, preset="clean", pitch=0):
    p = PRESETS[preset]
    src = path_in
    if p["wpe"]:
        src = path_out + ".wpe.wav"
        dereverb(path_in, src, *p["wpe"])
    pre = ""
    if p.get("reverb"):
        sup = path_out + ".sup.wav"
        rt60, floor, smooth = p["reverb"]
        suppress_reverb(src, sup, rt60=rt60, floor_db=floor, smooth=smooth)
        src = sup
        pre = f"volume={-20 - integrated_lufs(src):.2f}dB,"
    loudnorm(src, path_out, pre + pitch_filter(pitch) + p["chain"])


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
