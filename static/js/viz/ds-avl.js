/* ==========================================================================
   AVL rotations.

   Four cases, and the whole difficulty is telling them apart. So every rebalance
   frame names the case (LL, RR, LR, RL), says which node went out of balance,
   and gives its balance factor before and after.

   Balance factor here is height(left) - height(right). Anything outside -1..+1
   forces a rotation, and the rotation always happens at the LOWEST unbalanced
   ancestor, which is the detail most people miss.
   ========================================================================== */
(function () {
  const { el } = GG;

  const node = k => ({ key: k, left: null, right: null, h: 1 });
  const H = n => (n ? n.h : 0);
  const BF = n => (n ? H(n.left) - H(n.right) : 0);
  const fix = n => { n.h = 1 + Math.max(H(n.left), H(n.right)); return n; };
  const clone = n => (n ? { key: n.key, h: n.h, left: clone(n.left), right: clone(n.right) } : null);

  const rotR = y => { const x = y.left; y.left = x.right; x.right = y; fix(y); fix(x); return x; };
  const rotL = x => { const y = x.right; x.right = y.left; y.left = x; fix(x); fix(y); return y; };

  function parseKeys(text) {
    const ks = String(text || '').split(/[^0-9-]+/).filter(Boolean).map(Number);
    if (!ks.length) throw new Error('Give some keys, e.g. 10 20 30.');
    if (ks.length > 20) throw new Error('Twenty keys is plenty to hit every rotation.');
    return ks;
  }

  function simulate(values) {
    const keys = parseKeys(values.keys);
    let root = null;
    const out = [];
    let notes = [];

    out.push({ caption: 'Empty tree. A node is balanced while |height(left) - ' +
                        'height(right)| is at most 1.', root: null, hit: null });

    keys.forEach(key => {
      notes = [];

      const ins = n => {
        if (!n) { notes.push('Key ' + key + ' becomes a new leaf.'); return node(key); }
        if (key === n.key) { notes.push('Key ' + key + ' is already present.'); return n; }
        if (key < n.key) n.left = ins(n.left); else n.right = ins(n.right);
        fix(n);

        const bf = BF(n);
        if (bf > 1 && key < n.left.key) {
          notes.push('Node ' + n.key + ' now has balance factor ' + bf +
                     '. The new key went into the LEFT subtree of its LEFT child, so ' +
                     'this is the LL case: one right rotation at ' + n.key + '.');
          return rotR(n);
        }
        if (bf < -1 && key > n.right.key) {
          notes.push('Node ' + n.key + ' now has balance factor ' + bf +
                     '. The new key went into the RIGHT subtree of its RIGHT child, so ' +
                     'this is the RR case: one left rotation at ' + n.key + '.');
          return rotL(n);
        }
        if (bf > 1 && key > n.left.key) {
          notes.push('Node ' + n.key + ' has balance factor ' + bf +
                     ', but the key went RIGHT of the LEFT child. That is the LR case, ' +
                     'and a single rotation will not fix it: rotate left at ' +
                     n.left.key + ' first, then right at ' + n.key + '.');
          n.left = rotL(n.left);
          return rotR(n);
        }
        if (bf < -1 && key < n.right.key) {
          notes.push('Node ' + n.key + ' has balance factor ' + bf +
                     ', and the key went LEFT of the RIGHT child. RL case: rotate ' +
                     'right at ' + n.right.key + ' first, then left at ' + n.key + '.');
          n.right = rotR(n.right);
          return rotL(n);
        }
        return n;
      };

      root = ins(root);
      out.push({
        caption: 'Insert ' + key + '. ' + notes.join(' ') +
                 (notes.length === 1 ? ' No rebalancing needed.' : ''),
        root: clone(root), hit: key,
      });
    });

    out.push({
      caption: 'Done. Height ' + H(root) + ' for ' + count(root) + ' node(s); a ' +
               'perfectly balanced tree of that size would be height ' +
               Math.ceil(Math.log(count(root) + 1) / Math.LN2) + '.',
      root: clone(root), hit: null,
    });
    return out;
  }

  const count = n => (n ? 1 + count(n.left) + count(n.right) : 0);

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    if (!frame.root) {
      host.appendChild(el('p', { class: 'dim small' }, ['Empty tree.']));
      return;
    }
    const depth = H(frame.root);
    const W = Math.max(340, Math.pow(2, Math.min(depth, 5)) * 46);
    const VGAP = 64, Hgt = depth * VGAP + 40;
    const svg = ns('svg', { viewBox: '0 0 ' + W + ' ' + Hgt, class: 'viz-svg',
                            role: 'img', 'aria-label': 'AVL tree' });

    (function place(n, left, right, d) {
      if (!n) return;
      const x = (left + right) / 2, y = 26 + d * VGAP;
      if (n.left) {
        svg.appendChild(ns('line', { x1: x, y1: y + 15, x2: (left + x) / 2,
          y2: y + VGAP - 15, stroke: 'rgba(255,255,255,.22)' }));
        place(n.left, left, x, d + 1);
      }
      if (n.right) {
        svg.appendChild(ns('line', { x1: x, y1: y + 15, x2: (x + right) / 2,
          y2: y + VGAP - 15, stroke: 'rgba(255,255,255,.22)' }));
        place(n.right, x, right, d + 1);
      }
      const bf = BF(n);
      const bad = Math.abs(bf) > 1;
      const hit = n.key === frame.hit;
      svg.appendChild(ns('circle', { cx: x, cy: y, r: 16,
        fill: hit ? '#e8b43e' : bad ? 'rgba(229,83,75,.25)' : '#1a212c',
        stroke: bad ? '#e5534b' : hit ? '#fff' : 'rgba(255,255,255,.35)',
        'stroke-width': bad || hit ? 2 : 1.2 }));
      const t = ns('text', { x: x, y: y + 4, 'text-anchor': 'middle',
        'font-family': 'ui-monospace, monospace', 'font-size': '12',
        'font-weight': '700', fill: hit ? '#0b0f16' : '#e9eef5' });
      t.textContent = String(n.key);
      svg.appendChild(t);
      const b = ns('text', { x: x + 20, y: y - 10, 'font-family': 'ui-monospace, monospace',
        'font-size': '10', fill: bad ? '#e5534b' : '#6f7d91' });
      b.textContent = (bf > 0 ? '+' : '') + bf;
      svg.appendChild(b);
    })(frame.root, 20, W - 20, 0);

    host.appendChild(svg);
    host.appendChild(el('div', { class: 'viz-state' }, [
      chip('height ' + H(frame.root), 'mono'),
      chip(count(frame.root) + ' node(s)', 'mono'),
      chip('root ' + frame.root.key, 'on'),
      chip('small numbers are balance factors'),
    ]));
  }

  function ns(tag, attrs) {
    const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.keys(attrs || {}).forEach(k => n.setAttribute(k, attrs[k]));
    return n;
  }
  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('ds-avl', {
    title: 'AVL rotations',
    subtitle: 'Insert keys and watch the tree rebalance. Every rotation frame names ' +
              'the case - LL, RR, LR or RL - and the node that went out of balance.',
    glyph: 'V',
    topic: 'trees',
    note: 'four rotation cases, balance factors',
    inputs: [
      { key: 'keys', label: 'Keys to insert', hint: '(in this order)', type: 'text',
        value: '10 20 30 40 50 25' },
    ],
    build: simulate,
    draw: draw,
  });
})();
