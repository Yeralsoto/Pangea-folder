/* ============================================================
   PANGEA — the asset-type morph.

   Each asset type is an explicit outline in viewBox units, drawn
   the way the building actually is: vertical walls vertical,
   roof pitches straight, eaves where eaves go.

   Two shapes can only be interpolated if they carry the same
   number of points, so every outline is RESAMPLED to a fixed
   count by inserting extra points ALONG its segments. Original
   vertices are never moved, so corners stay exactly square at
   rest — the earlier version sampled a height function instead,
   which turned every wall into a one-sample diagonal.

   Detail (lot lines, windows, framing) is clipped to the current
   silhouette, so nothing can spill into open sky.
   ============================================================ */
(function () {
  'use strict';

  var root = document.querySelector('[data-assettypes]');
  if (!root) return;

  var shape  = root.querySelector('[data-at-shape]');
  var detail = root.querySelector('[data-at-detail]');
  var label  = root.querySelector('[data-at-label]');
  var meter  = root.querySelector('[data-at-meter]');
  var btns   = Array.prototype.slice.call(root.querySelectorAll('[data-at]'));
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var K = 96;          /* points every outline is resampled to */
  var BASE = 100;

  /* ---------- outlines, in viewBox units (200 x 118, ground at y=100) ---------- */
  var TYPES = [
    { name: 'Land & lots',
      pts: [[8,100],[12,94],[188,94],[192,100]],
      detail: [ {l:[44,94,44,100]}, {l:[80,94,80,100]}, {l:[116,94,116,100]},
                {l:[152,94,152,100]}, {l:[12,94,188,94]} ] },

    { name: 'Single-family',
      pts: [[62,100],[62,64],[54,64],[100,34],[146,64],[138,64],[138,100]],
      detail: [ {x:70,y:72,w:14,h:12}, {x:92,y:72,w:14,h:12},
                {x:114,y:72,w:14,h:12}, {x:92,y:88,w:14,h:12} ] },

    { name: 'Multifamily',
      pts: [[50,100],[50,54],[46,54],[46,48],[154,48],[154,54],[150,54],[150,100]],
      detail: [ {x:58,y:58,w:12,h:9}, {x:78,y:58,w:12,h:9}, {x:98,y:58,w:12,h:9},
                {x:118,y:58,w:12,h:9}, {x:138,y:58,w:12,h:9},
                {x:58,y:72,w:12,h:9}, {x:78,y:72,w:12,h:9}, {x:98,y:72,w:12,h:9},
                {x:118,y:72,w:12,h:9}, {x:138,y:72,w:12,h:9},
                {x:58,y:86,w:12,h:9}, {x:78,y:86,w:12,h:9}, {x:98,y:86,w:12,h:9},
                {x:118,y:86,w:12,h:9}, {x:138,y:86,w:12,h:9} ] },

    { name: 'Commercial',
      pts: [[18,100],[18,66],[14,66],[14,60],[186,60],[186,66],[182,66],[182,100]],
      detail: [ {l:[18,78,182,78]},
                {x:26,y:66,w:20,h:9}, {x:54,y:66,w:20,h:9}, {x:82,y:66,w:20,h:9},
                {x:110,y:66,w:20,h:9}, {x:138,y:66,w:20,h:9},
                {x:26,y:84,w:20,h:12}, {x:110,y:84,w:48,h:12} ] },

    { name: 'Hospitality & hotels',
      pts: [[22,100],[22,76],[64,76],[64,28],[60,28],[60,24],[152,24],[152,28],
            [148,28],[148,100]],
      detail: [ {x:72,y:34,w:12,h:9}, {x:90,y:34,w:12,h:9}, {x:108,y:34,w:12,h:9}, {x:126,y:34,w:12,h:9},
                {x:72,y:48,w:12,h:9}, {x:90,y:48,w:12,h:9}, {x:108,y:48,w:12,h:9}, {x:126,y:48,w:12,h:9},
                {x:72,y:62,w:12,h:9}, {x:90,y:62,w:12,h:9}, {x:108,y:62,w:12,h:9}, {x:126,y:62,w:12,h:9},
                {x:72,y:76,w:12,h:9}, {x:90,y:76,w:12,h:9}, {x:108,y:76,w:12,h:9}, {x:126,y:76,w:12,h:9},
                {x:30,y:84,w:12,h:9}, {x:46,y:84,w:12,h:9},
                {l:[86,100,86,88]}, {l:[114,100,114,88]}, {l:[86,88,114,88]} ] },

    { name: 'Short-term rentals',
      pts: [[46,100],[46,72],[40,72],[74,50],[108,72],[102,72],[102,100],
            [118,100],[118,78],[113,78],[142,60],[171,78],[166,78],[166,100]],
      detail: [ {x:62,y:78,w:14,h:11}, {x:64,y:92,w:10,h:8},
                {x:132,y:84,w:12,h:9} ] },

    { name: 'Long-term rentals',
      pts: [[30,100],[30,76],[54,58],[78,76],[102,58],[126,76],[150,58],[174,76],
            [174,100]],
      detail: [ {x:38,y:82,w:12,h:9}, {x:86,y:82,w:12,h:9}, {x:134,y:82,w:12,h:9},
                {l:[78,76,78,100]}, {l:[126,76,126,100]} ] },

    { name: 'Renovation & flips',
      pts: [[52,100],[52,66],[44,66],[90,38],[128,62],[128,76],[156,76],[156,100]],
      detail: [ {x:62,y:74,w:14,h:11}, {x:84,y:74,w:14,h:11},
                {l:[128,82,156,82]}, {l:[128,90,156,90]},
                {l:[136,76,136,100]}, {l:[148,76,148,100]} ] },

    { name: 'New construction',
      pts: [[40,100],[40,74],[80,74],[80,54],[120,54],[120,34],[160,34],[160,100]],
      detail: [ {l:[52,100,52,74]}, {l:[66,100,66,74]}, {l:[94,100,94,54]},
                {l:[108,100,108,54]}, {l:[134,100,134,34]}, {l:[148,100,148,34]},
                {l:[40,86,160,86]}, {l:[40,64,120,64]}, {l:[80,44,160,44]} ] }
  ];

  /* ---------- resample an outline to exactly K points ---------- */
  function resample(pts, n) {
    var segs = [], total = 0, i;
    for (i = 0; i < pts.length - 1; i++) {
      var d = Math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]);
      segs.push(d); total += d;
    }
    var extra = n - pts.length;
    if (extra < 0) extra = 0;
    var alloc = segs.map(function (d) { return Math.floor(extra * d / total); });
    var used = alloc.reduce(function (a, b) { return a + b; }, 0);
    var k = 0;
    while (used < extra) { alloc[k % alloc.length]++; used++; k++; }

    var out = [];
    for (var s = 0; s < segs.length; s++) {
      out.push(pts[s].slice());
      for (var j = 1; j <= alloc[s]; j++) {
        var t = j / (alloc[s] + 1);
        out.push([pts[s][0] + (pts[s + 1][0] - pts[s][0]) * t,
                  pts[s][1] + (pts[s + 1][1] - pts[s][1]) * t]);
      }
    }
    out.push(pts[pts.length - 1].slice());
    return out;
  }

  TYPES.forEach(function (t) { t.frame = resample(t.pts, K); });

  function pathFrom(p) {
    var d = 'M' + p[0][0].toFixed(1) + ' ' + BASE;
    for (var i = 0; i < p.length; i++) d += ' L' + p[i][0].toFixed(1) + ' ' + p[i][1].toFixed(1);
    return d + ' L' + p[p.length - 1][0].toFixed(1) + ' ' + BASE + ' Z';
  }

  /* ---------- detail, clipped to the silhouette ---------- */
  var clipPath = null;
  (function makeClip() {
    var svg = root.querySelector('[data-at-svg]');
    var defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    var cp = document.createElementNS('http://www.w3.org/2000/svg', 'clipPath');
    cp.setAttribute('id', 'atClip');
    clipPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    cp.appendChild(clipPath);
    defs.appendChild(cp);
    svg.insertBefore(defs, svg.firstChild);
    detail.setAttribute('clip-path', 'url(#atClip)');
  })();

  function drawDetail(items) {
    var out = '';
    items.forEach(function (it, i) {
      if (it.l) {
        out += '<path class="atd" style="--i:' + i + '" d="M' + it.l[0] + ' ' + it.l[1] +
               ' L' + it.l[2] + ' ' + it.l[3] + '"/>';
      } else {
        out += '<rect class="atd atd--f" style="--i:' + i + '" x="' + it.x + '" y="' + it.y +
               '" width="' + it.w + '" height="' + it.h + '"/>';
      }
    });
    detail.innerHTML = out;
  }

  /* ---------- morph ---------- */
  var cur = TYPES[0].frame.map(function (p) { return p.slice(); });
  var target = TYPES[0].frame;
  var index = 0, raf = null, timer = null;

  function tick() {
    var moving = false;
    for (var i = 0; i < K; i++) {
      for (var a = 0; a < 2; a++) {
        var d = target[i][a] - cur[i][a];
        if (Math.abs(d) > 0.02) { cur[i][a] += d * 0.17; moving = true; }
        else cur[i][a] = target[i][a];
      }
    }
    var d2 = pathFrom(cur);
    shape.setAttribute('d', d2);
    clipPath.setAttribute('d', d2);
    raf = moving ? requestAnimationFrame(tick) : null;
  }

  function show(i, fromUser) {
    index = ((i % TYPES.length) + TYPES.length) % TYPES.length;
    var t = TYPES[index];
    target = t.frame;
    if (!raf) raf = requestAnimationFrame(tick);

    detail.classList.remove('is-in');
    setTimeout(function () { drawDetail(t.detail); detail.classList.add('is-in'); }, 200);

    if (label) label.textContent = t.name;
    btns.forEach(function (b, k) { b.parentNode.setAttribute('aria-current', String(k === index)); });
    if (meter) meter.style.width = ((index + 1) / TYPES.length * 100) + '%';
    if (fromUser) restart();
  }

  function restart() {
    clearInterval(timer);
    if (reduce) return;
    timer = setInterval(function () { show(index + 1); }, 4500);
  }
  function stop() { clearInterval(timer); timer = null; }

  btns.forEach(function (b) {
    var i = parseInt(b.getAttribute('data-at'), 10);
    b.addEventListener('click', function () { show(i, true); });
    b.addEventListener('mouseenter', function () { show(i, true); });
    b.addEventListener('focus', function () { show(i, true); });
  });

  var d0 = pathFrom(cur);
  shape.setAttribute('d', d0);
  clipPath.setAttribute('d', d0);
  drawDetail(TYPES[0].detail);
  detail.classList.add('is-in');
  show(0);

  if (reduce) return;
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (e) { e.isIntersecting ? restart() : stop(); });
    }, { threshold: 0.3 }).observe(root);
  } else restart();
})();
