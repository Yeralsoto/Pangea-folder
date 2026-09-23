# Pangea Ventures International — website

Phase 2 of the brand rollout: the full site the Brand Book and Brand Guidelines
sketch as a hero mock-up on page 30 / 14.

Static HTML, CSS and vanilla JS. No build step, no dependencies, no framework.
Deploy by uploading the folder to any static host (Netlify, Vercel, Cloudflare
Pages, S3, or plain nginx).

## Run locally

```bash
python3 serve.py 4173
```

Then open <http://localhost:4173>.

`.claude/launch.json` is an **attach** config, not a launch one: it points the
preview at `http://localhost:4173` rather than spawning its own copy. Start
the server yourself with the command above; the preview connects to it. This
avoids a second process fighting for the port.

## Structure

```
index.html              The whole page. One document, one story.
assets/css/pangea.css   Tokens, layout, components, motion.
assets/js/pangea.js     Progressive enhancement only.
assets/img/topo.svg     Hero contour field (generated, do not hand-edit).
assets/js/lifecycle-3d.js     The rotating site model in section 03 (WebGL).
assets/js/lifecycle-model.js  2D fallback for the same model.
assets/vendor/three.module.min.js  Three.js r160, MIT. Vendored on purpose.
assets/logos/           SVG lockups (+ PNG in assets/logos/png).
tools/make_topo.py      Regenerates assets/img/topo.svg.
serve.py                Local static server for preview.
```

## The hero

Built to the approved hero on Brand Book p.30 / Guidelines p.14: the Forest
panel inset in a Bone frame, the reversed lockup at full size, four nav links
and no button in the bar, a Bone-filled primary action with an outlined
secondary, and a topographic contour field behind it all.

The contour field is real topography, not decoration: `tools/make_topo.py`
evaluates a smooth terrain function and traces its contour lines with marching
squares, so the lines nest around high ground and run long and parallel across
the flats. Retune the peaks in `field()` and regenerate:

```bash
python3 tools/make_topo.py assets/img/topo.svg
```

On Forest grounds the primary action is Bone, per the mockup. Terracotta stays
the one signal on Bone grounds and in the data.

## The narrative spine

The page is built to be read top to bottom as one argument, not browsed as a
set of panels.

| # | Section | What it does |
|---|---------|--------------|
| — | Hero | The primary tagline, on Deep Forest. |
| 01 | Our story | The supercontinent breaks apart. Real continent silhouettes, pinned and centred, splitting and drifting to today's map as the text scrolls past. |
| — | Positioning | "Most real estate firms are paid to close a transaction." |
| 02 | What we believe | The six beliefs. |
| 03 | The full cycle | Five stages with a live progress meter, beside a rotating site model that builds from raw land to an operating hotel as you read. |
| 04 | What we build | Land, Building, Hospitality, Rentals — four written sections, each with its own drawn plat, section or elevation that draws itself on entry. |
| — | Every asset type | The nine classes as a typographic register. |
| — | Markets | Four markets as an editorial register — place, coordinate, one sentence. No cards. |
| 05 | Who we work with | Each client type, what they arrive with, and what we actually do. |
| 04 | Services | Five lines, rates in expandable panels. |
| — | Service standards | 1 day · 48 hours · 5 days · Same day. |
| — | The disclosure block | A live Parcel 4-37 block, rows landing in order. |
| — | The symbol | Spire, wings and open arch, isolated on hover or tap. |
| — | Founders / Contact | Erin Berger and Yeraldin Soto. |

## The Americas coverage map

`tools/make_americas.py` draws the Markets map in the same language as the
Pangea map in section 01 — one landmass, sand on Forest, hairline seams — so
the two read as the same system.

It says two different things, and the distinction is the point:

- **On the ground** (terracotta, solid) — a market we work in ourselves.
- **We underwrite here** (sand, hollow) — a market we will model but not
  operate.

That is the honest version of a coverage map. It is not a client-density map,
and it does not imply work we have not done. Pins are real coordinates and
drop in sequence once the map is on screen.

## Corners and grounds

Two tokens carry every corner, so nothing drifts:

- `--r-sm: 7px` — buttons, controls, focus rings
- `--r-md: 12px` — panels, images, blocks, the model canvas

There are no hard-coded radii left in the stylesheet. Every dark block uses
`var(--forest)`; verified identical at `rgb(39,55,45)` across the footer, the
model canvas, the coverage map and the article bands.

## The lockup, and why the bar does not use the full one

The brand book sets a 140px minimum width for the horizontal lockup. At
navigation scale the bar was rendering it 86–120px wide — under the minimum —
and at that size "VENTURES INTERNATIONAL" is roughly two pixels tall and
cannot be read.

The bar now uses the **symbol beside a wordmark-only mark**, which is legible
at every size it appears. The full lockup, subline and all, stays in the
opening and the footer where it has room.

`assets/logos/pangea-wordmark-only-{white,bone,forest}.svg` are derived from
the supplied wordmark artwork by cropping the viewBox to the PANGEA row —
nothing distorted, recoloured or retyped. **Worth adding to the official kit**,
since every brand hits this problem the first time it builds a nav.

## Navigation

- **Desktop (≥1024px):** top-level items — The firm, The work, Engage — each
  opening its own submenu on click, plus Insights as a direct link. One open
  at a time; click away or Escape closes.
- **Phone:** everything in the burger, full screen.
- Rates are no longer splashed across the menu. They live inside Engage →
  Services & rates, where someone looking for them will go.

## Navigation rules

- **Every page carries the mark, and the mark always goes home.** The homepage
  logo links to `#top`; every `insights/` page links to `../index.html`.
  Footer logos link home too.
- One CSS trap caused a real bug here: `.nav__logo .is-dark` was positioned
  `absolute` so it could crossfade over `.is-light` on the homepage. Article
  pages ship a single mark, so the link collapsed to zero height and the logo
  vanished. The rule is now `.is-light + .is-dark`, which only lifts the dark
  mark out of flow when it is actually stacked on another.
- `tools/check_links.py`-style verification is run as part of the build notes:
  all internal hrefs resolve.

## The opening

A Forest curtain, the mark, the wordmark, the line, then it lifts to the hero.
**Once per session** — it is a greeting, not a toll booth — and any click, key,
scroll or tap skips it immediately. Removed entirely under
`prefers-reduced-motion`.

## Reading experience (articles)

Long text should arrive, not confront:

- A **section rail** on the left, built from the article's own headings, marking
  where you are as you scroll. Appears above 1152px; the article is unchanged
  below that.
- **Blocks arrive as they enter** — paragraphs, headings, lists, pull quotes,
  figures — rather than sitting there as a wall.
- **Bar comparisons fill** when they land, plotting only values we have.
- A **key-figure strip** (`.keys`) pulls numbers out of the prose so a scanner
  still gets the argument.

Urgency here comes from the material being current and dated, not from
countdowns or pressure devices. The brand book rules out pushy and salesy, and
a firm selling "truth on time" cannot manufacture scarcity.

## Motion

Deliberately quiet, and all of it off under `prefers-reduced-motion`:

- A terracotta hairline at the top reports read progress.
- Major headings arrive word by word from behind their own baseline.
- Section rules draw from the left rather than fading in.
- Figures count up when they land.
- Nothing loops, nothing bounces, nothing slides in from the side.

## The cycle (homepage)

`assets/js/cycle.js` draws the five stages as a ring, with a runner travelling
it continuously so the loop reads as a loop rather than a list. Hover, click
or tab a stage to hold it; it releases after six seconds and resumes.

Each asset type is tagged with **every stage it belongs to**, not one:
you underwrite all nine at Evaluate, build some at Create, run the income ones
at Operate, and exit nearly all at Optimize. Holding a stage lights only what
belongs there.

The viewBox is padded to `-78 -30 476 380` because the stage labels sit 46
units beyond the ring — with `overflow:visible` they painted over the panel
next to them.

## The drawings (section 04)

Land, Building, Hospitality and Rentals each carry a technical drawing —
a plat, a section, two elevations — generated by `tools/make_drawings.py`
as inline SVG.

They are **staged sequences, not single reveals**. Groups carry `data-step`;
the sequencer releases them in order, each step's strokes drawing themselves
from their own path length, shortest first, then its fills, labels and any
counter. A caption under the drawing names what just appeared and changes
with each step. The last step holds as the informative state.

| Drawing | What it teaches, step by step |
|---------|-------------------------------|
| Land | 18.4 acres → frontage on one road → six numbered lots → three back the creek |
| Building | Grade → footing and slab → frame → roof at 6:12 → dried in |
| Hospitality | Five levels → forty rooms → glazed → 93% sold, three vacant |
| Rentals | Four units → doors → eight windows → three let, one turning |

**Terracotta marks what is wrong, not what is right.** In the hotel it is the
three vacant rooms out of forty; in the rentals it is the unit that is
turning. That keeps the accent to a few per cent of the drawing, and it is
what the brand book means by "the single number, action or risk that matters".
It also keeps the diagrams honest: 37 of 40 really is 93%, and 3 of 4 really
is 75%.

These are drawings, not more 3D, on purpose: plats, sections and elevations
are what the firm actually produces.

## The site model (section 03)

A site model on a turntable, rendered in WebGL with Three.js: a real sun with
soft shadows, a sky/ground hemisphere bounce, a procedural environment map so
the glass and plaster have something to reflect, physically-based materials
and ACES tone mapping. It reads as an architectural render rather than a
diagram.

**The library is vendored**, not loaded from a CDN: `assets/vendor/three.module.min.js`,
Three.js r160, MIT, 670 KB on disk and about 167 KB gzipped. The site has no
external runtime dependency and works offline.

**There is a fallback.** `lifecycle-model.js` draws the same model on a 2D
canvas — hand-rolled vertices, rotation about Y, perspective projection,
painter's depth sorting, no dependency. It starts when WebGL is unavailable,
when the 3D module throws, and when the module never loads at all (a failed
import is caught by a timer, so the panel is never left empty). Because a
canvas that has issued a WebGL context can never return a 2D one, the
fallback is handed a fresh canvas element.

Only a handful of rooms are lit. Terracotta is the signal, not the cladding —
a facade of glowing windows would blow the brand's ≤8%.

**The canvas is transparent on purpose.** ACES tone mapping would push a
Forest clear colour off `#27372D`, leaving the panel a shade away from every
other Forest surface on the site. The canvas clears to alpha 0 and CSS paints
`var(--forest)` behind it, so the match is exact — verified as
`rgb(39,55,45)` on both.

The model reports the **construction step**, which is finer than the five
stage names beside it:

| phase | step |
|-------|------|
| 0.00 | Raw parcel · one road frontage |
| 0.55 | Boundary walked, topography shot |
| 0.95 | Plat: setbacks, yield and access |
| 1.30 | Site cleared, building pad graded |
| 1.52 | Access road in, services trenched |
| 1.74 | Footings and slab poured |
| 1.95–2.48 | Structure rising, one level at a time, to topped out |
| 2.70 | Envelope closed |
| 2.92 | Glazed |
| 3.12 | Terrace, parking and landscape |
| 3.34 | Handover · the asset starts operating |
| 3.80 | Stabilised · held, or sold |

Levels go up individually rather than the whole frame scaling, which is the
part that reads as building rather than as a box being stretched. Trees and
cars are there for scale, not decoration — without them the massing has no
size.

Both renderers are driven by `phase` (0 → 4), read from the position of the five `.stage`
elements, so the model and the written stages never drift apart:

| phase | stage | what is drawn |
|-------|-------|----------------|
| 0 | Identify | Bare parcel, boundary, ground contours |
| 1 | Evaluate | Plat lines, setbacks, yield |
| 2 | Create | Structural frame at full height, six plates |
| 3 | Operate | Solid massing, glazing, lit rooms, terrace |
| 4 | Optimize | Stabilised, set-back crown |

Walls are lit by a sun fixed in *camera* space, so whichever face turns toward
the viewer is the one that lights up — that is what makes it read as an object
rather than a flat sticker. Terracotta appears only in the lit rooms.

The canvas animates only while it is on screen, and pins to the top on narrow
screens so the transformation plays while the stages are read. Under
`prefers-reduced-motion` it draws one static frame of the finished asset.

## Staying distinct from yeraldinsoto.com

They are separate identities and must not read as the same site. The risk is
real: that site runs a cream ground, a high-contrast display serif
(Bodoni / Cormorant / Cinzel) and an amber-terracotta accent at #B5603A —
close neighbours to Bone, Newsreader and Terracotta #C46738.

The separation is deliberate, not accidental:

- **No cards.** Asset types, markets and clients are hairline registers, not
  boxes. A rule separates two things more quietly than a card, and it keeps
  the page from reading as software.
- **Forest leads, not cream.** The hero, the story, the asset grid, the
  disclosure block, the contact and the footer are all Deep Forest, with
  Umber carrying the markets. A visitor's first and last impression is dark
  green, where yeraldinsoto.com is cream throughout.
- **Terracotta is rationed.** It marks the active stage, risk, the one figure
  in the disclosure block and the lit rooms in the model. Nowhere else. It is
  never a surface, a heading colour, or a button on a light ground.
- **Documentary, not editorial.** Left-aligned, rule-driven, numbered
  sections, uppercase labels, tabular figures, coordinates. Newsreader is set
  tight (-0.025em) so it reads as an investment memorandum rather than a
  fashion masthead.
- **Geist, not a geometric sans.** Precise grotesk for every figure and label.

If either brand moves, re-check this section first.

## Brand compliance

- **Colour** is `03 Colors/pangea-tokens.css`, unchanged, as CSS custom
  properties. Roles are respected: Terracotta is the one signal, Clay carries
  text-size accents, Mineral Gold and Warm Sand are never text on Bone.
- **Type** is Newsreader 300/400 (display) and Geist 400/500 (text and
  figures), from Google Fonts, on the 1.25 scale with tabular figures and
  −0.02em tracking above 31px.
- **The wordmark is never typed.** Every instance of PΛNGEΛ on the page is the
  supplied SVG artwork.
- **Copy** is taken from `09 Copy/Pangea Brand Copy.txt` and the Brand Book.
  The few connective lines written for the site follow the voice rules and
  avoid every word on the never-use list.
- The Parcel 4-37 disclosure block is labelled **Example** — it is the brand's
  specimen, not a live deal.

## Accessibility

- Contrast follows the palette's documented WCAG 2.1 ratios.
- The disclosure categories carry a shape as well as a colour, so the block
  still reads in black and white.
- `prefers-reduced-motion` disables the plate drift, the reveals and the
  staggered rows; nothing is hidden behind an animation.
- Full keyboard support on the menu, the services accordion and the symbol
  anatomy. With JavaScript off, every word on the page is present and visible.

## Insights library

`tools/make_insights.py` is the single source. Every article page, the
`insights/` index and the homepage band are written from one `ARTICLES` list,
so they cannot drift. Adding a piece means adding an entry and re-running it.

Eight of a planned fifteen are written, and they deliberately span the whole
cycle rather than clustering on land:

| Piece | Stage | Sourced |
|-------|-------|---------|
| For the first time since 2022, more apartments were absorbed than built | Multifamily | 4 |
| A short-term rental that cannot get a permit is worth nothing | Operate · STR | 3 |
| The bid you get is not the budget you wrote | Create · construction | 4 |
| The eight per cent is not the cost of property management | Operate · PM | worked example |
| Plan the exit before you sign the purchase agreement | Optimize · disposition | framework |
| The lot shortage ended | Identify · land | 4 |
| Medellín is not one market | Evaluate · residential | 4 |
| The split that looked good and wasn't | Worked example · land | labelled |

Three of eight are land. The rest are multifamily, short-term rentals,
construction, property management and disposition — which is the point: the
library has to demonstrate the full cycle, not assert it.

**Rules for this library, which matter more than the word count:**

- Every figure is sourced and linked. Where a number could not be verified it
  does not appear.
- Worked examples are labelled as worked examples. They are illustrative and
  typical; they are not client files, and they never imply a deal we did.
- Bar comparisons only plot values we actually have. No interpolated points,
  no invented trend lines.

Still to write (7): reading a hospitality P&L; Costa Rica Central Valley;
build-to-rent maths; the entitlement timeline that ate the return; setting
rent and defending it; when to refinance rather than sell; training an
operating team.

## Not built yet

- Spanish version (`Claridad en todo el ciclo inmobiliario.` — the approved
  ES copy is in the brand kit, ready to drop in).
- Seven of the fifteen insight pieces.
- **`hello@pangeaventures.com` has to exist.** Every call to action on the
  site points at it. Nothing else does.

## No names, by decision

The site speaks as the firm. There is no founders section, no bylines and no
personal addresses — one shared inbox instead. Worth knowing the trade-off:
for a new firm, named people are usually the strongest credibility available,
because trust attaches to people before it attaches to a company. If that
changes, the founders section is in git history and drops straight back in.

Nothing on the site claims a track record it does not have. There is no
client count, no transaction total and no trading history — the record band
says 2026 and says plainly that fifteen is the number being taken, not held.
- A real contact form. The CTAs currently open email to the founders.
