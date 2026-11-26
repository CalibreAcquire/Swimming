# Brand reel rebuild (26 Nov 2026)

Jake's request: re-create his boosted reel (172K views; screen recording in Drive Inbox) as a more polished,
professional video. Original: music only, four drone shots of past deals with white outlines and labels
(Shop & Uppers Loughton, Mixed-use Freehold Whitechapel, Development Bow, Whitechapel skyline), then kinetic text
"stop using rightmove as a property investor / start investing with purpose / mixed-use, unbroken residential,
commercial, always freehold / secure off market property", Calibre Acquire wordmark. 17 s.

Footage (found via Mark Steele's emails and Jake's Drive; addresses from Jake):
- Loughton = 110 High Road; Whitechapel = 339-343 Commercial Road; Bow = 611-613 Roman Road.
- `raw/Pinned Instagram Post.mp4` (Capcut folder, a 1080p YouTube video): Loughton 172-181 s, Whitechapel 182-188 s,
  street aerial 189-192 s (Mark's drone, outlines drawn in).
- `raw/611-613 Roman Road.mp4`: Bow 5-8 s (outline), skyline 9-11 s.
- Mark's own folders (High Road,110; Commercial Road,343; Lighthouse Apartments 3@339) show no files to this account.

Changes for the rules: "Stop using Rightmove" -> "Stop scrolling the portals" (no portal names in public content).
Look: warm style (DM Sans, dark grid cards, cream headlines, warm grade); the two landscape drone shots are framed
panels on the dark grid (their outlines are too wide for a 9:16 crop). Cuts on the beat of House 02 (744).
End: wordmark + calibreacquire.co.uk/register, then Jake's outro.

`edl/build_reel.py` -> `edl/reel.json`, rendered with `scripts/listing_edit.py` (new: "fit" panels).
v1: 21.9 s + outro, 1080x1920 30 fps, -14.0 LUFS, -1.0 dBTP. Frames checked per shot.

## Drone footage source (26 Nov)
The drone videos (with and without outlines) were by Mode Photo, Loughton (Skye Don, skye@modephoto.co.uk), sent
9 Feb 2026 and replaced 12 Feb (white outlines, Jake's request) via Dropbox. That link now shows "File Deleted".
Jake's brief to them: 339-341 Commercial Road = three terraced buildings; IG10 4HJ extends to the back incl. five garages.
`611-613 Roman Road.mp4` (12 Feb) is probably theirs. Draft re-request to Skye saved in Jake's Outlook Drafts (not sent).
When the originals arrive: replace the framed 1080p crops of Loughton and Whitechapel with full-resolution shots.
