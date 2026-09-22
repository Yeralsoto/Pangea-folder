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

<header class="nav nav--art" data-solid="true">
  <div class="nav__bar">
    <a class="nav__logo" href="../index.html" aria-label="{site} — home">
      <img class="is-dark" src="../assets/logos/pangea-horizontal-twotone.svg" alt="{site}">
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
    <p class="footer__legal">© 2026 {site} · Founders Erin Berger and Yeraldin Soto</p>
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
      <a class="btn btn--signal" href="mailto:erin@pangeaventures.com?subject=A%20deal%20to%20underwrite">Send us the deal</a>
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
      <a class="btn btn--signal" href="mailto:erin@pangeaventures.com?subject=A%%20deal%%20to%%20underwrite">Send us the deal</a>
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
