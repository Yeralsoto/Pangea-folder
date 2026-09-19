#!/usr/bin/env python3
"""
Build the break-apart map for section 01.

Continents are held in modern lon/lat, projected equirectangular. Each also
carries the transform that puts it back in its Pangea position, so the scene
can be interpolated: progress 0 = the supercontinent, 1 = the world today.

    python3 tools/make_continents.py > /dev/null   (writes into index.html)
"""
import io, re

W, H = 1000, 500
def xy(lon, lat):
    return ((lon + 180) / 360.0 * W, (90 - lat) / 180.0 * H)

# Simplified outlines — recognisable, not cartographic.
LANDS = {
 "north-america": [(-168,65),(-155,71),(-128,70),(-100,73),(-82,73),(-62,66),(-56,52),
                   (-66,48),(-70,43),(-74,39),(-81,31),(-80,25),(-90,29),(-97,26),
                   (-105,20),(-110,23),(-114,30),(-124,35),(-125,48),(-135,58),(-152,59),(-168,65)],
 "south-america":[(-81,8),(-72,11),(-62,11),(-52,5),(-44,-2),(-35,-6),(-39,-16),(-48,-25),
                  (-54,-34),(-62,-40),(-66,-46),(-68,-55),(-74,-53),(-73,-44),(-71,-33),
                  (-70,-23),(-75,-14),(-80,-5),(-81,8)],
 "africa":       [(-17,15),(-10,27),(0,36),(11,37),(24,32),(35,31),(43,12),(51,12),(48,0),
                  (40,-10),(35,-22),(26,-34),(18,-34),(13,-23),(9,-2),(5,5),(-8,5),(-17,15)],
 "eurasia":      [(-10,36),(-2,44),(3,52),(8,58),(25,71),(60,72),(95,77),(130,73),(160,70),
                  (180,66),(170,60),(155,52),(142,46),(132,35),(122,31),(120,22),(108,12),
                  (100,6),(98,16),(92,22),(80,22),(72,25),(62,25),(52,28),(44,38),(36,36),
                  (28,41),(18,40),(8,44),(-10,36)],
 "india":        [(68,24),(76,30),(88,26),(92,22),(87,18),(83,10),(77,8),(72,16),(68,24)],
 "australia":    [(114,-22),(122,-17),(131,-12),(142,-11),(147,-19),(153,-26),(150,-37),
                  (141,-38),(131,-32),(124,-34),(115,-34),(114,-22)],
 "antarctica":   [(-58,-64),(-30,-70),(0,-68),(28,-70),(52,-66),(64,-72),(48,-79),
                  (10,-81),(-28,-79),(-56,-73),(-58,-64)],
}

# Pangea, given as the TARGET CENTROID each landmass moves to, plus a rotation
# about its own centre. Shapes share one fill, so slight overlaps merge into a
# single mass — the goal is one continent, not a geological reconstruction.
PANGEA_TARGET = {
 "north-america": (430, 150,  40),
 "eurasia":       (650, 170,  24),
 "africa":        (520, 285, -14),
 "south-america": (405, 305,  42),
 "india":         (612, 322, -34),
 "australia":     (688, 372, -30),
 "antarctica":    (533, 415,   6),
}

def path_and_centroid(pts):
    P = [xy(lo, la) for lo, la in pts]
    d = "M" + " L".join("%.1f %.1f" % p for p in P) + " Z"
    cx = sum(p[0] for p in P) / len(P)
    cy = sum(p[1] for p in P) / len(P)
    return d, cx, cy

groups = []
for name, pts in LANDS.items():
    d, cx, cy = path_and_centroid(pts)
    tx, ty, rot = PANGEA_TARGET[name]
    dx, dy = tx - cx, ty - cy
    groups.append(
        '            <g class="land" data-dx="%d" data-dy="%d" data-rot="%d" '
        'data-cx="%.1f" data-cy="%.1f">'
        '<path d="%s"/></g>' % (round(dx), round(dy), rot, cx, cy, d))
    print("  %-15s centroid (%.0f,%.0f) -> (%d,%d)  d=(%+d,%+d)"
          % (name, cx, cy, tx, ty, round(dx), round(dy)))

svg = ('<svg class="drift" viewBox="0 0 %d %d" role="img" '
       'aria-label="The supercontinent Pangea breaking apart into today\'s continents as you scroll">\n'
       '          <g class="drift__lands">\n%s\n          </g>\n        </svg>'
       % (W, H, "\n".join(groups)))

doc = io.open('index.html', encoding='utf-8').read()
m = re.search(r'<svg class="drift".*?</svg>', doc, re.S)
assert m, "drift svg not found"
doc = doc[:m.start()] + svg + doc[m.end():]
io.open('index.html', 'w', encoding='utf-8').write(doc)
print("wrote %d landmasses into index.html" % len(groups))
