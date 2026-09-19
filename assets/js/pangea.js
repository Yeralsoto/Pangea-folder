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

  /* ---------- 3. The continent: six plates drift into one landmass ---------- */
  (function () {
    var svg = $('.plates');
    if (!svg) return;
    var plates = $$('.plate', svg);
    if (!plates.length) return;

    if (reduce) { plates.forEach(function (p) { p.style.transform = 'none'; }); return; }

    function apply() {
      var r = svg.getBoundingClientRect();
      var vh = window.innerHeight || 1;
      /* progress 0 -> 1 as the figure travels from just below the fold
         to roughly the middle of the viewport */
      var start = vh * 0.92, end = vh * 0.34;
      var p = (start - r.top) / (start - end);
      p = p < 0 ? 0 : p > 1 ? 1 : p;
      var eased = 1 - Math.pow(1 - p, 3);   /* easeOutCubic */
      var away = 1 - eased;

      plates.forEach(function (g) {
        var dx  = parseFloat(g.getAttribute('data-dx'))  || 0;
        var dy  = parseFloat(g.getAttribute('data-dy'))  || 0;
        var rot = parseFloat(g.getAttribute('data-rot')) || 0;
        g.style.transform =
          'translate(' + (dx * away).toFixed(2) + 'px,' + (dy * away).toFixed(2) + 'px) ' +
          'rotate(' + (rot * away).toFixed(2) + 'deg)';
        g.style.opacity = (0.45 + 0.55 * eased).toFixed(3);
      });
      /* the seams between the plates close as the continent assembles */
      svg.style.setProperty('--seam', (1 - eased * 0.9).toFixed(3));
    }
    onScroll(apply);
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
