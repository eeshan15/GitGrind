/* Shared plumbing: DOM helpers, API client, router, toasts, tooltips. */
window.GG = (function () {
  'use strict';

  const S = {
    state: null, route: 'overview', detailId: null, seenBadges: null,
    /* UI preferences that live only in the browser. Engine settings live in the
       database and come down inside state.prefs. */
    ui: { reducedMotion: false, subjSort: 'risk', lastPanel: null },
    /* half-finished form values, kept so a refresh or an accidental close does
       not throw away typing */
    drafts: {},
  };

  const LS = 'gitgrind.ui.v3';

  /* ------------------------------ dom ---------------------------------- */
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  function el(tag, attrs, kids) {
    const n = document.createElement(tag);
    if (attrs) for (const k in attrs) {
      const v = attrs[k];
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') n.className = v;
      else if (k === 'text') n.textContent = v;
      else if (k === 'html') n.innerHTML = v;
      else if (k.startsWith('on') && typeof v === 'function') n.addEventListener(k.slice(2), v);
      else if (k === 'dataset') for (const d in v) n.dataset[d] = v[d];
      else n.setAttribute(k, v);
    }
    (Array.isArray(kids) ? kids : kids ? [kids] : []).forEach(c => {
      if (c === null || c === undefined || c === false) return;
      n.appendChild(typeof c === 'object' ? c : document.createTextNode(String(c)));
    });
    return n;
  }

  const esc = s => String(s === null || s === undefined ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

  /* ------------------------------ format -------------------------------- */
  function hm(mins) {
    mins = Math.round(mins || 0);
    if (!mins) return '0m';
    const h = Math.floor(mins / 60), m = mins % 60;
    if (!h) return m + 'm';
    return m ? h + 'h ' + m + 'm' : h + 'h';
  }

  function ago(iso) {
    if (!iso) return 'never';
    const d = new Date(iso + 'T00:00:00');
    const days = Math.round((new Date().setHours(0, 0, 0, 0) - d.setHours(0, 0, 0, 0)) / 86400000);
    if (days === 0) return 'today';
    if (days === 1) return 'yesterday';
    if (days < 7) return days + 'd ago';
    if (days < 30) return Math.floor(days / 7) + 'w ago';
    if (days < 365) return Math.floor(days / 30) + 'mo ago';
    return Math.floor(days / 365) + 'y ago';
  }

  function nice(iso) {
    if (!iso) return '';
    const d = new Date(iso.length > 10 ? iso : iso + 'T00:00:00');
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  }

  const num = n => (n === null || n === undefined ? '--' : Number(n).toLocaleString());
  const signed = n => (n > 0 ? '+' : '') + n;

  /* subject colour is derived from the slug so it never shifts */
  function hueOf(slug) {
    let h = 0;
    for (let i = 0; i < slug.length; i++) h = (h * 31 + slug.charCodeAt(i)) % 360;
    return h;
  }
  const colorOf = slug => 'hsl(' + hueOf(slug) + ' 62% 56%)';

  /* ------------------------------- api ---------------------------------- */
  async function api(path, opts) {
    const o = Object.assign({ headers: {} }, opts || {});
    if (o.body !== undefined && typeof o.body !== 'string') {
      o.headers['Content-Type'] = 'application/json';
      o.body = JSON.stringify(o.body);
      o.method = o.method || 'POST';
    }
    const res = await fetch('/api' + path, o);
    let data = null;
    try { data = await res.json(); } catch (e) { data = null; }
    if (!res.ok) throw new Error((data && data.error) || ('Request failed (' + res.status + ')'));
    return data;
  }

  /* ------------------------------ toasts -------------------------------- */
  function toast(title, body, kind) {
    announce(title + (body ? '. ' + body : ''));
    const host = $('#toasts');
    const t = el('div', { class: 'toast' + (kind ? ' ' + kind : '') }, [
      el('b', { text: title }),
      body ? el('span', { text: body }) : null,
    ]);
    host.appendChild(t);
    setTimeout(() => {
      t.classList.add('out');
      setTimeout(() => t.remove(), 300);
    }, kind === 'bad' ? 6000 : 4200);
  }

  /* ------------------------------ tooltip ------------------------------- */
  const tipEl = () => $('#tip');
  function showTip(html, x, y) {
    const t = tipEl();
    t.innerHTML = html;
    t.hidden = false;
    const r = t.getBoundingClientRect();
    let left = x - r.width / 2;
    left = Math.max(8, Math.min(left, window.innerWidth - r.width - 8));
    let top = y - r.height - 11;
    if (top < 8) top = y + 18;
    t.style.left = left + 'px';
    t.style.top = top + 'px';
  }
  const hideTip = () => { tipEl().hidden = true; };

  function bindTip(node, htmlFn) {
    node.addEventListener('mouseenter', e => {
      const r = e.currentTarget.getBoundingClientRect();
      showTip(htmlFn(e.currentTarget), r.left + r.width / 2, r.top);
    });
    node.addEventListener('mouseleave', hideTip);
  }

  /* --------------------------- count-up ---------------------------------- */
  function countTo(node, target, opts) {
    const o = Object.assign({ dur: 620, dp: 0, suffix: '', prefix: '' }, opts || {});
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      node.textContent = o.prefix + Number(target).toFixed(o.dp) + o.suffix;
      return;
    }
    const from = 0, t0 = performance.now();
    function step(now) {
      const p = Math.min(1, (now - t0) / o.dur);
      const eased = 1 - Math.pow(1 - p, 3);
      const v = from + (target - from) * eased;
      node.textContent = o.prefix + v.toFixed(o.dp) + o.suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  /* grow bars after paint so the CSS transition is visible */
  function growBars(root) {
    requestAnimationFrame(() => {
      $$('[data-w]', root || document).forEach(b => {
        b.style.width = b.dataset.w + '%';
        delete b.dataset.w;
      });
    });
  }

  /* --------------------------- preferences ------------------------------- */
  function loadPrefs() {
    try {
      const raw = window.localStorage.getItem(LS);
      if (raw) Object.assign(S.ui, JSON.parse(raw));
    } catch (e) { /* private mode, or storage disabled: defaults are fine */ }
    applyMotion();
  }

  function savePrefs() {
    try { window.localStorage.setItem(LS, JSON.stringify(S.ui)); }
    catch (e) { /* nothing to do; prefs just will not persist */ }
  }

  function applyMotion() {
    const osPref = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const off = !!(S.ui.reducedMotion || osPref);
    document.body.classList.toggle('reduced-motion', off);
    return off;
  }

  const motionOff = () => document.body.classList.contains('reduced-motion');

  function setReducedMotion(on) {
    S.ui.reducedMotion = !!on;
    savePrefs();
    applyMotion();
  }

  /* Adopt the engine-side reduced_motion setting once state arrives, so the
     preference survives moving to another browser. */
  function adoptServerPrefs(prefs) {
    if (!prefs) return;
    if (prefs.reduced_motion && !S.ui.reducedMotion) {
      S.ui.reducedMotion = true;
      savePrefs();
      applyMotion();
    }
  }

  /* --------------------------- draft keeping ---------------------------- */
  function draft(key, value) {
    if (value === undefined) return S.drafts[key];
    S.drafts[key] = value;
    return value;
  }
  const clearDraft = key => { delete S.drafts[key]; };

  /* Snapshot every field inside a container, and put it back later. */
  function snapshot(root) {
    const out = {};
    $$('input,select,textarea', root).forEach(f => {
      if (!f.id) return;
      out[f.id] = f.type === 'checkbox' ? f.checked : f.value;
    });
    return out;
  }
  function restore(root, values) {
    if (!values) return;
    $$('input,select,textarea', root).forEach(f => {
      if (!(f.id in values)) return;
      if (f.type === 'checkbox') f.checked = !!values[f.id];
      else f.value = values[f.id];
    });
  }

  /* ------------------------- screen reader voice ------------------------- */
  /* Toasts are visual. Anything worth a toast is also worth announcing, so the
     app is usable without watching the corner of the screen. */
  function announce(text) {
    const live = $('#live');
    if (!live) return;
    live.textContent = '';
    setTimeout(() => { live.textContent = text; }, 40);
  }

  /* ------------------------------ modals -------------------------------- */
  let openModal = null;
  let returnFocus = null;

  const FOCUSABLE = 'a[href],button:not([disabled]),input:not([type=hidden]):not([disabled]),' +
                    'select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';

  function modal(id, on) {
    const m = $(id);
    if (!m) return;
    if (on) {
      returnFocus = document.activeElement;
      $('#scrim').hidden = false;
      m.hidden = false;
      openModal = id;
      document.body.classList.add('modal-open');
      const f = m.querySelector('input:not([type=hidden]),select,textarea,button.btn-primary');
      if (f) setTimeout(() => f.focus(), 60);
    } else {
      m.hidden = true;
      if (openModal === id) openModal = null;
      if (!$$('.modal').some(x => !x.hidden)) {
        $('#scrim').hidden = true;
        document.body.classList.remove('modal-open');
        /* Send focus back where it came from, so keyboard users do not get
           dumped at the top of the document after every dialog. */
        if (returnFocus && returnFocus.isConnected) returnFocus.focus();
        returnFocus = null;
      }
    }
  }

  const closeAll = () => {
    $$('.modal').forEach(m => (m.hidden = true));
    $('#scrim').hidden = true;
    document.body.classList.remove('modal-open');
    openModal = null;
    if (returnFocus && returnFocus.isConnected) returnFocus.focus();
    returnFocus = null;
  };

  /* Keep Tab inside the open dialog. */
  document.addEventListener('keydown', e => {
    if (e.key !== 'Tab' || !openModal) return;
    const m = $(openModal);
    if (!m) return;
    const items = $$(FOCUSABLE, m).filter(n => n.offsetParent !== null);
    if (!items.length) return;
    const first = items[0], last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });
/* ------------------------------ splash --------------------------------- */
  /* Three beats, one clock. The table below is the only place timing lives; CSS
     describes what each beat looks like, keyed off data-phase, and the phase is
     mirrored onto <body> so the app shell can start arriving before the splash
     leaves.

       enter    the crest travels in from the left and settles in the centre
       sparkle  dust lifts, motes scatter, the metal catches the light
       idle     the finished icon, locked, breathing
  */
  const PHASES = [
    ['enter',   900],
    ['sparkle', 800],
    ['idle',    600],
  ];
  const SPLASH_MIN_MS = PHASES.reduce((a, p) => a + p[1], 0);
  const SPLASH_MAX_MS = SPLASH_MIN_MS + 4000;   /* never hang forever */
  const bootStart = Date.now();
  let splashGone = false;

  /* Particles are a loop, not markup. Each one gets its own position, distance
     and delay as custom properties; CSS does the rest. */
  function seedParticles() {
    const dust = $('#splashDust');
    if (dust && !dust.childElementCount) {
      for (let i = 0; i < 18; i++) {
        const p = el('i', {});
        p.style.setProperty('--x', (Math.random() * 100).toFixed(1) + '%');
        p.style.setProperty('--y', (Math.random() * 100).toFixed(1) + '%');
        p.style.setProperty('--d', (Math.random() * 900).toFixed(0) + 'ms');
        p.style.setProperty('--r', (6 + Math.random() * 22).toFixed(0) + 'px');
        dust.appendChild(p);
      }
    }
    const motes = $('#splashMotes');
    if (motes && !motes.childElementCount) {
      for (let i = 0; i < 26; i++) {
        const angle = (i / 26) * Math.PI * 2 + Math.random() * 0.4;
        const far = 80 + Math.random() * 70;
        const p = el('i', {});
        p.style.setProperty('--fx', (Math.cos(angle) * far).toFixed(1) + 'px');
        p.style.setProperty('--fy', (Math.sin(angle) * far).toFixed(1) + 'px');
        p.style.setProperty('--d', (Math.random() * 300).toFixed(0) + 'ms');
        p.style.setProperty('--s', (2 + Math.random() * 4).toFixed(1) + 'px');
        motes.appendChild(p);
      }
    }
  }

  function runPhases() {
    const node = $('#splash');
    if (!node) return;
    seedParticles();
    const set = name => {
      if (node.parentNode) node.dataset.phase = name;
      document.body.dataset.splashPhase = name;
    };
    set(PHASES[0][0]);
    let elapsed = 0;
    PHASES.forEach(([name], i) => {
      if (i === 0) return;
      elapsed += PHASES[i - 1][1];
      setTimeout(() => set(name), elapsed);
    });
  }

  function splashDone(force) {
    if (splashGone) return;
    const elapsed = Date.now() - bootStart;
    const hold = motionOff() || force ? 0 : Math.max(0, SPLASH_MIN_MS - elapsed);
    if (hold > 0) {
      setTimeout(() => splashDone(true), hold);
      return;
    }
    splashGone = true;

    document.body.classList.remove('booting');
    document.body.classList.add('booted');

    const node = $('#splash');
    if (!node) return;
    node.classList.add('gone');
    setTimeout(() => { if (node.parentNode) node.remove(); }, motionOff() ? 0 : 600);
  }

  document.addEventListener('DOMContentLoaded', () => {
    const node = $('#splash');
    if (!node) return;
    document.body.classList.add('booting');

    if (motionOff()) {
      node.dataset.phase = 'idle';
      document.body.dataset.splashPhase = 'idle';
    } else {
      runPhases();
    }

    setTimeout(() => splashDone(true), SPLASH_MAX_MS);

    const skip = $('#splashSkip');
    if (skip) skip.onclick = () => splashDone(true);
    const bail = e => {
      if (splashGone) { document.removeEventListener('keydown', bail); return; }
      if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        splashDone(true);
        document.removeEventListener('keydown', bail);
      }
    };
    document.addEventListener('keydown', bail);
  });
  /* ---------------------------- shortcuts -------------------------------- */
  const SHORTCUTS = [];

  /* Register one keyboard shortcut. Shown in the help dialog automatically, so
     the list can never drift out of date. */
  function key(combo, label, fn, opts) {
    SHORTCUTS.push(Object.assign({ combo: combo, label: label, fn: fn }, opts || {}));
  }

  function typing(node) {
    if (!node) return false;
    const t = (node.tagName || '').toLowerCase();
    return t === 'input' || t === 'select' || t === 'textarea' || node.isContentEditable;
  }

  document.addEventListener('keydown', e => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const inField = typing(document.activeElement);
    const pressed = e.key;
    for (const s of SHORTCUTS) {
      if (s.combo !== pressed) continue;
      if (inField && !s.inFields) continue;
      if (s.needsModal && openModal !== s.needsModal) continue;
      if (!s.needsModal && openModal) continue;
      e.preventDefault();
      s.fn(e);
      return;
    }
  });

  function shortcutHelp() {
    const body = $('#keysBody');
    if (!body) return;
    body.innerHTML = '';
    const grid = el('div', { class: 'keys-grid' });
    SHORTCUTS.filter(s => !s.hidden).forEach(s => {
      grid.appendChild(el('kbd', {}, [s.combo === ' ' ? 'Space' : s.combo]));
      grid.appendChild(el('span', {}, [s.label]));
    });
    body.appendChild(grid);
    body.appendChild(el('p', { class: 'dim small', style: 'margin:18px 0 0' },
      ['Shortcuts are off while you are typing in a field. Press Escape to close ' +
       'any dialog.']));
    modal('#modalKeys', true);
  }

  /* ------------------------------ router -------------------------------- */
  const ROUTES = ['overview', 'subjects', 'practice', 'readiness', 'bank',
                  'achievements', 'doubts', 'activity'];

  function markNav() {
    const links = $$('#topnav a');
    let active = null;
    links.forEach(a => {
      const on = a.dataset.route === S.route;
      a.classList.toggle('on', on);
      if (on) active = a;
    });
    const marker = $('#navMarker');
    if (marker && active) {
      marker.style.left = active.offsetLeft + 'px';
      marker.style.width = active.offsetWidth + 'px';
    }
  }

  function show(route, detailId) {
    S.route = route;
    S.detailId = detailId || null;
    $$('.view').forEach(v => (v.hidden = true));
    const target = $('#view-' + route);
    if (target) {
      target.hidden = false;
      /* restart the enter animation on every switch */
      target.style.animation = 'none';
      void target.offsetWidth;
      target.style.animation = '';
    }
    markNav();
    /* Move focus into the view so screen readers and keyboard users land in the
       new content rather than staying on the nav link. */
    const host = $('#content');
    if (host) host.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' });
  }

  function parseHash() {
    const h = (location.hash || '#/overview').replace(/^#\/?/, '');
    const parts = h.split('/').filter(Boolean);
    if (parts[0] === 'subject' && parts[1]) return { route: 'detail', id: parseInt(parts[1], 10) };
    const r = ROUTES.includes(parts[0]) ? parts[0] : 'overview';
    return { route: r, id: null };
  }

  /* ---------------------------- small helpers ---------------------------- */
  /* Bands used all over the UI. Each returns a glyph as well as a class, so no
     piece of information is carried by colour alone. */
  function band(pct) {
    if (pct >= 80) return { cls: 'strong', glyph: '#', label: 'strong' };
    if (pct >= 60) return { cls: 'ok', glyph: '+', label: 'ok' };
    if (pct >= 35) return { cls: 'weak', glyph: '~', label: 'weak' };
    return { cls: 'critical', glyph: '!', label: 'critical' };
  }

  const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
  const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0);

  /* An honest empty state: say what is missing and what to press. */
  function empty(glyph, title, body, action) {
    const kids = [
      el('span', { class: 'empty-glyph' }, [glyph]),
      el('b', {}, [title]),
      el('p', {}, [body]),
    ];
    if (action) kids.push(action);
    return el('div', { class: 'empty' }, kids);
  }

  return {
    S, $, $$, el, esc, hm, ago, nice, num, signed, colorOf, hueOf,
    api, toast, announce, showTip, hideTip, bindTip, countTo, growBars,
    modal, closeAll, show, parseHash, markNav, ROUTES,
    loadPrefs, savePrefs, setReducedMotion, adoptServerPrefs, motionOff,
    draft, clearDraft, snapshot, restore,
    key, shortcutHelp, band, clamp, pct, empty,splashDone,
    get openModal() { return openModal; },
  };
})();
