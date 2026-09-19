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

## Structure

```
index.html              The whole page. One document, one story.
assets/css/pangea.css   Tokens, layout, components, motion.
assets/js/pangea.js     Progressive enhancement only.
assets/img/topo.svg     Hero contour field (generated, do not hand-edit).
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
| 01 | Our story | The six plates of Pangea drift together into one landmass as you scroll. The seams fade as they lock. This is the brand's core metaphor made literal. |
| — | Positioning | "Most real estate firms are paid to close a transaction." |
| 02 | What we believe | The six beliefs. |
| 03 | The full cycle | Five stages with a live progress meter in the sticky column. |
| — | Asset types / Markets | Every asset type; the four markets with coordinates. |
| 04 | Services | Five lines, rates in expandable panels. |
| — | Service standards | 1 day · 48 hours · 5 days · Same day. |
| 05 | How we speak | "We write" against "we never write", plus the word lists. |
| — | The disclosure block | A live Parcel 4-37 block, rows landing in order. |
| — | The symbol | Spire, wings and open arch, isolated on hover or tap. |
| — | Founders / Contact | Erin Berger and Yeraldin Soto. |

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

## Not built yet

- Spanish version (`Claridad en todo el ciclo inmobiliario.` — the approved
  ES copy is in the brand kit, ready to drop in).
- Insights / writing section — no content exists for it yet, so the nav
  carries Services in that slot rather than a dead link.
- A real contact form. The CTAs currently open email to the founders.
