"""Builds edl/youtube.json for the Budget video: kept takes, captions, cards."""
import json

KEEP = [  # source seconds, the take used for each script line (see notes.md); take starts
    # trimmed past the breath before them on 26 Oct (Jake: deep breaths, e.g. 6:05)
    (83.45, 91.25), (91.55, 99.65), (105.35, 124.05), (124.80, 142.50), (148.15, 152.80),
    (155.35, 172.00), (176.30, 181.35), (183.80, 207.70), (208.00, 229.65), (241.25, 248.35),
    (248.60, 270.30), (283.48, 297.00), (317.48, 324.27), (333.85, 341.80), (342.15, 366.45),
    (367.25, 390.70), (398.20, 404.70), (413.38, 419.92), (428.50, 441.65), (443.95, 450.10),
    (458.25, 463.80), (464.28, 478.40), (493.85, 496.00), (499.90, 509.65), (547.40, 551.29),
    (555.25, 560.76), (628.72, 638.25), (640.05, 661.35), (682.66, 692.70), (694.75, 702.30),
    (713.07, 728.90), (731.75, 736.70), (740.25, 746.30), (762.65, 766.55), (775.85, 784.80),
    (795.80, 815.60), (815.85, 820.70), (842.28, 852.40), (853.40, 865.05), (877.80, 883.80),
    (884.15, 901.40), (906.90, 928.98), (933.20, 942.95), (944.75, 961.30), (977.50, 990.60),
    (990.80, 1004.35), (1004.48, 1016.60),
]

CAPTIONS = """
On Wednesday, | John Healey delivers | his first [BUDGET] | as *Chancellor.* The biggest tax change | for landlords this year | won't be in his [SPEECH.]
It was announced | last year, November. It's [ALREADY LAW] | and it starts in | [APRIL 2027,] | whatever he says | on the day.
In this video, | I'll go through | what's already *confirmed* | for landlords, | what's been [RULED OUT,] | and what's still | only a [RUMOUR.] I'll show you | what the April 2027 change | does to a typical | landlord's [TAX BILL,] | with *real numbers.* And at the end, | I'll go through | [FOUR THINGS] | worth checking | in your own portfolio | before *Wednesday.*
Every Budget, | the same thing happens. The headlines fill up | with what *might* change, | and some landlords | make [BIG DECISIONS] | on the back of them. If you already own a property | that isn't performing, | that pressure is [WORSE,] | because you're already wondering | whether to [HOLD IT] | or [SELL IT.]
But a decision made | on a [RUMOUR] | is made before you know | what's *actually* changing.
I'm Jake, | the founder of | [CALIBRE ACQUIRE.] I've been in property | for [14 YEARS,] | and last year | we transacted on over | [£30 MILLION] | in *mixed-use buildings,* | *residential blocks* | and *commercial property.* I help investors | get out of *underperforming* property assets | and into ones | that work [HARDER] | for them.
Let's start with | what's already [CONFIRMED,] | because none of this | depends on *Wednesday.*
First, | [PROPERTY INCOME TAX.] From 6th of April 2027, | rental profit gets | its [OWN TAX RATES.] The basic rate goes | from 20% | to [22%,] | the higher rate | from 40% | to [42%] | and the additional rate | from 45% | to [47%.] This was announced | at last November's Budget, | and it became [LAW] | in March this year.
The tax credit you get | on *mortgage interest* | also goes up | from 20% | to [22%.] So landlords | with bigger mortgages | feel *slightly less* | of the increase. There's also a change | to how your | [PERSONAL ALLOWANCE] | is used. From April 2027, | it goes against your | [SALARY FIRST,] | and only then | against your *rental income.*
If you earn a good salary, | this probably makes | [NO DIFFERENCE] | to you, | because your job | already uses up | your allowance.
Then there's | [MAKING TAX DIGITAL.] Since April this year, | landlords with combined rental, | self-employed income | over [£50,000] | have had to keep | *digital records* | and report to HMRC | every [QUARTER.] From April 2027, | that threshold drops | to [£30,000.] It's based on your income | [BEFORE EXPENSES,] | not your *profit.*
And then there's | the [HIGH VALUE] | [COUNCIL TAX SURCHARGE,] | which most people call | the [MANSION TAX.] It applies to | *residential property in England* | worth [£2 MILLION] | or more, | from [APRIL 2028.] For most landlords watching this, | it [WON'T APPLY.]
If you're considering a property | and want to [STRESS TEST] it | within a few minutes, | I built a set of | [FREE DEAL CALCULATORS] | that let you do that.
There's one for *mixed-use,* | one for *HMOs* | and one for *single residential.* Comment [SEND] below | and I'll send them over, | or use the link | in the description.
Here's what the | April 2027 change | actually means | in [POUNDS.] Take a landlord | on a good salary, | so they're already | a [HIGHER-RATE] | taxpayer. Their rental income, | after running costs | but before mortgage interest, | is [£30,000] | a year. Their mortgage interest | is [£12,000] | a year. So their *real profit,* | the money they actually keep | before tax, | is [£18,000.]
Today, | they pay [40%] | on the full £30,000, | which is [£12,000.] They get a [20%] credit | on the £12,000 | of interest, | which is [£2,400] | back. So their tax bill | is [£9,600.] From April 2027, | it's [42%] | on £30,000, | which is [£12,600.]
The credit becomes | [22%] | of £12,000, | which is [£2,640] | back.
So their tax bill | is [£9,960.] That's [£360] | a year more.
On its own, | that's *not* the number | to worry about. The number to look at | is [£9,960] | of tax | on [£18,000] | of *real profit.* That's an | [EFFECTIVE TAX RATE] | of [55%.]
That's down to | [SECTION 24,] | which stopped individual landlords | deducting their mortgage interest | *in full.*
The April 2027 change | adds a bit more | on top of a cost | that was [ALREADY THERE.]
I learned this [MYSELF.] I owned a one-bed flat | in *Brentwood* | in my own name. On paper, | it yielded about [6%.] Once the service charge, | ground rent | and tax were paid, | it was [LOSING MONEY] | every month. I sold it | at a [£30,000 LOSS] | to get it out.
Holding it for longer | would have cost me [MORE.]
Some landlords look at | a [LIMITED COMPANY] | as the answer. A company can deduct | its mortgage interest | *in full,* | and it pays | [CORPORATION TAX] | instead of income tax.
But taking money out | of a company | has its [OWN TAX,]
and moving properties | you already own | into a company | can trigger | [STAMP DUTY] | and [CAPITAL GAINS TAX.]
It works well for some people | and *badly* for others, | so speak to an [ACCOUNTANT] | before you make that move. I'll cover it properly | in a *separate video* | next month.
Now, | what's been [RULED OUT?] [STAMP DUTY.] In July, | the Prime Minister said | there would be | [NO CHANGE] | to stamp duty | in this Budget. He also ruled out | replacing stamp duty | and council tax | with a single | *annual property tax,* | for now. So if you're buying, | your stamp duty bill | on Thursday | will be the [SAME] | as it is today.
Then there's | [CAPITAL GAINS TAX.] There was talk of | bringing it in line | with income tax, | which would have taken | the higher rate | on property gains | from [24%] | to [40%] | or more.
The Chancellor is reported | to have *rejected* that, | but it's been [REPORTED,] | not announced, | and a *smaller increase* | is still possible.
To put that in pounds, | a higher-rate landlord | with a [£200,000] gain | pays about | [£47,000] | in tax today, | after the £3,000 allowance. At 40%, | that same gain | would have cost | nearly [£79,000.]
That leaves | what's still a [RUMOUR.] A smaller rise | in *capital gains tax.*
Some form of | [COUNCIL TAX REFORM,] | which the Prime Minister | has said he supports, | without giving | any detail.
And [WIDER TAX RISES,] | which the Chancellor | hasn't ruled out.
I'm recording this | [BEFORE THE BUDGET,] | so anything I've called a rumour | could be *confirmed* | or *dropped* | on Wednesday. The Budget also | isn't the only thing | [MOVING.]
The Bank of England rate | is [3.75%.] It was held in September, | but three of the nine | committee members | voted to raise it | to [4%.] Inflation rose | to [3.5%] | in September, | up from 3.1% | in August. The next rate decision | is on | [THURSDAY 5TH NOVEMBER.]
So here are the | [FOUR THINGS] | worth checking | before *Wednesday.*
First, | run each property | on the April 2027 rates | and work out | what you *actually keep* | after tax. Not the yield on paper, | the money that | [ENDS UP WITH YOU.]
Second, | if you're selling | and the capital gains rumours | worry you, | it's worth knowing | that for tax purposes, | a sale usually happens | when contracts are | [EXCHANGED,] | not when it *completes.*
The last time | capital gains went up, | in [OCTOBER 2024,] | the new rates applied | from [BUDGET DAY.]
But you can't get a sale | to exchange | in [TWO DAYS.] One of our sales, | a block of *five flats* | on Holloway Road, | took [12 MONTHS] | from agreeing the deal | to completion. Rushing a sale | because of a rumour | usually means | accepting a *weaker price* | or skipping checks | on the *legal work.*
Third, | check whether | [MAKING TAX DIGITAL] | applies to you | from April. If your rental | and self-employed income | before expenses | was over [£30,000] | in 2025 to 2026 | tax year, | it [DOES.] Fourth, | [SEPARATE THE PROPERTY] | from the *headlines.* If a property | is performing well, | a Budget rumour | isn't a reason | to [SELL IT.]
If it isn't performing, | that's a reason | to [LOOK AT IT,] | whatever the Chancellor says | on Wednesday. The decision should come | from the [PROPERTY,] | not from the *speech.*
If you found this useful, | send it to someone | who's looking at | their own portfolio | before the Budget. It could save them | significant amount | on the next deal. I'll go through | what was actually announced | the day after the Budget, | so if you want to be kept up to date | with new property strategies, | then [SUBSCRIBE.]
If you're looking to move out | of a *weaker property* | and into a | [FREEHOLD BUILDING] | in a strong location, | our registered investors | see new properties [FIRST,] | with one week's | [EXCLUSIVITY] | before they go | to the open market.
If you want to be notified | when properties like this | become available, | you can register at | calibreacquire.co.uk/register. I look at every registration | [PERSONALLY,] | and if it's a good fit, | I'll reach out.
And if you own a property | and want to know about | what it's worth today, | we built an | [INSTANT VALUATION] | tool | that we use for | our own internal valuations. You can get that at | calibreacquire.co.uk/instant-valuation.
"""

def card(a, b, style, text):
    return {"from": a, "to": b, "style": style, "text": text}

CARDS = [
    card(93.85, 99.6, "black", "~The biggest change for landlords~ / *Already law* / starts April 2027"),
    card(105.6, 118.5, "white", "~In this video~ / Already confirmed / Ruled out / Still a rumour / *A landlord's tax bill, in pounds*"),
    card(175.2, 178.6, "black", "~Part 1~ / *Already confirmed*"),
    card(188.1, 202.3, "white", "~Property income tax · from 6 April 2027~ / Basic rate: 20% → *22%* / Higher rate: 40% → *42%* / Additional rate: 45% → *47%*"),
    card(202.45, 207.65, "black", "~Already law~ / Announced at the November 2025 Budget / *Law since March 2026*"),
    card(208.1, 214.0, "white", "~Tax credit on mortgage interest~ / *20% → 22%*"),
    card(223.4, 229.6, "black", "~Personal allowance · from April 2027~ / *Salary first* / then rental income"),
    card(254.6, 270.25, "white", "~Making Tax Digital~ / Since April 2026: income over *£50,000* / From April 2027: income over *£30,000* / Digital records · quarterly reports to HMRC / Income before expenses, not profit"),
    card(286.0, 294.1, "black", "~High Value Council Tax Surcharge~ / *£2 million or more* / Residential property in England · from April 2028"),
    card(334.0, 341.7, "black", "~Free deal calculators~ / Mixed-use · HMO · Single residential / *calibreacquire.co.uk/investment-calculators* / Comment [SEND]"),
    card(351.75, 366.4, "white", "~A higher-rate landlord~ / Rental income before interest: £30,000 / Mortgage interest: £12,000 / *Real profit: £18,000*"),
    card(367.3, 383.0, "white", "~Today~ / 40% × £30,000 = £12,000 / 20% credit × £12,000 = −£2,400 / *Tax bill: £9,600*"),
    card(398.25, 417.1, "white", "~From April 2027~ / 42% × £30,000 = £12,600 / 22% credit × £12,000 = −£2,640 / *Tax bill: £9,960*"),
    card(417.45, 419.7, "black", "~The difference~ / *£360 a year*"),
    card(431.85, 441.6, "black", "~The number to look at~ / £9,960 of tax on £18,000 of profit / *An effective tax rate of 55%*"),
    card(445.9, 450.05, "white", "~Section 24~ / *Mortgage interest can't be deducted in full*"),
    card(470.9, 478.4, "black", "~My one-bed flat · Brentwood~ / About 6% on paper / Losing money every month / *Sold at a £30,000 loss*"),
    card(502.9, 509.25, "white", "~Limited company~ / Mortgage interest deducted in full / *Corporation tax, not income tax*"),
    card(555.25, 560.55, "black", "~But~ / Taking money out has its own tax / *Moving properties in can trigger stamp duty and capital gains tax*"),
    card(631.4, 634.45, "white", "~Before you move~ / *Speak to an accountant*"),
    card(640.05, 643.4, "black", "~Part 2~ / *Ruled out*"),
    card(645.0, 656.5, "white", "~Ruled out by the Prime Minister · July~ / *No change to stamp duty* / No single annual property tax, for now"),
    card(683.2, 692.7, "white", "~Capital gains tax · higher rate on property~ / Today: *24%* / Talked about: 40% or more"),
    card(697.5, 702.25, "black", "~Capital gains tax~ / *Reported, not announced* / A smaller increase is still possible"),
    card(716.9, 728.85, "white", "~£200,000 gain · higher-rate landlord~ / Today, after the £3,000 allowance: *about £47,000* / At 40%: *nearly £79,000*"),
    card(731.8, 746.3, "black", "~Part 3 · still a rumour~ / A smaller rise in capital gains tax / Council tax reform / Wider tax rises"),
    card(796.4, 805.0, "white", "~Bank of England base rate~ / *3.75%* / Held in September · 3 of 9 voted for 4%"),
    card(805.95, 811.9, "white", "~Inflation~ / *3.5% in September* / up from 3.1% in August"),
    card(811.95, 815.6, "black", "~Next rate decision~ / *Thursday 5 November*"),
    card(815.9, 820.7, "black", "~Before Wednesday~ / 1 · Run each property on the April 2027 rates / 2 · Know when a sale counts for tax / 3 · Check Making Tax Digital / 4 · Separate the property from the headlines"),
    card(846.9, 852.4, "white", "~Check 1~ / *What you actually keep after tax* / not the yield on paper"),
    card(858.0, 865.05, "white", "~Check 2 · capital gains tax~ / *A sale happens at exchange* / not at completion"),
    card(878.0, 883.8, "black", "~October 2024~ / *New capital gains rates applied from Budget day*"),
    card(887.95, 894.0, "white", "~Five flats · Holloway Road~ / *12 months* / from agreeing the deal to completion"),
    card(911.85, 920.95, "white", "~Check 3 · Making Tax Digital from April 2027~ / *Over £30,000* / rental and self-employed income before expenses, 2025 to 2026"),
    card(921.05, 924.45, "black", "~Check 4~ / *Separate the property from the headlines*"),
    card(939.3, 942.95, "black", "*The decision should come from the property,* / not from the speech."),
    card(994.5, 1000.0, "black", "~Apply to join the list~ / *calibreacquire.co.uk/register*"),
    card(1012.4, 1016.6, "white", "~Instant valuation~ / *calibreacquire.co.uk/instant-valuation*"),
]

window = [KEEP[0][0], KEEP[-1][1]]
cuts = [[round(a[1], 2), round(b[0], 2)] for a, b in zip(KEEP, KEEP[1:]) if b[0] - a[1] > 0.02]
GRADE_NEUTRAL = "curves=master='0/0 0.12/0.09 0.45/0.52 0.8/0.86 1/1',eq=saturation=1.04,colorbalance=rm=-0.01:bm=0.015:rh=-0.01:bh=0.01"
edl = {
    "title": "Budget week: what's already confirmed for landlords and what's rumour",
    "type": "educational",
    "source": "../raw/Budget.MP4",
    "transcript": "../transcript/phrases_large_fixed.json",
    "format": "16x9",
    "window": window,
    "cuts": cuts,
    "max_gap": 0.45,
    "silence_db": "auto",
    "anchor": [668, 275],
    "zoom": {"wide": 1.0, "tight": 1.28, "every": 4.0},
    "shots": [],
    "grade": GRADE_NEUTRAL,
    "audio": {"preset": "full"},
    "music": {"track": 609, "start": 120, "bed": -30},
    "broll": [],
    "cards": CARDS,
    "captions": " ".join(l.strip() for l in CAPTIONS.strip().splitlines()),
    "srt_terms": ["Budget", "Making Tax Digital", "High Value Council Tax Surcharge", "Section 24",
                  "Comment SEND", "Prime Minister", "Chancellor"],
}
json.dump(edl, open("edl/youtube.json", "w"), indent=2, ensure_ascii=False)
open("edl/youtube.json", "a").write("\n")
print(len(KEEP), "takes,", len(cuts), "cuts,", len(CARDS), "cards")
# overlap check
cs = sorted(CARDS, key=lambda c: c["from"])
for x, y in zip(cs, cs[1:]):
    if y["from"] < x["to"]:
        print("CARD OVERLAP", x["from"], y["from"])
