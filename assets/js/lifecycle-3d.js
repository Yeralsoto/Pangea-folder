/* ============================================================
   PANGEA — the lifecycle model, lit for real.
   Three.js r160 (vendored, MIT). Real sun with soft shadows, a
   sky/ground hemisphere bounce, a procedural environment for
   reflections, physically-based materials and ACES tone mapping.

   Same contract as the 2D fallback: the scene is driven by
   `phase` (0 -> 4) read from the five .stage elements, so the
   model and the written stages never drift apart.

   If WebGL is missing or this throws, the 2D canvas renderer in
   lifecycle-model.js is started instead.
   ============================================================ */
import * as THREE from '../vendor/three.module.min.js';

const canvas = document.getElementById('cycle-model');
const caption = document.querySelector('[data-model-caption]');

function fallback() {
  /* A canvas that has handed out a WebGL context can never return a 2D one,
     so give the fallback a fresh element in the same place. */
  if (canvas) {
    const fresh = canvas.cloneNode(false);
    fresh.dataset.gl = '0';
    canvas.replaceWith(fresh);
  }
  if (window.PangeaModel2D) window.PangeaModel2D();
}

if (!canvas) { /* nothing to do */ } else {
  try { boot(); } catch (err) { console.warn('[pangea] 3D model unavailable', err); fallback(); }
}

function boot() {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  canvas.dataset.gl = '1';

  /* ---------- palette ---------- */
  const C = {
    sky:    0xEDE7DB,
    ground: 0x27372D,
    earth:  0x6F6A4E,
    plaster:0xDCD6C9,
    plaster2:0xC3BBAA,
    roof:   0x4A4F47,
    frame:  0xB5AD99,
    glass:  0x24332C,
    lit:    0xC46738,
    deck:   0x97886C,
    sand:   0xC9B69B,
    bg:     0x24322A,
  };

  /* ---------- scene ---------- */
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(C.bg);
  scene.fog = new THREE.Fog(C.bg, 240, 520);

  const camera = new THREE.PerspectiveCamera(30, 1, 1, 800);
  camera.position.set(0, 104, 208);
  camera.lookAt(0, 16, 0);

  /* Procedural sky/ground gradient, run through PMREM so glass and
     plaster actually have something to reflect. */
  (function environment() {
    const w = 8, h = 64, data = new Uint8Array(w * h * 4);
    const top = [237, 231, 219], bot = [38, 52, 44];
    for (let y = 0; y < h; y++) {
      const t = Math.pow(y / (h - 1), 0.85);
      const r = Math.round(top[0] + (bot[0] - top[0]) * t);
      const g = Math.round(top[1] + (bot[1] - top[1]) * t);
      const b = Math.round(top[2] + (bot[2] - top[2]) * t);
      for (let x = 0; x < w; x++) {
        const i = (y * w + x) * 4;
        data[i] = r; data[i + 1] = g; data[i + 2] = b; data[i + 3] = 255;
      }
    }
    const tex = new THREE.DataTexture(data, w, h);
    tex.mapping = THREE.EquirectangularReflectionMapping;
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.needsUpdate = true;
    const pmrem = new THREE.PMREMGenerator(renderer);
    scene.environment = pmrem.fromEquirectangular(tex).texture;
    pmrem.dispose();
    tex.dispose();
  })();

  /* ---------- light ---------- */
  const sun = new THREE.DirectionalLight(0xFFF1DC, 2.6);
  sun.position.set(74, 108, 56);
  sun.castShadow = true;
  /* A 2048 map is wasteful on a phone-sized canvas. */
  const shadowRes = window.innerWidth < 900 ? 1024 : 2048;
  sun.shadow.mapSize.set(shadowRes, shadowRes);
  sun.shadow.bias = -0.0006;
  sun.shadow.normalBias = 0.5;
  const sc = sun.shadow.camera;
  sc.left = -130; sc.right = 130; sc.top = 130; sc.bottom = -130;
  sc.near = 20; sc.far = 320;
  scene.add(sun);

  scene.add(new THREE.HemisphereLight(C.sky, C.ground, 0.85));

  const fill = new THREE.DirectionalLight(0xCFE0D6, 0.35);
  fill.position.set(-80, 46, -60);
  scene.add(fill);

  /* ---------- materials ---------- */
  const M = {
    earth:  new THREE.MeshStandardMaterial({ color: C.earth, roughness: 1, metalness: 0 }),
    plaster:new THREE.MeshStandardMaterial({ color: C.plaster, roughness: 0.82, metalness: 0 }),
    plaster2:new THREE.MeshStandardMaterial({ color: C.plaster2, roughness: 0.88, metalness: 0 }),
    roof:   new THREE.MeshStandardMaterial({ color: C.roof, roughness: 0.9, metalness: 0 }),
    frame:  new THREE.MeshStandardMaterial({ color: C.frame, roughness: 0.75, metalness: 0 }),
    glass:  new THREE.MeshStandardMaterial({ color: C.glass, roughness: 0.08, metalness: 0.5 }),
    lit:    new THREE.MeshStandardMaterial({ color: 0x2A3A33, roughness: 0.2, metalness: 0.2,
                                             emissive: new THREE.Color(C.lit), emissiveIntensity: 0 }),
    deck:   new THREE.MeshStandardMaterial({ color: C.deck, roughness: 0.95, metalness: 0 }),
    line:   new THREE.MeshStandardMaterial({ color: C.sand, roughness: 0.9, metalness: 0,
                                             transparent: true, opacity: 0 }),
  };

  /* ---------- helpers ---------- */
  const root = new THREE.Group();
  scene.add(root);

  /** Box whose base sits on y = 0, so scaling the group in Y grows it upward. */
  function box(w, h, d, mat, x, y, z) {
    const g = new THREE.BoxGeometry(w, h, d);
    g.translate(0, h / 2, 0);
    const m = new THREE.Mesh(g, mat);
    m.position.set(x, y, z);
    m.castShadow = true;
    m.receiveShadow = true;
    return m;
  }

  const PARCEL = { w: 126, d: 94 };
  const MAIN = { x0: -40, x1: 40, z0: -15, z1: 15, h: 34 };
  const WING = { x0: -40, x1: -8, z0: 15, z1: 35, h: 12 };
  const FLOORS = 6;

  /* ---------- 00 the land ---------- */
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(PARCEL.w, PARCEL.d), M.earth);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  root.add(ground);

  const apron = new THREE.Mesh(new THREE.PlaneGeometry(460, 460),
    new THREE.MeshStandardMaterial({ color: 0x33402F, roughness: 1 }));
  apron.rotation.x = -Math.PI / 2;
  apron.position.y = -0.4;
  apron.receiveShadow = true;
  root.add(apron);

  [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(([sx, sz]) => {
    root.add(box(1.2, 6, 1.2, M.frame, sx * PARCEL.w / 2, 0, sz * PARCEL.d / 2));
  });

  /* ---------- 01 plat ---------- */
  const plat = new THREE.Group();
  root.add(plat);
  for (let i = -1; i <= 1; i++) {
    plat.add(box(0.7, 0.3, PARCEL.d - 8, M.line, i * 31, 0.1, 0));
  }
  [-16, 16].forEach(z => plat.add(box(PARCEL.w - 8, 0.3, 0.7, M.line, 0, 0.1, z)));

  /* ---------- 02 structure ---------- */
  const frame = new THREE.Group();
  root.add(frame);
  for (let gx = MAIN.x0; gx <= MAIN.x1 + 0.1; gx += 16) {
    for (let gz = MAIN.z0; gz <= MAIN.z1 + 0.1; gz += 15) {
      frame.add(box(1.5, MAIN.h, 1.5, M.frame, gx, 0, gz));
    }
  }
  for (let lv = 1; lv <= FLOORS; lv++) {
    const y = (MAIN.h / FLOORS) * lv;
    const slab = box(MAIN.x1 - MAIN.x0 + 3, 0.9, MAIN.z1 - MAIN.z0 + 3, M.frame, 0, y - 0.9, 0);
    frame.add(slab);
  }

  /* ---------- 03 massing ---------- */
  const mass = new THREE.Group();
  root.add(mass);

  const mainW = MAIN.x1 - MAIN.x0, mainD = MAIN.z1 - MAIN.z0;
  mass.add(box(mainW, MAIN.h, mainD, M.plaster, 0, 0, 0));
  mass.add(box(mainW + 2.4, 1.4, mainD + 2.4, M.plaster2, 0, MAIN.h, 0));

  const wingW = WING.x1 - WING.x0, wingD = WING.z1 - WING.z0;
  mass.add(box(wingW, WING.h, wingD, M.plaster2,
               (WING.x0 + WING.x1) / 2, 0, (WING.z0 + WING.z1) / 2));
  mass.add(box(wingW + 2, 1.2, wingD + 2, M.roof,
               (WING.x0 + WING.x1) / 2, WING.h, (WING.z0 + WING.z1) / 2));

  const deck = box(34, 0.8, 20, M.deck, 23, 0, 28);
  mass.add(deck);

  /* glazing: a band per floor on all four elevations */
  const litRooms = [];
  const fh = MAIN.h / FLOORS;
  /* Only a handful of rooms carry light. Terracotta is the signal, not the
     cladding — a facade of glowing windows would blow the brand's ≤8%. */
  const LIT = new Set(['0-1', '1-4', '2-0', '3-3', '4-5']);
  for (let lv = 0; lv < FLOORS; lv++) {
    const y = lv * fh + fh * 0.3;
    for (let c = 0; c < 6; c++) {
      const x = MAIN.x0 + 6 + c * 13.6;
      ['front', 'back'].forEach((side, si) => {
        const z = si === 0 ? MAIN.z1 + 0.15 : MAIN.z0 - 0.15;
        const isLit = si === 0 && LIT.has(lv + '-' + c);
        const mat = isLit ? M.lit.clone() : M.glass;
        const p = box(9, fh * 0.5, 0.4, mat, x, y, z);
        p.castShadow = false;
        mass.add(p);
        if (isLit) litRooms.push(mat);
      });
    }
    [MAIN.x0 - 0.15, MAIN.x1 + 0.15].forEach(x => {
      for (let e = 0; e < 2; e++) {
        const p = box(0.4, fh * 0.5, 9, M.glass, x, y, MAIN.z0 + 6 + e * 13);
        p.castShadow = false;
        mass.add(p);
      }
    });
  }

  /* ---------- 04 crown ---------- */
  const crown = new THREE.Group();
  root.add(crown);
  crown.add(box(mainW - 18, 7, mainD - 6, M.plaster, 0, MAIN.h, 0));
  crown.add(box(mainW - 16, 1, mainD - 4, M.plaster2, 0, MAIN.h + 7, 0));
  crown.add(box(0.8, 12, 0.8, M.frame, 26, MAIN.h + 8, 0));

  /* ---------- phase ---------- */
  const stageEls = Array.prototype.slice.call(document.querySelectorAll('.stage'));
  const CAPTIONS = [
    'Raw parcel · boundary and topography',
    'Plat, setbacks and yield',
    'Structure · six levels',
    'Operating asset · glazed and occupied',
    'Stabilised · held, or sold'
  ];
  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const ramp = (v, a, b) => clamp((v - a) / (b - a), 0, 1);
  const ease = t => t * t * (3 - 2 * t);
  const band = (v, a, b, c, d) => Math.min(ramp(v, a, b), 1 - ramp(v, c, d));

  function readPhase() {
    if (!stageEls.length) return 4;
    const line = window.innerHeight * 0.52;
    const c = stageEls.map(s => { const r = s.getBoundingClientRect(); return r.top + r.height / 2; });
    if (line <= c[0]) return 0;
    if (line >= c[c.length - 1]) return c.length - 1;
    for (let i = 0; i < c.length - 1; i++) {
      if (line >= c[i] && line <= c[i + 1]) return i + (line - c[i]) / (c[i + 1] - c[i] || 1);
    }
    return 0;
  }

  function setOpacity(group, v) {
    const on = v > 0.01;
    group.visible = on;
    group.traverse(o => {
      if (!o.material) return;
      o.material.transparent = v < 0.99;
      o.material.opacity = v;
    });
  }

  let capIndex = -1;
  function applyPhase(p) {
    const survey = band(p, 0.30, 0.85, 1.90, 2.45);
    const fr     = band(p, 1.10, 1.60, 2.35, 2.85);
    const rise   = ease(ramp(p, 1.10, 1.90));
    const solid  = ease(ramp(p, 2.10, 2.85));
    const glass  = ease(ramp(p, 2.45, 2.95));
    const lit    = ease(ramp(p, 2.60, 3.05));
    const cr     = ease(ramp(p, 2.40, 2.90));

    M.line.opacity = survey * 0.9;
    plat.visible = survey > 0.01;

    frame.visible = fr > 0.01 && rise > 0.01;
    frame.scale.y = Math.max(rise, 0.001);
    setOpacity(frame, fr);

    mass.visible = solid > 0.01;
    mass.scale.y = Math.max(rise, 0.001);
    if (solid > 0.01) setOpacity(mass, solid);

    M.glass.opacity = glass;
    M.glass.transparent = glass < 0.99;
    litRooms.forEach(m => { m.emissiveIntensity = lit * 1.15; });

    crown.visible = cr > 0.01;
    crown.scale.y = Math.max(cr, 0.001);
    if (cr > 0.01) setOpacity(crown, cr);

    const ci = clamp(Math.floor(p + 0.3), 0, CAPTIONS.length - 1);
    if (ci !== capIndex) {
      capIndex = ci;
      if (caption) caption.textContent = CAPTIONS[ci];
      canvas.setAttribute('aria-label', 'Site model, rotating: ' + CAPTIONS[ci]);
    }
  }

  /* ---------- size ---------- */
  function resize() {
    const r = canvas.getBoundingClientRect();
    if (!r.width) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    renderer.setPixelRatio(dpr);
    renderer.setSize(r.width, r.height, false);
    camera.aspect = r.width / r.height;
    camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener('resize', () => { resize(); if (reduce) renderOnce(); }, { passive: true });

  /* ---------- loop ---------- */
  let phase = 0, running = false, last = 0;

  function renderOnce() {
    applyPhase(phase);
    renderer.render(scene, camera);
  }

  function frameLoop(t) {
    if (!running) return;
    const dt = Math.min((t - last) / 1000 || 0, 0.05);
    last = t;
    root.rotation.y += dt * 0.16;
    const target = readPhase();
    phase += (target - phase) * Math.min(dt * 4, 1);
    renderOnce();
    requestAnimationFrame(frameLoop);
  }

  if (reduce) {
    phase = 4;
    root.rotation.y = -0.6;
    renderOnce();
    return;
  }

  const start = () => { if (!running) { running = true; last = performance.now(); requestAnimationFrame(frameLoop); } };
  const stop = () => { running = false; };

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(es => es.forEach(e => (e.isIntersecting ? start() : stop())),
                             { rootMargin: '140px' }).observe(canvas);
  } else start();

  document.addEventListener('visibilitychange', () => { document.hidden ? stop() : start(); });
}
