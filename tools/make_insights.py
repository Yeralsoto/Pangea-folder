#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the Insights library.

One generator, one template. Adding a piece means adding an entry to
ARTICLES and re-running this — the index page and every article page are
written from the same data, so they cannot drift apart.

    python3 tools/make_insights.py
"""
import io, os, re

SITE = "Pangea Ventures International"

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Pangea Insights</title>
<meta name="description" content="{dek}">
<meta name="theme-color" content="#27372D">
<link rel="icon" href="../assets/logos/pangea-avatar.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,300;6..72,400&family=Geist:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/pangea.css">
</head>
<body class="art-body">

<header class="nav nav--art" data-solid="false">
  <div class="nav__bar">
    <a class="nav__logo" href="../index.html" aria-label="{site} — home">
      <img class="is-light" src="../assets/logos/pangea-horizontal-reversed.svg" alt="{site}">
    </a>
    <nav class="nav__links" aria-label="Primary">
      <a href="index.html">Insights</a>
      <a href="../index.html#how">How it works</a>
      <a href="../index.html#contact">Contact</a>
    </nav>
  </div>
</header>

<main id="main">
'''

FOOT = '''</main>

<footer class="footer">
  <div class="wrap footer__grid">
    <a href="../index.html"><img src="../assets/logos/pangea-horizontal-reversed.svg" alt="{site}"></a>
    <p class="label">Land. Capital. Operations.</p>
    <p class="footer__legal">© 2026 {site}</p>
  </div>
</footer>

<!-- exit prompt, same as the homepage -->
<div class="exit" id="exit-prompt" hidden aria-hidden="true">
  <div class="exit__scrim" data-exit-close></div>
  <div class="exit__panel" role="dialog" aria-modal="true" aria-labelledby="exit-title" tabindex="-1">
    <p class="label exit__eyebrow">Before you go</p>
    <h2 id="exit-title" class="exit__title">Have a deal you cannot read?</h2>
    <p class="exit__body">Send it over. We will underwrite it against the model it actually fits and come back inside 48 hours with the assumptions, the downside, the primary risk, and one of three words: proceed, renegotiate, pass.</p>
    <div class="exit__actions">
      <a class="btn btn--signal" href="mailto:hello@pangeaventures.com?subject=A%20deal%20to%20underwrite">Send us the deal</a>
      <button class="btn btn--ghost-dark" type="button" data-exit-close>Not right now</button>
    </div>
    <p class="exit__note">No list, no sequence. One reply, from one of us.</p>
  </div>
</div>

<script src="../assets/js/pangea.js" defer></script>
</body>
</html>
'''



# --------------------------------------------------------------------------
# header motifs — same drawing language as the section 04 figures
# --------------------------------------------------------------------------
def motif(kind):
    if kind == "lots":
        cells = []
        for i in range(10):
            x = 40 + i * 62
            cells.append('<rect class="df%s" x="%d" y="74" width="46" height="70"/>'
                         % ("" if i < 6 else " sig", x))
            cells.append('<path class="dl" d="M%d 74 L%d 144"/>' % (x, x))
        body = ('<path class="dl" d="M28 60 L672 60"/>'
                '<path class="dl" d="M28 158 L672 158"/>'
                + "".join(cells) +
                '<path class="dl" d="M28 176 L672 176"/>')
    elif kind == "peaks":
        body = ('<path class="dl" d="M28 118 C 120 44, 200 132, 290 76 S 460 32, 560 94 '
                'S 640 126, 672 102"/>'
                '<path class="dl" d="M28 148 C 130 90, 210 156, 300 114 S 470 78, 566 128 '
                'S 646 152, 672 138"/>')
        for i, h in [(0, 62), (1, 44), (2, 36), (3, 28)]:
            x = 150 + i * 112
            body += ('<rect class="df%s" x="%d" y="%d" width="56" height="%d"/>'
                     % (" sig" if i == 3 else "", x, 176 - h, h))
        body += '<path class="dl" d="M28 176 L672 176"/>'
    elif kind == "stack":
        body = '<path class="dl" d="M32 34 L668 34"/>'
        for r in range(4):
            y = 44 + r * 38
            for c in range(9):
                x = 46 + c * 68
                empty = (r == 0 and c in (3, 7))
                body += ('<rect class="df%s" x="%d" y="%d" width="54" height="26"/>'
                         % (" sig" if empty else "", x, y))
            body += '<path class="dl" d="M32 %d L668 %d"/>' % (y + 32, y + 32)
    elif kind == "keys":
        body = '<path class="dl" d="M28 60 L672 60"/><path class="dl" d="M28 186 L672 186"/>'
        for i in range(14):
            x = 40 + i * 46
            h = 34 + (i % 3) * 16
            body += ('<rect class="df%s" x="%d" y="%d" width="34" height="%d"/>'
                     % (" sig" if i in (4, 9) else "", x, 178 - h, h))
    elif kind == "gantt":
        body = '<path class="dl" d="M32 34 L32 194"/>'
        for i, (x0, w) in enumerate([(60, 200), (150, 240), (280, 190), (360, 230), (470, 170)]):
            y = 48 + i * 30
            body += '<path class="dl" d="M32 %d L668 %d"/>' % (y + 22, y + 22)
            body += ('<rect class="df%s" x="%d" y="%d" width="%d" height="15"/>'
                     % (" sig" if i == 4 else "", x0, y, w))
    elif kind == "waterfall":
        body = '<path class="dl" d="M28 52 L672 52"/><path class="dl" d="M28 182 L672 182"/>'
        for i, h in [(0, 118), (1, 96), (2, 80), (3, 60), (4, 96)]:
            x = 70 + i * 118
            body += ('<rect class="df%s" x="%d" y="%d" width="82" height="%d"/>'
                     % (" sig" if i == 4 else "", x, 174 - h, h))
    elif kind == "doors":
        body = '<path class="dl" d="M28 196 L672 196"/>'
        for i in range(8):
            x = 44 + i * 80
            body += ('<path class="dl" d="M%d 196 L%d 76 L%d 52 L%d 76 L%d 196"/>'
                     % (x, x, x + 32, x + 64, x + 64))
            body += ('<rect class="df%s" x="%d" y="120" width="28" height="34"/>'
                     % (" sig" if i in (2, 6) else "", x + 18))
    else:
        body = '<path class="dl" d="M40 52 L660 44 L664 148 L44 156 Z"/>'
        for i in range(1, 4):
            x0 = 40 + i * 156
            body += '<path class="dl" d="M%d %d L%d %d"/>' % (x0, 50 - i, x0 + 2, 154 - i)
        body += ('<rect class="df sig" x="508" y="50" width="152" height="100"/>'
                 '<path class="dl" d="M24 172 L676 164"/>'
                 '<path class="dl" d="M24 182 L676 174"/>')
    # class="dwg" matters: that is where .dl gets fill:none. Without it every
    # closed path in these motifs fills solid black.
    return ('<svg class="dwg" viewBox="0 0 700 210" data-draw aria-hidden="true">'
            '<g class="dstep" data-step="0">%s</g></svg>' % body)

# --------------------------------------------------------------------------
# helpers for article bodies
# --------------------------------------------------------------------------
def p(t):        return '<p class="art__p">%s</p>' % t
def h2(t):       return '<h2 class="art__h2">%s</h2>' % t
def pull(t):     return '<p class="art__pull">%s</p>' % t
def note(t):     return '<p class="art__note">%s</p>' % t
def ul(items):   return '<ul class="art__list">%s</ul>' % "".join('<li>%s</li>' % i for i in items)


def bars(caption, rows, unit=""):
    """Honest two-or-three value comparison. Only values we actually have."""
    top = max(r[1] for r in rows)
    out = []
    for i, (label, val, tone) in enumerate(rows):
        w = val / top * 100.0
        out.append(
          '<div class="bar" style="--i:%d">'
          '<span class="bar__l">%s</span>'
          '<span class="bar__track"><span class="bar__fill%s" style="--w:%.1f%%"></span></span>'
          '<span class="bar__v">%s%s</span></div>'
          % (i, label, ' bar__fill--sig' if tone else '', w, val, unit))
    return ('<figure class="art__fig"><div class="bars" data-bars>%s</div>'
            '<figcaption class="art__figcap">%s</figcaption></figure>'
            % ("".join(out), caption))


# --------------------------------------------------------------------------
ARTICLES = [
{
 "slug": "the-quiet-turn-in-multifamily",
 "tone": "forest", "motif": "stack",
 "kicker": "United States · Multifamily",
 "title": "For the first time since 2022, more apartments were absorbed than built.",
 "dek": "Supply has been the whole story in multifamily for three years. That "
        "story just ended, and most underwriting has not caught up.",
 "date": "September 2026",
 "read": "6 min",
 "body": [
   p("Every multifamily pro forma written between 2023 and 2025 had the same weak point: "
     "a lease-up assumption made in a market being flooded with new units. Concessions ate "
     "the first year. Rent growth arrived late or not at all."),
   p("That pressure is lifting, and the crossover is measurable."),
   bars("Trailing four quarters to Q2 2026, US multifamily, thousands of units. Absorption "
        "exceeded deliveries for the first time since early 2022.",
        [("Absorbed", 362, False), ("Delivered", 358, True)], unit="k"),
   p("Net absorption was 167,500 units in Q2 2026 alone, nearly double the 84,300 of Q1. "
     "Deliveries fell to 77,700, down 14% year over year, and 2026 completions are projected "
     "to fall 28% to about 382,000 units. Vacancy came down to 4.3%, below the long-run "
     "average of roughly 5%."),
   h2("Why the rent number looks disappointing anyway"),
   p("Average asking rent reached $2,257 in Q2 2026 — up only 0.5% year over year, but 1.5% "
     "on the quarter. That gap is the whole point. The annual figure is still carrying the "
     "damage of the supply wave; the quarterly figure is what the market is doing now."),
   pull("Year-over-year rent tells you where the market has been. Quarter-over-quarter tells "
        "you where it is."),
   p("Regional leaders are not where the last cycle's money went. The Midwest led at about 2% "
     "annual rent growth, then the Northeast at 1.7% and the Pacific at 1.4% — the markets "
     "that never got a supply wave in the first place."),
   h2("What we would actually check"),
   ul(["The submarket delivery pipeline for the next eight quarters, not the metro one. "
       "Metro-level easing means nothing if four hundred units are opening a mile away.",
       "Concessions still embedded in the comps. A quoted rent with two months free is not "
       "that rent, and it will not renew at that rent.",
       "Whether your lease-up assumption was written during the flood and never revisited.",
       "Operating expenses, especially insurance and taxes, which did not ease at all while "
       "rents were flat."]),
   note("A market turning is not the same as a market that has turned. Absorption beat "
        "deliveries by about four thousand units out of 360,000 — a rounding error that "
        "happens to point the right way."),
 ],
 "sources": [
   ("CBRE — US multifamily fundamentals improve in Q2 2026 as demand outpaces new supply",
    "https://www.cbre.com/press-releases/us-multifamily-fundamentals-improve-q2-2026-demand-outpaces-new-supply"),
   ("CBRE — Q1 2026 US multifamily figures",
    "https://www.cbre.com/insights/figures/q1-2026-us-multifamily-figures"),
   ("Apartments.com — The supply slowdown: 2026 outlook for development and vacancy",
    "https://www.apartments.com/grow/learning-center/supply-vacancy-outlook-2026"),
   ("Greystone — Key multifamily takeaways for Q2 2026",
    "https://www.greystone.com/insights/key-multifamily-takeaways-for-q2-2026/"),
 ],
},
{
 "slug": "regulation-is-the-first-screen",
 "tone": "forest", "motif": "doors",
 "kicker": "Short-term rentals · Operations",
 "title": "A short-term rental that cannot get a permit is worth nothing, however well it pencils.",
 "dek": "Nightly rate is the last thing to check, not the first. New York removed "
        "roughly 83% of its short-term listings with a single law.",
 "date": "September 2026",
 "read": "7 min",
 "body": [
   p("People bring us short-term rental deals with the revenue projection on page one. "
     "Occupancy, average daily rate, a seasonality curve, a number at the bottom. It is "
     "almost always the wrong page to start on."),
   p("Start with whether the city will let you operate at all."),
   pull("New York's Local Law 18 cut short-term listings by roughly 83% in its first year. "
        "Long-term listings rose about 29%. Nothing about the buildings changed."),
   p("Every one of those owners had a working model the week before. The model was never the "
     "risk. The permit was."),
   h2("The market underneath is actually steady"),
   p("Once you are past the regulatory screen, 2026 is a reasonable year to be operating. "
     "AirDNA forecasts average occupancy of 57.4%, slightly above the pre-pandemic 57.0%, with "
     "demand and available listings both growing about 2.7% and RevPAR up 2.9% on stronger "
     "nightly rates."),
   bars("US short-term rental listing growth. Supply discipline is what is holding occupancy "
        "up, not a demand surge.",
        [("2021–22 peak", 20.0, True), ("2026 forecast", 4.6, False)], unit="%"),
   p("Listing growth of 4.6% against a peak near 20% is the whole reason rates are holding. "
     "Mortgage rates back above 6% delayed the new supply that lower borrowing costs were "
     "expected to bring, which is good news if you already own and a harder entry if you do not."),
   p("Rate growth accelerated through the year, from 0.7% year over year in January to roughly "
     "3% by spring. The strongest RevPAR moves were in supply-constrained cities — San Francisco "
     "+12.1%, Anaheim +11.0%, Philadelphia +10.1% — while the fastest supply growth is expected "
     "in small-city, rural and mid-size markets. Those two facts belong in the same sentence: "
     "where supply can arrive, it will."),
   h2("What we would actually check"),
   ul(["The ordinance, in full, before the LOI. Permit caps, primary-residence requirements, "
       "minimum-night rules, whether permits transfer on sale.",
       "Whether the state preempts local bans, which can make a dull market the safer one.",
       "Pending legislation, not just current law. A deal underwritten on today's rules and "
       "closed under tomorrow's is not a deal.",
       "The long-term rent as a floor. If the property does not work as a boring annual lease, "
       "you are not buying a building, you are buying a permit."]),
   note("The last point is the whole discipline. A short-term rental that also works as a "
        "long-term rental has a downside. One that only works nightly has a regulatory "
        "cliff instead."),
 ],
 "sources": [
   ("AirDNA via PR Newswire — Steady demand and slower new supply define US short-term rentals in 2026",
    "https://www.prnewswire.com/news-releases/steady-demand-and-slower-new-supply-define-us-short-term-rentals-in-2026-airdna-finds-302820776.html"),
   ("Hotel News Resource — AirDNA 2026 short-term rental outlook",
    "https://www.hotelnewsresource.com/article142057.html"),
   ("STR regulation reset 2026: where Airbnb still pays",
    "https://ahlend.com/str-regulation-reset-2026/"),
 ],
},
{
 "slug": "the-bid-you-get-is-not-the-budget-you-wrote",
 "tone": "forest", "motif": "gantt",
 "kicker": "Construction · Development management",
 "title": "The bid you get is not the budget you wrote.",
 "dek": "Materials are running +6.4% while final-demand prices run +3.5%. "
        "Contractors are closing that gap in the back half of 2026, and it "
        "closes on your project.",
 "date": "September 2026",
 "read": "7 min",
 "body": [
   p("There is a particular silence on a job when the bids come back. Somebody has to say the "
     "number out loud, and the number is not the one in the feasibility study that got the "
     "deal approved."),
   p("In 2026 there is a specific, documentable reason for that, and it is worth understanding "
     "before you send the drawings out."),
   h2("Materials moved first. Bids are moving second."),
   bars("Year-over-year change, 2026. The gap between what contractors pay and what they have "
        "been charging is the repricing still to come.",
        [("Materials inputs", 6.4, True), ("Final-demand prices", 3.5, False)], unit="%"),
   p("Underneath that average, individual lines are far worse: copper up 36% year over year, "
     "aluminium up 45%, US hot-rolled steel up 27%. Tariffs of up to 50% are landing on "
     "structural steel, aluminium and other imported products."),
   p("Contractors absorbed some of this. They are not going to keep absorbing it — they have "
     "neither the margin nor the appetite, and bid prices in the back half of 2026 are expected "
     "to close the gap. The baseline for final project cost, materials and margin together, is "
     "running around 5% year over year."),
   pull("A budget written in January and bid in October is not a budget. It is a hypothesis "
        "about margin compression that somebody else has to fund."),
   h2("Labour is the constraint people underestimate"),
   p("Construction wages are up over 4% year over year, and 9–11% in high-demand markets and "
     "specialised trades. More than 60% of metro markets report labour shortages. Data centre "
     "construction is actively pulling crews away from multifamily, healthcare and industrial "
     "work, because it pays better."),
   p("That matters beyond cost. A trade you cannot staff is a schedule you cannot hold, and "
     "schedule is where a development deal usually dies — not in the line items, but in the "
     "carry on an extra two quarters."),
   h2("What we would actually check"),
   ul(["An escalation allowance sized to the gap above, not a flat 3% because that is what "
       "the last deal used.",
       "When the estimate was written and when the bid date is. Every month between them is "
       "risk somebody is carrying.",
       "Which packages are tariff-exposed — structural steel, aluminium, electrical gear — "
       "and whether they can be bought early or substituted.",
       "Whether the GC has the crews, not just the price. A low bid from a contractor who "
       "cannot staff it is the most expensive bid on the table.",
       "The contingency, tested against a 5% escalation and a two-quarter delay together, "
       "because they arrive together."]),
   note("None of this argues against building. It argues for bidding earlier, buying long-lead "
        "packages sooner, and writing the escalation into the model at the number the market "
        "is actually printing."),
 ],
 "sources": [
   ("JLL — 2026 mid-year US construction perspective",
    "https://www.jll.com/en-us/insights/2026-midyear-us-construction-perspective"),
   ("CRE Daily — US construction costs climb as tariff and labor pressures mount",
    "https://www.credaily.com/briefs/us-construction-costs-climb-as-tariff-and-labor-pressures-mount/"),
   ("Tax Credit Advisor — 2026 US construction cost outlook, Q2 update",
    "https://www.taxcreditadvisor.com/articles/2026-us-construction-cost-outlook-q2-update/"),
   ("HB Capital — CRE construction costs 2026: tariffs, labor and replacement cost",
    "https://www.hbcapitalre.com/cre-construction-costs-2026-tariffs-labor/"),
 ],
},
{
 "slug": "what-property-management-actually-costs",
 "tone": "forest", "motif": "keys",
 "kicker": "Operations · Property management",
 "title": "The eight per cent is not the cost of property management.",
 "dek": "A worked example of where an operating year actually leaks, and why "
        "the management fee is almost never the number to argue about.",
 "date": "September 2026",
 "read": "6 min",
 "body": [
   note("A worked example, not a client file. The figures are illustrative and chosen because "
        "they are ordinary."),
   p("Owners negotiate the management fee harder than anything else in the operating budget. "
     "It is visible, it is a percentage, and it feels like the one line you control."),
   p("Take a small building: eight units, $1,800 a month each, $172,800 gross potential. "
     "Management at 8% is $13,824. Argue it down to 6% and you have saved $3,456."),
   p("Now look at what else happened that year."),
   h2("Where the year actually went"),
   ul(["<strong>Vacancy and turnover.</strong> Two units turned. Three weeks empty each, plus "
       "paint, clean and a lock change. Call it $4,600 in lost rent and $2,400 in make-ready.",
       "<strong>Delinquency.</strong> One tenant went two months down before anyone moved. "
       "$3,600, most of which never comes back.",
       "<strong>Deferred maintenance.</strong> A roof repair postponed twice became a roof "
       "repair plus a ceiling. The difference is not the roof, it is the ceiling.",
       "<strong>Under-market rent.</strong> Three units never got the renewal increase because "
       "nobody ran the comps in time. At $75 a month each, that is $2,700 this year and it "
       "compounds into the next."]),
   pull("You saved $3,456 on the fee. Turnover alone cost twice that, and the rent you did "
        "not raise costs it again every year."),
   h2("What the fee is actually buying"),
   p("The manager who charges 8% and holds turnover to one unit, catches the delinquency in "
     "week two and brings you the renewal comps unprompted is not more expensive than the one "
     "at 6%. They are several thousand dollars cheaper, and the gap widens every year you hold."),
   p("This is also why operations belong in the underwriting. A rental model with a management "
     "fee line and no turnover assumption, no delinquency allowance and no annual rent review "
     "is not modelling the building. It is modelling a spreadsheet."),
   h2("What we would actually check"),
   ul(["Turnover rate and average days vacant, in writing, for the manager's existing portfolio.",
       "How delinquency is escalated, and on what day.",
       "Whether anyone is contractually responsible for reviewing rents at renewal.",
       "The maintenance reserve, and whether last year's deferred items are in this year's budget.",
       "What the manager does not do, which is usually where the surprise lives."]),
 ],
 "sources": [],
},
{
 "slug": "the-exit-you-planned-before-you-bought",
 "tone": "forest", "motif": "waterfall",
 "kicker": "Investment · Disposition",
 "title": "Plan the exit before you sign the purchase agreement.",
 "dek": "Hold, improve, refinance, sell or reinvest. Most owners only seriously "
        "consider the option they happen to be standing in.",
 "date": "September 2026",
 "read": "6 min",
 "body": [
   p("An asset that no longer fits your goals is a decision waiting to be made. Most of the "
     "time nobody makes it. The building keeps running, the statements keep arriving, and the "
     "decision gets deferred by another quarter because nothing is actually on fire."),
   p("That is a choice too. It is just an unpriced one."),
   h2("There are five options, always"),
   ul(["<strong>Hold.</strong> Defensible when the asset still does what you bought it to do "
       "and the capital has nowhere better to be. Say that out loud and it stops being a default.",
       "<strong>Improve.</strong> Capital in, income out. Only if the return on that specific "
       "spend beats the return on selling and redeploying.",
       "<strong>Refinance.</strong> Takes chips off the table without triggering tax or losing "
       "the asset. Constrained by rates and by what the asset now appraises at.",
       "<strong>Sell.</strong> Clean, taxable, final. The only option that actually tests "
       "whether the value you have been reporting yourself is real.",
       "<strong>Reinvest.</strong> Sell and roll, with the structure decided before the "
       "clock starts, not after."]),
   pull("The question is never \u201cis this a good asset\u201d. It is \u201cis this the "
        "best available home for this capital, today\u201d. Those have different answers."),
   h2("Why the exit belongs in the acquisition model"),
   p("A decision made at acquisition shows up years later in the operating budget, and the exit "
     "is the clearest case. Financing structure decides whether refinancing is even available. "
     "Entity structure decides what selling costs you. The debt maturity decides when you are "
     "forced to act, and being forced is how people sell into a bad quarter."),
   p("Underwrite the exit at the same time as the entry, and the hold period stops being "
     "whatever happened."),
   h2("What we would actually check"),
   ul(["Debt maturity against your intended hold. If the loan matures first, the loan is "
       "choosing your exit.",
       "What the asset would trade at today, honestly, not at the number in your own model.",
       "The tax consequence of each of the five options, before one of them becomes urgent.",
       "Whether the capital has a better home. If you cannot name it, holding is a real answer.",
       "Who is responsible for revisiting this, and on what date."]),
   note("We ask every owner the same thing once a year: if you did not already own this, "
        "would you buy it today at this price? A no is not an instruction to sell. It is an "
        "instruction to look properly."),
 ],
 "sources": [],
},
{
 "slug": "the-lot-shortage-ended",
 "tone": "forest", "motif": "lots",
 "kicker": "United States · Land",
 "title": "The lot shortage ended. Most people are still pricing like it didn’t.",
 "dek": "Finished-lot supply in the US has loosened for seven straight quarters. "
        "What that does to a land deal you underwrote in 2022.",
 "date": "September 2026",
 "read": "6 min",
 "body": [
   p("For four years the answer to almost any land question in the United States was the same: "
     "there are not enough finished lots. Builders would take anything with a recorded plat and "
     "utilities to the stick. You could underwrite sloppily and be rescued by scarcity."),
   p("That is over, and the change is not subtle."),
   bars("Zonda New Home Lot Supply Index. Higher means looser supply; the index reached its "
        "all-time low in Q2 2022 and, for the first time since 2016, the national market now "
        "reads as appropriately supplied.",
        [("Q2 2022 · all-time low", 35.8, True), ("Q2 2026", 85.2, False)]),
   p("Zonda’s index rose for a seventh consecutive quarter in Q2 2026, and lot supply loosened in "
     "27 of the 30 major metros it tracks over the preceding twelve months. Austin, Atlanta and "
     "Denver now read as significantly oversupplied. Los Angeles and Philadelphia still do not — "
     "which is the whole point."),
   h2("The national number is the least useful number"),
   p("An index that aggregates thirty metros tells you the weather, not whether it is raining on "
     "your parcel. A deal in an oversupplied metro and a deal in a constrained one are no longer "
     "the same trade, and they have not been for about eighteen months."),
   p("What matters on a specific site is narrower: how many competing finished lots sit inside the "
     "same school attendance zone and the same price band, who controls them, and how long the "
     "builders buying there have been extending their takedown schedules."),
   pull("Scarcity was doing work in your model that you may have credited to your own judgement."),
   h2("What this does to the numbers"),
   p("Three things move at once, and they compound:"),
   ul(["Absorption slows. A sell-out you modelled at 24 months is the assumption most likely to "
       "break, and it is the one with the largest effect on a levered return.",
       "Takedowns stretch. Builders who competed for contracts now negotiate them, and the "
       "schedule is the first term they reopen.",
       "Your carry runs anyway. Interest, taxes and management do not care about absorption."]),
   p("Meanwhile the cost side has not loosened with the supply. Impact fees, permitting and "
     "infrastructure requirements are embedded in the basis, and they do not come back out when "
     "the market softens."),
   h2("What we would actually check"),
   p("Before anything else, the downside case at 36 months rather than 24. If the deal only works "
     "at the base case, it is not a deal, it is a bet on a market that has already turned once."),
   p("Then the competing pipeline — not listings, but entitled-and-unbuilt lots, which is where "
     "the real overhang sits. Then whether the builders in that submarket are still signing "
     "contracts or quietly running out standing inventory at nine-plus months of supply, which is "
     "roughly where new single-family sat nationally in mid-2026."),
   note("None of this says do not buy land. It says the thing that used to cover a thin "
        "underwrite is gone, so the underwrite has to carry the deal on its own."),
 ],
 "sources": [
   ("Zonda — New Home Lot Supply Index", "https://zondahome.com/new-home-lot-supply-index-2/"),
   ("ResiClub — Austin, Atlanta, Denver ‘significantly oversupplied’ lot inventory",
    "https://www.resiclubanalytics.com/p/austin-atlanta-denver-boast-significantly-oversupplied-lot-inventory-homebuilders"),
   ("HousingWire — Builders face a tougher math problem as completed inventory rises",
    "https://www.housingwire.com/articles/new-home-supply-9-6-months/"),
   ("Business Report — From shortage to surplus: homebuilder lot supply swings fast",
    "https://www.businessreport.com/article/from-shortage-to-surplus-homebuilder-lot-supply-swings-fast"),
 ],
},
{
 "slug": "medellin-is-not-one-market",
 "tone": "umber", "motif": "peaks",
 "kicker": "Colombia · Residential",
 "title": "Medellín is not one market. It is about nine.",
 "dek": "Prime neighbourhood pricing in Medellín spans roughly three to one. "
        "Buying the city average is how foreign capital gets hurt here.",
 "date": "September 2026",
 "read": "7 min",
 "body": [
   p("Most people arrive in Medellín with one number in their head — a price per square metre they "
     "read somewhere — and start comparing apartments against it. The number is real. It is also "
     "an average of neighbourhoods that behave nothing like each other."),
   bars("Asking prices per square foot, prime Medellín neighbourhoods, 2026. The spread between "
        "El Poblado and Sabaneta is roughly three to one at the top of each range.",
        [("El Poblado", 250, False), ("Laureles", 160, False),
         ("Envigado", 140, False), ("Sabaneta", 120, True)], unit=" /ft²"),
   p("El Poblado runs about $200–$250 per square foot. Laureles $120–$160. Envigado $100–$140. "
     "Sabaneta $80–$120. These are not tiers of quality so much as four different businesses: "
     "different buyers, different tenants, different regulatory attention, different exit."),
   h2("The tailwind is credit, not enthusiasm"),
   p("Colombian mortgage rates have come down to roughly 11% from peaks above 16%. That single "
     "move does more for local demand than any amount of foreign interest, because it changes what "
     "a Colombian household can service. Prices in Medellín are expected to grow about 5–8% in "
     "nominal terms across 2026; across Antioquia, 6–9%."),
   p("Read those figures in nominal pesos, and read them against Colombian inflation before you "
     "call them a return. If you are holding in dollars, the currency is a second position you "
     "took whether you meant to or not."),
   pull("If you are holding in dollars, the currency is a second position you took whether you "
        "meant to or not."),
   h2("Liquidity is the part people skip"),
   p("Well-priced apartments in Medellín are transacting in roughly 90 to 150 days. Overpriced "
     "stock takes considerably longer — and “overpriced” here often means priced off the city "
     "average rather than off the building’s own comparable set."),
   p("Momentum is not where the tourist maps say either. Through mid-2026 the strongest asking-price "
     "movement has been in Ciudad del Río, Guayabal and Manila, roughly 6–12% year over year, with "
     "the sharpest pressure on small units in Manila and on modern stock in Ciudad del Río."),
   h2("What we would actually check"),
   ul(["The building’s own comparable set — same estrato, same age band, same unit size — not the "
       "neighbourhood average and certainly not the city average.",
       "Days on market for units that actually closed, not the ones still listed.",
       "Whether the exit buyer is Colombian. If the answer is “a foreigner like me”, the pool is "
       "far thinner than the listing volume suggests.",
       "The peso. Model the return in both currencies and be explicit about which one you are "
       "actually being paid in."]),
   note("Antioquia sales rose 32.2% across the first nine months of the prior year and have since "
        "moderated. A market that ran that hard and then cooled is exactly the kind that rewards "
        "reading a specific building instead of a headline."),
 ],
 "sources": [
   ("Global Property Guide — Colombia residential market analysis 2026",
    "https://www.globalpropertyguide.com/latin-america/colombia/price-history"),
   ("Medellín real estate prices 2026, $/sq ft by neighbourhood",
    "https://mikezapata.realestate/medellin-real-estate"),
   ("TheLatinvestor — Medellín property price forecasts 2026",
    "https://thelatinvestor.com/blogs/news/medellin-price-forecasts"),
   ("TheLatinvestor — Antioquia property price forecasts 2026",
    "https://thelatinvestor.com/blogs/news/antioquia-price-forecasts"),
 ],
},
{
 "slug": "the-split-that-looked-good",
 "tone": "linen", "motif": "split",
 "kicker": "Worked example · Land",
 "title": "The split that looked good and wasn’t.",
 "dek": "A worked example of a four-lot exempt split where every number was right "
        "and the deal still lost money. The error is made on day one, every time.",
 "date": "September 2026",
 "read": "8 min",
 "body": [
   note("This is a worked example, not a client file. The numbers are illustrative and chosen "
        "because they are typical, not because they are ours."),
   p("Twenty acres on a paved county road. Zoning allows a minimum two-acre lot. The owner wants "
     "$240,000 and will carry paper. Finished two-acre lots in the same corridor have been trading "
     "around $95,000."),
   p("The arithmetic anyone would do: four lots at $95,000 is $380,000 against a $240,000 basis. "
     "Some survey and legal, a culvert or two, and you are looking at a comfortable spread on a "
     "six-month hold."),
   p("That deal loses money. Here is where."),
   h2("One: the exemption was not free"),
   p("Most exempt-split statutes limit how many parcels you can create, how often, and from what "
     "parent tract — and several reset the clock rather than the count. Create the fourth parcel "
     "and the fifth makes the whole thing a subdivision, which means a plat, a plan review, and an "
     "improvement standard for the road you were planning to leave as it is."),
   p("The fee is small. The month is not. Ninety days of review on a deal you modelled at six "
     "months is a quarter of your hold, spent before anything is sellable."),
   h2("Two: frontage is not access"),
   p("Four lots on a shared gravel drive is one legal access point serving four parcels. Many "
     "counties treat that as a private road and apply a private road standard — width, base, "
     "drainage, turnaround, sometimes a maintenance agreement recorded against every lot."),
   pull("The comp had frontage. Your lots have an easement. Those are not the same product, and "
        "the buyer’s lender knows it."),
   p("Now the comparables stop being comparable. A $95,000 lot with its own county frontage is not "
     "the same asset as a $95,000 lot at the end of a shared easement, and the difference shows up "
     "as a discount, a longer marketing period, or a buyer who cannot get financed."),
   h2("Three: the last lot pays for everything"),
   p("Culvert, drive, survey, plat if you triggered it, legal, closing costs on four separate "
     "transactions, the carry across a hold that is now ten months rather than six. Call it "
     "$70,000–$90,000 in a corridor where that is unremarkable."),
   p("The spread you started with was $140,000. You have spent most of it, and the lots you are "
     "selling are worth less than the ones you comped. The fourth lot — the one that made the "
     "arithmetic work — is the one that triggered the review that caused the delay."),
   h2("What would have caught it"),
   ul(["Reading the split ordinance before the LOI, not before closing. It is public, it is "
       "usually four pages, and it is the single highest-return document in the trade.",
       "Comping access, not acreage. Pull the comps’ deeds and check whether they front the county "
       "road or hang off an easement.",
       "Modelling three lots instead of four. If the deal only works at four, the ordinance is "
       "underwriting your deal, not you.",
       "Costing the road to the standard the county can require, not the one you hope it will "
       "accept."]),
   p("A three-lot version of this deal, underwritten honestly, is thinner and it closes. That is "
     "usually the choice — not between a good deal and a bad one, but between a modest deal you "
     "can actually execute and an attractive one that quietly depends on a rule nobody read."),
 ],
 "sources": [],
},
]


# --------------------------------------------------------------------------
def render_article(a):
    body = "\n      ".join(a["body"])
    src = ""
    if a["sources"]:
        items = "".join('<li><a href="%s" rel="noopener nofollow" target="_blank">%s</a></li>'
                        % (u, t) for t, u in a["sources"])
        src = ('<section class="art__sources"><p class="label">Sources</p>'
               '<ol class="art__srclist">%s</ol></section>' % items)
    return (HEAD.format(title=a["title"], dek=a["dek"], site=SITE) + '''
<article class="art">
  <div class="wrap art__wrap">
    <div class="arthead arthead--%s rv">%s</div>
    <header class="art__head">
      <p class="label art__kicker rv">%s</p>
      <h1 class="art__title rv" style="--rv-delay:70ms">%s</h1>
      <p class="art__dek rv" style="--rv-delay:140ms">%s</p>
      <p class="art__meta rv" style="--rv-delay:200ms">%s · %s read</p>
    </header>
    <div class="art__body">
      %s
    </div>
    %s
    <aside class="art__cta">
      <h2>Have one of these on your desk?</h2>
      <p>Send it. We will underwrite it against the model it actually fits and come back inside 48 hours with a recommendation: proceed, renegotiate or pass.</p>
      <a class="btn btn--signal" href="mailto:hello@pangeaventures.com?subject=A%%20deal%%20to%%20underwrite">Send us the deal</a>
    </aside>
    <p class="art__back"><a href="index.html">← All insights</a></p>
  </div>
</article>
''' % (a["tone"], motif(a["motif"]), a["kicker"], a["title"], a["dek"],
            a["date"], a["read"], body, src)
            + FOOT.format(site=SITE))


def render_index(arts):
    rows = "\n".join('''      <li class="ins rv">
        <a class="ins__link" href="%s.html">
          <span class="ins__thumb arthead--%s">%s</span>
          <span class="ins__text">
            <span class="label ins__kicker">%s</span>
            <span class="ins__title">%s</span>
            <span class="ins__dek">%s</span>
            <span class="ins__meta">%s · %s read</span>
          </span>
        </a>
      </li>''' % (a["slug"], a["tone"], motif(a["motif"]), a["kicker"], a["title"],
                 a["dek"], a["date"], a["read"])
      for a in arts)
    return (HEAD.format(title="Insights", site=SITE,
            dek="Field notes on land, construction, hospitality and rental assets "
                "across the United States and Latin America.")
      + '''
<section class="section art-index">
  <div class="wrap">
    <div class="sec-head rv"><p class="label">Insights</p></div>
    <h1 class="rv" style="font-size:var(--d-1);max-width:16ch;margin-bottom:1rem">Field notes, with the working shown.</h1>
    <p class="lede measure rv" style="margin-bottom:clamp(2.5rem,6vh,4rem)">What we are reading in the markets we work in, and the mistakes we watch people make in each of them. Every figure is sourced. Where we are guessing, we say so.</p>
    <ol class="inslist">
''' + rows + '''
    </ol>
  </div>
</section>
''' + FOOT.format(site=SITE))


os.makedirs("insights", exist_ok=True)
for a in ARTICLES:
    io.open("insights/%s.html" % a["slug"], "w", encoding="utf-8").write(render_article(a))
io.open("insights/index.html", "w", encoding="utf-8").write(render_index(ARTICLES))

# keep the homepage band in step with the library
home = io.open("index.html", encoding="utf-8").read()
rows = "\n".join('''      <li class="ins rv">
        <a class="ins__link" href="insights/%s.html">
          <span class="ins__thumb arthead--%s">%s</span>
          <span class="ins__text">
            <span class="label ins__kicker">%s</span>
            <span class="ins__title">%s</span>
            <span class="ins__dek">%s</span>
            <span class="ins__meta">%s · %s read</span>
          </span>
        </a>
      </li>''' % (a["slug"], a["tone"], motif(a["motif"]), a["kicker"], a["title"],
               a["dek"], a["date"], a["read"])
    for a in ARTICLES)
home = re.sub(r"<!-- INSIGHTS:START -->.*?<!-- INSIGHTS:END -->",
              "<!-- INSIGHTS:START -->\n" + rows + "\n<!-- INSIGHTS:END -->",
              home, flags=re.S)
io.open("index.html", "w", encoding="utf-8").write(home)
print("homepage band updated")
print("wrote %d articles + index" % len(ARTICLES))
for a in ARTICLES:
    print("  insights/%s.html  (%d sources)" % (a["slug"], len(a["sources"])))
