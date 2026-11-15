"""Letters video (C0404S03): YouTube edit. Script: script/2026-11-23_letters_script.txt.
Takes chosen from transcript/phrases_large.json (large-v3, phrase by phrase); see notes.md for the take log.
Run from the project folder: python3 edl/build_youtube.py"""
import json

CAPTIONS = open("edl/captions_youtube.txt").read().strip()

edl = {
    "title": "I Sent 64,998 Letters to London Property Owners",
    "type": "educational",
    "source": "../raw/C0404S03.MP4",
    "transcript": "../transcript/phrases_large.json",
    "format": "16x9",
    "window": [9.45, 430.75],
    "cuts": [
        [23.45, 30.50],    # first take of "The list that sold the most buildings..."
        [40.75, 53.50],    # "In this video" false starts (incl. swearing)
        [69.20, 72.15],    # "If you are no-"
        [118.75, 127.90],  # "17 went on to instruction..." stumbles
        [148.80, 154.00],  # "then something changes, a tenant leaves, a loan account" -> retake
        [192.00, 197.50],  # first "Now, the part that surprised me"
        [230.85, 240.45],  # "What matters is how many..." false starts
        [300.60, 305.05],  # "it isn't a secret club either, it's knocking on door" (cut off)
        [310.20, 318.40],  # third take of the secret-club line (second take kept, says "sign" as scripted)
        [325.30, 329.10],  # "If it's under offer" misread
        [335.80, 341.20],  # "The buyers who get the best buildings" restart
        [354.69, 360.20],  # "if you can't say in this one sentence ... match it to anyone" -> retake
        [371.55, 381.90],  # first solicitor take
        [388.20, 393.70],  # "slow a commercial deal by downtime" -> retake
    ],
    "max_gap": 0.45,
    "silence_db": "auto",
    "anchor": [630, 280],
    "zoom": {"wide": 1.0, "tight": 1.28, "every": 5.0},
    "shots": [],
    "audio": {"preset": "full"},
    "music": {"track": 609, "start": 60, "bed": -30},
    "broll": [],
    "cards": [
        {"from": 19.30, "to": 23.30, "style": "black",
         "text": "~Since January 2023~ / [64,998] letters / 329 replies / 11 sales / *Nearly £14 million*"},
        {"from": 58.30, "to": 68.90, "style": "white",
         "text": "~In this video~ / 65,000 letters, 11 sales / Why the worst reply rate sold the most / What happened to the pub / What off-market means / *Four things to have ready*"},
        {"from": 112.00, "to": 132.05, "style": "white",
         "text": "~January 2023 to October 2026~ / Letters sent: 64,998 / Replies: 329 / Valuations: 65 / Instructions to sell: 17 / *Sold: 11*"},
        {"from": 132.71, "to": 138.87, "style": "black",
         "text": "~Roughly~ / *One sale* / for every 5,900 letters"},
        {"from": 180.23, "to": 191.26, "style": "black",
         "text": "~Free valuation report~ / *calibreacquire.co.uk/valuation-promotion* / Code [SOCIALS]"},
        {"from": 204.30, "to": 215.41, "style": "white",
         "text": "~Reply rate vs sales~ / East London: 0.3% replied · *9 sold* / North London: 1.4% replied · *1 sold*"},
        {"from": 261.86, "to": 268.30, "style": "white",
         "text": "~The Deanswift · Shadwell~ / Sold vacant · *£1,250,000* / Now open and trading / Hotel use applied for upstairs"},
        {"from": 318.50, "to": 325.12, "style": "black",
         "text": "~Off-market~ / Not cheap / Not a secret club / *First look, before the public launch*"},
        {"from": 403.80, "to": 408.38, "style": "white",
         "text": "~Be ready~ / 1 · Criteria / 2 · Finance / 3 · Solicitor / *4 · Speed*"},
        {"from": 424.37, "to": 430.55, "style": "black",
         "text": "~Apply to join the list~ / *calibreacquire.co.uk/register*"},
    ],
    "captions": CAPTIONS,
    "srt_terms": ["Companies House", "Deancross Street", "Shadwell", "East London", "North London", "Emran"],
}
json.dump(edl, open("edl/youtube.json", "w"), indent=1, ensure_ascii=False)
print("wrote edl/youtube.json")
