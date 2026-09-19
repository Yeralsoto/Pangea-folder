/* ============================================================
   PANGEA — the lifecycle model
   A site model on a turntable: the same parcel carried through
   all five stages, from raw land to an operating asset.

   Hand-rolled 3D on 2D canvas — real vertices, a rotation about
   Y, an elevated camera, perspective projection and painter's
   depth sorting. No dependency, no WebGL.

   The scene state is driven by `phase` (0 -> 4), read from the
   position of the five .stage elements, so the model and the
   written stages stay in step.
   ============================================================ */
(function () {
  'use strict';

  var canvas = document.getElementById('cycle-model');
  if (!canvas || !canvas.getContext) return;

  var ctx     = canvas.getContext('2d');
  var caption = document.querySelector('[data-model-caption]');
  var reduce  = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- palette ---------- */
  var FOREST = [39, 55, 45], BONE = [241, 236, 226], SAND = [201, 182, 155],
      TERRA  = [196, 103, 56], LINEN = [230, 222, 207], UMBER = [89, 65, 50];

  function rgba(c, a) { return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + a + ')'; }
  function mix(a, b, t) {
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]
      .map(Math.round);
  }

  /* ---------- helpers ---------- */
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function ramp(v, a, b) { return clamp((v - a) / (b - a), 0, 1); }        // 0->1 across [a,b]
  function ease(t) { return t * t * (3 - 2 * t); }                          // smoothstep
  function band(v, a, b, c, d) { return Math.min(ramp(v, a, b), 1 - ramp(v, c, d)); }

  /* ---------- geometry of the asset ---------- */
  var PARCEL = { x0: -62, x1: 62, z0: -46, z1: 46 };
  var MAIN   = { x0: -40, x1: 40, z0: -15, z1: 15, h: 34 };   // the slab
  var WING   = { x0: -40, x1: -8, z0: 15, z1: 35, h: 12 };    // the low wing
  var DECK   = { x0: 6,   x1: 40, z0: 18, z1: 38 };           // terrace
  var FLOORS = 6;

  /* Ground contour lines — the same language as the hero's topo field. */
  var CONTOURS = (function () {
    var out = [];
    for (var k = 0; k < 8; k++) {
      var base = PARCEL.z0 + 2 + k * 12, pts = [];
      for (var x = PARCEL.x0; x <= PARCEL.x1; x += 4) {
        pts.push([x, 0, base + 5.5 * Math.sin(x / 21 + k * 0.85) + 1.5 * Math.sin(x / 9)]);
      }
      out.push(pts);
    }
    return out;
  })();

  /* Which window cells are lit. Fixed, not random, so it never flickers. */
  var LIT = { '0-1': 1, '0-4': 1, '1-2': 1, '2-0': 1, '2-3': 1, '3-5': 1, '4-2': 1, '5-4': 1,
             '1-6': 1, '3-7': 1, '4-6': 1 };

  /* ---------- camera ---------- */
  var theta = -0.6, ELEV = 0.46, DIST = 560;
  var W = 0, H = 0, cx = 0, cy = 0, scale = 1;

  function project(x, y, z) {
    var ct = Math.cos(theta), st = Math.sin(theta);
    var rx = x * ct - z * st;
    var rz = x * st + z * ct;
    var ce = Math.cos(ELEV), se = Math.sin(ELEV);
    var ry = y * ce - rz * se;
    var rd = y * se + rz * ce;
    var f  = DIST / (DIST - rd);
    return { X: cx + rx * f * scale, Y: cy - ry * f * scale, d: rd };
  }

  /* ---------- draw list (painter's algorithm) ---------- */
  var prims = [];
  function push(depth, fn) { prims.push({ d: depth, fn: fn }); }

  function polyline(pts3, stroke, width, dash) {
    if (!stroke) return;
    var p = pts3.map(function (q) { return project(q[0], q[1], q[2]); });
    var depth = 0;
    for (var i = 0; i < p.length; i++) depth += p[i].d;
    depth /= p.length;
    push(depth, function () {
      ctx.beginPath();
      ctx.setLineDash(dash || []);
      ctx.lineWidth = width || 1;
      ctx.strokeStyle = stroke;
      ctx.moveTo(p[0].X, p[0].Y);
      for (var i = 1; i < p.length; i++) ctx.lineTo(p[i].X, p[i].Y);
      ctx.stroke();
      ctx.setLineDash([]);
    });
  }

  function face(pts3, fill, stroke, width) {
    var p = pts3.map(function (q) { return project(q[0], q[1], q[2]); });
    var depth = 0;
    for (var i = 0; i < p.length; i++) depth += p[i].d;
    depth /= p.length;
    push(depth, function () {
      ctx.beginPath();
      ctx.moveTo(p[0].X, p[0].Y);
      for (var i = 1; i < p.length; i++) ctx.lineTo(p[i].X, p[i].Y);
      ctx.closePath();
      if (fill)   { ctx.fillStyle = fill; ctx.fill(); }
      if (stroke) { ctx.lineWidth = width || 1; ctx.strokeStyle = stroke; ctx.stroke(); }
    });
  }

  function rectY(b, y) {                       // horizontal rectangle at height y
    return [[b.x0, y, b.z0], [b.x1, y, b.z0], [b.x1, y, b.z1], [b.x0, y, b.z1]];
  }

  /* Sun azimuth, fixed in CAMERA space (the normal is rotated by theta before
     the comparison). Walls are vertical, so shading depends only on which way
     a face turns — which is what makes the massing read as a real object
     rather than a flat sticker. ~+1.05 rad puts the key light front-right, so
     whatever rotates toward the viewer is the face that lights up. */
  var SUN = 1.05;

  function lambert(nx, nz) {
    var ct = Math.cos(theta), st = Math.sin(theta);
    var az = Math.atan2(nx * st + nz * ct, nx * ct - nz * st);
    return 0.20 + 0.52 * Math.max(0, Math.cos(az - SUN));
  }

  /* The four walls of a box, each as its own face so they sort correctly. */
  function boxWalls(b, y0, y1, tint, alpha, stroke) {
    var w = [
      { p: [[b.x0, y0, b.z0], [b.x1, y0, b.z0], [b.x1, y1, b.z0], [b.x0, y1, b.z0]], n: [0, -1] },
      { p: [[b.x1, y0, b.z0], [b.x1, y0, b.z1], [b.x1, y1, b.z1], [b.x1, y1, b.z0]], n: [1, 0] },
      { p: [[b.x1, y0, b.z1], [b.x0, y0, b.z1], [b.x0, y1, b.z1], [b.x1, y1, b.z1]], n: [0, 1] },
      { p: [[b.x0, y0, b.z1], [b.x0, y0, b.z0], [b.x0, y1, b.z0], [b.x0, y1, b.z1]], n: [-1, 0] }
    ];
    for (var i = 0; i < w.length; i++) {
      var L = lambert(w[i].n[0], w[i].n[1]);
      /* lit faces go toward Bone, shaded faces fall toward Umber */
      var col = L > 0.30 ? mix(FOREST, BONE, (L - 0.30) * 1.15 + 0.14)
                         : mix(FOREST, UMBER, 0.14 + L * 0.5);
      face(w[i].p, rgba(col, alpha), stroke);
    }
  }

  /* ---------- the scene ---------- */
  function scene(phase) {
    prims.length = 0;

    /* Timed so the model state matches the stage being read:
       0 Identify land · 1 Evaluate plat · 2 Create frame ·
       3 Operate finished and lit · 4 Optimize stabilised. */
    var survey  = band(phase, 0.30, 0.85, 1.90, 2.45);        // plat overlay
    var frame   = band(phase, 1.10, 1.60, 2.35, 2.85);        // structural frame
    var rise    = ease(ramp(phase, 1.10, 1.90));              // build height
    var solid   = ease(ramp(phase, 2.10, 2.85));              // massing
    var glass   = ease(ramp(phase, 2.45, 2.95));              // glazing
    var lit     = ease(ramp(phase, 2.60, 3.05));              // occupancy
    var landFad = 1 - 0.7 * ease(ramp(phase, 0.70, 1.90));    // contours recede

    /* --- ground --- */
    face(rectY(PARCEL, 0), rgba(mix(FOREST, SAND, 0.10), 0.55), null);

    for (var i = 0; i < CONTOURS.length; i++) {
      polyline(CONTOURS[i], rgba(SAND, 0.30 * landFad), 1);
    }

    /* parcel boundary + corner posts */
    var b = rectY(PARCEL, 0).concat([[PARCEL.x0, 0, PARCEL.z0]]);
    polyline(b, rgba(SAND, 0.75), 1.2);
    [[PARCEL.x0, PARCEL.z0], [PARCEL.x1, PARCEL.z0],
     [PARCEL.x1, PARCEL.z1], [PARCEL.x0, PARCEL.z1]].forEach(function (c) {
      polyline([[c[0], 0, c[1]], [c[0], 6, c[1]]], rgba(SAND, 0.8), 1.2);
    });

    /* --- 02 survey: plat lines and setbacks --- */
    if (survey > 0.01) {
      var a = 0.5 * survey;
      [-30, 0, 30].forEach(function (x) {
        polyline([[x, 0.2, PARCEL.z0], [x, 0.2, PARCEL.z1]], rgba(BONE, a * 0.5), 1, [4, 5]);
      });
      [-16, 16].forEach(function (z) {
        polyline([[PARCEL.x0, 0.2, z], [PARCEL.x1, 0.2, z]], rgba(BONE, a * 0.5), 1, [4, 5]);
      });
      var set = { x0: PARCEL.x0 + 9, x1: PARCEL.x1 - 9, z0: PARCEL.z0 + 9, z1: PARCEL.z1 - 9 };
      polyline(rectY(set, 0.3).concat([[set.x0, 0.3, set.z0]]),
               rgba(TERRA, 0.55 * survey), 1.2, [6, 5]);
    }

    /* --- 03 structure: columns and floor plates --- */
    if (frame > 0.01 && rise > 0.01) {
      var fa = 0.75 * frame, top = MAIN.h * rise;
      for (var gx = MAIN.x0; gx <= MAIN.x1 + 0.1; gx += 16) {
        for (var gz = MAIN.z0; gz <= MAIN.z1 + 0.1; gz += 15) {
          polyline([[gx, 0, gz], [gx, top, gz]], rgba(SAND, fa), 1);
        }
      }
      for (var lv = 1; lv <= FLOORS; lv++) {
        var y = (MAIN.h / FLOORS) * lv;
        if (y > top) break;
        polyline(rectY(MAIN, y).concat([[MAIN.x0, y, MAIN.z0]]), rgba(BONE, fa * 0.6), 1);
      }
      var wtop = WING.h * rise;
      polyline(rectY(WING, wtop).concat([[WING.x0, wtop, WING.z0]]), rgba(SAND, fa * 0.7), 1);
    }

    /* --- 04 massing --- */
    if (solid > 0.01) {
      var mh = MAIN.h * rise, wh = WING.h * rise;

      /* contact shadow, so the massing sits on the land instead of floating */
      var sh = { x0: MAIN.x0 - 3, x1: MAIN.x1 + 12, z0: MAIN.z0 - 2, z1: MAIN.z1 + 9 };
      face(rectY(sh, 0.05), rgba([20, 30, 24], 0.42 * solid), null);

      boxWalls(WING, 0, wh, null, 0.93 * solid, rgba(SAND, 0.32 * solid));
      face(rectY(WING, wh), rgba(mix(FOREST, BONE, 0.30), 0.96 * solid), rgba(SAND, 0.4 * solid));

      boxWalls(MAIN, 0, mh, null, 0.94 * solid, rgba(SAND, 0.38 * solid));
      face(rectY(MAIN, mh), rgba(mix(FOREST, BONE, 0.24), 0.97 * solid), rgba(SAND, 0.45 * solid));

      /* set-back crown — gives the silhouette something to be */
      if (rise > 0.97) {
        var CR = { x0: MAIN.x0 + 9, x1: MAIN.x1 - 9, z0: MAIN.z0 + 3, z1: MAIN.z1 - 3 };
        var crown = ease(ramp(phase, 2.40, 2.90));
        var cy2 = MAIN.h + 7 * crown;
        boxWalls(CR, MAIN.h, cy2, null, 0.95 * crown, rgba(SAND, 0.4 * crown));
        face(rectY(CR, cy2), rgba(mix(FOREST, BONE, 0.30), 0.96 * crown), rgba(SAND, 0.45 * crown));
        /* parapet line + a single mast */
        polyline(rectY(MAIN, MAIN.h + 1.4).concat([[MAIN.x0, MAIN.h + 1.4, MAIN.z0]]),
                 rgba(SAND, 0.5 * crown), 1);
        polyline([[MAIN.x1 - 14, cy2, 0], [MAIN.x1 - 14, cy2 + 11, 0]],
                 rgba(SAND, 0.55 * crown), 1);
      }

      /* --- glazing: a band per floor on the two long faces --- */
      if (glass > 0.01) {
        var fh = MAIN.h / FLOORS;
        for (var lvl = 0; lvl < FLOORS; lvl++) {
          var yb = lvl * fh + fh * 0.28, yt = lvl * fh + fh * 0.78;
          if (yt > mh) break;
          for (var col = 0; col < 6; col++) {
            var wx0 = MAIN.x0 + 4 + col * 12.3, wx1 = wx0 + 9;
            var isLit = LIT[lvl + '-' + col] ? lit : 0;
            var gl = rgba(mix(LINEN, TERRA, isLit), (0.18 + 0.5 * isLit) * glass);
            face([[wx0, yb, MAIN.z1], [wx1, yb, MAIN.z1], [wx1, yt, MAIN.z1], [wx0, yt, MAIN.z1]], gl, null);
            face([[wx0, yb, MAIN.z0], [wx1, yb, MAIN.z0], [wx1, yt, MAIN.z0], [wx0, yt, MAIN.z0]],
                 rgba(mix(LINEN, TERRA, isLit), (0.12 + 0.4 * isLit) * glass), null);
          }
          /* the short ends, so no side of the building is a blank slab */
          for (var e = 0; e < 2; e++) {
            var wz0 = MAIN.z0 + 4 + e * 13, wz1 = wz0 + 9;
            var eLit = LIT[lvl + '-' + (e + 6)] ? lit : 0;
            var eg = rgba(mix(LINEN, TERRA, eLit), (0.15 + 0.45 * eLit) * glass);
            face([[MAIN.x1, yb, wz0], [MAIN.x1, yb, wz1], [MAIN.x1, yt, wz1], [MAIN.x1, yt, wz0]], eg, null);
            face([[MAIN.x0, yb, wz0], [MAIN.x0, yb, wz1], [MAIN.x0, yt, wz1], [MAIN.x0, yt, wz0]],
                 rgba(mix(LINEN, TERRA, eLit), (0.11 + 0.36 * eLit) * glass), null);
          }
        }
      }

      /* --- terrace --- */
      face(rectY(DECK, 0.4), rgba(mix(FOREST, SAND, 0.42), 0.8 * solid), rgba(SAND, 0.4 * solid));
      var rail = rectY(DECK, 4).concat([[DECK.x0, 4, DECK.z0]]);
      polyline(rail, rgba(SAND, 0.4 * solid), 1);
    }

    /* paint far to near */
    prims.sort(function (a, b) { return a.d - b.d; });
    for (var k = 0; k < prims.length; k++) prims[k].fn();
  }

  /* ---------- phase from the written stages ---------- */
  var stageEls = Array.prototype.slice.call(document.querySelectorAll('.stage'));
  var CAPTIONS = [
    'Raw parcel · boundary and topography',
    'Plat, setbacks and yield',
    'Structure · six levels',
    'Operating asset · glazed and occupied',
    'Stabilised · held, or sold'
  ];

  function readPhase() {
    if (!stageEls.length) return 0;
    var line = window.innerHeight * 0.52;
    var c = stageEls.map(function (s) {
      var r = s.getBoundingClientRect();
      return r.top + r.height / 2;
    });
    if (line <= c[0]) return 0;
    if (line >= c[c.length - 1]) return c.length - 1;
    for (var i = 0; i < c.length - 1; i++) {
      if (line >= c[i] && line <= c[i + 1]) {
        return i + (line - c[i]) / (c[i + 1] - c[i] || 1);
      }
    }
    return 0;
  }

  /* ---------- sizing ---------- */
  function resize() {
    var rect = canvas.getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = rect.width; H = rect.height;
    canvas.width  = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    cx = W / 2;
    cy = H * 0.68;
    scale = Math.min(W / 168, H / 132);
  }

  /* ---------- loop ---------- */
  var phase = 0, target = 0, running = false, last = 0, capIndex = -1;

  function frame(t) {
    if (!running) return;
    var dt = Math.min((t - last) / 1000 || 0, 0.05);
    last = t;

    if (!reduce) theta += dt * 0.16;               /* ~40s per revolution */
    target = readPhase();
    phase += (target - phase) * Math.min(dt * 4, 1);

    ctx.clearRect(0, 0, W, H);
    scene(phase);

    var ci = clamp(Math.floor(phase + 0.3), 0, CAPTIONS.length - 1);
    if (ci !== capIndex && caption) {
      capIndex = ci;
      caption.textContent = CAPTIONS[ci] || '';
      canvas.setAttribute('aria-label',
        'Illustrative site model, rotating: ' + (CAPTIONS[ci] || ''));
    }
    requestAnimationFrame(frame);
  }

  function start() {
    if (running) return;
    running = true; last = performance.now();
    requestAnimationFrame(frame);
  }
  function stop() { running = false; }

  resize();
  window.addEventListener('resize', function () {
    resize();
    /* Nothing is animating under reduced motion, so redraw the static frame
       or the canvas would come back blank at the new size. */
    if (reduce) { ctx.clearRect(0, 0, W, H); scene(phase); }
  }, { passive: true });

  if (reduce) {
    /* One static frame, drawn at the finished stage. */
    phase = 4; theta = -0.6;
    ctx.clearRect(0, 0, W, H);
    scene(phase);
    if (caption) caption.textContent = CAPTIONS[4];
    return;
  }

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (e) { e.isIntersecting ? start() : stop(); });
    }, { rootMargin: '120px' }).observe(canvas);
  } else {
    start();
  }
})();
