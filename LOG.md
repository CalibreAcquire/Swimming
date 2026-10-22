> **Superseded** by `CLAUDE.md` (22 Oct 2026) and `brand/learnings.md`. Kept for history.

# Work log

Everything done for Jake (Calibre Acquire), newest first. Read this at the start of
every session; add to it at the end of every piece of work. Preferences that apply
to all future work also go in `VIDEO_STYLE.md`.

---

## 2026-10-22 — Project 01: "How a valuation actually gets calculated"

**Delivered:** YouTube edit (3:03, 1080p) + 4 reels (9:16), upload copy, thumbnail,
subtitles. Files in `projects/01-valuation/` (videos themselves are not in git —
Jake has the finals; re-render with `tools/calibre_edit.py render <edit.json>`).

**Status:** Jake uploading to YouTube (channel "Jake Benson"), at the Video
elements step on 22 Oct. End screen suggestions given (see below).

### What Jake asked for and decided (in order)
1. Wants a professional editor for YouTube + Instagram reels; property content.
2. Style: fast cuts; captions in varied formats, key words `#FFDE59` and/or italic,
   standard words white; cut-aways to black brand cards (white text) and white
   cards (black text); zoom in/out and mini zooms; little B-roll, only relevant,
   nothing heavily animated; property footage shown while talking about it.
3. Fonts: Garamond (we use EB Garamond), Cormorant Garamond, Montserrat. Logos:
   "C." monogram and CALIBRE ACQUIRE wordmark, black and white — use lightly.
4. Deliverables per video: 16:9 YouTube + several 9:16 reels (hooks/snippets).
   Music: Claude chooses each time. Raw footage 4–8 min (up to 10), on Drive.
5. Review flow: breakdown + stills/drafts before final render. Agreed.
6. Look: luxurious, engaging, authentic, professional.
7. Reference video (jun_yuh ad) analysed → stacked word-by-word captions adopted;
   YouTube pace a bit slower than reels. Liked the Calibre version of the stack.
8. Draft 1 feedback: false start "I'm Jake, found—" left in → caught by building
   `tools/find_retakes.py` (phrase-level retake detector).
9. "if it were **let**" is correct (transcripts mishear it as "there").
10. **No yellow on cards** — white cards with yellow looked cheap. Cards now: small
    spaced label, hairline, Cormorant italic headline, black/white only.
11. Audio: wanted better quality → built `tools/voice.py`. Compared A/B/C, then
    asked for deeper and fuller → **preset `deep` chosen (option D)**, no pitch shift.
12. Music added: YouTube "Autofahren" (Mixkit 770), reels "House 02" (Mixkit 744).
13. Big breath at 0:38 → editor now trims breaths before/after phrases.
14. Vercel "Preview deployment failed" emails were from the `swimming` repo's
    Vercel project → `vercel.json` disables deploys of the `video-editor` branch.
15. Approved all five drafts → finals rendered and sent.
16. Copy: **no emojis** (look AI-written); also dropped long dashes and slogans.
    Links: calibreacquire.co.uk, /investment-calculators, /register. Instagram:
    @calibreacquire (company), @jake_s_benson (Jake).
17. Thumbnail: two versions (B with yellow "PRICE." recommended, A monochrome).
18. Asked Claude to remember everything (this file) and to suggest end screen videos.

### End screen suggestion (Project 01)
Other topics in Jake's Drive "YouTube" folder (published status unknown):
"Four questions to ask before you make an offer", "611 Roman Road – Development
Breakdown", "Leasehold vs freehold", "479 Hornsey Road – New Listing", "Sold
offices for Craig". Recommended: Four questions (main), 611 Roman Road (second),
Subscribe button. Start at 2:50, elements on the right-hand side.

### Technical notes
- Raw footage is 720p 25fps from a camera mic; suggested 4K + a lav/wireless mic.
- Drive files > 10 MB: download via drive.usercontent.google.com (folder shared by link;
  network allowlist includes drive.usercontent.google.com and drive.google.com).
- Drive connector can't upload large files; send finals via chat.
- Whole-file dereverb OOM'd (14 GB) → now 20 s blocks.
