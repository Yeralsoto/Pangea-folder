/* ============================================================
   PANGEA — the cycle.

   Five stages on a ring. A runner travels the arc continuously,
   so the loop reads as a loop rather than a diagram. Hovering,
   clicking or tabbing a stage holds it and shows what an asset
   can become at that point.
   ============================================================ */
(function () {
  'use strict';

  var root = document.querySelector('[data-cycle]');
  if (!root) return;

  var svg     = root.querySelector('.cy__svg');
  var nodes   = Array.prototype.slice.call(root.querySelectorAll('[data-node]'));
  var arcs    = Array.prototype.slice.call(root.querySelectorAll('[data-arc]'));
  var labels  = Array.prototype.slice.call(root.querySelectorAll('[data-label]'));
  var outs    = Array.prototype.slice.call(root.querySelectorAll('.cy__out'));
  var runner  = root.querySelector('.cy__runner');
  var cNum    = root.querySelector('.cy__centreN');
  var cName   = root.querySelector('.cy__centre');
  var cSub    = root.querySelector('.cy__centreS');
  var pSub    = root.querySelector('[data-cy-sub]');
  var pDet    = root.querySelector('[data-cy-detail]');
  var reduce  = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var STAGES = [
    ['Identify', 'The land',          'Markets, data, leads, acquisitions'],
    ['Evaluate', 'What it could be',  'Underwriting, diligence, risk, strategy'],
    ['Create',   'What it becomes',   'Entitlement, construction, execution'],
    ['Operate',  'What gets managed', 'Rentals, hospitality, management'],
    ['Optimize', 'What comes next',   'Hold, refinance, sell, reinvest']
  ];

  var R = 128, CX = 160, CY = 160;
  var index = 0, held = false, t0 = null, raf = null;

  function point(a) {
    return [CX + R * Math.cos(a), CY + R * Math.sin(a)];
  }

  function paint(i) {
    index = i;
    var s = STAGES[i];
    cNum.textContent  = ('0' + (i + 1)).slice(-2);
    cName.textContent = s[0];
    cSub.textContent  = s[1];
    if (pSub) pSub.textContent = s[1];
    if (pDet) pDet.textContent = s[2];

    nodes.forEach(function (n, k)  { n.setAttribute('data-on', String(k === i)); });
    labels.forEach(function (l, k) { l.setAttribute('data-on', String(k === i)); });
    arcs.forEach(function (a, k)   { a.setAttribute('data-on', String(k === i)); });
    outs.forEach(function (o) {
      var list = (o.getAttribute('data-stages') || '').split(',');
      o.setAttribute('data-on', String(list.indexOf(String(i)) !== -1));
    });
  }

  /* the runner keeps moving; the ring is a loop, not a list */
  function frame(t) {
    if (t0 === null) t0 = t;
    var p = ((t - t0) / 17000) % 1;                 /* one lap every 17s */
    var a = -Math.PI / 2 + p * Math.PI * 2;
    var xy = point(a);
    runner.setAttribute('cx', xy[0].toFixed(1));
    runner.setAttribute('cy', xy[1].toFixed(1));
    if (!held) {
      var i = Math.floor(((p + 0.1) % 1) * 5);
      if (i !== index) paint(i);
    }
    raf = requestAnimationFrame(frame);
  }

  function hold(i) {
    held = true;
    paint(i);
    clearTimeout(hold._t);
    hold._t = setTimeout(function () { held = false; }, 6000);
  }

  nodes.forEach(function (n, i) {
    n.setAttribute('tabindex', '0');
    n.setAttribute('role', 'button');
    n.setAttribute('aria-label', STAGES[i][0] + ' — ' + STAGES[i][1]);
    ['mouseenter', 'click', 'focus'].forEach(function (ev) {
      n.addEventListener(ev, function () { hold(i); });
    });
    n.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); hold(i); }
    });
  });
  labels.forEach(function (l, i) {
    l.addEventListener('mouseenter', function () { hold(i); });
    l.addEventListener('click', function () { hold(i); });
  });
  outs.forEach(function (o) {
    o.addEventListener('mouseenter', function () {
      var first = (o.getAttribute('data-stages') || '0').split(',')[0];
      hold(parseInt(first, 10));
    });
  });

  paint(0);
  if (reduce) { runner.style.display = 'none'; return; }

  function start() { if (!raf) { t0 = null; raf = requestAnimationFrame(frame); } }
  function stop()  { if (raf) { cancelAnimationFrame(raf); raf = null; } }

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (e) { e.isIntersecting ? start() : stop(); });
    }, { threshold: 0.25 }).observe(root);
  } else start();
})();
