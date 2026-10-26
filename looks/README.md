# Look tests (26 Oct 2026)

Jake: still an orange/yellow tinge on the Budget video. Default is now **no adjustment** (`DEFAULT_GRADE = "null"`
in `scripts/calibre_edit.py`; EDLs set no `grade`). Same 3 seconds of the office footage (Budget.MP4 at 464.3 s) in
each clip. When Jake picks one, put its filter in `DEFAULT_GRADE` and record it in `brand/learnings.md`.

| Clip | Look | ffmpeg filter | Wall R−B (neutral ≈ 0) |
|---|---|---|---|
| 0 | No adjustment (as filmed) | `null` | 12 |
| 1 | White balance only | `colorchannelmixer=rr=0.973:bb=1.028` | 2 |
| 2 | White balance + softer skin | `colorchannelmixer=rr=0.973:bb=1.028,eq=saturation=0.9` | 2 |
| 3 | White balance + brighter | `colorchannelmixer=rr=0.973:bb=1.028,curves=master='0/0 0.12/0.09 0.45/0.52 0.8/0.86 1/1'` | 2 |
| 4 | Cooler | `colorchannelmixer=rr=0.96:gg=0.988:bb=1.04,eq=saturation=0.92` | −3 |

The white balance numbers are measured on this office's wall; another location needs its own measurement.
