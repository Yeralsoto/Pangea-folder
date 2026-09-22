/* ============================================================
   PANGEA VENTURES INTERNATIONAL — site behaviour
   Progressive enhancement only. Nothing here is required to
   read the page; with JS off, all content is present and visible.
   ============================================================ */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- rAF-throttled scroll bus ---------- */
  var scrollFns = [], ticking = false;
  function onScroll(fn) { scrollFns.push(fn); fn(); }
  function tick() {
    ticking = false;
    for (var i = 0; i < scrollFns.length; i++) scrollFns[i]();
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(tick); }
  }, { passive: true });
  window.addEventListener('resize', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(tick); }
  }, { passive: true });

  /* ---------- 1. Nav: transparent over the forest hero, solid after ---------- */
  (function () {
    var nav = $('.nav'), hero = $('.hero');
    if (!nav) return;
    onScroll(function () {
      var solid;
      if (hero) {
        /* Flip before the hero panel's bone frame slides under the bar,
           so Bone nav text is never sitting on Bone. */
        solid = hero.getBoundingClientRect().bottom <= nav.offsetHeight + 8;
      } else {
        solid = window.scrollY > 80;
      }
      nav.setAttribute('data-solid', solid ? 'true' : 'false');
    });
  })();

  /* ---------- 1b. Mobile menu ---------- */
  (function () {
    var nav = $('.nav'), btn = $('.nav__burger'), panel = $('#nav-panel');
    if (!nav || !btn || !panel) return;
    var lbl = $('.nav__burgerLabel', btn);

    function set(open) {
      nav.setAttribute('data-menu', String(open));
      btn.setAttribute('aria-expanded', String(open));
      panel.hidden = !open;
      if (lbl) lbl.textContent = open ? 'Close' : 'Menu';
    }
    set(false);

    btn.addEventListener('click', function () {
      set(btn.getAttribute('aria-expanded') !== 'true');
    });
    panel.addEventListener('click', function (e) {
      if (e.target.closest('a')) set(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && btn.getAttribute('aria-expanded') === 'true') {
        set(false); btn.focus();
      }
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 768) set(false);
    }, { passive: true });
  })();

  /* ---------- 2. Reveal on enter ---------- */
  (function () {
    var els = $$('.rv');
    if (!els.length) return;
    if (reduce || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });
    els.forEach(function (el) { io.observe(el); });
  })();

  /* ---------- 3. Pangea breaking apart ---------- */
  (function () {
    var svg = $('.drift');
    if (!svg) return;
    var lands = $$('.land', svg);
    var cap = $('[data-drift-caption]');
    if (!lands.length) return;

    /* progress 0 = the supercontinent, 1 = the world today */
    function apply(p) {
      var away = 1 - Math.pow(1 - p, 2.2);           /* slow start, then release */
      lands.forEach(function (g) {
        var dx  = parseFloat(g.getAttribute('data-dx'))  || 0;
        var dy  = parseFloat(g.getAttribute('data-dy'))  || 0;
        var rot = parseFloat(g.getAttribute('data-rot')) || 0;
        var cx  = parseFloat(g.getAttribute('data-cx')) || 0;
        var cy  = parseFloat(g.getAttribute('data-cy')) || 0;
        var k = 1 - away;                             /* 1 = still in Pangea */
        g.setAttribute('transform',
          'translate(' + (dx * k).toFixed(2) + ',' + (dy * k).toFixed(2) + ') ' +
          'rotate(' + (rot * k).toFixed(2) + ',' + cx + ',' + cy + ')');
      });
      /* the seams open as the landmass splits */
      svg.style.setProperty('--seam', (0.15 + 0.85 * away).toFixed(3));
      if (cap) {
        cap.textContent = away < 0.5
          ? 'Pangea · 200 million years ago'
          : 'Today · the same land, in pieces';
      }
    }

    if (reduce) { apply(1); return; }

    var section = svg.closest('.story');
    onScroll(function () {
      var vh = window.innerHeight || 1;
      var p;
      if (section && section.offsetHeight > vh * 1.2) {
        /* pinned: progress tracks the section's travel, so the whole
           break-apart happens while the map is centred */
        var r = section.getBoundingClientRect();
        var travel = Math.max(r.height - vh, 1);
        p = (vh * 0.12 - r.top) / travel;
      } else {
        /* not pinned: track the figure's centre across the viewport, so the
           break plays while the map is actually on screen */
        var f = svg.getBoundingClientRect();
        var mid = f.top + f.height / 2;
        p = (vh * 0.82 - mid) / (vh * 0.52);
      }
      apply(p < 0 ? 0 : p > 1 ? 1 : p);
    });
  })();

  /* ---------- 4. Lifecycle: active stage + progress meter ---------- */
  (function () {
    var list = $('[data-stages]');
    if (!list) return;
    var stages = $$('.stage', list);
    var fill   = $('[data-cycle-fill]');
    var count  = $('[data-cycle-count]');
    if (!stages.length) return;

    onScroll(function () {
      var line = window.innerHeight * 0.55;
      var active = 0;
      stages.forEach(function (s, i) {
        var r = s.getBoundingClientRect();
        if (r.top <= line) active = i;
      });
      /* before the list is reached at all, nothing is lit */
      var first = stages[0].getBoundingClientRect();
      var lit = first.top <= line;

      stages.forEach(function (s, i) {
        s.setAttribute('data-active', String(lit && i === active));
      });
      var n = lit ? active + 1 : 1;
      if (fill)  fill.style.width = (lit ? (n / stages.length) * 100 : 0) + '%';
      if (count) count.textContent = '0' + n + ' / 0' + stages.length;
    });
  })();

  /* ---------- 5. Symbol anatomy ---------- */
  (function () {
    var grid = $('[data-symbol]');
    if (!grid) return;
    var items = $$('.anatomy li', grid);

    function focus(part) {
      if (part) grid.setAttribute('data-focus', part);
      else grid.removeAttribute('data-focus');
      items.forEach(function (li) {
        var btn = $('button', li);
        li.setAttribute('aria-current', String(!!part && btn && btn.getAttribute('data-part') === part));
      });
    }

    items.forEach(function (li) {
      var btn = $('button', li);
      if (!btn) return;
      var part = btn.getAttribute('data-part');
      btn.addEventListener('mouseenter', function () { focus(part); });
      btn.addEventListener('focus',      function () { focus(part); });
      btn.addEventListener('click',      function () {
        focus(grid.getAttribute('data-focus') === part ? null : part);
      });
    });
    grid.addEventListener('mouseleave', function () { focus(null); });
  })();

  /* ---------- 6. Services accordion ---------- */
  (function () {
    var host = $('[data-services]');
    if (!host) return;
    $$('.svc', host).forEach(function (svc) {
      var head  = $('.svc__head', svc);
      var panel = $('.svc__panel', svc);
      var tog   = $('.svc__toggle', svc);
      if (!head || !panel) return;

      head.setAttribute('role', 'button');
      head.setAttribute('tabindex', '0');
      head.setAttribute('aria-expanded', 'false');
      head.setAttribute('aria-controls', panel.id);

      function set(open) {
        svc.setAttribute('data-open', String(open));
        head.setAttribute('aria-expanded', String(open));
        panel.setAttribute('aria-hidden', String(!open));
        if (tog) tog.textContent = open ? 'Close −' : 'Details +';
      }
      set(false);

      head.addEventListener('click', function () {
        set(svc.getAttribute('data-open') !== 'true');
      });
      head.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
          e.preventDefault();
          set(svc.getAttribute('data-open') !== 'true');
        }
      });
    });
  })();

  /* ---------- 7. Disclosure block: rows land in order ---------- */
  (function () {
    var table = $('[data-dblock]');
    if (!table) return;
    var rows = $$('.d-row', table);
    if (!rows.length) return;
    if (reduce || !('IntersectionObserver' in window)) {
      rows.forEach(function (r) { r.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        rows.forEach(function (r, i) {
          setTimeout(function () { r.classList.add('is-in'); }, i * 110);
        });
        io.disconnect();
      });
    }, { threshold: 0.2 });
    io.observe(table);
  })();

  /* ---------- 8. Current section in the nav ---------- */
  (function () {
    var links = $$('.nav__links a[href^="#"]').filter(function (a) {
      return !a.classList.contains('nav__cta');
    });
    if (!links.length) return;
    var targets = links.map(function (a) { return document.getElementById(a.hash.slice(1)); });
    onScroll(function () {
      var line = window.innerHeight * 0.4, current = -1;
      targets.forEach(function (t, i) {
        if (t && t.getBoundingClientRect().top <= line) current = i;
      });
      links.forEach(function (a, i) {
        a.style.opacity = i === current ? '1' : '';
      });
    });
  })();
})();

/* ============================================================
   Technical drawings — staged, informative sequences.
   Each <svg data-draw> holds groups tagged data-step. They are released
   in order: the line work of a step draws itself from its own path
   length, its fills and labels follow, the caption says what appeared,
   and any counter counts up. The final step holds.
   ============================================================ */
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var figs = Array.prototype.slice.call(document.querySelectorAll('svg[data-draw]'));
  if (!figs.length) return;

  var STEP_MS = 1000;      /* dwell on each step */
  var DRAW_MS = 760;       /* how long one stroke takes to draw */

  function prepare(svg) {
    Array.prototype.forEach.call(svg.querySelectorAll('.dl'), function (el) {
      var len = 0;
      try { len = el.getTotalLength(); } catch (e) {}
      if (!len) return;
      el.style.strokeDasharray = len;
      el.style.strokeDashoffset = len;
      el.dataset.len = len;
    });
  }

  function countUp(el, ms) {
    var to = +el.dataset.countTo || 0, suffix = el.dataset.suffix || '';
    var t0 = null;
    function frame(t) {
      if (t0 === null) t0 = t;
      var k = Math.min((t - t0) / ms, 1);
      el.textContent = Math.round(to * (1 - Math.pow(1 - k, 3))) + suffix;
      if (k < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function runStep(svg, g) {
    g.classList.add('is-on');
    var lines = Array.prototype.slice.call(g.querySelectorAll('.dl'));
    lines.sort(function (a, b) { return (+a.dataset.len || 0) - (+b.dataset.len || 0); });
    lines.forEach(function (el, i) {
      el.style.transition = 'stroke-dashoffset ' + DRAW_MS +
        'ms cubic-bezier(.22,.61,.36,1) ' + (i * 38) + 'ms';
      el.style.strokeDashoffset = '0';
    });
    Array.prototype.forEach.call(g.querySelectorAll('.dnum'), function (el) {
      countUp(el, 1100);
    });
  }

  function play(figure) {
    var svg = figure.svg, steps = figure.steps, caps = figure.caps;
    steps.forEach(function (g, i) {
      setTimeout(function () {
        runStep(svg, g);
        caps.forEach(function (c, j) { c.classList.toggle('is-on', j === i); });
      }, i * STEP_MS);
    });
  }

  var items = figs.map(function (svg) {
    var fc = svg.parentNode.querySelector('[data-dwg-cap]');
    return {
      svg: svg,
      steps: Array.prototype.slice.call(svg.querySelectorAll('.dstep')),
      caps: fc ? Array.prototype.slice.call(fc.querySelectorAll('.dwg__capItem')) : []
    };
  });

  if (reduce || !('IntersectionObserver' in window)) {
    items.forEach(function (f) {
      f.steps.forEach(function (g) { g.classList.add('is-on'); });
      f.caps.forEach(function (c, j) { c.classList.toggle('is-on', j === f.caps.length - 1); });
      Array.prototype.forEach.call(f.svg.querySelectorAll('.dnum'), function (el) {
        el.textContent = (el.dataset.countTo || '') + (el.dataset.suffix || '');
      });
    });
    return;
  }

  items.forEach(function (f) { prepare(f.svg); });

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      var f = items.filter(function (x) { return x.svg === e.target; })[0];
      if (f) play(f);
    });
  }, { threshold: 0.3 });

  items.forEach(function (f) { io.observe(f.svg); });
})();

/* ============================================================
   Exit prompt. Shows once per session, on intent to leave on a
   pointer device, or after a deep scroll then a long pause on
   touch (where there is no such thing as leaving the viewport).
   ============================================================ */
(function () {
  'use strict';
  var root = document.getElementById('exit-prompt');
  if (!root) return;

  var KEY = 'pangea.exit.seen';
  try { if (sessionStorage.getItem(KEY)) return; } catch (e) { /* private mode */ }

  var panel = root.querySelector('.exit__panel');
  var lastFocus = null;
  var armed = false;

  function open() {
    if (root.dataset.open === '1') return;
    root.dataset.open = '1';
    try { sessionStorage.setItem(KEY, '1'); } catch (e) {}
    lastFocus = document.activeElement;
    root.hidden = false;
    root.setAttribute('aria-hidden', 'false');
    requestAnimationFrame(function () { root.classList.add('is-open'); });
    if (panel) panel.focus();
    document.addEventListener('keydown', onKey);
  }

  function close() {
    root.classList.remove('is-open');
    root.setAttribute('aria-hidden', 'true');
    document.removeEventListener('keydown', onKey);
    setTimeout(function () { root.hidden = true; }, 420);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function onKey(e) {
    if (e.key === 'Escape') { close(); return; }
    if (e.key !== 'Tab' || !panel) return;
    var f = panel.querySelectorAll('a[href], button');
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  Array.prototype.forEach.call(root.querySelectorAll('[data-exit-close]'), function (el) {
    el.addEventListener('click', close);
  });

  /* Don't fire at someone who just arrived. */
  setTimeout(function () { armed = true; }, 12000);

  if (window.matchMedia('(pointer: fine)').matches) {
    document.addEventListener('mouseout', function (e) {
      if (!armed || e.relatedTarget || e.clientY > 8) return;
      open();
    });
  } else {
    /* Touch: read most of the page, then stop for a while. */
    var idle = null;
    window.addEventListener('scroll', function () {
      if (!armed) return;
      var d = document.documentElement;
      var past = (window.scrollY + window.innerHeight) / d.scrollHeight;
      if (past < 0.55) return;
      clearTimeout(idle);
      idle = setTimeout(open, 9000);
    }, { passive: true });
  }
})();
