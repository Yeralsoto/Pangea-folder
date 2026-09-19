#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the four technical drawings for section 04.

Each drawing is a staged sequence, not a single reveal: groups carry
data-step, and the sequencer in pangea.js releases them in order while the
caption explains what just appeared. The last step holds as the informative
state.

    python3 tools/make_drawings.py
"""
import io, re

VB = "0 0 460 300"

def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

def poly(pts, cls, extra=""):
    d = "M" + " L".join("%.1f %.1f" % p for p in pts) + " Z"
    return '<path class="%s" d="%s"%s/>' % (cls, d, extra)

def line(a, b, cls="dl"):
    return '<path class="%s" d="M%.1f %.1f L%.1f %.1f"/>' % (cls, a[0], a[1], b[0], b[1])

def text(x, y, s, cls="dt", extra=""):
    return '<text class="%s" x="%.1f" y="%.1f"%s>%s</text>' % (cls, x, y, extra, s)

def inset(pts, k=0.955):
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return [(cx + (p[0] - cx) * k, cy + (p[1] - cy) * k) for p in pts]

def step(n, body):
    return '<g class="dstep" data-step="%d">%s</g>' % (n, "".join(body))

def figure(label, steps, caps):
    caplist = "".join('<span class="dwg__capItem" data-cap="%d">%s</span>' % (i, c)
                      for i, c in enumerate(caps))
    return ('<svg class="dwg" viewBox="%s" data-draw role="img" aria-label="%s">%s</svg>'
            '<figcaption class="dwg__cap" data-dwg-cap>%s</figcaption>'
            % (VB, label, "".join(steps), caplist))

# ============================================================ 01 · LAND
A, B = (32, 72), (428, 60)          # rear boundary
D, C = (36, 214), (432, 202)        # front boundary, onto the road
N = 6
tops   = [lerp(A, B, i / N) for i in range(N + 1)]
bots   = [lerp(D, C, i / N) for i in range(N + 1)]
CREEK_LOTS = {3, 4, 5}              # the three that back the creek

lots, numbers, lotlines, premium = [], [], [], []
for i in range(N):
    quad = [tops[i], tops[i + 1], bots[i + 1], bots[i]]
    lots.append(poly(inset(quad), "df lot", ' style="--i:%d"' % i))
    if i in CREEK_LOTS:
        premium.append(poly(inset(quad), "df lot--premium",
                            ' style="--i:%d"' % (i - min(CREEK_LOTS))))
    cx = sum(p[0] for p in quad) / 4
    cy = sum(p[1] for p in quad) / 4
    numbers.append(text(cx, cy + 3, "%d" % (i + 1), "dt dt--lot",
                        ' text-anchor="middle" style="--i:%d"' % i))
    if 0 < i:
        lotlines.append(line(tops[i], bots[i]))

creek = ('<path class="dl dl--creek" d="M250 78 C 290 62, 318 86, 352 72 '
         'S 414 56, 448 68"/>')

road_ticks = [line(bots[i], (bots[i][0] - 2, bots[i][1] + 22)) for i in range(N + 1)]

land = figure(
 "Plat: an 18.4 acre parcel divided into six numbered lots, with road "
 "frontage and a creek behind lots four to six",
 [ step(0, [poly([A, B, C, D], "dl dl--bdy"),
            line((32, 44), (428, 32)), line((32, 38), (32, 50)), line((428, 26), (428, 38)),
            text(230, 26, "18.4 AC", extra=' text-anchor="middle"')]),
   step(1, ['<path class="dl" d="M14 248 L450 236"/>',
            '<path class="dl" d="M14 264 L450 252"/>'] + road_ticks +
           [text(232, 284, "ROAD FRONTAGE", extra=' text-anchor="middle"')]),
   step(2, lotlines + lots + numbers),
   step(3, [creek] + premium + numbers +
           [text(448, 52, "CREEK", "dt dt--sig", ' text-anchor="end"')]),
 ],
 ["One parcel. 18.4 acres.",
  "Frontage on a single road.",
  "Six lots, drawn before the land is bought.",
  "Three back the creek. Those three set the price of the rest."])

# ======================================================== 02 · BUILDING
GRADE = 262
building = figure(
 "Section through a two-storey house: grade, footing, frame, roof and openings",
 [ step(0, ['<path class="dl" d="M14 %d L446 %d"/>' % (GRADE, GRADE),
            '<path class="dl" d="M96 %d L96 240 L364 240 L364 %d"/>' % (GRADE, GRADE),
            text(230, 288, "GRADE", extra=' text-anchor="middle"')]),
   step(1, ['<path class="dl" d="M96 240 L96 224 L364 224 L364 240"/>',
            '<path class="dl" d="M108 224 L352 224"/>',
            line((60, 224), (92, 224)), text(16, 228, "FFL 0.00")]),
   step(2, ['<path class="dl" d="M112 224 L112 106"/>',
            '<path class="dl" d="M348 224 L348 106"/>',
            '<path class="dl" d="M112 166 L348 166"/>'] +
           [line((136 + i * 44, 224), (136 + i * 44, 166)) for i in range(5)] +
           [line((136 + i * 44, 166), (136 + i * 44, 106)) for i in range(5)] +
           [line((60, 166), (108, 166)), text(16, 170, "FFL 2.70")]),
   step(3, ['<path class="dl" d="M92 108 L230 44 L368 108"/>',
            '<path class="dl" d="M112 106 L348 106"/>',
            text(230, 32, "6:12 PITCH", extra=' text-anchor="middle"')]),
   step(4, [poly([(134, 212), (176, 212), (176, 182), (134, 182)], "df", ' style="--i:0"'),
            poly([(206, 212), (248, 212), (248, 182), (206, 182)], "df", ' style="--i:1"'),
            poly([(278, 224), (320, 224), (320, 178), (278, 178)], "df", ' style="--i:2"'),
            poly([(150, 152), (192, 152), (192, 124), (150, 124)], "df", ' style="--i:3"'),
            poly([(268, 152), (310, 152), (310, 124), (268, 124)], "df", ' style="--i:4"'),
            text(230, 288, "DRIED IN", extra=' text-anchor="middle"')]),
 ],
 ["Grade, and where the house sits on it.",
  "Footing and slab.",
  "Frame. Two levels, studs at 16 inches.",
  "Roof at a 6:12 pitch.",
  "Dried in. Openings cut, weather out."])

# ===================================================== 03 · HOSPITALITY
ROWS, COLS = 5, 8                      # forty rooms
# Terracotta marks the vacancy, not the sale: 37 of 40 sold is 93%, and the
# three that did not are the number worth reporting.
VACANT = {(1, 5), (3, 2), (4, 6)}
rooms, vac = [], []
for r in range(ROWS):
    for cc in range(COLS):
        x, y = 104 + cc * 32, 92 + r * 30
        idx = r * COLS + cc
        if (r, cc) in VACANT:
            vac.append('<rect class="df room vacant" x="%d" y="%d" width="20" height="17" '
                       'style="--i:%d"/>' % (x, y, idx))
        else:
            rooms.append('<rect class="df room sold" x="%d" y="%d" width="20" height="17" '
                         'style="--i:%d"/>' % (x, y, idx))

hotel = figure(
 "Elevation of a five-storey hotel: forty rooms, ten of them lit, with an "
 "occupancy readout",
 [ step(0, ['<path class="dl" d="M14 266 L446 266"/>',
            '<path class="dl" d="M88 266 L88 80 L372 80 L372 266"/>',
            '<path class="dl" d="M74 80 L386 80"/>',
            '<path class="dl" d="M330 80 L330 44"/>']),
   step(1, ['<path class="dl" d="M88 %d L372 %d"/>' % (86 + i * 30, 86 + i * 30)
            for i in range(6)] +
           [line((56, 86), (84, 86)), text(20, 90, "L5"),
            line((56, 236), (84, 236)), text(20, 240, "L1")]),
   step(2, rooms + ['<path class="dl" d="M168 266 L168 234 L292 234 L292 266"/>',
            text(230, 258, "ENTRY", extra=' text-anchor="middle"')]),
   step(3, vac + [text(388, 286, "OCCUPANCY", extra=' text-anchor="end"'),
            text(14, 286, "3 ROOMS VACANT", "dt dt--sig"),
            '<text class="dnum" x="446" y="286" text-anchor="end" '
            'data-count-to="93" data-suffix="%">0%</text>']),
 ],
 ["Five levels.",
  "Forty rooms.",
  "Glazed, and open.",
  "Ninety-three per cent sold tonight. We report the three that are not."])

# ========================================================= 04 · RENTALS
units, doors, wins, litwins = [], [], [], []
for u in range(4):
    x0 = 52 + u * 90
    units.append('<path class="dl" d="M%d 262 L%d 154 L%d 118 L%d 154 L%d 262"/>'
                 % (x0, x0, x0 + 45, x0 + 90, x0 + 90))
    units.append('<path class="dl" d="M%d 200 L%d 200"/>' % (x0, x0 + 90))
    doors.append('<path class="dl" d="M%d 262 L%d 222 L%d 222 L%d 262"/>'
                 % (x0 + 34, x0 + 34, x0 + 56, x0 + 56))
    turning = (u == 2)                             # unit 3 is between tenants
    for k, (wx, wy) in enumerate([(x0 + 14, 166), (x0 + 52, 166)]):
        cls = "df room vacant" if turning else "df room sold"
        (litwins if turning else wins).append(
            '<rect class="%s" x="%d" y="%d" width="24" height="20" style="--i:%d"/>'
            % (cls, wx, wy, u * 2 + k))

rentals = figure(
 "Elevation of four attached rental units, three let and one turning, with "
 "an occupancy readout",
 [ step(0, ['<path class="dl" d="M14 262 L446 262"/>'] + units),
   step(1, doors + [text(230, 108, "4 UNITS", extra=' text-anchor="middle"')]),
   step(2, wins),
   step(3, litwins + [text(388, 288, "LET", extra=' text-anchor="end"'),
            '<text class="dnum" x="446" y="288" text-anchor="end" '
            'data-count-to="75" data-suffix="%">0%</text>',
            text(52, 288, "UNIT 3 TURNING", "dt dt--sig")]),
 ],
 ["Four units, attached.",
  "One door each.",
  "Eight windows to keep an eye on.",
  "Three let. The fourth is turning, and that is the one we chase."])

# ---------------------------------------------------------------- inject
doc = io.open("index.html", encoding="utf-8").read()
for sid, content in [("land", land), ("building", building),
                     ("hospitality", hotel), ("rentals", rentals)]:
    pat = re.compile(r'(<article class="var rv" id="var-%s">.*?<figure class="var__fig">)'
                     r'.*?(</figure>)' % sid, re.S)
    assert pat.search(doc), sid
    doc = pat.sub(lambda m: m.group(1) + content + m.group(2), doc, count=1)
io.open("index.html", "w", encoding="utf-8").write(doc)
print("four staged drawings injected")
