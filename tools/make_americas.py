#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The Americas coverage map for the Markets section.

Same visual language as the Pangea map in section 01 — one landmass, sand on
Forest, hairline seams — so the two read as the same system. Markers are real
coordinates, and they say two different things:

  · on the ground   — a market we work in ourselves (terracotta, solid)
  · underwriting    — a market we will model but not operate (sand, hollow)

That distinction is the honest version of a coverage map, and it is the one
worth showing.

    python3 tools/make_americas.py
"""
import io, re

W, H = 540, 660
LON0, LON1 = -172.0, -28.0
LAT0, LAT1 = 74.0, -58.0

def xy(lon, lat):
    x = (lon - LON0) / (LON1 - LON0) * W
    y = (LAT0 - lat) / (LAT0 - LAT1) * H
    return x, y

NORTH = [(-168,65),(-155,71),(-128,70),(-100,73),(-82,73),(-62,66),(-56,52),
         (-66,48),(-70,43),(-74,39),(-81,31),(-80,25),(-90,29),(-97,26),
         (-105,20),(-110,23),(-114,30),(-124,35),(-125,48),(-135,58),(-152,59)]
CENTRAL = [(-97,16),(-92,15),(-88,16),(-83,10),(-79,9),(-77,8),(-82,8),(-86,11),
           (-91,13),(-95,15)]
SOUTH = [(-81,8),(-72,11),(-62,11),(-52,5),(-44,-2),(-35,-6),(-39,-16),(-48,-25),
         (-54,-34),(-62,-40),(-66,-46),(-68,-55),(-74,-53),(-73,-44),(-71,-33),
         (-70,-23),(-75,-14),(-80,-5)]
ISLANDS = [
  [(-78,23),(-74,22),(-77,20),(-82,22)],                       # Cuba
  [(-74,19),(-69,19),(-68,18),(-72,18)],                       # Hispaniola
]

def path(pts):
    return "M" + " L".join("%.1f %.1f" % xy(lo, la) for lo, la in pts) + " Z"

# label, lon, lat, kind, anchor, dx, dy — the nudges keep the Central
# American cluster from writing over itself.
MARKERS = [
 ("United States",  -98.58,  39.83, "ground", "start",  12,   4),
 ("México",         -99.13,  19.43, "cover",  "end",   -12,  -2),
 ("Costa Rica",     -84.09,   9.93, "ground", "end",   -12,  -7),
 ("Panamá",         -79.52,   8.98, "cover",  "end",   -12,  12),
 ("Rep. Dominicana",-69.93,  18.49, "cover",  "start",  12,  -2),
 ("Antioquia · Eje Cafetero", -75.60, 5.50, "ground", "start", 12, 8),
 ("Ecuador",        -78.47,  -0.18, "cover",  "end",   -12,   0),
 ("Perú",           -77.04, -12.05, "cover",  "end",   -12,   0),
 ("Chile",          -70.67, -33.45, "cover",  "end",   -12,   0),
 ("Argentina",      -58.38, -34.60, "cover",  "start",  12,   0),
]

lands = "".join('<path class="am__land" d="%s"/>' % path(p)
                for p in [NORTH, CENTRAL, SOUTH] + ISLANDS)

pins = []
for i, (label, lon, lat, kind, anchor, dx, dy) in enumerate(MARKERS):
    x, y = xy(lon, lat)
    cls = "am__pin am__pin--" + kind
    pins.append(
      '<g class="%s" style="--i:%d">'
      '<circle class="am__ring" cx="%.1f" cy="%.1f" r="9"/>'
      '<circle class="am__dot" cx="%.1f" cy="%.1f" r="3.4"/>'
      '<text class="am__label" x="%.1f" y="%.1f" text-anchor="%s">%s</text>'
      '</g>' % (cls, i, x, y, x, y, x + dx, y + 3.6 + dy, anchor, label))

svg = ('<svg class="am" viewBox="0 0 %d %d" role="img" '
       'aria-label="Coverage map of the Americas. Markets we work in on the ground: '
       'the United States, Antioquia and the Eje Cafetero in Colombia, and Costa Rica. '
       'Markets we underwrite across: Mexico, Panama, the Dominican Republic, Ecuador, '
       'Peru, Chile and Argentina.">'
       '<g class="am__lands">%s</g>%s</svg>' % (W, H, lands, "".join(pins)))

legend = ('<ul class="am__key">'
          '<li><span class="am__sw am__sw--ground"></span>On the ground</li>'
          '<li><span class="am__sw am__sw--cover"></span>We underwrite here</li>'
          '</ul>')

block = ('<figure class="am__fig rv">%s%s</figure>' % (svg, legend))

doc = io.open("index.html", encoding="utf-8").read()
if "am__fig" in doc:
    doc = re.sub(r'<figure class="am__fig rv">.*?</figure>', block, doc, flags=re.S)
else:
    anchor_s = '    <ol class="mks">'
    assert anchor_s in doc
    doc = doc.replace(anchor_s, block + "\n" + anchor_s, 1)
io.open("index.html", "w", encoding="utf-8").write(doc)
print("americas map injected · %d markers" % len(MARKERS))
