# Calibre Acquire video editing

This repo is the video editing pipeline for Calibre Acquire's YouTube videos and
Instagram reels (property content).

- `VIDEO_STYLE.md` — the house editing style. Follow it for every edit and
  update it when the user refines a preference.
- `brand/logos/` — logo files. `brand/fonts/` — brand fonts (install to
  `~/.fonts` and run `fc-cache -f` before rendering text).
- Raw footage and example videos arrive via Google Drive. Never commit video
  files to the repo.
- Workflow: analyse footage → share a breakdown and still frames for approval →
  render the 16:9 YouTube edit and the 9:16 reel clips.
