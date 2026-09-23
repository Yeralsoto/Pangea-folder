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
<title>{title} — Pangea Field Notes</title>
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
    <a class="nav__logo" href="../index.html" aria-label="Pangea Ventures International — home">
      <img class="nav__sym" src="../assets/logos/pangea-symbol-reversed.svg" alt="">
      <span class="nav__lock">
        <img class="nav__word" src="../assets/logos/pangea-wordmark-only-bone.svg" alt="Pangea">
        <span class="nav__desc">Ventures International</span>
      </span>
    </a>
    <nav class="nav__links" aria-label="Primary">
      <a href="../index.html#cycle">What we do</a>
      <a href="../index.html#services">Services</a>
      <a href="../insights/index.html">Field Notes</a>
      <a href="../about.html">About us</a>
      <a href="../index.html#contact">Contact</a>
    </nav>
    <button class="nav__menu" type="button" aria-expanded="false" aria-controls="menu">
      <span class="nav__menuLabel">Menu</span>
      <span class="nav__menuIcon" aria-hidden="true"><i></i><i></i><i></i></span>
    </button>
  </div>
</header>

<div class="menu" id="menu" hidden aria-hidden="true">
  <div class="menu__inner">
    <nav aria-label="All sections">
      <ul class="menu__list">
        <li><a href="../index.html" style="--i:0"><span class="menu__n">I</span><span class="menu__b"><span class="menu__t">Home</span><span class="menu__d">Clarity across the real estate lifecycle</span></span></a></li>
        <li><a href="../index.html#cycle" style="--i:1"><span class="menu__n">II</span><span class="menu__b"><span class="menu__t">What we do</span><span class="menu__d">The full cycle, land through operations</span></span></a></li>
        <li><a href="../index.html#services" style="--i:2"><span class="menu__n">III</span><span class="menu__b"><span class="menu__t">Services</span><span class="menu__d">How we work, and what it costs</span></span></a></li>
        <li><a href="../insights/index.html" style="--i:3"><span class="menu__n">IV</span><span class="menu__b"><span class="menu__t">Field Notes</span><span class="menu__d">Fifteen pieces on markets and deals</span></span></a></li>
        <li><a href="../about.html" style="--i:4"><span class="menu__n">V</span><span class="menu__b"><span class="menu__t">About us</span><span class="menu__d">The firm, and the mark</span></span></a></li>
        <li><a href="../index.html#contact" style="--i:5"><span class="menu__n">VI</span><span class="menu__b"><span class="menu__t">Contact</span><span class="menu__d">Reply inside one business day</span></span></a></li>
      </ul>
    </nav>
    <p class="menu__foot">Reply inside one business day. Bad news the same day we find it.</p>
  </div>
</div>

<main id="main">
'''

FOOT = '''</main>

<footer class="footer">
  <div class="wrap footer__grid">
    <a href="../index.html"><img src="../assets/logos/pangea-horizontal-reversed.svg" alt="{site}"></a>
    <p class="label">From opportunity to operation.</p>
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





def _num(s):
    """Pull a signed number out of a display string like '+4.6%' or '−5.1%'."""
    t = s.replace("−", "-").replace("–", "-")
    m = re.search(r"-?\d+(?:\.\d+)?", t)
    return float(m.group(0)) if m else 0.0


def _g(w, h, kind, parts, caption, cls="art__fig dgm"):
    return ('<figure class="%s" data-dgm>'
            '<svg class="dwg dwg--ink dwg--%s" viewBox="0 0 %d %d" data-draw aria-hidden="true">'
            '<g class="dstep" data-step="0">%s</g></svg>'
            '<figcaption class="art__figcap">%s</figcaption></figure>'
            % (cls, kind, w, h, "".join(parts), caption))


def bars(caption, rows, unit="", prefix=""):
    """Magnitude comparison, drawn. The axis and every bar outline stroke
    themselves on, then the fills arrive underneath."""
    W, PAD, ROW, BARMAX = 300, 16, 44, 224
    n = len(rows)
    H = PAD + n * ROW + 6
    top = max(abs(r[1]) for r in rows) or 1
    parts = ['<path class="dl dl--ax" d="M1 %d V%d"/>' % (PAD + 4, PAD + n * ROW - 8)]
    for i, (label, val, tone) in enumerate(rows):
        t = PAD + i * ROW
        w = max(7.0, abs(val) / float(top) * BARMAX)
        parts.append('<text class="dt" x="6" y="%d">%s</text>' % (t + 10, label))
        parts.append('<rect class="df bfl%s" x="1" y="%d" width="%.1f" height="16"/>'
                     % (' bfl--sig' if tone else '', t + 16, w))
        parts.append('<path class="dl%s" d="M1 %d H%.1f V%d H1 Z"/>'
                     % (' dl--res' if tone else '', t + 16, 1 + w, t + 32))
        v = ('{:,.1f}'.format(val).rstrip('0').rstrip('.')
             if isinstance(val, float) and val != int(val) else '{:,}'.format(int(val)))
        parts.append('<text class="dt dt--v%s" x="%.1f" y="%d">%s%s%s</text>'
                     % (' dt--sig' if tone else '', 1 + w + 9, t + 29, prefix, v, unit))
    return _g(W, H, "plot", parts, caption)


def board(caption, up, down):
    """Two directions off one centre line. Gains run right, give-backs run
    left, so the spread is the picture rather than two lists to compare."""
    W, CX, PAD, ROW, BARMAX = 300, 150, 34, 24, 98
    rows = ([(m, _num(v), v, True) for m, v in up] +
            [(m, _num(v), v, False) for m, v in down])
    rows.sort(key=lambda r: -r[1])
    n = len(rows)
    H = PAD + n * ROW + 10
    parts = [
      '<text class="dt dt--hd" x="%d" y="14" text-anchor="end">Giving back</text>' % (CX - 9),
      '<text class="dt dt--hd" x="%d" y="14">Pulling away</text>' % (CX + 9),
      '<path class="dl dl--ax" d="M%d 22 V%d"/>' % (CX, PAD + n * ROW - 4),
    ]
    top = max(abs(r[1]) for r in rows) or 1
    for i, (market, val, disp, gain) in enumerate(rows):
        y = PAD + i * ROW
        w = max(5.0, abs(val) / top * BARMAX)
        if gain:
            parts.append('<rect class="df bfl" x="%d" y="%d" width="%.1f" height="12"/>'
                         % (CX, y, w))
            parts.append('<path class="dl" d="M%d %d H%.1f V%d H%d Z"/>'
                         % (CX, y, CX + w, y + 12, CX))
            parts.append('<text class="dt" x="%d" y="%d" text-anchor="end">%s</text>'
                         % (CX - 9, y + 9, market))
            parts.append('<text class="dt dt--v" x="%.1f" y="%d">%s</text>'
                         % (CX + w + 7, y + 9, disp))
        else:
            parts.append('<rect class="df bfl--sig" x="%.1f" y="%d" width="%.1f" height="12"/>'
                         % (CX - w, y, w))
            parts.append('<path class="dl dl--res" d="M%d %d H%.1f V%d H%d Z"/>'
                         % (CX, y, CX - w, y + 12, CX))
            parts.append('<text class="dt" x="%d" y="%d">%s</text>' % (CX + 9, y + 9, market))
            parts.append('<text class="dt dt--v dt--sig" x="%.1f" y="%d" text-anchor="end">%s</text>'
                         % (CX - w - 7, y + 9, disp))
    return _g(W, H, "board", parts, caption)


def flow(caption, nodes, signal=None):
    """A chain where each link causes the next. Drawn top to bottom so the
    labels have room, with the link that matters marked."""
    W, X, PAD, ROW = 300, 20, 18, 46
    n = len(nodes)
    H = PAD + (n - 1) * ROW + 26
    parts = []
    for i, node in enumerate(nodes):
        y = PAD + i * ROW
        sig = (node == signal)
        if i < n - 1:
            parts.append('<path class="dl" d="M%d %d V%d"/>' % (X, y + 7, y + ROW - 13))
            parts.append('<path class="dl" d="M%d %d L%d %d L%d %d"/>'
                         % (X - 4, y + ROW - 18, X, y + ROW - 12, X + 4, y + ROW - 18))
        parts.append('<circle class="df tip%s" cx="%d" cy="%d" r="%s"/>'
                     % (' tip--sig' if sig else '', X, y, '4.5' if sig else '3.2'))
        if sig:
            parts.append('<circle class="dl dl--res" cx="%d" cy="%d" r="8"/>' % (X, y))
        parts.append('<text class="dt%s" x="%d" y="%d">%s</text>'
                     % (' dt--sig' if sig else '', X + 18, y + 4, node))
    return _g(W, H, "flow", parts, caption)

def branch(caption, source, takes, result):
    """A drawn diagram: where a number starts, what peels off it, what is left.

    Emitted as .dwg/.dl line work so it draws itself when the panel goes live.
    """
    W, H = 300, 90 + len(takes) * 46 + 80
    spine_x = 52
    top_y, bot_y = 64, H - 62
    parts = []

    # the source block
    parts.append('<path class="dl" d="M18 18 H200 V46 H18 Z"/>')
    parts.append('<text class="dt dt--lg" x="30" y="37">%s</text>' % source)
    parts.append('<path class="dl" d="M%d 46 V%d"/>' % (spine_x, top_y))

    # each deduction peels to the right
    for i, (label, amt) in enumerate(takes):
        y = top_y + i * 46
        parts.append('<path class="dl" d="M%d %d C %d %d, %d %d, %d %d"/>'
                     % (spine_x, y, spine_x, y + 22, spine_x + 42, y + 10, spine_x + 96, y + 26))
        parts.append('<circle class="df tip" cx="%d" cy="%d" r="3"/>' % (spine_x + 96, y + 26))
        parts.append('<text class="dt" x="%d" y="%d">%s</text>' % (spine_x + 106, y + 29, label))
        if amt:
            parts.append('<text class="dt dt--sig" x="%d" y="%d" text-anchor="end">%s</text>'
                         % (W - 12, y + 29, amt))

    # the spine continues to what is left
    parts.append('<path class="dl" d="M%d %d V%d"/>' % (spine_x, top_y, bot_y))
    parts.append('<path class="dl dl--res" d="M18 %d H200 V%d H18 Z"' % (bot_y, bot_y + 30) + '/>')
    parts.append('<text class="dt dt--lg dt--sig" x="30" y="%d">%s</text>' % (bot_y + 20, result))

    return ('<figure class="art__fig dgm" data-dgm>'
            '<svg class="dwg dwg--ink dwg--branch" viewBox="0 0 %d %d" data-draw aria-hidden="true">'
            '<g class="dstep" data-step="0">%s</g></svg>'
            '<figcaption class="art__figcap">%s</figcaption></figure>'
            % (W, H, "".join(parts), caption))

def steps(caption, items):
    """A sequence whose parts need sentences, so the prose stays HTML and the
    drawing is the rail beside it: the node marks, the line grows down to the
    next one, and the reader watches the sequence build."""
    out = []
    for i, (n, t, d) in enumerate(items):
        out.append(
          '<li class="stp" style="--i:%d">'
          '<span class="stp__rail" aria-hidden="true"><i class="stp__dot"></i></span>'
          '<span class="stp__b">'
          '<span class="stp__n">%s</span>'
          '<span class="stp__t">%s</span>'
          '<span class="stp__d">%s</span></span></li>' % (i, n, t, d))
    return ('<figure class="art__fig dgm" data-dgm>'
            '<ol class="stps">%s</ol>'
            '<figcaption class="art__figcap">%s</figcaption></figure>'
            % ("".join(out), caption))


def keys(items):
    """Figures pulled out of the prose for a scanner."""
    out = "".join(
      '<div class="keyf%s" style="--i:%d"><span class="keyf__n">%s</span>'
      '<span class="keyf__t">%s</span></div>'
      % (' keyf--sig' if sig else '', i, n, t)
      for i, (n, t, sig) in enumerate(items))
    return '<div class="keys dgm" data-dgm>%s</div>' % out

# --------------------------------------------------------------------------
ARTICLES = [
{
 "slug": "costa-rica-gross-is-not-net",
 "tone": "forest", "motif": "keys",
 "kicker": "Costa Rica · Residential",
 "title": "A 7.6% yield that arrives as 5.5%.",
 "dek": "Costa Rica advertises gross. What reaches a foreign owner in the "
        "Central Valley is a different number, and the gap is the whole decision.",
 "date": "September 2026",
 "read": "7 min",
 "body": [
   p("Costa Rica is sold to foreign buyers on yield. The number quoted is almost always "
     "gross, and gross is a description of the rent, not of what you keep."),
   branch("Residential yield in San José, 2026. Gross is the rent. Net is what reaches "
          "an owner eight hours away.",
     "GROSS 7.5%",
     [("Management", "−0.7"), ("Maintenance", "−0.5"), ("Vacancy", "−0.4"),
      ("HOA", "−0.3"), ("Municipal tax", "−0.1")],
     "NET 5.5%"),
   p("National gross sits around 7.63% in Q2 2026 and San José around 7.5%, with most "
     "landlords between 6% and 9% depending on the neighbourhood. Net lands around 5.5%, "
     "and most standard investment properties deliver 4% to 6.5% once recurring costs are "
     "paid. Amenity-heavy buildings sit at the bottom of that range; professionally managed "
     "ones give up another slice for the privilege of not doing the work yourself."),
   pull("Five and a half per cent, in dollars, in a stable country, is a perfectly good "
        "answer. It is just not the answer on the brochure."),
   h2("Where the yield actually is"),
   ul(["San Pedro, beside the UCR campus — roughly 6% to 8%, student and staff demand.",
       "Rohrmoser, the non-trophy units — 5.5% to 7%.",
       "Curridabat, Freses and Granadilla — 5.5% to 7%.",
       "The Heredia and Belén border, near the corporate parks — 6% to 8%."]),
   p("Notice what is absent: the trophy addresses. Escazú and Santa Ana run $1,200 to "
     "$2,000 per square metre, and a three-bedroom in a gated community is $350,000 to "
     "$600,000. Those are good places to own a home. They are not where the yield is."),
   h2("Two things a foreign buyer should price in"),
   p("Liquidity first. Average days on market in San José is around 180. Well-priced stock "
     "in La Sabana, Rohrmoser or Escazú moves in 90 to 150. If your exit assumption is three "
     "months, it is wrong."),
   p("Then the buyer pool. About 40% of San José transactions involve an international "
     "buyer — which is healthy demand and also a warning. A market where nearly half the "
     "bids come from abroad is a market whose liquidity depends on conditions somewhere "
     "else."),
   keys([("7.63%", "National gross yield, Q2 2026", False),
         ("5.5%", "San José net, after costs", True),
         ("180 days", "Average time to sell", False)]),
   h2("What we would actually check"),
   ul(["Net, modelled line by line: HOA, management, maintenance reserve, vacancy, "
       "municipal tax, and the cost of being eight hours away.",
       "Whether the building's amenities are an asset or a monthly bill with a pool "
       "attached.",
       "Days on market for units that actually closed in that specific corridor.",
       "The rental demand source — students, corporate, tourism — and what happens to it "
       "in a soft year.",
       "Title and the concession question on anything near the coast, which is a different "
       "article and a longer one."]),
   note("Prices are expected to rise roughly 3% to 6% a year in dollar terms. That is the "
        "appreciation case, and it is reasonable. Just do not add it to a gross yield and "
        "call the total a return."),
 ],
 "sources": [
   ("Global Property Guide — Costa Rica gross rental yields",
    "https://www.globalpropertyguide.com/latin-america/costa-rica/rental-yields"),
   ("TheLatinvestor — San José rental yields 2026",
    "https://thelatinvestor.com/blogs/news/san-jose-rental-yields"),
   ("TheLatinvestor — San José real estate market analysis 2026",
    "https://thelatinvestor.com/blogs/news/san-jose-real-estate-market"),
   ("Costa Rica property prices by region 2026",
    "https://costaricaretirementvacationproperties.com/articles/real-estate-articles/costa-rica-property-prices-by-region-2026.html"),
 ],
},
{
 "slug": "reading-a-hotel-p-and-l",
 "tone": "forest", "motif": "keys",
 "kicker": "Hospitality · Operations",
 "title": "A hotel P&L has one line that tells you whether it is being run or just occupied.",
 "dek": "Occupancy flatters. RevPAR is honest. GOPPAR is the one an owner "
        "should actually be paid on.",
 "date": "September 2026",
 "read": "7 min",
 "body": [
   p("Every under-performing hotel we have looked at reported strong occupancy. Filling "
     "rooms is easy — you drop the rate until they fill. The question is what was left "
     "after."),
   steps("Read the statement in this order. Each line answers the one above it.",
     [("01", "Occupancy",
       "Rooms sold over rooms available. Tells you the building is busy. Tells you nothing "
       "about whether being busy was worth it."),
      ("02", "ADR",
       "Average daily rate. Occupancy and ADR move against each other; either alone can be "
       "bought with the other."),
      ("03", "RevPAR",
       "Revenue per available room — ADR times occupancy. The first line that cannot be "
       "gamed by discounting, because discounting shows up in it."),
      ("04", "TRevPAR",
       "Total revenue per available room, including food, beverage, spa, parking. Separates "
       "a hotel from a room-rental business."),
      ("05", "GOPPAR",
       "Gross operating profit per available room. What the asset actually produced before "
       "debt and ownership costs. This is the number to underwrite."),
      ("06", "Flow-through",
       "Of each extra dollar of revenue, how much reached GOP. Below about 40% on incremental "
       "revenue, the operation is leaking.")]),
   branch("Where room revenue goes before it becomes gross operating profit. The "
          "proportions vary; the order does not.",
     "TOTAL REVENUE",
     [("Rooms cost", "variable"), ("Channel commission", "15–20%"),
      ("Undistributed", "fixed"), ("Utilities", "fixed"), ("Maintenance", "deferred?")],
     "GOP"),
   pull("Occupancy is a vanity metric with a hospitality degree. GOPPAR is the job."),
   h2("The costs that move and the costs that do not"),
   p("Rooms cost is largely variable — housekeeping, linen, amenities, commissions. "
     "Undistributed cost is largely not — administration, sales, utilities, maintenance. "
     "That split is why a hotel at 55% occupancy and one at 75% are not the same business "
     "even at the same RevPAR."),
   p("Channel mix is where the quiet money goes. OTA commission at 15–20% on a large share "
     "of the book is a discount you pay whether or not you needed it. The direct-booking "
     "share is a P&L line disguised as a marketing metric."),
   h2("What we would actually check"),
   ul(["GOPPAR against the competitive set, not RevPAR. Two hotels with identical RevPAR "
       "can be twenty points apart on GOP margin.",
       "Flow-through on the last twelve months, which reveals whether growth is being "
       "converted or spent.",
       "Channel mix and the true cost of each channel, commission included.",
       "The maintenance reserve, and what was deferred to make last year look better.",
       "Whether the management agreement pays the operator on revenue or on profit. They "
       "behave differently, and only one of them is aligned with you."]),
   note("If you are buying a hotel on a broker's occupancy figure, you are buying the one "
        "number the seller can produce most cheaply."),
 ],
 "sources": [],
},
{
 "slug": "the-entitlement-that-ate-the-return",
 "tone": "forest", "motif": "gantt",
 "kicker": "Worked example · Entitlement",
 "title": "The deal did not fail. It just took nineteen months longer than the model.",
 "dek": "A worked example of an entitlement timeline, and why delay is the risk "
        "that quietly outranks cost.",
 "date": "September 2026",
 "read": "8 min",
 "body": [
   note("A worked example, not a client file. The sequence is typical; the months are "
        "illustrative."),
   p("Cost overruns get the attention because they arrive as invoices. Delay arrives as "
     "nothing at all — no letter, no line item, just another month where the carry runs and "
     "nothing is sellable."),
   p("On a levered deal, delay is usually the larger of the two."),
   steps("An entitlement sequence that was modelled at eleven months.",
     [("01", "Pre-application · modelled 1, took 2",
       "Staff are booked three weeks out. The first meeting produces a list of studies "
       "nobody budgeted."),
      ("02", "Studies · modelled 3, took 6",
       "Traffic, drainage, environmental, and a wetland delineation the seller swore was "
       "not needed. Two of them can run in parallel. The wetland one cannot."),
      ("03", "Formal submittal · modelled 1, took 1",
       "The only stage that behaved."),
      ("04", "Review cycles · modelled 3, took 9",
       "Three rounds of comments rather than one. Each round is a full review clock, not a "
       "continuation of the last."),
      ("05", "Public hearing · modelled 2, took 7",
       "Continued once at a neighbour's request, then again when a commissioner was absent. "
       "Hearings are calendars, not decisions."),
      ("06", "Recording and permits · modelled 1, took 5",
       "Conditions of approval had to be satisfied before recording, and two of them needed "
       "a utility company with its own queue.")]),
   keys([("11 mo", "Modelled", False), ("30 mo", "Actual", True), ("+19 mo", "Of carry nobody priced", False)]),
   h2("Why the model broke"),
   p("Not because any single step was unreasonable. Because the model assumed every step "
     "ran once, in sequence, at the posted duration — and entitlement is a queue of "
     "queues, each with its own clock and each able to restart."),
   pull("Nineteen months of carry on a levered basis is not a delay. It is the return."),
   h2("What we would actually do"),
   ul(["Model three timelines: posted, realistic, and bad. Underwrite the middle one and "
       "survive the third.",
       "Ask the jurisdiction how many review rounds the last five comparable applications "
       "took. It is public, and it is the single most predictive number available.",
       "Identify which studies can run in parallel and start those the week of the LOI, "
       "not after closing.",
       "Price the carry per month explicitly so the cost of a slipped hearing is visible on "
       "the page rather than absorbed.",
       "Negotiate the contingency period against the realistic timeline, not the posted one.",
       "Know which conditions of approval depend on a third party, because those are the "
       "ones with no deadline at all."]),
   note("This deal still made money. It made roughly a third of what the model said, which "
        "is a different conversation to have before an investor's capital is in than after."),
 ],
 "sources": [],
},
{
 "slug": "build-to-rent-is-a-different-business",
 "tone": "forest", "motif": "doors",
 "kicker": "Build-to-rent · Underwriting",
 "title": "Build-to-rent is not building houses and then renting them.",
 "dek": "The product, the cost plan and the exit are all different from "
        "for-sale. Underwrite it as for-sale and the margin disappears on handover.",
 "date": "September 2026",
 "read": "7 min",
 "body": [
   p("The pitch is tidy: you are already building houses, rent them instead of selling "
     "them, and keep the income. The arithmetic is not tidy at all, because almost every "
     "assumption you carry over from for-sale is wrong in the new business."),
   h2("Three things change on day one"),
   steps("What actually differs, and what it does to the model.",
     [("01", "The buyer is a yield, not a family",
       "A for-sale house is priced against comparable sales. A build-to-rent house is "
       "priced against a capitalisation rate on its net income. Those two numbers move "
       "independently, and only one of them cares about your finish level."),
      ("02", "Spec follows durability, not taste",
       "The cost plan changes shape: harder surfaces, simpler mechanicals, fewer bespoke "
       "items, longer-life finishes. Some line items go up. The ones that exist to win a "
       "weekend buyer come out."),
      ("03", "Operations start before completion",
       "Leasing, maintenance and management are a business you now own from the first "
       "certificate of occupancy. In for-sale they were somebody else's problem on closing "
       "day.")]),
   pull("In for-sale you are paid once, on the highest price. In build-to-rent you are paid "
        "every month, on the lowest cost of keeping it full."),
   h2("The arithmetic that actually governs it"),
   p("Value is net operating income divided by cap rate, so every dollar of annual NOI is "
     "worth many dollars of value at exit. At a 6% cap, $1 of recurring monthly saving is "
     "worth roughly $200 of asset value. That is why the durable dishwasher is not a "
     "preference — it is a capital decision."),
   p("It also means the vacancy and turnover assumptions matter more than the construction "
     "contingency. A one-point move in stabilised occupancy will usually outweigh a "
     "reasonable overrun on the build."),
   h2("What we would actually check"),
   ul(["The exit cap rate, stress-tested a full point in the wrong direction.",
       "Turnover cost per unit and expected tenure, because those two numbers set the "
       "operating floor.",
       "Whether the spec was written for a renter or inherited from the last for-sale plan.",
       "Who leases and manages it, at what cost, and whether that cost is in the model at "
       "all.",
       "Whether the site works as for-sale if the rental thesis fails. If it does not, the "
       "downside has no floor."]),
   note("Build-to-rent is a good business run as a business. It is a poor one run as a "
        "for-sale project that changed its mind after the drawings were finished."),
 ],
 "sources": [],
},
{
 "slug": "setting-rent-and-defending-it",
 "tone": "forest", "motif": "keys",
 "kicker": "Operations · Rentals",
 "title": "The rent you set in week one is the rent you argue about for five years.",
 "dek": "Most owners price to fill, then spend the tenancy trying to recover. "
        "Here is the other order.",
 "date": "September 2026",
 "read": "6 min",
 "body": [
   p("An empty unit is loud. Every day it sits there, the pressure to drop the ask rises, "
     "and the drop feels small — fifty dollars, seventy-five, whatever ends the discomfort."),
   p("Run the arithmetic before you do it, because it is rarely the trade people think."),
   bars("A $1,800 unit: what a $75 discount costs against what two extra weeks empty cost, "
        "over a two-year tenancy.",
        [("Discount of $75/mo", 1800, True), ("Two weeks vacant", 900, False)], prefix="$"),
   p("Seventy-five dollars a month across twenty-four months is $1,800. Two more weeks of "
     "vacancy at $1,800 a month is about $900. Holding the rent and waiting a fortnight is "
     "the cheaper outcome, and it is the one that feels worse."),
   pull("Vacancy is a one-off cost. A discount is an annuity you granted to someone else."),
   h2("Set it on evidence, not on the last listing"),
   ul(["Comparable <em>closed</em> leases, not asking rents. Asking rents are opinions.",
       "Same building where possible, then same block, then same school zone. Not the "
       "neighbourhood average.",
       "Adjust for what a tenant actually pays for: parking, in-unit laundry, outdoor "
       "space, which floor, whether utilities are included.",
       "Check what concessions the comps carried. A month free on a twelve-month lease is "
       "an 8% discount wearing a disguise."]),
   h2("Then defend it at renewal, which is where the money is"),
   p("The cheapest rent increase in this business is the one on a tenant who is already "
     "there. No turn cost, no vacancy, no make-ready, no listing. And it is the one most "
     "often skipped, because nobody owns the calendar item."),
   p("Three units left unreviewed at $75 below market is $2,700 a year, and it compounds, "
     "because next year's increase is calculated off this year's mistake."),
   keys([("$1,800", "Cost of a $75 discount over two years", True),
         ("~$900", "Cost of two extra weeks vacant", False),
         ("90 days", "When the renewal conversation should start", False)]),
   h2("What we would actually check"),
   ul(["Whether anyone is contractually responsible for reviewing rent at renewal, and on "
       "what date.",
       "Days-to-lease for the last three vacancies, which tells you whether the price was "
       "right or merely accepted.",
       "The concession history in the comp set, not just the headline rents.",
       "Renewal rate. Below about 50% you do not have a pricing problem, you have an "
       "operations problem."]),
 ],
 "sources": [],
},
{
 "slug": "two-countries-one-rent-number",
 "tone": "forest", "motif": "stack",
 "kicker": "United States · Markets",
 "title": "There is no American rental market. There are about a hundred and sixty-five.",
 "dek": "Ninety-two of them are posting negative rent growth while the Twin Cities "
        "run at +4.6%. The national figure describes neither.",
 "date": "September 2026",
 "read": "9 min",
 "body": [
   p("National rent fell about 1.5% year over year through February 2026. That single "
     "number is the least useful fact in this piece, because 92 of the 165 major metros are "
     "negative and the rest are not, and the gap between the two ends is nearly ten points."),
   p("Read the national figure and you will underwrite the wrong half of the country."),
   board("Year-over-year metro rent growth, 2026. Nearly ten points separate the Twin "
         "Cities from San Antonio.",
     [("Twin Cities", "+4.6%"), ("Chicago", "+4.1%"), ("Detroit", "+4.0%"),
      ("Cleveland", "+4.0%"), ("St. Louis", "+4.0%"), ("Kansas City", "+3.9%"),
      ("Philadelphia", "+2.9%")],
     [("San Antonio", "−5.1%"), ("Austin", "−4.0%"), ("Denver", "−3.1%"),
      ("Tampa", "−2.8%"), ("Phoenix", "−2.7%")]),
   h2("This is a supply story, not a demand story"),
   p("The instinct is to read the losing column as places people are leaving. They are not. "
     "Austin, Denver, Phoenix and Tampa still take population. What they also took was an "
     "enormous delivery pipeline, and the pipeline landed into a market that had already "
     "priced the growth."),
   p("Concessions did the rest. A quoted rent with two months free is not that rent, and it "
     "does not renew at that rent either."),
   pull("The Midwest did not win. It simply never got a supply wave, so nothing had to be "
        "given back."),
   p("The winning column is mostly markets with limited new deliveries and an affordability "
     "advantage that never went away. The Northeast is projected to run 4–5% annually and "
     "the Midwest 3–4.5%. Neither is exciting. Both are bankable."),
   h2("Land tells the same story a year earlier"),
   p("Cross the rent table against finished-lot supply and the pattern repeats. Austin, "
     "Atlanta and Denver read as significantly oversupplied on lots. Los Angeles and "
     "Philadelphia still do not."),
   flow("Lot supply leads rent by roughly a cycle. By the time rent turns, the land market "
        "has already told you.",
     ["Lots loosen", "Builders slow", "Deliveries land", "Concessions", "Rent gives back"],
     signal="Lots loosen"),
   p("That is the practical value of watching land even if you never buy any: it is the "
     "earliest honest signal in the chain."),
   h2("What this changes about a deal"),
   ul(["<strong>Underwrite the submarket, never the metro.</strong> Nashville and Austin "
       "both contain streets that are tightening. The metro average will not find them.",
       "<strong>Ask what has been delivered, not what is planned.</strong> Planned units "
       "get cancelled. Delivered units compete with you on the day they open.",
       "<strong>Treat a falling metro as an entry, not a veto.</strong> San Antonio at "
       "−5.1% is a bad place to own a lease-up finished last year and a reasonable place to "
       "buy one from someone who did.",
       "<strong>Check concessions in the comps.</strong> In the losing column they are "
       "doing a lot of quiet work on the quoted numbers.",
       "<strong>In the winning column, check why.</strong> Limited deliveries can mean a "
       "constrained market or a market nobody wants to build in. Those are different."]),
   keys([("92 / 165", "Major metros with negative rent growth", True),
         ("+4.6%", "Twin Cities, the strongest", False),
         ("−5.1%", "San Antonio, the weakest", False)]),
   note("We do not have a favourite market. We have a method, and it produces different "
        "answers in different places — which is the point. If someone tells you one region "
        "is the play right now, ask them what the delivery pipeline does in 2027."),
 ],
 "sources": [
   ("CRE Daily — Midwest leads 2026 US multifamily rent growth as Sun Belt lags",
    "https://www.credaily.com/briefs/midwest-leads-2026-us-multifamily-rent-growth-as-sun-belt-lags/"),
   ("Yardi Matrix — National multifamily market report",
    "https://www.yardimatrix.com/blog/national-multifamily-market-report/"),
   ("National Apartment Association — 2026 apartment housing outlook",
    "https://naahq.org/news/2026-apartment-housing-outlook"),
   ("Apartment List — National rent report",
    "https://www.apartmentlist.com/research/national-rent-data"),
   ("ResiClub — Lot inventory by metro",
    "https://www.resiclubanalytics.com/p/austin-atlanta-denver-boast-significantly-oversupplied-lot-inventory-homebuilders"),
 ],
},
{
 "slug": "reading-a-renovation-bid",
 "tone": "forest", "motif": "gantt",
 "kicker": "Worked example · Houston, Texas",
 "title": "Three bids, forty thousand dollars apart, for the same house.",
 "dek": "How we read a renovation estimate, what the spread actually means, "
        "and the line items where the money quietly leaves.",
 "date": "September 2026",
 "read": "9 min",
 "body": [
   note("A worked example, not a client file. The house, the bids and the numbers "
        "are illustrative and chosen because they are typical of the corridor."),
   p("A 1960s ranch inside the Beltway. Twenty-two hundred square feet, original kitchen, "
     "one bathroom down to the studs already, a roof with maybe three years left. The plan "
     "is a full cosmetic renovation plus a bathroom addition, then a sale."),
   p("Three general contractors walk it. The bids come back at $118,000, $142,000 and "
     "$157,000. Most people take the middle one because the low one feels risky and the "
     "high one feels greedy. That is not reading a bid. That is picking one."),
   h2("The spread is information, not noise"),
   p("A forty-thousand-dollar spread on the same scope means the three contractors are not "
     "pricing the same job. Before comparing a single number, we make them comparable."),
   steps("How we get three bids onto the same basis.",
     [("01", "Normalise the scope",
       "One schedule of work, line by line, in the same order for all three. Anything a "
       "bidder excluded gets added back at someone else's price so every total covers the "
       "same house."),
      ("02", "Separate allowances from quotes",
       "An allowance is a guess with a number on it. Tile at $4/sq ft, appliances at "
       "$6,000, fixtures at $2,400 — those are placeholders, and they are where a low bid "
       "gets its low."),
      ("03", "Price the exclusions",
       "Permits, dumpsters, portable toilet, temporary power, final clean. Cheap "
       "individually, four to seven thousand together, and routinely left off."),
      ("04", "Test the schedule against the carry",
       "Twelve weeks and twenty weeks are different deals. At a typical hard-money rate "
       "the extra two months can cost more than the gap between two of the bids."),
      ("05", "Check the contingency is real",
       "On a sixty-year-old house, ten per cent is optimistic. We budget fifteen and hope "
       "to hand it back."),
      ("06", "Read the payment schedule",
       "Front-loaded draws transfer risk to you. We want draws that trail completed work, "
       "with a retainage that survives to the punch list.")]),
   pull("A low bid is not a cheaper house. It is usually the same house with fewer things "
        "written down."),
   h2("Where the money actually leaves"),
   p("Once the three are on one basis, the $118,000 bid became $139,000 — allowances at "
     "realistic numbers, permits added, and a twenty-week schedule instead of twelve. The "
     "$157,000 bid became $151,000, because it already included the things the others left "
     "out. The real spread was twelve thousand, not forty."),
   keys([("$139k", "Low bid, normalised", False),
         ("$151k", "High bid, normalised", False),
         ("$12k", "The actual spread", True)]),
   p("That is a decision you can make. Forty thousand is not — it is three documents "
     "describing three different projects."),
   h2("What we do on a renovation, in practice"),
   ul(["Walk the scope and write it once, so every bidder prices the same thing.",
       "Solicit and level the bids, including the exclusions nobody mentions.",
       "Select the contractor on schedule certainty and crew availability, not price alone.",
       "Hold the draw schedule, inspect before releasing, keep retainage.",
       "Weekly reporting: where we are, what is next, what it costs.",
       "Change orders priced and approved before the work, not discovered on the invoice."]),
   flow("A change order that follows this path costs what it says. One that skips a step "
        "arrives as a surprise on a draw request.",
     ["Issue found", "Priced", "Approved", "Scheduled", "Built", "Inspected", "Drawn"],
     signal="Approved"),
   h2("The same discipline scales"),
   p("Nothing above is specific to a cosmetic renovation. A ground-up build has the same "
     "structure with more line items and a longer schedule: normalise the scope, separate "
     "allowance from quote, price the exclusions, test the programme against the carry, "
     "and hold the draws against completed work."),
   note("If you have bids on your desk and cannot tell whether they describe the same job, "
        "send them. Levelling three bids is a couple of hours of work and it is the "
        "cheapest hours in the project."),
 ],
 "sources": [],
},
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
   bars("The fee saving set against what the same operating year actually leaked. "
        "Every bar but the first is money the fee negotiation never touched.",
        [("Fee saved, 8% \u2192 6%", 3456, True),
         ("Lost rent, two turns", 4600, False),
         ("Delinquency", 3600, False),
         ("Rent never raised", 2700, False),
         ("Make-ready", 2400, False)], prefix="$"),
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
   keys([("$3,456", "Saved by arguing the fee down two points", False),
         ("$13,300", "Leaked elsewhere in the same year", True),
         ("3.8\u00d7", "The second number over the first", False)]),
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
   steps("Five options, always. Most owners only seriously consider the one they "
         "happen to be standing in.",
     [("01", "Hold",
       "Defensible when the asset still does what you bought it to do and the capital has "
       "nowhere better to be. Say that out loud and it stops being a default."),
      ("02", "Improve",
       "Capital in, income out. Only if the return on that specific spend beats the return "
       "on selling and redeploying."),
      ("03", "Refinance",
       "Takes chips off the table without triggering tax or losing the asset. Constrained "
       "by rates and by what the asset now appraises at."),
      ("04", "Sell",
       "Clean, taxable, final. The only option that actually tests whether the value you "
       "have been reporting yourself is real."),
      ("05", "Reinvest",
       "Sell and roll, with the structure decided before the clock starts, not after.")]),
   pull("The question is never \u201cis this a good asset\u201d. It is \u201cis this the "
        "best available home for this capital, today\u201d. Those have different answers."),
   h2("Why the exit belongs in the acquisition model"),
   p("A decision made at acquisition shows up years later in the operating budget, and the exit "
     "is the clearest case. Financing structure decides whether refinancing is even available. "
     "Entity structure decides what selling costs you. The debt maturity decides when you are "
     "forced to act, and being forced is how people sell into a bad quarter."),
   flow("What deferring the decision actually sets in motion. Nothing here is a surprise; "
        "each link is visible years ahead of the one that hurts.",
     ["Decision deferred", "Debt matures", "Options narrow to one",
      "Forced to act", "Sell into a bad quarter"],
     signal="Debt matures"),
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
         ("Envigado", 140, False), ("Sabaneta", 120, True)], prefix="$", unit="/ft²"),
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

   branch("Where the $140,000 spread goes. The article\u2019s own range for these costs is "
          "$70,000\u2013$90,000 in total, so what is left is $50,000\u2013$70,000 \u2014 "
          "before the access discount takes its cut of the sale price too.",
          "SPREAD $140,000",
          [("Culvert and drive", ""),
           ("Survey and legal", ""),
           ("Plat and plan review", ""),
           ("Closing \u00d7 4", ""),
           ("Four extra months of carry", "")],
          "$50\u201370k LEFT"),   keys([("4", "The lot count that triggered the review", True),
         ("6 \u2192 10 mo", "Hold, modelled against actual", False),
         ("$50\u201370k", "Spread left, before the access discount", False)]),
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
  <header class="ah">
      <div class="ah__rail" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
      <div class="ah__inner">
        <p class="label ah__kicker rv">%s</p>
        <h1 class="ah__title rv" data-mask style="--rv-delay:60ms">%s</h1>
        <p class="ah__dek rv" style="--rv-delay:140ms">%s</p>
        <p class="ah__meta rv" style="--rv-delay:200ms">%s · %s read</p>
      </div>
  </header>
  <div class="wrap art__wrap">
    <div class="art__body">
      %s
    </div>
    <aside class="art__pin" data-pin aria-hidden="true"></aside>
    %s
    <aside class="art__cta">
      <h2>Have one of these on your desk?</h2>
      <p>Send it. We will underwrite it against the model it actually fits and come back inside 48 hours with a recommendation: proceed, renegotiate or pass.</p>
      <a class="btn btn--signal" href="mailto:hello@pangeaventures.com?subject=A%%20deal%%20to%%20underwrite">Send us the deal</a>
    </aside>
    <p class="art__back"><a href="index.html">← All field notes</a></p>
  </div>
</article>
''' % (a["kicker"], a["title"], a["dek"], a["date"], a["read"], body, src)
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
    return (HEAD.format(title="Field Notes", site=SITE,
            dek="Field notes on land, construction, hospitality and rental assets "
                "across the United States and Latin America.")
      + '''
<section class="section art-index">
  <div class="wrap">
    <div class="sec-head rv"><p class="label">Field Notes</p></div>
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
