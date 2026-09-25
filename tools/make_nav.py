# -*- coding: utf-8 -*-
"""Single source for the header and the menu panel on every page.

One flat set of names, everywhere. No submenus: on a laptop the top bar
carries them, on a phone the burger opens the same list stacked one below
the other, numbered the way the practice site does it.
"""
import io, re, glob

# numeral, name, descriptor, href template ({p} = path back to the site root)
# Every item is its own page. A menu click is a navigation, not a scroll.
ITEMS = [
    ("I",   "Home",        "Clarity across the real estate lifecycle", "{p}index.html"),
    ("II",  "What we do",  "The full cycle, land through operations",  "{p}what-we-do.html"),
    ("III", "Markets",     "Where we are on the ground, and where we underwrite", "{p}markets.html"),
    ("IV",  "Services",    "How we work, and what it costs",           "{p}services.html"),
    ("V",   "Field Notes", "Fifteen pieces on markets and deals",      "{p}insights/index.html"),
    ("VI",  "About us",    "The firm, and the mark",                   "{p}about.html"),
    ("VII", "Contact",     "Reply inside one business day",            "{p}contact.html"),
]
BAR = ["What we do", "Markets", "Services", "Field Notes", "About us", "Contact"]


def _href(tpl, p, home):
    h = tpl.format(p=p)
    if home and h == "index.html":
        h = "#top"
    return h


def header(p="", home=False, art=False):
    links = []
    for num, name, desc, tpl in ITEMS:
        if name not in BAR:
            continue
        links.append('      <a href="%s">%s</a>' % (_href(tpl, p, home), name))
    return (
'<header class="nav%s" data-solid="false">\n'
'  <div class="nav__bar">\n'
'    <a class="nav__logo" href="%s" aria-label="Pangea Ventures International — home">\n'
'      <img class="nav__sym" src="%sassets/logos/pangea-symbol-reversed.svg" alt="">\n'
'      <span class="nav__lock">\n'
'        <img class="nav__word" src="%sassets/logos/pangea-wordmark-only-bone.svg" alt="Pangea">\n'
'        <span class="nav__desc">Ventures International</span>\n'
'      </span>\n'
'    </a>\n'
'    <nav class="nav__links" aria-label="Primary">\n%s\n    </nav>\n'
'    <button class="nav__menu" type="button" aria-expanded="false" aria-controls="menu">\n'
'      <span class="nav__menuLabel">Menu</span>\n'
'      <span class="nav__menuIcon" aria-hidden="true"><i></i><i></i><i></i></span>\n'
'    </button>\n'
'  </div>\n'
'</header>' % (" nav--art" if art else "",
               "#top" if home else (p + "index.html"), p, p, "\n".join(links)))


def panel(p="", home=False):
    rows = []
    for i, (num, name, desc, tpl) in enumerate(ITEMS):
        rows.append(
'        <li><a href="%s" style="--i:%d">'
'<span class="menu__n">%s</span>'
'<span class="menu__b"><span class="menu__t">%s</span>'
'<span class="menu__d">%s</span></span></a></li>'
            % (_href(tpl, p, home), i, num, name, desc))
    return (
'<div class="menu" id="menu" hidden aria-hidden="true">\n'
'  <div class="menu__inner">\n'
'    <nav aria-label="All sections">\n'
'      <ul class="menu__list">\n%s\n      </ul>\n'
'    </nav>\n'
'    <p class="menu__foot">Reply inside one business day. '
'Bad news the same day we find it.</p>\n'
'  </div>\n'
'</div>' % "\n".join(rows))


HEAD_RE = re.compile(r'<header class="nav[^"]*"[^>]*>.*?</header>', re.S)
MENU_RE = re.compile(r'<div class="menu" id="menu".*?\n</div>', re.S)


def apply(path, p, home):
    s = io.open(path, encoding='utf-8').read()
    art = 'nav nav--art' in s
    n = len(HEAD_RE.findall(s))
    assert n == 1, "%s: %d headers" % (path, n)
    s = HEAD_RE.sub(lambda m: header(p, home, art), s, count=1)

    if MENU_RE.search(s):
        s = MENU_RE.sub(lambda m: panel(p, home), s, count=1)
    else:                                    # give every page the burger panel
        s = s.replace('</header>', '</header>\n\n' + panel(p, home), 1)
    io.open(path, 'w', encoding='utf-8').write(s)
    return path


if __name__ == "__main__":
    done = [apply('index.html', '', True)]
    for f in ('about.html', 'what-we-do.html', 'markets.html',
              'services.html', 'contact.html'):
        done.append(apply(f, '', False))
    for f in sorted(glob.glob('insights/*.html')):
        done.append(apply(f, '../', False))
    print("nav + menu written to %d pages" % len(done))
