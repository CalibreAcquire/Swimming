# Calibre Acquire — Video Style Guide

The editing rules applied to every YouTube video and Instagram reel. Update this
file as the style is refined.

## Look and feel
Every video should feel **luxurious, engaging, authentic and professional**.

- **Luxurious** — restrained, elegant typography; generous spacing on cards;
  clean colour grade; refined music. No cheap effects, stickers or emoji.
- **Engaging** — fast cuts, varied captions, zooms and text cards keep momentum.
- **Authentic** — real footage and real properties; keep the speaker's natural
  delivery; B-roll only when relevant.
- **Professional** — consistent brand fonts, colours and logo use; clean audio;
  smooth eased zooms; hard cuts over flashy transitions.

## Deliverables per raw video
- **YouTube** — full edit, 16:9 (1920×1080).
- **Reels** — several 9:16 (1080×1920) clips cut from the same footage:
  hooks and standalone snippets of the strongest moments.
- Raw footage is typically 4–8 minutes (up to 10).

## Pacing
- Fast cuts throughout to keep the audience engaged.
- Remove dead air, pauses, ums/ahs and retakes. Target: no gap longer than
  ~0.3s between words (reels); slightly more breathing room on YouTube.
- Something changes on screen roughly every 2–3s on reels (cut, zoom, card,
  footage) and every 3–5s on YouTube.

## Script structure (reels)
Hook (first 3–5s) → problem → solution → proof (numbers) → credibility → CTA.
Each new section gets a fresh visual: a card, property footage or new framing.

## Typography
Fonts live in `brand/fonts/` (all SIL Open Font License).

| Font               | Role                                                 |
|--------------------|------------------------------------------------------|
| Montserrat         | Standard caption and card text — clean, legible      |
| Cormorant Garamond | Key words and card headlines — elegant serif, italic |
| EB Garamond        | Alternate serif (open-source Garamond)               |

## On-screen captions
- Captions shown over the talking footage.
- Standard words: white (`#FFFFFF`).
- Key words: `#FFDE59` (yellow) and/or *italic*.
- Vary the caption format through the video so it doesn't feel static.
- **Stacked word-by-word captions** (main reel style): 1–3 words on screen,
  built up in tiers in the lower-middle of the frame:
  - connective words — Cormorant Garamond *italic*, white
  - supporting words — Montserrat ExtraBold, white
  - the key word — Montserrat Black CAPS, `#FFDE59`, large
- Numbers, prices and names are always key words ("£180K", "40% BELOW").
- **CTA switch**: for the final call to action, change to sentence chunks in
  black boxes, so it reads as "this is the ask".
- See `reference/example-01-analysis.md` for the reference this came from.

## Full-screen text cards
Cut away from the talking footage to a full-screen card for emphasis.

| Card  | Background | Standard text | Emphasis options |
|-------|------------|---------------|------------------|
| Brand | Black      | White         | Bold, italic     |
| Light | White      | Black         | Bold, italic     |

The black card is the Calibre Acquire brand look. **No yellow on cards** — it
looks cheap on white; `#FFDE59` is reserved for key words in captions over footage.

Card typography: a small spaced-out label in caps (Montserrat SemiBold), a fine
hairline under it, then the headline in Cormorant Garamond italic. Supporting
lines in Montserrat Medium. Plenty of empty space; small monogram at the bottom.

## Logos
Files in `brand/logos/` (transparent PNGs; supplied originals in `originals/`).

| File                  | Use                                         |
|-----------------------|---------------------------------------------|
| `monogram-white.png`  | Small watermark on footage; black cards     |
| `monogram-black.png`  | White cards                                 |
| `wordmark-white.png`  | Black intro/outro card                      |
| `wordmark-black.png`  | White intro/outro card                      |

Keep logo use light — subtle watermark and occasional card use, never dominant.

## Zooms
- Zoom in, zoom out and mini zooms (small punch-ins) on the talking footage.

## B-roll
- Use sparingly, and only when it's relevant to what's being said.
- No heavily animated B-roll. Keep it clean and real.

## Property footage
- When a specific property is discussed, show its footage while it's being
  talked about, especially for specific details of that property.

## Audio
- Voice chain (`tools/voice.py`): high-pass, light dereverb, EQ (less boxiness,
  more presence and air), de-essing, compression, -14 LUFS.
- Best results start at the shoot: a lavalier or shotgun mic close to the
  speaker beats any processing of a camera mic across the room.

## Music
- Chosen per video from `music/library.json` (Mixkit free licence: commercial
  use, no attribution). Prefer tracks with no vocals, little energy in the
  300 Hz–3.5 kHz speech band and steady energy (no big drops or builds).
- Defaults: YouTube — "Autofahren" (luxury deep house); reels — "House 02"
  (elegant, steady deep house).
- Level: bed at −30 LUFS on YouTube, −27 on reels (voice is −14), dipping a few
  dB under speech; fade in at the start, fade out over the last few seconds.
- Voice preset: `deep` (deeper, fuller tone) — chosen by the user.

## Links and handles
- Website: https://www.calibreacquire.co.uk
- Free deal calculators: https://www.calibreacquire.co.uk/investment-calculators
- Off-market access / register: https://www.calibreacquire.co.uk/register
- Instagram: @calibreacquire (company), @jake_s_benson (Jake)

## Writing style (titles, descriptions, captions)
- **No emojis.** They make copy look AI-written.
- No long dashes (—) and no neat three-part slogans ("Same X. Different Y.
  Different Z."). Use commas and full stops.
- Plain, measured, first person ("I", "we"). Reuse Jake's own phrasing from the
  video wherever possible; it's how he actually talks.
- UK English (£, "let", "HMO"). Keep hashtags to the end, 6–8 on Instagram.

## Process
- Take time over each video. Quality beats speed.
- Before rendering, share a breakdown (planned cuts, captions, cards, B-roll)
  plus still frames for approval.
