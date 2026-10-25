# Stamp duty on mixed-use

Raw (Drive file): `C0373S03.MP4` talking head, 7:49, 1280×720 25fps, office. No script supplied;
edited from the phrase-level transcript. On the YouTube Content Plan as "Mixed-use and stamp duty:
how one shop changes the bill" (publish 27 Oct). Delivered on 23 Oct while Jake was away: finals
rendered without draft review.

Type: educational. Structure: hook (£123,750 vs £49,500) → self-intro (£30m line) → pain point →
proof (339-343 Commercial Road) → promise → calculator CTA → what counts as mixed-use → rates →
two live examples (Brompton, Hornsey Road) → genuine commercial → six-dwelling route (separate
video) → full cost to buy → empty shop risk → when it's worth it → share/subscribe → register CTA.

## Take selection (edl/youtube.json, window 31.75–455.8)
| Block | Take used | Cut | Reason |
|---|---|---|---|
| Opening | 31.75 | 0–31.75 | sound check chatter |
| "So is a unit…" | second (231.6) | 228.45–235.2 | first trailed off |
| Full cost example | last ("So take the 1.2 million as an example") | 292.3–316.85 | first take said "plus 1,200", then "do that bit again" |
| Empty shop | second | 366.2–376.6 | "usually after… wait, no" |
| Summary | last | 411.2–419.6 | "commercial tenon. A commercial, so…" restart |

## Figures (SDLT checked against the rates Jake reads, which match the current bands)
- £1.2m residential with 5% surcharge: 2,500 + 33,750 + 27,500 + 60,000 = £123,750. Non-residential: 2,000 + 47,500 = £49,500. Difference £74,250.
- Brompton £1m: £93,750 vs £39,500 (brochure £39,500). Hornsey Road £1.3m: £138,750 vs £54,500.
- Cash in: 300,000 + 123,750 = £423,750; 360,000 + 49,500 = £409,500; gap £14,250 ("closer to 14,000").
- "339 to 343 Commercial Road… sold at £3.65 million": Property (Master) shows £3,600,000. Jake
  (23 Oct): keep as spoken. Captions only, no card.
- Hornsey Road "under offer" is true now; may be out of date later (posting 27 Oct keeps it current).

## Graphics
12 cards: £74,250 hook, title, calculators (URL + Comment SEND), mixed-use definition, residential
rates, non-residential rates (both "at the time of filming"), Brompton, Hornsey Road, genuine
commercial list, cash-in comparison, deciding factor, register URL. B-roll: Brompton exterior.

## Audio and music
Preset `full`. YouTube music: "Autofahren" (770, from 200 s); reels "House 02" (744).

## Reels (9:16)
1. One commercial unit: £74,250 less stamp duty (0:27)
2. Mixed-use stamp duty: what counts as commercial (0:27)
3. The stamp duty saving isn't the whole story (0:39)
None contain the £30m line. Reel events carry a Budget check (rates as at filming).

monday.com: Content & Filming (Master) item 3305374498.

## Fixes after final QA (23 Oct, before hand-back)
- Opening stumble hidden in a stretched word: "On a… what… on a £1.2 million". Now "On" +
  cut 32.47–35.15 + "a £1.2 million purchase".
- Hidden retake: "It makes less sense when the commercial unit is the weakest part" said twice;
  first take 401.3–405.55 cut (large-v3 word times patched in, backup in work/).
- Cut points inside words moved ("under", "it", "deposit", "fit", "clear").
- Pauses measured against the noise floor (`silence_db: auto`); YouTube about 5:25.

## Finals QA (23 Oct)
Exports v1: YouTube 5:20, reels 0:23 / 0:26 / 0:37, SRT (90 subtitles), story.
All four −14.0/−14.1 LUFS, −1.3 to −1.5 dBTP, music 12.6–17.3 dB under voice, 0 caption overlaps.
Frames at all 66 YouTube cuts: no black or flash frames. Opening now "On a £1.2 million purchase".
Dropped-sound spans checked with large-v3 and levels: all breaths. Repeat check: only the rates
lists and parallel phrases.

## v2 (25 Oct)
Lighting grade B (Jake's choice on the listing test) on all four. Exports `_youtube_v2.mp4` + `.srt` (text unchanged), reels `_v2`. QA −14.0/−14.1 LUFS, −1.3 to −1.5 dBTP, 0 overlaps. Outlook events point at v2.
