/* ==========================================================================
   Conflict serializability.

   A schedule is conflict serializable exactly when its precedence graph has no
   cycle, so this builds that graph edge by edge and then looks for a cycle. Each
   edge says which pair of operations conflicted and why, because "R and W on the
   same item from different transactions" is the whole rule.

   Schedule format, space separated:  R1(A) W2(A) R2(B) W1(B)
   ========================================================================== */
(function () {
  const { el } = GG;

  function parseSchedule(text) {
    const raw = String(text || '').trim().split(/[\s,;]+/).filter(Boolean);
    if (!raw.length) throw new Error('Write a schedule, e.g. R1(A) W2(A) R2(B) W1(B).');
    if (raw.length > 24) throw new Error('Twenty-four operations is plenty.');
    return raw.map((tok, i) => {
      const m = tok.match(/^([RWrw])\s*(\d+)\s*\(\s*([A-Za-z]\w*)\s*\)$/);
      if (!m) throw new Error('"' + tok + '" should look like R1(A) or W2(B).');
      return { i, op: m[1].toUpperCase(), txn: 'T' + m[2], item: m[3].toUpperCase(),
               text: m[1].toUpperCase() + m[2] + '(' + m[3].toUpperCase() + ')' };
    });
  }

  const conflict = (a, b) =>
    a.item === b.item && a.txn !== b.txn && (a.op === 'W' || b.op === 'W');

  function findCycle(nodes, edges) {
    const adj = {};
    nodes.forEach(n => { adj[n] = []; });
    edges.forEach(e => { if (adj[e.from].indexOf(e.to) === -1) adj[e.from].push(e.to); });

    const colour = {}, parent = {};
    let cycle = null;
    const visit = u => {
      colour[u] = 1;
      for (const v of adj[u]) {
        if (cycle) return;
        if (!colour[v]) { parent[v] = u; visit(v); }
        else if (colour[v] === 1) {
          /* v is grey, so u -> v closes a cycle. Walk the parent chain from u
             back to v, then reverse it and close the loop, otherwise the path
             comes out reversed and with v duplicated at the wrong end. */
          const path = [];
          let x = u;
          while (x !== v && x !== undefined) { path.push(x); x = parent[x]; }
          path.push(v);
          path.reverse();
          path.push(v);
          cycle = path;
        }
      }
      colour[u] = 2;
    };
    nodes.forEach(n => { if (!colour[n] && !cycle) visit(n); });
    return cycle;
  }

  function topological(nodes, edges) {
    const indeg = {}, adj = {};
    nodes.forEach(n => { indeg[n] = 0; adj[n] = []; });
    edges.forEach(e => {
      if (adj[e.from].indexOf(e.to) === -1) { adj[e.from].push(e.to); indeg[e.to]++; }
    });
    const q = nodes.filter(n => !indeg[n]).sort();
    const order = [];
    while (q.length) {
      const u = q.shift();
      order.push(u);
      adj[u].forEach(v => { if (--indeg[v] === 0) q.push(v); });
      q.sort();
    }
    return order.length === nodes.length ? order : null;
  }

  function simulate(values) {
    const ops = parseSchedule(values.schedule);
    const txns = [];
    ops.forEach(o => { if (txns.indexOf(o.txn) === -1) txns.push(o.txn); });
    txns.sort();

    const out = [];
    const edges = [];

    out.push({
      caption: 'Schedule over ' + txns.length + ' transaction(s): ' + txns.join(', ') +
               '. Two operations conflict when they touch the same item, belong to ' +
               'different transactions, and at least one is a write.',
      ops, txns, edges: [], at: -1, cycle: null, order: null,
    });

    for (let j = 1; j < ops.length; j++) {
      for (let i = 0; i < j; i++) {
        if (!conflict(ops[i], ops[j])) continue;
        const from = ops[i].txn, to = ops[j].txn;
        const dup = edges.some(e => e.from === from && e.to === to);
        if (!dup) edges.push({ from, to, why: ops[i].text + ' before ' + ops[j].text });
        out.push({
          caption: ops[i].text + ' and ' + ops[j].text + ' conflict on ' + ops[i].item +
                   ' (' + (ops[i].op === 'W' && ops[j].op === 'W' ? 'write-write'
                          : ops[i].op === 'W' ? 'write then read' : 'read then write') +
                   '), and ' + ops[i].text + ' comes first. ' +
                   (dup ? 'That edge ' + from + ' -> ' + to + ' is already there.'
                        : 'So ' + from + ' must come before ' + to +
                          ' in any equivalent serial schedule: add edge ' +
                          from + ' -> ' + to + '.'),
          ops, txns, edges: edges.map(e => Object.assign({}, e)),
          at: j, cycle: null, order: null,
        });
      }
    }

    const cycle = findCycle(txns, edges);
    if (cycle) {
      out.push({
        caption: 'The precedence graph contains the cycle ' + cycle.join(' -> ') +
                 '. Each edge says one transaction must precede another, and a cycle ' +
                 'means those demands contradict each other. The schedule is NOT ' +
                 'conflict serializable.',
        ops, txns, edges, at: -1, cycle, order: null,
      });
    } else {
      const order = topological(txns, edges);
      out.push({
        caption: 'No cycle in the precedence graph, so the schedule IS conflict ' +
                 'serializable. It is equivalent to the serial schedule ' +
                 order.join(' -> ') + '.',
        ops, txns, edges, at: -1, cycle: null, order,
      });
    }
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    /* the schedule as a timeline */
    const strip = el('div', { class: 'viz-sched' });
    frame.ops.forEach((o, i) => {
      strip.appendChild(el('span', {
        class: 'viz-op' + (i === frame.at ? ' at' : '') + (o.op === 'W' ? ' w' : ' r'),
        text: o.text,
      }));
    });
    host.appendChild(strip);

    /* precedence graph, transactions on a circle */
    const n = frame.txns.length;
    const R = Math.min(90, 34 + n * 14);
    const size = (R + 44) * 2;
    const svg = ns('svg', { viewBox: '0 0 ' + size + ' ' + size, class: 'viz-svg',
                            role: 'img', 'aria-label': 'Precedence graph' });
    const cx = size / 2, cy = size / 2, pos = {};
    frame.txns.forEach((t, i) => {
      const a = (i / n) * Math.PI * 2 - Math.PI / 2;
      pos[t] = { x: cx + R * Math.cos(a), y: cy + R * Math.sin(a) };
    });

    const inCycle = (a, b) => {
      if (!frame.cycle) return false;
      for (let i = 0; i < frame.cycle.length - 1; i++) {
        if (frame.cycle[i] === a && frame.cycle[i + 1] === b) return true;
      }
      return false;
    };

    frame.edges.forEach(e => {
      const a = pos[e.from], b = pos[e.to];
      if (!a || !b) return;
      const bad = inCycle(e.from, e.to);
      const dx = b.x - a.x, dy = b.y - a.y;
      const len = Math.sqrt(dx * dx + dy * dy) || 1;
      const sx = a.x + (dx / len) * 20, sy = a.y + (dy / len) * 20;
      const ex = b.x - (dx / len) * 22, ey = b.y - (dy / len) * 22;
      svg.appendChild(ns('line', { x1: sx, y1: sy, x2: ex, y2: ey,
        stroke: bad ? '#e5534b' : 'rgba(232,180,62,.8)',
        'stroke-width': bad ? 2.6 : 1.6 }));
      /* arrow head */
      const ang = Math.atan2(dy, dx);
      svg.appendChild(ns('polygon', {
        points: [ex, ey,
                 ex - 8 * Math.cos(ang - 0.4), ey - 8 * Math.sin(ang - 0.4),
                 ex - 8 * Math.cos(ang + 0.4), ey - 8 * Math.sin(ang + 0.4)].join(' '),
        fill: bad ? '#e5534b' : 'rgba(232,180,62,.9)',
      }));
    });

    frame.txns.forEach(t => {
      const p = pos[t];
      const bad = frame.cycle && frame.cycle.indexOf(t) !== -1;
      svg.appendChild(ns('circle', { cx: p.x, cy: p.y, r: 19,
        fill: bad ? 'rgba(229,83,75,.2)' : '#1a212c',
        stroke: bad ? '#e5534b' : 'rgba(255,255,255,.35)',
        'stroke-width': bad ? 2 : 1.2 }));
      const tx = ns('text', { x: p.x, y: p.y + 4, 'text-anchor': 'middle',
        'font-family': 'ui-monospace, monospace', 'font-size': '12',
        'font-weight': '700', fill: bad ? '#e5534b' : '#e9eef5' });
      tx.textContent = t;
      svg.appendChild(tx);
    });
    host.appendChild(svg);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(frame.edges.length + ' edge(s)', 'mono'),
      frame.cycle ? chip('cycle ' + frame.cycle.join(' -> '), 'bad')
        : frame.order ? chip('serial order ' + frame.order.join(' -> '), 'good')
        : chip('building the graph'),
    ]));
  }

  function ns(tag, attrs) {
    const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.keys(attrs || {}).forEach(k => n.setAttribute(k, attrs[k]));
    return n;
  }
  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('dbms-serial', {
    title: 'Conflict serializability',
    subtitle: 'Build the precedence graph one conflicting pair at a time, then look ' +
              'for a cycle. No cycle means an equivalent serial order exists.',
    glyph: 'T',
    topic: 'concurrency-control',
    note: 'precedence graph, cycle detection',
    inputs: [
      { key: 'schedule', label: 'Schedule', hint: '(R1(A) W2(A) ...)', type: 'text',
        value: 'R1(A) W2(A) R2(B) W1(B)' },
    ],
    build: simulate,
    draw: draw,
  });
})();
