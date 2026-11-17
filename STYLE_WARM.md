> **The warm style.** Jake chose it on 17 Nov 2026 ("use it for my next video"), from a screen
> recording of an Instagram ad he saved to Drive (00 Inbox – To File, `ScreenRecording_11-17-2026
> 08-14-55_1.mp4`). We take the look only, never the content. Set `"look": "warm"` in the EDL
> (`scripts/calibre_edit.py`). Everything not covered here (audio, music, outros, links, writing
> style, content rules) stays as in `VIDEO_STYLE.md` and `CLAUDE.md`.

# Calibre Acquire: warm style

Calm, cinematic and premium. Warm low light on the talking head; graphics that look like
physical objects on a dark desk; plain one-line captions. Restraint over effects.

## What the reference does (measured)
- 2:09 portrait ad. 41 shots, a visual change every 2.5 s (median), 3.2 s on average.
- About half the running time is full-screen graphics, half talking head. They alternate
  roughly every sentence.
- Speech is fast and tight: about 250 words a minute, almost no pauses (longest 0.9 s).
- Talking head: one locked-off framing, mostly static. Occasional cut between a medium and a
  slightly tighter shot. No zoom pops, no whooshes, no transitions.
- Loud and dense audio (-12 LUFS, LRA 2.6). We stay at -14 LUFS.

## Picture
- **Grade:** `WARM_GRADE` in `calibre_edit.py`: office white balance, then a warm 4400 K shift,
  softer contrast, slightly lower brightness, gentle vignette. On location, swap the first
  filter for that location's white balance (EDL `grade`).
- **Filming (for new shoots, not Fabian House's Thursday re-record, which must match part 1):**
  darker room; warm practical lights in the background (lamps, candles, warm bulbs) out of
  focus; soft warm key light from one side (about 3200-4000 K); shallow depth of field
  (f/1.8-2.8), Jake well away from the wall; neutral knit or plain clothing in cream, beige,
  brown or black. The grade warms the image, but the candlelit depth comes from the set.
- **Framing:** one main framing; cut to a slightly tighter one now and then. EDL
  `zoom: {"wide": 1.0, "tight": 1.12, "every": 6.0}` and no `pop` shots.
- **Pace:** `max_gap` 0.2 on reels and 0.25 on YouTube.

## Captions
- One line, 2-4 words a phrase, sentence case, DM Sans SemiBold, white, soft blurred
  shadow, in the lower middle of the frame (over the chest). The whole phrase appears at
  once; no word-by-word build, no yellow, no italics, no caps.
- Write the captions markup plainly: no `[KEY]` or `*italic*` (the renderer ignores them and
  keeps your case). Use `|` to break phrases.
- Hidden while a card is on screen.

## Hook title
- `title_card` renders as bold black DM Sans on white boxes, one box per line, for the
  first 1.5-2.5 s (like a thumbnail on the first frame). Short: 3-7 words.

## Graphics (full-screen cards)
- Near-black background (#0E0C0A) with a faint grid.
- Small spaced label in caps, warm grey (`~LABEL~`). Headline in DM Sans Medium, cream
  #EFE6D8 (`*headline*`). Big figures in DM Sans SemiBold (`[£1,250,000]`) **count up**
  over 0.75 s and land on the exact figure. Supporting line in plain text.
- `"panel": true`: the text sits on a cream paper panel (#E5D7C0) with a soft shadow and
  dark ink. Use it for a property, a deal or a document.
- Lines fade and rise in one after another. Monogram small at the bottom.
- Use cards far more often than in the house style: aim for a graphic every second or third
  sentence, each one showing the single fact being said (a figure, a date, a name, a
  comparison, a short list).
- Figures must still match the script exactly. No yellow anywhere.
- Ideas from the reference to build as needed (one at a time, by hand or as new card types):
  a timeline slider for "a few years ago", a see-saw for a trade-off, a two-line chart
  ("you" vs the market), toggles for a yes/no question, polaroid photos of people or
  buildings, an envelope or folder for a document, a receipt for a cost.

## Brand
- This look adds warm cream and brown to black, white and grey for this style (Jake's
  choice, 17 Nov 2026). Fonts: DM Sans for captions and cards; Montserrat and Cormorant are
  not used in this look.
- Small "C." monogram watermark as before. Outros as before.

## Test
`projects/2026-11-23_letters/work/warm_test/` (not in git): Reel A rebuilt in this look
(`test9.json`), first render 17 Nov.
