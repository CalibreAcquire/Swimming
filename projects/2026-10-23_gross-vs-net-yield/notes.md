# Gross yield vs net yield

Raw (Drive file): `C0372S03.MP4` talking head, 10:59, 1280×720 25fps, office. No script supplied;
edited from the phrase-level transcript (`transcript/retakes.txt`). Delivered on 23 Oct while Jake
was away ("continue without my input"): finals rendered without draft review.

Type: educational. Structure: hook (6.5% advertised, 4.1% earned) → self-intro (£30m line) → pain
point → proof (Fabian House, £4.775m, matches the YouTube Content Plan) → promise → calculator CTA →
definitions → five costs → leasehold flat vs illustrative freehold → two traps (Brompton as the
bills example) → what to ask for → finance → summary → share/subscribe → register CTA.

## Take selection (edl/youtube.json, window 94.9–649.6)
| Block | Take used | Cut | Reason |
|---|---|---|---|
| Opening | second hook take (94.9) | 0–94.9 | first take started with chatter, then "try that one more time" |
| "On every sale like that…" | second (150.3) | 145.15–150.25 | first trailed off |
| Voids | last ("…no rent coming in") | 222.75–229.8 | false start + repeat |
| Flat costs | last | 281.15–287.75 | misread figures ("£19.50", "£13.50"), repeated void line |
| Freehold example | third | 309.5–313.35 | "Here's an illustrative, here's an illustrative…" |
| Freehold costs | last | 333.45–336.95, 339.8–345.1 | repeated repairs reserve and management lines |
| Trap 2 / Brompton | last clean takes | 390.8–449.0, 460.6–492.5, 500.0–527.7 | several restarts, "I'm not doing it anymore" |
| Finance | second | 565.2–572.8 | repeated line |
| "Ask for the costs…" | second | 608.7–614.5 | first said "cost" and trailed off |

Whisper's "$" for £ corrected in captions. Figures checked: flat 16,250 − 2,500 − 300 − 1,950 −
1,354 = 10,146 → 4.06% (4.1%); freehold 60,000 − 15,250 = 44,750 → 5.59% (5.6%); Brompton 9.03% /
7.84% / £36,380 / 10.7% from the brochure.

## Graphics
15 cards (black/white, no yellow): title, calculators (URL + Comment SEND), definitions, five costs,
flat, flat after costs, freehold, freehold after costs, Trap 1, Trap 2, Brompton (9.03% / 7.84%),
ask-for list, Brompton finance (illustrative), summary line, register URL. B-roll: Brompton
exterior (upper floors) over "a building for sale in Brompton".

## Audio and music
Preset `full`. YouTube music: "Moon Walk" (609, from 40 s); reels "House 02" (744).

## Reels (9:16)
1. A 6.5% yield that earns 4.1% (0:20)
2. £250,000 flat at 6.5%: the real numbers (0:30)
3. Two traps that make yields look better (0:31)
4. Before you offer, ask for these (0:22)
None contain the £30m line.

monday.com: Content & Filming (Master) item 3305366116.

## Fixes after final QA (23 Oct, before hand-back)
- Cut points that sat inside words moved to the word end (they dropped "wifi", "rooms", "you",
  "repair", "listing" and clipped "per cent").
- Two retakes whisper had merged into one stretched word, found by re-transcribing with large-v3:
  "a freehold with a shop and three flats, priced at £800,000" (first take 315.45–320.5 cut) and
  "If you found this useful…" (first take 624.45–628.85 cut). Transcript patched with large-v3 word
  times there (backup in work/).
- Renderer now measures pauses against this recording's noise floor (`silence_db: auto`), so long
  pauses are tightened; YouTube about 5:26.
