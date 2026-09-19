#!/usr/bin/env python3
"""
Generate the Pangea hero's topographic contour field.

True contour lines (marching squares) over a smooth terrain field, so the
lines behave like a real topographic map: they nest around high ground and
run long and parallel across the flats. Output is a single static SVG.

    python3 tools/make_topo.py assets/img/topo.svg
"""
import sys, math

W, H = 1600, 900
NX, NY = 140, 84           # sampling grid
LEVELS = 34
MIN_POINTS = 6             # drop specks


def field(x, y):
    """Terrain height at (x, y). Tuned to match the brand book hero."""
    def bump(cx, cy, sx, sy):
        return math.exp(-(((x - cx) ** 2) / (2 * sx * sx) +
                          ((y - cy) ** 2) / (2 * sy * sy)))
    v = 0.0
    v += 1.00 * bump(1105, 225, 360, 265)   # the high ground, upper right
    v += 0.38 * bump(1520, 520, 280, 250)   # shoulder falling away east
    v += 0.30 * bump(470, -40, 520, 240)    # gentle swell, upper left
    v -= 0.95 * (y / H)                     # regional dip southward
    v += 0.085 * math.sin(x / 300.0 + 1.1) * (0.25 + y / H)
    v += 0.045 * math.sin(x / 150.0 + 4.0) * (y / H)
    return v


def marching_squares(grid, level, xs, ys):
    """Return line segments where the field crosses `level`."""
    segs = []
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            a, b = grid[j][i],     grid[j][i + 1]        # top-left, top-right
            c, d = grid[j + 1][i + 1], grid[j + 1][i]    # bot-right, bot-left
            idx = (1 if a > level else 0) | (2 if b > level else 0) \
                | (4 if c > level else 0) | (8 if d > level else 0)
            if idx == 0 or idx == 15:
                continue
            x0, x1 = xs[i], xs[i + 1]
            y0, y1 = ys[j], ys[j + 1]

            def ip(p, q, v1, v2):                      # linear interpolation
                t = 0.5 if v2 == v1 else (level - v1) / (v2 - v1)
                t = 0.0 if t < 0 else 1.0 if t > 1 else t
                return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)

            TL, TR, BR, BL = (x0, y0), (x1, y0), (x1, y1), (x0, y1)
            top    = ip(TL, TR, a, b)
            right  = ip(TR, BR, b, c)
            bottom = ip(BL, BR, d, c)
            left   = ip(TL, BL, a, d)

            table = {
                1:  [(left, top)],      2:  [(top, right)],
                3:  [(left, right)],    4:  [(right, bottom)],
                5:  [(left, top), (right, bottom)],
                6:  [(top, bottom)],    7:  [(left, bottom)],
                8:  [(bottom, left)],   9:  [(bottom, top)],
                10: [(top, right), (bottom, left)],
                11: [(bottom, right)],  12: [(right, left)],
                13: [(right, top)],     14: [(top, left)],
            }
            segs.extend(table[idx])
    return segs


def join(segs, tol=3):
    """Chain segments end-to-end into polylines."""
    def key(p):
        return (round(p[0] / tol), round(p[1] / tol))
    ends = {}
    for s in segs:
        ends.setdefault(key(s[0]), []).append(s)
        ends.setdefault(key(s[1]), []).append(s)

    used, lines = set(), []
    for seg in segs:
        if id(seg) in used:
            continue
        used.add(id(seg))
        line = [seg[0], seg[1]]
        for _ in range(2):                      # extend forward, then backward
            while True:
                tail = line[-1]
                nxt = None
                for cand in ends.get(key(tail), []):
                    if id(cand) in used:
                        continue
                    if key(cand[0]) == key(tail):
                        nxt, pt = cand, cand[1]
                        break
                    if key(cand[1]) == key(tail):
                        nxt, pt = cand, cand[0]
                        break
                if nxt is None:
                    break
                used.add(id(nxt))
                line.append(pt)
            line.reverse()
        lines.append(line)
    return lines


def chaikin(pts, iterations=2):
    """Corner-cutting smoothing — turns the grid staircase into flowing line."""
    closed = (abs(pts[0][0] - pts[-1][0]) < 2 and abs(pts[0][1] - pts[-1][1]) < 2)
    for _ in range(iterations):
        out = [] if closed else [pts[0]]
        for i in range(len(pts) - 1):
            p, q = pts[i], pts[i + 1]
            out.append((p[0] * 0.75 + q[0] * 0.25, p[1] * 0.75 + q[1] * 0.25))
            out.append((p[0] * 0.25 + q[0] * 0.75, p[1] * 0.25 + q[1] * 0.75))
        if not closed:
            out.append(pts[-1])
        else:
            out.append(out[0])
        pts = out
    return pts


def decimate(pts, min_d=5.0):
    """Drop points that add no visible shape, to keep the file small."""
    out = [pts[0]]
    for p in pts[1:-1]:
        q = out[-1]
        if (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= min_d * min_d:
            out.append(p)
    out.append(pts[-1])
    return out


def main(out_path):
    xs = [W * i / (NX - 1) for i in range(NX)]
    ys = [H * j / (NY - 1) for j in range(NY)]
    grid = [[field(x, y) for x in xs] for y in ys]

    lo = min(min(r) for r in grid)
    hi = max(max(r) for r in grid)

    paths = []
    for k in range(1, LEVELS):
        level = lo + (hi - lo) * k / LEVELS
        for line in join(marching_squares(grid, level, xs, ys)):
            if len(line) < MIN_POINTS:
                continue
            line = decimate(chaikin(line))
            if len(line) < 4:
                continue
            d = "M" + " L".join("%d %d" % (round(p[0]), round(p[1])) for p in line)
            paths.append('<path d="%s"/>' % d)

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
        '<g fill="none" stroke="#C9B69B" stroke-opacity="0.2" '
        'stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round">'
        '%s</g></svg>'
    ) % (W, H, "".join(paths))

    with open(out_path, "w") as f:
        f.write(svg)
    print("%s — %d contour paths, %.1f KB" % (out_path, len(paths), len(svg) / 1024.0))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "assets/img/topo.svg")
