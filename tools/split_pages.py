# -*- coding: utf-8 -*-
"""One-shot: break the homepage into real pages.

The menu used to send every item to an anchor on index.html. Four of the six
destinations are now their own page, so a menu click is a navigation rather
than a scroll. Run once; afterwards the pages are ordinary files.
"""
import io, re, sys
sys.path.insert(0, 'tools')
import make_nav as N

SRC = io.open('index.html', encoding='utf-8').read()

# --- carve the homepage into banner-delimited blocks ----------------------
BANNER = re.compile(r'<!-- =+ (.*?) =+ -->')
marks = [(m.start(), m.group(1).strip()) for m in BANNER.finditer(SRC)]
head_end = SRC.index('<main id="main">')
main_end = SRC.index('</main>')

blocks = {}
order = []
inside = [(p, n) for p, n in marks if head_end < p < main_end]
for i, (pos, name) in enumerate(inside):
    end = inside[i + 1][0] if i + 1 < len(inside) else main_end
    blocks[name] = SRC[pos:end].rstrip() + "\n"
    order.append(name)

HOME     = ['HERO', '01 OUR STORY', 'POSITIONING', 'THE RECORD',
            '02 BELIEFS', '05 CLIENTS', 'INSIGHTS']
WHATWEDO = ['03 THE FULL CYCLE', '04 WHAT WE BUILD', 'ASSET TYPES', 'MARKETS']
SERVICES = ['HOW IT WORKS', '04 SERVICES', 'STANDARDS', 'DISCLOSURE BLOCK']
CONTACT  = ['CONTACT']

missing = [b for b in HOME + WHATWEDO + SERVICES + CONTACT if b not in blocks]
assert not missing, "already split, or banners changed: %s" % missing
extra = [b for b in order if b not in HOME + WHATWEDO + SERVICES + CONTACT]
assert not extra, "unassigned blocks: %s" % extra

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
 '<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,300;'
 '6..72,400&family=Geist:wght@400;500&display=swap" rel="stylesheet">\n'
 '<link rel="stylesheet" href="assets/css/pangea.css">')

FOOTER = '''<footer class="footer">
  <div class="wrap footer__grid">
    <a href="index.html" aria-label="Pangea Ventures International — home"><img src="assets/logos/pangea-horizontal-reversed.svg" alt="Pangea Ventures International"></a>
    <p class="label">From opportunity to operation.</p>
    <p class="footer__legal">&copy; 2026 Pangea Ventures International</p>
  </div>
</footer>'''


def page(title, desc, names, scripts, lede=None):
    body = "\n".join(blocks[n] for n in names)
    head = ('<!doctype html>\n<html lang="en">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>%s — Pangea Ventures International</title>\n'
            '<meta name="description" content="%s">\n'
            '<meta name="theme-color" content="#27372D">\n'
            '<link rel="icon" href="assets/logos/pangea-avatar.svg" type="image/svg+xml">\n'
            '%s\n</head>\n<body>\n'
            '<div class="progress" aria-hidden="true"><span data-progress></span></div>\n'
            % (title, desc, FONTS))
    return (head + N.header('', home=False, art=True) + "\n\n"
            + N.panel('', home=False) + "\n\n<main id=\"main\">\n\n"
            + (lede or "") + body + "\n</main>\n\n" + FOOTER + "\n\n"
            + "\n".join(scripts) + "\n</body>\n</html>\n")


def lede(eyebrow, h1, sub):
    return ('<section class="phead">\n  <div class="wrap">\n'
            '    <p class="label phead__eyebrow rv">%s</p>\n'
            '    <h1 class="phead__h1 rv" data-mask style="--rv-delay:90ms">%s</h1>\n'
            '    <p class="phead__sub rv" style="--rv-delay:180ms">%s</p>\n'
            '  </div>\n</section>\n\n' % (eyebrow, h1, sub))


JS_BASE = ['<script src="assets/js/pangea.js" defer></script>']
JS_CYCLE = JS_BASE + [
    '<script src="assets/js/lifecycle-model.js" defer></script>',
    '<script src="assets/js/cycle.js" defer></script>',
    '<script type="module" src="assets/js/lifecycle-3d.js"></script>']

io.open('what-we-do.html', 'w', encoding='utf-8').write(page(
    "What we do",
    "The full real estate lifecycle — land, building, hospitality and rentals — "
    "the asset types we underwrite, and the markets we work in.",
    WHATWEDO, JS_CYCLE,
    lede("What we do",
         "One cycle, five stages, every asset type.",
         "Most firms sell you one stage and hand you off. We carry a deal from "
         "the first look at the land through the day it is operating, and we "
         "underwrite every asset type against the model it actually fits.")))

io.open('services.html', 'w', encoding='utf-8').write(page(
    "Services",
    "Three ways to work with Pangea, what each engagement covers, the standards "
    "we hold ourselves to, and how we evaluate a deal.",
    SERVICES, JS_BASE,
    lede("Services",
         "Hire us, bring us a deal, or invest alongside us.",
         "Three ways in, one standard of work. Below: what each engagement "
         "covers, what we commit to on timing and candour, and the order we "
         "actually evaluate a deal in.")))

io.open('contact.html', 'w', encoding='utf-8').write(page(
    "Contact",
    "Tell us about the asset and we will tell you what we actually think. "
    "Reply inside one business day.",
    CONTACT, JS_BASE))

# --- trim the homepage ----------------------------------------------------
out = SRC
for n in WHATWEDO + SERVICES + CONTACT:
    assert out.count(blocks[n]) == 1, n
    out = out.replace(blocks[n], "")
out = re.sub(r'\n{4,}', '\n\n\n', out)
io.open('index.html', 'w', encoding='utf-8').write(out)

print("wrote what-we-do.html, services.html, contact.html")
print("homepage keeps:", ", ".join(HOME))
