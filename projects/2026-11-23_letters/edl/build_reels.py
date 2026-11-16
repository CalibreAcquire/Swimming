"""Letters video reels (9:16), from the script's Instagram plan:
  A  (sends people to YouTube): the opening numbers, 64,998 letters -> 11 sales, worst reply rate sold the most
  B  (trial reel, built to be saved): the four things to have ready
Neither contains the "£30 million" line (Instagram rule). Run from the project folder."""
import json

BASE = dict(source="../raw/C0404S03.MP4", transcript="../transcript/phrases_large_fixed.json", format="9x16",
            max_gap=0.3, silence_db="auto", anchor=[630, 280], zoom={"wide": 1.0, "tight": 1.15, "every": 2.6},
            audio={"preset": "full"}, cards=[], broll=[], shots=[])

A = dict(BASE, window=[9.45, 40.75], cuts=[[23.45, 30.50]],
         title_card={"text": "64,998 letters / [11 SALES]", "dur": 2.8},
         music={"track": 750, "start": 19, "bed": -27},
         captions="Since January 2023, | we've sent | [64,998 LETTERS] | to London | property owners. [329] of them | wrote back, | "
                  "and [11] of those buildings | have now sold | for nearly | [£14 MILLION] | between them. The list that sold | "
                  "the *most buildings* | had the [LOWEST] | reply rate | of any that we've sent. And the first deal | came from | "
                  "a *single letter* | to a [DERELICT PUB] | in Shadwell.")

B = dict(BASE, window=[341.31, 408.40], cuts=[[354.69, 360.20], [371.55, 381.90], [388.20, 397.40]],
         title_card={"text": "Four things / to have [READY]", "dur": 2.8},
         music={"track": 443, "start": 14, "bed": -27},
         captions="The buyers | who get these buildings | are rarely the ones | with the *most money.* They're the ones | who are [READY.] "
                  "There are | [FOUR THINGS] | to have in place. First, | your [CRITERIA.] Write down | the areas | and the type of building, | "
                  "your price range | and the minimum yield | you'd expect. If you can't say it | in [ONE SENTENCE,] | an agent | "
                  "can't match you | to anything. Then there's | [FINANCE.] Have an agreement | in principle | or proof of funds | "
                  "*before* you view, | not after | you offer. There's also | your [SOLICITOR.] Line up one | who does | commercial and | "
                  "mixed-use work | before you find | the building. And then there's | [SPEED.] When the right building | comes up, | "
                  "view it | within a few days | and decide | within a [WEEK.] Good buildings | don't wait | for *second viewings.*")

for name, e in [("reel-a-letters-to-sales", A), ("reel-b-four-things", B)]:
    json.dump(e, open(f"edl/{name}.json", "w"), indent=1, ensure_ascii=False)
    print("wrote", name)
