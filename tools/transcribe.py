# Transcribe a video with word-level timestamps.
# Usage: python3 tools/transcribe.py <video> <out.json>   (needs: pip install faster-whisper)
# Audio is decoded with ffmpeg rather than PyAV to avoid PyAV version clashes.
import sys, json
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
m = WhisperModel("small", device="cpu", compute_type="int8")
import subprocess, numpy as np
pcm = subprocess.run(["ffmpeg","-v","error","-i",src,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True,check=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
segs, info = m.transcribe(audio, word_timestamps=True, vad_filter=False)
res = {"language": info.language, "segments": []}
for s in segs:
    res["segments"].append({"start": s.start, "end": s.end, "text": s.text,
        "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for w in s.words]})
json.dump(res, open(out, "w"), indent=1)
print("done", len(res["segments"]))
