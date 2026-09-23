/* ============================================================
   PANGEA — the asset-type morph.

   One silhouette that changes shape for each asset type. Every
   shape is sampled from a height profile at the SAME number of
   points, so any two can be interpolated directly — no path
   matching, no library, no guessing about point counts.

   Details (lot lines, windows, framing) live on a second layer
   and cross-fade, because they cannot be interpolated.
   ============================================================ */
(function () {
  'use strict';

  var root = document.querySelector('[data-assettypes]');
  if (!root) return;

  var svg    = root.querySelector('[data-at-svg]');
  var shape  = root.querySelector('[data-at-shape]');
  var detail = root.querySelector('[data-at-detail]');
  var label  = root.querySelector('[data-at-label]');
  var meter  = root.querySelector('[data-at-meter]');
  var btns   = Array.prototype.slice.call(root.querySelectorAll('[data-at]'));
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var N = 180;            /* samples across the width */
  var W = 200, BASE = 100, MAXH = 86;

  /* ---------- shape language ---------- */
  function box(x0, x1, h) {
    return function (x) { return (x >= x0 && x <= x1) ? h : 0; };
  }
  function gable(x0, x1, wall, peak) {
    var mid = (x0 + x1) / 2, half = (x1 - x0) / 2;
    return function (x) {
      if (x < x0 || x > x1) return 0;
      return wall + (peak - wall) * (1 - Math.abs(x - mid) / half);
    };
  }
  function stack() {
    var fns = Array.prototype.slice.call(arguments);
    return function (x) {
      var h = 0;
      for (var i = 0; i < fns.length; i++) h = Math.max(h, fns[i](x));
      return h;
    };
  }
  function sample(fn) {
    var a = [];
    for (var i = 0; i < N; i++) {
      var x = i / (N - 1) * 100;
      a.push(Math.max(0, Math.min(1, fn(x))));
    }
    return a;
  }

  /* windows / lot lines / framing, in viewBox units */
  function win(cols, rows, x0, x1, top, bottom) {
    var out = [], cw = (x1 - x0) / cols, rh = (bottom - top) / rows;
    for (var c = 0; c < cols; c++) {
      for (var r = 0; r < rows; r++) {
        out.push({ x: x0 + c * cw + cw * 0.28, y: top + r * rh + rh * 0.26,
                   w: cw * 0.44, h: rh * 0.44 });
      }
    }
    return out;
  }
  function vlines(xs, y0, y1) {
    return xs.map(function (x) { return { line: [x, y0, x, y1] }; });
  }

  var TYPES = [
    { name: 'Land & lots',
      profile: sample(box(4, 96, 0.05)),
      detail: vlines([26, 48, 70, 92, 14], 95, 100)
                .concat([{ line: [4, 95, 96, 95] }]) },

    { name: 'Single-family',
      profile: sample(stack(box(34, 66, 0.30), gable(30, 70, 0.30, 0.50))),
      detail: win(3, 1, 36, 64, 80, 92).concat([{ x: 48, y: 92, w: 5, h: 8 }]) },

    { name: 'Multifamily',
      profile: sample(box(24, 76, 0.50)),
      detail: win(5, 4, 27, 73, 60, 96) },

    { name: 'Commercial',
      profile: sample(stack(box(10, 90, 0.28), box(10, 90, 0.30))),
      detail: win(9, 2, 13, 87, 78, 96) },

    { name: 'Hospitality & hotels',
      profile: sample(stack(box(32, 72, 0.76), box(12, 32, 0.32))),
      detail: win(5, 6, 35, 69, 38, 94).concat(win(3, 2, 15, 30, 76, 96)) },

    { name: 'Short-term rentals',
      profile: sample(stack(gable(26, 50, 0.24, 0.40), gable(56, 80, 0.24, 0.40))),
      detail: win(2, 1, 30, 46, 84, 94).concat(win(2, 1, 60, 76, 84, 94)) },

    { name: 'Long-term rentals',
      profile: sample(stack(gable(14, 38, 0.22, 0.34), gable(38, 62, 0.22, 0.34),
                            gable(62, 86, 0.22, 0.34))),
      detail: win(1, 1, 22, 30, 86, 95).concat(win(1, 1, 46, 54, 86, 95))
               .concat(win(1, 1, 70, 78, 86, 95)) },

    { name: 'Renovation & flips',
      profile: sample(stack(box(30, 50, 0.26), gable(28, 52, 0.26, 0.42),
                            box(50, 70, 0.40))),
      detail: win(2, 1, 33, 47, 86, 94)
               .concat([{ line: [50, 58, 50, 100] },
                        { line: [52, 56, 68, 56] },
                        { line: [52, 56, 52, 100] }]) },

    { name: 'New construction',
      profile: sample(stack(box(26, 44, 0.32), box(44, 62, 0.52), box(62, 80, 0.70))),
      detail: vlines([26, 44, 62, 80], 30, 100)
               .concat([{ line: [26, 68, 44, 68] }, { line: [44, 48, 62, 48] },
                        { line: [62, 30, 80, 30] }, { line: [26, 84, 80, 84] }]) }
  ];

  /* ---------- rendering ---------- */
  function pathFrom(h) {
    var d = 'M0 ' + BASE;
    for (var i = 0; i < N; i++) {
      d += ' L' + (i / (N - 1) * W).toFixed(1) + ' ' + (BASE - h[i] * MAXH).toFixed(1);
    }
    return d + ' L' + W + ' ' + BASE + ' Z';
  }

  function drawDetail(items) {
    var out = '';
    items.forEach(function (it, i) {
      if (it.line) {
        out += '<path class="atd" style="--i:' + i + '" d="M' + it.line[0] + ' ' +
               it.line[1] + ' L' + it.line[2] + ' ' + it.line[3] + '"/>';
      } else {
        out += '<rect class="atd atd--f" style="--i:' + i + '" x="' + it.x + '" y="' +
               it.y + '" width="' + it.w + '" height="' + it.h + '"/>';
      }
    });
    detail.innerHTML = out;
  }

  var cur = TYPES[0].profile.slice();
  var target = TYPES[0].profile;
  var index = 0, raf = null, timer = null;

  function ease(t) { return t * t * (3 - 2 * t); }

  function tick() {
    var moved = false;
    for (var i = 0; i < N; i++) {
      var d = target[i] - cur[i];
      if (Math.abs(d) > 0.0005) { cur[i] += d * 0.16; moved = true; }
      else cur[i] = target[i];
    }
    shape.setAttribute('d', pathFrom(cur));
    raf = moved ? requestAnimationFrame(tick) : null;
  }

  function show(i, fromUser) {
    index = ((i % TYPES.length) + TYPES.length) % TYPES.length;
    var t = TYPES[index];
    target = t.profile;
    if (!raf) raf = requestAnimationFrame(tick);

    detail.classList.remove('is-in');
    setTimeout(function () { drawDetail(t.detail); detail.classList.add('is-in'); }, 190);

    if (label) label.textContent = t.name;
    btns.forEach(function (b, k) {
      b.parentNode.setAttribute('aria-current', String(k === index));
    });
    if (meter) {
      meter.style.width = ((index + 1) / TYPES.length * 100) + '%';
    }
    if (fromUser) restart();
  }

  /* ---------- auto-advance, paused on interaction and off-screen ---------- */
  function restart() {
    clearInterval(timer);
    if (reduce) return;
    timer = setInterval(function () { show(index + 1); }, 3200);
  }
  function stop() { clearInterval(timer); timer = null; }

  btns.forEach(function (b) {
    var i = parseInt(b.getAttribute('data-at'), 10);
    b.addEventListener('click', function () { show(i, true); });
    b.addEventListener('mouseenter', function () { show(i, true); });
    b.addEventListener('focus', function () { show(i, true); });
  });

  drawDetail(TYPES[0].detail);
  detail.classList.add('is-in');
  shape.setAttribute('d', pathFrom(cur));
  show(0);

  if (reduce) return;
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (e) { e.isIntersecting ? restart() : stop(); });
    }, { threshold: 0.3 }).observe(root);
  } else restart();
})();
