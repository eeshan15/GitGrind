/* ==========================================================================
   Shortest paths and spanning trees.

   Dijkstra, Prim and Kruskal on the same graph, because the interesting thing is
   how similar they look and how differently they choose. Dijkstra relaxes by
   distance from a source; Prim grows a tree by cheapest border edge; Kruskal
   sorts every edge and takes what does not close a cycle.

   Edge format, one per line:  A B 4
   ========================================================================== */
(function () {
  const { el } = GG;

  const ALGOS = {
    dijkstra: 'Dijkstra (shortest path from a source)',
    prim:     'Prim (minimum spanning tree, grow from a vertex)',
    kruskal:  'Kruskal (minimum spanning tree, cheapest edge first)',
  };

  function parseGraph(text) {
    const edges = [];
    const nodes = [];
    String(text || '').split(/\n+/).map(l => l.trim()).filter(Boolean).forEach((l, i) => {
      const p = l.split(/[\s,]+/).filter(Boolean);
      if (p.length < 3) throw new Error('Line ' + (i + 1) + ': expected "A B 4".');
      const w = Number(p[2]);
      if (isNaN(w) || w < 0) throw new Error('Line ' + (i + 1) + ': "' + p[2] +
                                             '" is not a weight.');
      const a = p[0].toUpperCase(), b = p[1].toUpperCase();
      [a, b].forEach(x => { if (nodes.indexOf(x) === -1) nodes.push(x); });
      edges.push({ a, b, w });
    });
    if (!edges.length) throw new Error('Add some edges, e.g. A B 4.');
    if (nodes.length > 10) throw new Error('Ten vertices keeps the diagram readable.');
    nodes.sort();
    return { nodes, edges };
  }

  function simulate(values) {
    const G = parseGraph(values.edges);
    const algo = values.algo;
    const src = String(values.source || G.nodes[0]).toUpperCase();
    if (G.nodes.indexOf(src) === -1) throw new Error('"' + src + '" is not in the graph.');

    const out = [];
    const base = { G, algo, tree: [], visited: [], dist: {}, active: null };

    if (algo === 'kruskal') {
      const parent = {};
      G.nodes.forEach(n => { parent[n] = n; });
      const find = x => (parent[x] === x ? x : (parent[x] = find(parent[x])));
      const sorted = G.edges.slice().sort((x, y) => x.w - y.w || (x.a + x.b < y.a + y.b ? -1 : 1));
      const tree = [];
      let total = 0;

      out.push(Object.assign({}, base, {
        caption: 'Kruskal sorts every edge by weight: ' +
                 sorted.map(e => e.a + e.b + '(' + e.w + ')').join(', ') +
                 '. Then it takes them in that order, skipping any that would close a cycle.',
      }));

      sorted.forEach(e => {
        const ra = find(e.a), rb = find(e.b);
        if (ra === rb) {
          out.push(Object.assign({}, base, {
            tree: tree.slice(), active: e,
            caption: 'Edge ' + e.a + '-' + e.b + ' (' + e.w + ') is skipped: ' + e.a +
                     ' and ' + e.b + ' are already connected, so taking it would ' +
                     'close a cycle.',
          }));
          return;
        }
        parent[ra] = rb;
        tree.push(e);
        total += e.w;
        out.push(Object.assign({}, base, {
          tree: tree.slice(), active: e,
          caption: 'Take ' + e.a + '-' + e.b + ' (' + e.w + '): it joins two ' +
                   'separate components. Tree weight so far ' + total + '.',
        }));
      });

      out.push(Object.assign({}, base, {
        tree: tree.slice(),
        caption: 'Spanning tree complete with ' + tree.length + ' edge(s) and total ' +
                 'weight ' + total + '.' +
                 (tree.length === G.nodes.length - 1 ? ''
                  : ' The graph is disconnected, so this is a spanning forest.'),
      }));
      return out;
    }

    if (algo === 'prim') {
      const inTree = [src];
      const tree = [];
      let total = 0;

      out.push(Object.assign({}, base, {
        visited: inTree.slice(),
        caption: 'Prim starts at ' + src + ' and repeatedly takes the cheapest edge ' +
                 'that leaves the tree without coming back into it.',
      }));

      for (let guard = 0; inTree.length < G.nodes.length && guard < 100; guard++) {
        let best = null;
        G.edges.forEach(e => {
          const ain = inTree.indexOf(e.a) !== -1, bin = inTree.indexOf(e.b) !== -1;
          if (ain === bin) return;                    /* both in, or both out */
          if (!best || e.w < best.w) best = e;
        });
        if (!best) {
          out.push(Object.assign({}, base, {
            visited: inTree.slice(), tree: tree.slice(),
            caption: 'No edge leaves the tree, so the graph is disconnected and Prim ' +
                     'stops here having spanned only ' + inTree.join(', ') + '.',
          }));
          break;
        }
        const added = inTree.indexOf(best.a) === -1 ? best.a : best.b;
        inTree.push(added);
        tree.push(best);
        total += best.w;
        out.push(Object.assign({}, base, {
          visited: inTree.slice(), tree: tree.slice(), active: best,
          caption: 'The cheapest edge on the border is ' + best.a + '-' + best.b +
                   ' (' + best.w + '), so ' + added + ' joins the tree. Weight so far ' +
                   total + '.',
        }));
      }

      out.push(Object.assign({}, base, {
        visited: inTree.slice(), tree: tree.slice(),
        caption: 'Done. ' + tree.length + ' edge(s), total weight ' + total + '.',
      }));
      return out;
    }

    /* dijkstra */
    const dist = {}, prev = {};
    G.nodes.forEach(n => { dist[n] = Infinity; });
    dist[src] = 0;
    const done = [];

    out.push(Object.assign({}, base, {
      dist: Object.assign({}, dist),
      caption: 'Every distance starts at infinity except the source ' + src +
               ', which is 0. Dijkstra repeatedly settles the nearest unsettled vertex.',
    }));

    for (let guard = 0; done.length < G.nodes.length && guard < 100; guard++) {
      let u = null;
      G.nodes.forEach(n => {
        if (done.indexOf(n) !== -1) return;
        if (dist[n] === Infinity) return;
        if (u === null || dist[n] < dist[u]) u = n;
      });
      if (u === null) {
        out.push(Object.assign({}, base, {
          dist: Object.assign({}, dist), visited: done.slice(),
          caption: 'Everything reachable from ' + src + ' has been settled. The rest ' +
                   'stay at infinity because no path reaches them.',
        }));
        break;
      }

      done.push(u);
      out.push(Object.assign({}, base, {
        dist: Object.assign({}, dist), visited: done.slice(), active: null,
        caption: 'The nearest unsettled vertex is ' + u + ' at distance ' + dist[u] +
                 '. Once settled, that distance can never improve, which is the ' +
                 'whole guarantee Dijkstra rests on.',
      }));

      G.edges.forEach(e => {
        let v = null;
        if (e.a === u) v = e.b; else if (e.b === u) v = e.a; else return;
        if (done.indexOf(v) !== -1) return;
        const alt = dist[u] + e.w;
        if (alt < dist[v]) {
          const was = dist[v];
          dist[v] = alt;
          prev[v] = u;
          out.push(Object.assign({}, base, {
            dist: Object.assign({}, dist), visited: done.slice(), active: e,
            caption: 'Relax ' + u + '-' + v + ' (' + e.w + '): going through ' + u +
                     ' gives ' + alt + ', better than ' +
                     (was === Infinity ? 'infinity' : was) + '. Update ' + v + '.',
          }));
        }
      });
    }

    const treeEdges = Object.keys(prev).map(v => {
      const u = prev[v];
      return G.edges.find(e => (e.a === u && e.b === v) || (e.a === v && e.b === u));
    }).filter(Boolean);

    out.push(Object.assign({}, base, {
      dist: Object.assign({}, dist), visited: done.slice(), tree: treeEdges,
      caption: 'Final distances from ' + src + ': ' +
               G.nodes.map(n => n + '=' + (dist[n] === Infinity ? 'inf' : dist[n]))
                      .join(', ') + '.',
    }));
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const G = frame.G;
    const n = G.nodes.length;
    const R = Math.min(110, 40 + n * 13);
    const size = (R + 46) * 2;
    const svg = ns('svg', { viewBox: '0 0 ' + size + ' ' + size, class: 'viz-svg',
                            role: 'img', 'aria-label': 'Graph' });
    const cx = size / 2, cy = size / 2, pos = {};
    G.nodes.forEach((v, i) => {
      const a = (i / n) * Math.PI * 2 - Math.PI / 2;
      pos[v] = { x: cx + R * Math.cos(a), y: cy + R * Math.sin(a) };
    });

    const inTree = e => frame.tree.some(t => t === e ||
      (t.a === e.a && t.b === e.b && t.w === e.w));

    G.edges.forEach(e => {
      const a = pos[e.a], b = pos[e.b];
      const picked = inTree(e);
      const live = frame.active === e;
      svg.appendChild(ns('line', {
        x1: a.x, y1: a.y, x2: b.x, y2: b.y,
        stroke: live ? '#fff' : picked ? '#3fb950' : 'rgba(255,255,255,.16)',
        'stroke-width': live ? 3 : picked ? 2.6 : 1.2,
      }));
      const t = ns('text', { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 - 4,
        'text-anchor': 'middle', 'font-family': 'ui-monospace, monospace',
        'font-size': '11', fill: picked ? '#3fb950' : '#95a1b3' });
      t.textContent = String(e.w);
      svg.appendChild(t);
    });

    G.nodes.forEach(v => {
      const p = pos[v];
      const seen = frame.visited.indexOf(v) !== -1;
      svg.appendChild(ns('circle', { cx: p.x, cy: p.y, r: 19,
        fill: seen ? '#e8b43e' : '#1a212c',
        stroke: seen ? '#fff' : 'rgba(255,255,255,.35)', 'stroke-width': seen ? 2 : 1.2 }));
      const t = ns('text', { x: p.x, y: p.y + 4, 'text-anchor': 'middle',
        'font-family': 'ui-monospace, monospace', 'font-size': '12',
        'font-weight': '700', fill: seen ? '#0b0f16' : '#e9eef5' });
      t.textContent = v;
      svg.appendChild(t);
      if (frame.algo === 'dijkstra') {
        const d = frame.dist[v];
        const dt = ns('text', { x: p.x, y: p.y + 33, 'text-anchor': 'middle',
          'font-family': 'ui-monospace, monospace', 'font-size': '11',
          fill: d === Infinity ? '#6f7d91' : '#e8b43e' });
        dt.textContent = d === Infinity ? 'inf' : String(d);
        svg.appendChild(dt);
      }
    });
    host.appendChild(svg);

    const weight = frame.tree.reduce((a, e) => a + e.w, 0);
    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(ALGOS[frame.algo].split(' ')[0], 'on'),
      frame.algo === 'dijkstra'
        ? chip('settled ' + frame.visited.length + '/' + G.nodes.length, 'mono')
        : chip('tree edges ' + frame.tree.length, 'mono'),
      frame.algo === 'dijkstra' ? chip('') : chip('weight ' + weight, 'mono'),
    ]));
  }

  function ns(tag, attrs) {
    const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.keys(attrs || {}).forEach(k => n.setAttribute(k, attrs[k]));
    return n;
  }
  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('algo-graph', {
    title: 'Dijkstra, Prim and Kruskal',
    subtitle: 'Three greedy algorithms on the same graph. Watch how differently they ' +
              'choose the next edge, and why each choice is safe.',
    glyph: 'G',
    topic: 'shortest-paths',
    note: 'relaxation, MST, cycle avoidance',
    inputs: [
      { key: 'algo', label: 'Algorithm', type: 'select', value: 'dijkstra',
        options: Object.keys(ALGOS).map(k => ({ value: k, label: ALGOS[k] })) },
      { key: 'source', label: 'Source', hint: '(Dijkstra and Prim)', type: 'text',
        value: 'A' },
      { key: 'edges', label: 'Edges', hint: '(A B weight)', type: 'textarea',
        value: 'A B 4\nA C 2\nB C 1\nB D 5\nC D 8\nC E 10\nD E 2\nD F 6\nE F 3' },
    ],
    build: simulate,
    draw: draw,
  });
})();
