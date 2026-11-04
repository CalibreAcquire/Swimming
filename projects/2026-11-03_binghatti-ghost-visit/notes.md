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

## 3 Nov, 19:30: area-wide
Jake: 1,500 residents is fine. Don't tie it to Ghost; the footage can stand for the mix of Binghatti developments in Al Jaddaf. Reel 2 v3 ("The view, Binghatti, Al Jaddaf" / "10 Binghatti developments in Al Jaddaf") and reel 5 v2 (residences across the area: studio to 3 bed, ready now or handover by 2028, from AED 799,999 = Starfall and Wraith entry units, 22 Oct feed). The live feed lists 10 Al Jaddaf projects with stock on 22 Oct: Cullinan, Ghost, Ivory, Moonlight, Pinnacle, Spectre, Starfall, Starlight, Twilight, Wraith. Covers C v2 and E v2. Reel 1 (teaser, Ghost by name) went out tonight as it was.

## 3 Nov, 19:45: the walk-out ending
Jake: stitch the clip of him walking out from behind with the head-on one at the end. `end()` in build_series2.py: 0076 5.2–7.4 (from behind, through the lobby doors, no push so the cut stays clean) then 0080 10.0–16.8 (head-on, stepping out of the entrance and walking to camera), CTA from 1 s into the head-on shot. Other uses of 0076 swapped out so it doesn't repeat. Reels 2 to 7 re-rendered: 2 v4, 3 v3, 4 v3, 5 v3, 6 v2, 7 v2 (25 to 33 s with the outro), −14.0 to −14.4 LUFS, peaks −2.1 to −4.1 dBTP. Join checked on frames.

## 4 Nov: jitter and the walk-out
Jake: the videos looked jittery. Cause: listing_edit.py zoomed at the output size in whole pixels, so push-ins were still for two frames then jumped (43 of 74 frames static on reel 4's first shot). Now zoompan on a 3x frame: 0 static frames. Walk-out: behind shot 5.4–6.6 (cut as he reaches the doors), head-on 10.0–15.8 (a second shorter). Final files: reel2 v5, reel3 v4, reel4 v4, reel5 v4, reel6 v3, reel7 v3 (23 to 31 s with the outro), −14.0 to −14.4 LUFS, peaks −2.0 to −4.2 dBTP. Events updated.

## 4 Nov, late morning: the new footage
Jake added 12 4K clips (IMG_6712-6720, 6726, 6727; 6714 is 0.8 s, unused) and 15 HEIC photos (converted to work/*.jpg with pillow-heif): skyline and balcony views, living room, kitchen, corridor, lift lobby, the district from the street, ground-floor frontage, and empty shopfronts (6731-6736). Reels 2 to 7 rebuilt with them; shop lines now sit over the shopfronts. Final: reel2 v6, reel3 v5, reel4 v5, reel5 v5, reel6 v4, reel7 v4 (23 to 32 s), −14.0 to −14.4 LUFS, peaks −2.1 to −4.6 dBTP; every text frame checked. Events updated.

## 4 Nov: the investment case
Jake asked for real reasons to buy the offices or shops; figures from the Bayut/DLD summaries in Drive (publish/investment_case.md, with sample sizes). On screen: reel 3 adds Al Jaddaf shop rents +19% and the last 7 shops ~4% below what earlier buyers paid per sq ft (asking 3,687 vs sold 3,841); reel 4 adds 128 sold in seven weeks, Dubai office prices per sq ft +59%, two-thirds of Dubai office lettings under 1,000 sq ft; reel 6 is now commercial-only (Dubai offices +59%, sales +48%, JVC offices +34%, Al Jaddaf shop rents +19%, AED 173 per sq ft). No yields on screen (the income case is weak, 3-4% gross at Spectre). Small Al Jaddaf samples (offices 19 sales, shops 5) left off screen. reel3 v7, reel4 v7, reel6-commercial-numbers v1; cover H v2. Events updated with new captions.
