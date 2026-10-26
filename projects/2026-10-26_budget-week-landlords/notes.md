# Budget week: what's already confirmed for landlords and what's rumour

Raw (Drive › YouTube › Filmed): `Budget.MP4`, 17:09, 1280×720 25fps, office (same room as the
stamp duty and gross/net videos). Script: `script/script.txt` (sent by Jake on 26 Oct; he didn't
say "It is what it is"). On the YouTube Content Plan as "Budget week: what's already confirmed for
landlords and what's rumour" (26 Oct). The Budget is on Wednesday 28 Oct, so this goes out before it.

Type: educational. Structure follows the script: hook → in this video → pain point → self-intro
(£30m line) → confirmed → calculator CTA → worked example → Section 24 → own story → limited company
→ ruled out → rumours → Bank of England → four checks → share/subscribe → register → valuation.

## Transcription
Whole-file whisper merged many retakes (one "phrase" ran 100 s). New `scripts/phrase_transcribe.py`
splits at pauses measured against the room's noise floor (−35.4 dB here) and transcribes each of
the 176 phrases with large-v3 (`transcript/phrases_large.json`, used by the EDL). Doubtful spots
re-checked with large-v3 on short clips.

## Take selection (edl/youtube.json, built by work/build_edl.py)
| Script block | Take used (source s) | Left out | Why |
|---|---|---|---|
| Hook | third, 82.8–91.2 | 0–82.8 | chatter, setting up, two earlier takes, a false start ("…his phone") and muttering |
| Already law | 91.6–99.6 | | says "last year, November" (accepted paraphrase) |
| In this video | second, 105.4 | 101.3–105.3 | false start |
| Decision made on a rumour | third, 148.2 | 142.6–148.1 | two false starts |
| Self-intro | second, 155.4 | 153.2–155.2 | false start ("the founder of…"); says "£30 million pound" |
| Let's start | 176.3 | 172.5–176.3 | false start and a non-speech burst |
| Property income tax | 183.8 | 181.3–183.4 | first "First, property income tax" |
| Good salary | third, 241.3 | 231.4–241.2 | two incomplete takes |
| Mansion tax | second, 282.9 | 271–282.8 | incomplete take ("And there's the…") |
| Calculators | 316.9–324.3 + 333.9–341.8 | 297.8–316.8, 324.3–333.8 | "Come on", noise, "Comments down below…" |
| £2,640 credit | second, 398.2 | 391.2–397.1 | first take said "£2,400" (wrong figure) |
| £9,960 / £360 | 412.8–419.9 | 404.7–412.8, 419.9–428.5 | "Okay", and "that's the number to worry about" (missing "not"), "nine hun… I got that wrong" |
| Section 24 | second, 444.0 | 442.2–443.9 | false start |
| Cost already there | second, 458.3 | 451.2–458.2 | said "that cost" |
| Brentwood flat | first, 464.3–478.4 | 478.4–493.8 | first take is clean ("£30,000 loss to get it out"); later takes "30…", "30 grand", and "It is…" (Jake didn't want "It is what it is") |
| Limited company | 499.4–509.6, 547.4–551.3, 555.3–560.8, 628.2–638.2 | 509.6–547.4, 551.3–555.3, 560.8–628.2 | retakes, swearing, Jake out of shot (567–628). Dividend clause cut, see below |
| Capital gains example | second, 712.4 | 702.9–712.4 | "…a two… Oh God, come on" |
| Still a rumour | second, 731.8 | 729.3–731.8 | false start |
| Wider tax rises | fourth, 762.7 | 746.8–762.6 | "tax changes", two incomplete takes |
| Recording before the Budget | second, 775.9 | 766.9–775.8 | earlier take |
| Bank of England | 794.75 | 784.9–794.7 | "3 point… Oh my God", "slow down" and muttering |
| Check 1 | third, 842.2 | 820.7–842.1 | "on the 8th first", "Oh my God come on" |
| October 2024 | second, 877.8 | 865.1–877.7 | earlier take and "mmm" |
| Making Tax Digital check | second, 906.9 | 902.9–906.8 | "the make in taps" |
| Not performing | second, 933.2 | 929.0–933.2 | earlier take |
| Register CTA | second, 977.5 | 961.3–977.5 | "…one week's notice. Oh God" |
| Ending | 1004.5–1016.6 | 1016.6–1029 | the "Everything will remain confidential" line wasn't said |

### Content decisions (for Jake)
- **Dividend tax line cut.** Every take says "dividend tax rates went **up to** 2%" (script: "went up
  **by** 2%"). "Up to 2%" is wrong on screen, so the clause is cut cleanly: "…has its own tax, and
  moving properties you already own into a company can trigger stamp duty and capital gains tax."
- "It is what it is" isn't in the video.
- The final line ("Everything will remain confidential…") wasn't said, so the video ends on the
  instant valuation URL.

## Graphics
39 full-screen cards (black/white, no yellow), following each point: already law, in this video,
Part 1/2/3, the new tax rates, already law (Nov 2025 / March 2026), mortgage interest credit,
personal allowance, Making Tax Digital, mansion tax, calculators (Comment SEND), the worked example
(setup, today, from April 2027, £360, 55%), Section 24, Brentwood flat, limited company, accountant,
stamp duty ruled out, CGT rates, reported not announced, the £200,000 gain, rumours, Bank of England
rate, inflation, next decision, the four checks and each check, Holloway Road, closing line,
register and instant valuation URLs. All figures as in the script.

## Audio, colour, music
Preset `full`. Grade B (Jake's choice for this office). Music "Moon Walk" (609) on YouTube, "House 02"
(744) on reels. Pauses measured against the room's noise floor; the renderer now never trims
speech-level sound as a breath (it had clipped the end of "2027" and would have dropped "Fourth.").

## Reels (9:16), none with the £30m line
1. The biggest change is already law (0:33): hook + the new rates. Pre-Budget.
2. The real rate (1:02): the worked example, £9,600 → £9,960, 55%. Evergreen, built to be saved.
3. Exchange, not completion (0:32): pre-Budget.
4. Capital gains tax at 40%? (0:32): pre-Budget.
5. Making Tax Digital from £30,000 (0:20): evergreen.
