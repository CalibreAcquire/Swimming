# 10 & 12 High Street, Brompton (listing)

Raw (Drive folder "10-12 High Street, Brompton"): `10-12 High Street - New Listing.mp4` Jake to
camera, 3:51, 1280×720 25fps (new room, desk mic in shot but the audio is the camera mic);
Kim's photos (`raw/photos/`: exterior, shop1 = No. 10 hair studio, shop2 = No. 12 nails and spa,
10a, 12a), 6656 px. Brochure `script/10-12-High-Street-Brochure.pdf` is the fact source.
Kim's photo folder wasn't link-shared at first; Jake fixed it on 23 Oct.

Type: listing. Structure: hook (income, price) → location → building → numbers → lease events →
deal status → register CTA. No self-intro, calculator CTA or share/subscribe (none filmed).

## Edit
Window 23.05–219.3 (start after Jake sits down and adjusts the camera). Cut 166.45–187.8: false
start "The shop leases have tenant…" and Jake adjusting the camera. Long pause before "3,829"
removed by gap tightening. Jake made all decisions in his absence: finals rendered straight away.

## Figures checked against the brochure
£1,000,000 OIRO · £90,320 pa · 10 lettings · 2 shops at £10,000 pa on 10-year leases · HMO rooms
3 + 4, average £680 pcm bills included · flat £13,200 pa · 3,829 sq ft · 9.03% gross (Jake says
9%) · bills £995 pcm · £78,380 after bills, 7.84% (Jake says 7.8%) · 78% / 22% · SDLT £39,500
non-residential · 30% deposit, 6% IO: £36,380 pa, 10.7% · breaks 12/01/2027 and 31/07/2028.
Cards use the brochure's exact figures; captions follow what Jake says. Whisper heard "$36,380":
captions and SRT use £.

## Content rules
No "off-market". "It's available now before the full launch across all major property
platforms" kept (matches "available before full public launch"). Deal status card: "Now
available for sale, before full public launch". No data sources named.

## Photos
Avoided: 10a/DSC00496 and DSC00511 (tenants' clothes and belongings), shop2/DSC00624 (lash
business sign), shop2/DSC00652 (nail bar window lettering). Exterior framed on the upper floors
where possible; thumbnail C uses the upper part only (shop signs and phone number cropped).

## Reels (9:16)
1. The deal (0:20): hook, price, address, adjoining buildings.
2. The building (0:27): shops, HMOs, flat, with the photos.
3. The numbers (0:32): passing rent, net yield, returns (income split and SDLT cut).

monday.com: Content & Filming (Master) item 3305252775.

## Finals (23 Oct, rendered while Jake was away; drafts not reviewed by him)
- Exports v1: YouTube 2:42, reels 0:20 / 0:27 / 0:32, story, SRT (38 subtitles).
- QA: all four −14.0/−14.1 LUFS, −1.2 to −1.5 dBTP, music 13.8–17.1 dB under voice, 0 caption
  overlaps. Black-frame scan: the only black runs are the five black cards (10.3, 78.7, 122.0,
  148.0, 154.9 s). SRT figures checked: £90,320, £78,380, £39,500, £36,380 (whisper's "$" fixed),
  register URL intact.

## v2 reels (23 Oct)
Final QA on the next two videos found cut points sitting inside a word: the renderer judges a
word by its midpoint, so the word was dropped and clipped. Here: Reel 2 ended on "£13,200 a" (window
end 93.5 → 93.9, keeps "year"), Reel 3 lost "yield" (cut 130.0 → 130.45) and "in" at the end
(163.1). Re-rendered as `_reel2-the-building_v2.mp4` and `_reel3-the-numbers_v2.mp4`; Outlook
events for 31 Oct and 2 Nov now point at v2. YouTube master and Reel 1 unaffected.
calibre_edit.py now warns when a window end or cut start falls inside a word.

## v2 YouTube / v2-v3 reels (23 Oct, Jake's notes)
- 1:08 "I repeat myself": "In total, it's 3,829 square feet" was said three times; whisper had merged
  the first two into one 10-second word, so the retake check missed it. First two takes cut
  (93.9–103.4), transcript patched with re-transcribed word times (backup in work/).
- Reel 3 0:19 "pause too long": 1.1 s of near-silence before "With a 30% deposit". The renderer's
  fixed −38 dB silence threshold was below this room's noise floor (about −35 dB), so pauses weren't
  seen. Now `silence_db: auto` (threshold from the recording, −31.9 dB here). Whisper had also
  mistimed "£36,380", and the old gap rule dropped "eighty"; gaps now count as pauses only where the
  audio is quiet.
- Exports: `_youtube_v2.mp4` (2:26) + `.srt`, `_reel1-the-deal_v2.mp4` (0:19),
  `_reel2-the-building_v3.mp4` (0:25), `_reel3-the-numbers_v3.mp4` (0:32). QA: −14.0/−14.1 LUFS,
  −1.3/−1.5 dBTP, 0 caption overlaps; "In total" once; finance sentence complete (checked by
  transcribing the render section). Outlook events (25, 31 Oct, 2 Nov) point at these files.
- 1:49 (Jake): "which is a 10.7% return" said twice; whisper left the first out of the transcript.
  Cut 155.62–159.2 in the YouTube and Reel 3. Plan now warns on kept sound with no words.
  Exports: `_youtube_v3.mp4` (2:23) + `.srt`, `_reel3-the-numbers_v4.mp4` (0:30); Reel 1 v2 and
  Reel 2 v3 unchanged. QA −14.0 LUFS, −1.3/−1.5 dBTP, 0 overlaps.

## v4 (25 Oct, Jake: "looks dull")
- Lighting: Jake picked grade B from an A/B/C test (brighter mid-tones, warmer skin, blacks kept).
- Property photos over most of the building description: 21 in the YouTube (was 7), push/pull/pan
  moves, soft bottom shade (`broll_shade: 0.45`) so captions read on white rooms. Room photos
  matched to the house number being described. Zoom rhythm every 4 s.
- Exports: `_youtube_v4.mp4` (2:23) + `.srt`, `_reel1-the-deal_v3.mp4`, `_reel2-the-building_v4.mp4`,
  `_reel3-the-numbers_v5.mp4`. QA −14.0/−14.1 LUFS, −1.3 dBTP, 0 overlaps; black runs are the cards.
- Jake posting it on the evening of 25 Oct (the 16:10 slot passed during the re-edit).
