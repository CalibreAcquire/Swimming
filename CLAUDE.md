# Calibre Acquire video editing

This repo is the video editing pipeline for Calibre Acquire's YouTube videos and
Instagram reels (property content).

- `VIDEO_STYLE.md` — the house editing style. Follow it for every edit and
  update it when the user refines a preference.
- `brand/logos/` — logo files. `brand/fonts/` — brand fonts (install to
  `~/.fonts` and run `fc-cache -f` before rendering text).
- `reference/` — analyses of example videos the user likes.
- Raw footage and example videos arrive via Google Drive. Never commit video
  files to the repo (`.gitignore` covers `projects/*/src/` and renders).

## Tools
- `tools/transcribe.py <video> <out.json> [script.txt]` — word-level transcript
  (faster-whisper, `pip install faster-whisper fonttools`). Default model is
  `medium`; pass the read-aloud script when there is one.
- `tools/calibre_edit.py plan|render|stills <edit.json> …` — the editor. An edit
  file lists cuts (retakes), shots/zooms, caption markup and cards; see the
  docstring at the top of the file for every key and the markup syntax.

## Per video (`projects/NN-name/`)
1. Download from Drive into `src/` — files over 10MB can't go through the Drive
   connector; use `curl -L "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`
   (the folder is shared by link).
2. Transcribe, compare against the script, find retakes/fluffs (look for
   repeated phrases and long gaps).
3. Write `youtube.json` and `reel-*.json`, `plan` them, render `--draft`,
   check frames, write `BREAKDOWN.md`, share stills for approval.
4. Render finals (without `--draft`) once approved.
