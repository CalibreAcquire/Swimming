# Transcribe a video with word-level timestamps.
# Usage: python3 tools/transcribe.py <video> <out.json> [script.txt]   (needs: pip install faster-whisper)
# Passing the read-aloud script lifts its uncommon words (names, jargon) as hotwords.
# condition_on_previous_text is off: with it on, the model can loop and repeat a phrase.
# WHISPER_MODEL env var picks the model size (default "medium").
# Audio is decoded with ffmpeg rather than PyAV to avoid PyAV version clashes.
import sys, json, os
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
hot = None
if len(sys.argv) > 3:
    common = set("the a an and or of to in on for is it that this what we you i if be are with as by from at your our its".split())
    vocab = dict.fromkeys(w.strip(".,?!()\"'—") for w in open(sys.argv[3]).read().split())
    hot = " ".join(w for w in vocab if w and w.lower() not in common and (w[0].isupper() or len(w) > 7))[:600]
m = WhisperModel(os.environ.get("WHISPER_MODEL", "medium"), device="cpu", compute_type="int8")
import subprocess, numpy as np
pcm = subprocess.run(["ffmpeg","-v","error","-i",src,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True,check=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
segs, info = m.transcribe(audio, word_timestamps=True, vad_filter=True,
                            condition_on_previous_text=False, hotwords=hot)
res = {"language": info.language, "segments": []}
for s in segs:
    res["segments"].append({"start": s.start, "end": s.end, "text": s.text,
        "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for w in s.words]})
json.dump(res, open(out, "w"), indent=1)
print("done", len(res["segments"]))
