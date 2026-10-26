# Learnings: Jake's corrections and preferences

Read at the start of every job. Newest at the bottom of each section. Where this
file and CLAUDE.md disagree, ask Jake once, then record the answer here.

## Copy (titles, descriptions, captions)
- The "transacted over £Xm" line: Jake says £80m in some videos and £30m in others. Use whatever
  the video says. YouTube only (video, description), never on Instagram. (22 Oct 2026)
- No emojis anywhere: they make copy look AI-written. (22 Oct 2026)
- No long dashes (—) and no neat three-part slogans ("Same X. Different Y. Different Z.").
  Use commas and full stops. (22 Oct 2026)
- Reuse Jake's own phrasing from the video wherever possible. (22 Oct 2026)
- Instagram: @calibreacquire (company), @jake_s_benson (Jake). Website calibreacquire.co.uk.

## Publishing
- Don't cut extra or shorter reels from videos that are already done to fill the schedule; keep
  the reels as made. More reels come from new videos. (23 Oct 2026)
- Dubai/Binghatti: location shoots couldn't be arranged. Dubai content is a talking head on what's
  available and the market from what we know (diary: Wed 4 Nov, Dubai). Every Dubai post uses
  "comment DUBAI". (23 Oct 2026)
- Keep the monday.com "Content & Filming (Master)" board updated for every video (status, dates,
  notes, group). Jake asked for this on 22 Oct 2026; see CLAUDE.md environment notes.
- Jake is happy to upload and post while travelling (Dubai, 29 Oct-8 Nov 2026). Don't hold posts
  back for trips; pick slots around his shoots and calls and give the local time too. (22 Oct 2026)
- Jake can't plan content ahead: for every finished video, put each post (YouTube, reels,
  Story) in his Outlook diary as its own event with the file name, steps and caption to
  paste. He saves the exports himself. (22 Oct 2026)
- Every reel also goes up as a YouTube Short the same day: original export file, the
  full video as Related video, a plain title and short description. Put them in the same
  diary event as the reel. (22 Oct 2026)
- Every reel gets a 1080x1920 cover (`scripts/make_cover.py`): frame of Jake, stacked
  headline in the caption style over his chest, black monogram. Used as the Instagram
  cover and the Shorts thumbnail. (22 Oct 2026)
- Post a calculator (comment SEND) reel when Jake is around to reply, not just before
  he's away. (22 Oct 2026)

## Transcription
- "if it were **let**", not "there"/"rent": whisper mishears it. Check against the script. (22 Oct 2026)
- Whole-file transcription hides false starts ("I'm Jake, found— I'm Jake, the founder…").
  Always run `scripts/find_retakes.py` on the raw and again on the render. (22 Oct 2026)

## Cutting
- Cut audible breaths before the first word of a phrase. Jake spotted a big one at
  0:38 on video 01; the renderer now trims them automatically. (22 Oct 2026)

## B-roll
- Vertical (9:16) clips cropped into 16:9 only work for wide shots (rooms, exteriors); a
  person walking becomes a close-up of their back. Use those shots in the reels. (22 Oct 2026)
- Check B-roll for other companies' names or logos (e.g. a tenant's sign) and burned-in text
  before using it. (22 Oct 2026)
- Footage filmed weeks before posting: check any "this month" / deal-status lines are still
  true before publishing. (22 Oct 2026)

## Audio
- Voice preset `deep` (deeper, fuller): Jake chose it over clean/studio/pitch-shifted.
  No pitch shift. (22 Oct 2026)
- "The sound echoes, can we make it fuller" (Craig video): preset `full` is now the default. Stronger
  dereverb plus late-reverb suppression, more body in the EQ, gentle compression. Heavy compression
  and ffmpeg loudnorm's dynamic mode both lift the room echo back up between words, so the chain
  now ends with plain gain plus a limiter. Measure the echo tail on every new room. (22 Oct 2026)
- Strong echo suppression sounded robotic to Jake. He chose the gentle setting (Option A, about
  2.5 dB less echo). Don't push suppression harder; test any change on a short A/B clip first,
  before rendering whole videos. (22 Oct 2026)
- Music used on video 01: "Autofahren" (YouTube), "House 02" (reels), from brand/music. (22 Oct 2026)

## Graphics
- White cards with yellow text looked cheap: no yellow on cards. Cards = small spaced
  label, fine hairline, Cormorant Garamond italic headline, black/white only. (22 Oct 2026)
- Look Jake wants: luxurious, engaging, authentic, professional. (22 Oct 2026)

## Shooting (advice given to Jake)
- Video 01 was 720p from a camera mic. 4K and the wireless mic make punch-ins, reels and
  audio noticeably better.

## Style
- Jake retracted the style rules in the 22 Oct 2026 CLAUDE.md brief (DM Sans/Jost,
  black/white/grey only, straight cuts, SRT-only YouTube, minimal reel captions, intro
  sting, end card). **Keep the original style in `VIDEO_STYLE.md`**: stacked word-by-word
  captions burned in on YouTube and reels, #FFDE59 key words, Montserrat + Cormorant
  Garamond, zooms, black/white cards, music beds. (22 Oct 2026)
- Past-sale figures Jake says on camera (e.g. £3.65m where the board shows £3.6m) stay as spoken when the gap is small; don't hold the video for them (23 Oct 2026).
- Pauses: Jake notices pauses over about half a second as awkward (reel, 23 Oct 2026). Every EDL uses `silence_db: auto` so pauses are measured against the room's noise floor.
- Repeats: whisper can merge a repeated line into one long word. Check any word over 1.6 s and re-transcribe that span with large-v3 before rendering (23 Oct 2026).
- Hidden repeats: whisper leaves a repeated line out of the transcript ("which is a 10.7%" said twice at 1:49 in the listing). The plan now warns about kept sound with no words. Act on every such warning before rendering (23 Oct 2026).
- Office talking head looked dull. Jake chose grade B (25 Oct 2026): `curves=master='0/0 0.12/0.09 0.45/0.52 0.8/0.86 1/1',eq=saturation=1.12,colorbalance=rm=0.035:gm=0.005:bm=-0.035:rh=0.01:bh=-0.02`. Use it as `grade` on office footage. The old default desaturated and cooled the picture. Show lighting or look changes as a short A/B/C test clip before rendering.
- Listings: put property photos over most of the building description, with push, pull and pan moves, and `broll_shade: 0.45` so captions read on white rooms (25 Oct 2026).
- Never use the line "Everything will remain confidential" (Jake, 26 Oct 2026). If it's in a script, leave it out of the edit, captions, cards and copy; end the valuation CTA on the URL.
- Dividend tax: "up to 2%" is wrong, so a take that says it gets cut rather than kept (Jake approved the cut, 26 Oct 2026).
- Office grade, update (26 Oct 2026): the 25 Oct warm grade looked orange on the Budget video. Jake chose the neutral version: `curves=master='0/0 0.12/0.09 0.45/0.52 0.8/0.86 1/1',eq=saturation=1.04,colorbalance=rm=-0.01:bm=0.015:rh=-0.01:bh=0.01` (same brightness, white wall reads white). Use this as `grade` on office footage from now on, not the warm one above.
- Deep breaths: Jake heard a long pause and deep breath at 6:05 of the Budget video and a few others (26 Oct 2026). Whisper had stretched the first word of each take back over the breath. Run `scripts/breath_check.py` on every EDL before rendering and trim each take to start just before the voice.
