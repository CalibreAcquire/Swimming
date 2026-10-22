"""Voice processing for talking-head audio recorded on a camera mic.

Presets (chosen per edit with "audio": {"preset": ...}):
  basic   — high-pass, gentle compression, loudness normalise (the original chain)
  clean   — + light dereverb (WPE), EQ: less boxiness, more presence and air,
            de-essing, smoother compression
  studio  — + stronger dereverb, a touch of warmth, firmer compression and a soft
            expander that shortens the room tail between phrases

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

PRESETS = {
    "basic":  dict(wpe=None, chain="highpass=f=70,acompressor=threshold=-21dB:ratio=2.5:attack=8:release=160:makeup=2"),
    "clean":  dict(wpe=(20, 3), chain=EQ_CLEAN + ",acompressor=threshold=-24dB:ratio=3:attack=6:release=140:knee=4:makeup=3"),
    "studio": dict(wpe=(30, 2), chain=EQ_STUDIO + ",acompressor=threshold=-26dB:ratio=4:attack=5:release=120:knee=4:makeup=4,"
                                       "agate=threshold=0.012:ratio=1.8:range=0.35:attack=8:release=250:knee=4"),
}


def dereverb(path_in, path_out, taps, delay):
    """Weighted Prediction Error dereverberation (nara_wpe), channel by channel."""
    from nara_wpe.wpe import wpe
    from nara_wpe.utils import stft, istft
    x, sr = sf.read(path_in, always_2d=True)
    size, shift = 1536, 384  # 32 ms / 8 ms at 48 kHz
    out = np.zeros_like(x)
    for c in range(x.shape[1]):
        Y = stft(x[:, c][None], size=size, shift=shift)
        Z = wpe(Y.transpose(2, 0, 1), taps=taps, delay=delay, iterations=3,
                statistics_mode="full").transpose(1, 2, 0)
        out[:, c] = istft(Z, size=size, shift=shift)[0][:len(x)]
    sf.write(path_out, out, sr, subtype="PCM_24")


def loudnorm(path_in, path_out, chain, sr=48000):
    """Apply chain, then two-pass loudnorm so the level is exact without pumping."""
    target = "I=-14:TP=-1.5:LRA=9"
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path_in, "-af", f"{chain},loudnorm={target}:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)[-1])
    second = (f"{chain},loudnorm={target}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path_in, "-af", second, "-ar", str(sr), path_out], check=True)


def process(path_in, path_out, preset="clean"):
    p = PRESETS[preset]
    src = path_in
    if p["wpe"]:
        src = path_out + ".wpe.wav"
        dereverb(path_in, src, *p["wpe"])
    loudnorm(src, path_out, p["chain"])
