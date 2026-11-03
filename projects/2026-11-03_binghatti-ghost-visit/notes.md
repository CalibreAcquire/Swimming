# Dubai ghost visit teaser (3 Nov 2026)

Source: Drive › Binghatti – Investor Data › Binghatti ghost visit (5 iPhone clips, portrait, no speech; IMG_0079 is 0.2 s, unused).
Facts on screen from the Binghatti one-page summary (22 Oct 2026): six projects in Al Jaddaf and JVC. No prices (teaser holds them back).
Edit: `edl/build_teaser.py` → `edl/teaser.json`, rendered with `scripts/listing_edit.py`. Music: 744 House 02 (Brentwood used 770), bed −27 LUFS, room sound at −40.
QA (v2): −14.1 LUFS, 1080x1920 30 fps, 14.9 s + 4.6 s outro. Frames checked: text legible on sky and window; v2 moves the CTA above Jake's head (v1 sat on it).
Open: Binghatti's sign-off on co-branding is still outstanding (one-page summary); the BINGHATTI sign is visible on the tower at 3-5 s. No Binghatti name in the text or copy. Which building it is isn't stated in the files.

## 3 Nov, later: the reel set
Jake: Binghatti gave sign-off on co-branding; the building is Binghatti Ghost (Al Jaddaf; in the investor data: completed, developer handover 30 Apr 2026, 22 units available on 22 Oct, cheapest AED 1,162,500 for 436 sq ft; ready resales at Ghost were registered in October per the market report). He wants several videos posting from today.
Built 4 reels (`edl/build_reels.py`): 1 teaser (744), 2 the view (609), 3 walkthrough (770), 4 the numbers (175). Each opens on a different shot, has its own track and its own cover (A, C, D, E).
QA: all −14.1 to −14.4 LUFS. Reel 4 v1 peaked at −0.9 dBTP (track 175); v3 re-limits the audio only (video copied): −14.4 LUFS, −2.2 dBTP. Frames checked at every text line; CTA sits above Jake's head.
Open: reel 4's price is from 22 Oct, so the event says to check it before posting. All four use the same 22 s of footage; more clips (other rooms, amenities, the view at dusk) would make the next batch less repetitive.

## 3 Nov, later still: the information series
Jake: include the residential and commercial options; start with teasers, then more information each video. Reels 3 to 6 (`edl/build_series.py`):
- 3 residences (Ghost): studio to 3 bed (2026 DLD extract shows Ghost sales of studios, 1, 2 and 3 beds, freehold, ready resales from October), studios from AED 1,162,500 (live feed 22 Oct).
- 4 commercial (Spectre): no Ghost commercial units are in the 11 Oct commercial availability list, so the commercial reel uses Spectre (one-page summary: offices 705 to 4,018 sq ft from AED 1,864,999; retail from AED 8,922,999; handover 31 Dec 2028). Visuals: three renders from Binghatti's Spectre office brochure (pp. 2, 3 and the right half of 4), supplied for the campaign; no watermark.
- 5 costs: 4% DLD, AED 4,200 + about AED 620, 5% VAT on commercial (one-page summary and Buyer Costs tab).
- 6 Al Jaddaf (market report, 12 months to late Oct): apartment sales more than tripled, price per sq ft up 22%, studio rent AED 48,723 average.
Script changes: `listing_edit.py` takes stills (png/jpg loop for the shot) and frames a landscape source on its focus point (the first crop was centred, so renders lost the towers; v1 and v2 of reel 4 had it). QA: all −14.0 to −14.4 LUFS, peaks −1.6 to −2.1 dBTP (reel 6 re-limited, track 175 again). Every text frame checked.

## 3 Nov, evening: second pass with all the footage
I had only listed the first page of the Drive folder (5 clips); the folder holds 25 clips and 5 photos (each uploaded twice). All downloaded to raw/ (one copy each): entrance, lobby, concierge, lifts, kitchen, living, bedrooms, bathrooms, gardens, neighbouring towers.
Jake: emphasis on the shops and offices as an investment; include towers, flats, residents, shops directly below. Spectre Project Facts: 4B + G + 3P + 26 floors, Tower A 508 apartments, Tower B 204 apartments + 235 offices, 19 ground-floor shops (712 apartments). Residents: our estimate 1,472 (1.5/2/3/4 per studio/1/2/3 bed), shown as "around 1,500" and flagged in the reminder. The live feed says 230 offices (128 sold, 102 left), so the offices reel says "128 sold since the September launch" rather than a total.
Rebuilt reels 2 to 7 (`edl/build_series2.py`). Commercial figures sit over Spectre renders or communal areas, never over an apartment (v1 of reels 3 and 4 had the office price over a bedroom and the shop count over the Ghost entrance). Every reel ends on Jake walking out of the Ghost entrance with the CTA.
QA: −14.0 to −14.4 LUFS, peaks −1.8 to −4.1 dBTP (all re-limited). Every text frame checked.
