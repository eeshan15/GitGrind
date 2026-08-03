/* ==========================================================================
   B+ tree insertion.

   Splits are where the marks are, so every frame that splits says which node
   overflowed, where it was cut, and whether the separator was copied up (leaf)
   or pushed up (internal). That distinction is the single most common thing to
   get wrong in an exam, and it is invisible in a finished diagram.

   "Max keys" is keys per node, so a node with max 3 holds up to three keys and
   four pointers. Leaves are chained left to right, which is the whole point of a
   B+ tree over a B tree.
   ========================================================================== */
(function () {
  const { el } = GG;

  const node = leaf => ({ leaf, keys: [], kids: [] });
  const clone = n => ({
    leaf: n.leaf, keys: n.keys.slice(),
    kids: n.kids.map(clone),
  });

  function parseKeys(text) {
    const ks = String(text || '').split(/[^0-9]+/).filter(Boolean).map(Number);
    if (!ks.length) throw new Error('Give some keys, e.g. 10 20 30 40.');
    if (ks.length > 24) throw new Error('Twenty-four keys is enough to show every kind of split.');
    return ks;
  }

  function simulate(values) {
    const keys = parseKeys(values.keys);
    const mx = Math.max(2, Math.min(5, values.maxKeys | 0));

    let root = node(true);
    const out = [];
    let note = [];

    out.push({ caption: 'Empty tree. Each node holds at most ' + mx + ' key(s), so ' +
                        mx + ' + 1 = ' + (mx + 1) + ' pointers.',
               root: clone(root), inserting: null, highlight: [], mx });

    keys.forEach(key => {
      note = [];

      /* insert, returning {sep, right} when the child split */
      const ins = n => {
        if (n.leaf) {
          let i = 0;
          while (i < n.keys.length && n.keys[i] < key) i++;
          if (n.keys[i] === key) { note.push('Key ' + key + ' is already there; nothing changes.'); return null; }
          n.keys.splice(i, 0, key);
          if (n.keys.length <= mx) {
            note.push('Key ' + key + ' goes into a leaf that still has room.');
            return null;
          }
          const mid = Math.ceil(n.keys.length / 2);
          const right = node(true);
          right.keys = n.keys.slice(mid);
          n.keys = n.keys.slice(0, mid);
          note.push('That leaf now holds ' + (mx + 1) + ' keys, one too many. It splits ' +
                    'into [' + n.keys.join(' ') + '] and [' + right.keys.join(' ') + ']. ' +
                    'In a B+ tree the separator ' + right.keys[0] + ' is COPIED up - the ' +
                    'key itself stays in the leaf, because every key must be reachable ' +
                    'by scanning the leaves.');
          return { sep: right.keys[0], right };
        }

        let i = 0;
        while (i < n.keys.length && key >= n.keys[i]) i++;
        const up = ins(n.kids[i]);
        if (!up) return null;

        n.keys.splice(i, 0, up.sep);
        n.kids.splice(i + 1, 0, up.right);
        if (n.keys.length <= mx) return null;

        const mid = Math.floor(n.keys.length / 2);
        const promote = n.keys[mid];
        const right = node(false);
        right.keys = n.keys.slice(mid + 1);
        right.kids = n.kids.slice(mid + 1);
        n.keys = n.keys.slice(0, mid);
        n.kids = n.kids.slice(0, mid + 1);
        note.push('The parent overflows too. It splits and ' + promote +
                  ' is PUSHED up - unlike a leaf split, this key leaves the node ' +
                  'entirely, because internal keys are only separators.');
        return { sep: promote, right };
      };

      const up = ins(root);
      if (up) {
        const nr = node(false);
        nr.keys = [up.sep];
        nr.kids = [root, up.right];
        root = nr;
        note.push('The root split, so a new root holding ' + up.sep +
                  ' is created and the tree grows one level taller.');
      }

      out.push({
        caption: 'Insert ' + key + '. ' + note.join(' '),
        root: clone(root), inserting: key, highlight: [key], mx,
      });
    });

    const h = depth(root);
    out.push({
      caption: 'Done. ' + keys.length + ' key(s) inserted, height ' + h +
               ', and the leaves in order read ' +
               leafKeys(root).map(l => '[' + l.join(' ') + ']').join(' -> ') + '.',
      root: clone(root), inserting: null, highlight: [], mx,
    });
    return out;
  }

  const depth = n => (n.leaf ? 1 : 1 + depth(n.kids[0]));
  function leafKeys(n) {
    if (n.leaf) return [n.keys];
    return n.kids.reduce((a, k) => a.concat(leafKeys(k)), []);
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    /* lay the tree out level by level, spacing leaves evenly */
    const levels = [];
    (function walk(n, d) {
      levels[d] = levels[d] || [];
      levels[d].push(n);
      if (!n.leaf) n.kids.forEach(k => walk(k, d + 1));
    })(frame.root, 0);

    const KEY_W = 30, PAD = 12, VGAP = 74;
    const widths = new Map();
    const measure = n => {
      const own = Math.max(KEY_W, n.keys.length * KEY_W) + PAD;
      const w = n.leaf ? own
        : Math.max(own, n.kids.reduce((a, k) => a + measure(k) + 14, -14));
      widths.set(n, w);
      return w;
    };
    const totalW = Math.max(320, measure(frame.root) + 40);
    const totalH = levels.length * VGAP + 30;

    const svg = ns('svg', { viewBox: '0 0 ' + totalW + ' ' + totalH,
                            class: 'viz-svg', role: 'img', 'aria-label': 'B+ tree' });
    const boxes = [];

    (function place(n, left, d) {
      const w = widths.get(n);
      const cx = left + w / 2;
      const y = 20 + d * VGAP;
      boxes.push({ n, cx, y });
      if (n.leaf) return;
      let x = left + (w - n.kids.reduce((a, k) => a + widths.get(k) + 14, -14)) / 2;
      n.kids.forEach(k => {
        const kw = widths.get(k);
        svg.appendChild(ns('line', {
          x1: cx, y1: y + 26, x2: x + kw / 2, y2: y + VGAP - 4,
          stroke: 'rgba(255,255,255,.22)', 'stroke-width': 1.2,
        }));
        place(k, x, d + 1);
        x += kw + 14;
      });
    })(frame.root, 20, 0);

    /* chain the leaves, the defining feature of a B+ tree */
    const leafBoxes = boxes.filter(b => b.n.leaf).sort((a, b) => a.cx - b.cx);
    for (let i = 0; i < leafBoxes.length - 1; i++) {
      const a = leafBoxes[i], b = leafBoxes[i + 1];
      const aw = Math.max(KEY_W, a.n.keys.length * KEY_W);
      const bw = Math.max(KEY_W, b.n.keys.length * KEY_W);
      svg.appendChild(ns('line', {
        x1: a.cx + aw / 2, y1: a.y + 13, x2: b.cx - bw / 2, y2: b.y + 13,
        stroke: 'rgba(63,185,80,.55)', 'stroke-width': 1.4,
        'stroke-dasharray': '4 3',
      }));
    }

    boxes.forEach(({ n, cx, y }) => {
      const w = Math.max(KEY_W, n.keys.length * KEY_W);
      svg.appendChild(ns('rect', {
        x: cx - w / 2, y: y, width: w, height: 26, rx: 4,
        fill: n.leaf ? 'rgba(63,185,80,.12)' : 'rgba(232,180,62,.12)',
        stroke: n.leaf ? 'rgba(63,185,80,.5)' : 'rgba(232,180,62,.55)',
      }));
      n.keys.forEach((k, i) => {
        const hit = frame.highlight.indexOf(k) !== -1 && n.leaf;
        const x = cx - w / 2 + i * KEY_W;
        if (hit) {
          svg.appendChild(ns('rect', { x: x + 1, y: y + 1, width: KEY_W - 2,
            height: 24, rx: 3, fill: '#e8b43e' }));
        }
        const t = ns('text', { x: x + KEY_W / 2, y: y + 18, 'text-anchor': 'middle',
          'font-family': 'ui-monospace, monospace', 'font-size': '12',
          'font-weight': '700', fill: hit ? '#0b0f16' : '#e9eef5' });
        t.textContent = String(k);
        svg.appendChild(t);
        if (i) {
          svg.appendChild(ns('line', { x1: x, y1: y + 3, x2: x, y2: y + 23,
            stroke: 'rgba(255,255,255,.18)' }));
        }
      });
    });

    host.appendChild(svg);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(frame.inserting === null ? 'idle' : 'inserting ' + frame.inserting, 'on'),
      chip('max ' + frame.mx + ' keys / node', 'mono'),
      chip('height ' + depth(frame.root), 'mono'),
      chip(leafKeys(frame.root).length + ' leaf/leaves', 'mono'),
    ]));

    host.appendChild(el('p', { class: 'dim small', style: 'margin:10px 0 0' }, [
      'Gold nodes are internal separators, green nodes are leaves. The dashed ' +
      'green line is the leaf chain that makes a range scan cheap.',
    ]));
  }

  function ns(tag, attrs) {
    const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.keys(attrs || {}).forEach(k => n.setAttribute(k, attrs[k]));
    return n;
  }
  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('dbms-bplus', {
    title: 'B+ tree insertion',
    subtitle: 'Insert keys one at a time and watch the splits. Leaf splits copy ' +
              'the separator up; internal splits push it up - the frames say which.',
    glyph: 'B',
    topic: 'indexing',
    note: 'splits, height growth, leaf chain',
    inputs: [
      { key: 'maxKeys', label: 'Max keys per node', type: 'number',
        value: 3, min: 2, max: 5 },
      { key: 'keys', label: 'Keys to insert', hint: '(in this order)', type: 'text',
        value: '10 20 30 40 50 60 70' },
    ],
    build: simulate,
    draw: draw,
  });
})();
