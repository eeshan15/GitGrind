/* ==========================================================================
   Karnaugh map minimisation.

   The grid is drawn in Gray code order, which is the whole reason a K-map works:
   neighbouring cells differ in exactly one variable, so a group of adjacent ones
   is a term with that variable removed.

   Groups are found by Quine-McCluskey rather than by eye, then reduced to a
   minimal cover: essential prime implicants first, then the smallest set of the
   rest that finishes the job. That is exactly the procedure the exam wants, and
   doing it exhaustively means the answer is minimal rather than merely good.
   ========================================================================== */
(function () {
  const { el } = GG;

  const NAMES = 'ABCD';
  const GRAY = [0, 1, 3, 2];

  function parseList(text, max) {
    const out = [];
    String(text || '').split(/[^0-9]+/).filter(Boolean).forEach(t => {
      const n = Number(t);
      if (n >= 0 && n < max && out.indexOf(n) === -1) out.push(n);
    });
    return out.sort((a, b) => a - b);
  }

  const covers = (p, m) => ((m & ~p.mask) >>> 0) === p.value;

  /* ------------------------------------------------ Quine-McCluskey ------- */
  function primeImplicants(terms) {
    let cur = terms.map(t => ({ value: t, mask: 0 }));
    const primes = [];
    const seen = {};

    while (cur.length) {
      const used = new Array(cur.length).fill(false);
      const next = [];
      const nextSeen = {};

      for (let i = 0; i < cur.length; i++) {
        for (let j = i + 1; j < cur.length; j++) {
          if (cur[i].mask !== cur[j].mask) continue;
          const d = cur[i].value ^ cur[j].value;
          if (!d || (d & (d - 1))) continue;          /* must differ in one bit */
          used[i] = used[j] = true;
          const merged = { value: (cur[i].value & ~d) >>> 0, mask: cur[i].mask | d };
          const k = merged.value + ':' + merged.mask;
          if (!nextSeen[k]) { nextSeen[k] = 1; next.push(merged); }
        }
      }
      cur.forEach((p, i) => {
        if (used[i]) return;
        const k = p.value + ':' + p.mask;
        if (!seen[k]) { seen[k] = 1; primes.push(p); }
      });
      cur = next;
    }
    return primes;
  }

  function minimalCover(primes, wanted) {
    /* essentials: a minterm covered by exactly one prime implicant */
    const essential = [];
    wanted.forEach(m => {
      const hits = primes.filter(p => covers(p, m));
      if (hits.length === 1 && essential.indexOf(hits[0]) === -1) essential.push(hits[0]);
    });

    let left = wanted.filter(m => !essential.some(p => covers(p, m)));
    if (!left.length) return { chosen: essential, essential };

    /* exhaustive over the rest - the search space is tiny for four variables,
       and "nearly minimal" is not an acceptable answer in an exam */
    const rest = primes.filter(p => essential.indexOf(p) === -1);
    for (let size = 1; size <= rest.length; size++) {
      const pick = [];
      const found = (function search(start, k) {
        if (!k) {
          return left.every(m => pick.some(p => covers(p, m)));
        }
        for (let i = start; i <= rest.length - k; i++) {
          pick.push(rest[i]);
          if (search(i + 1, k - 1)) return true;
          pick.pop();
        }
        return false;
      })(0, size);
      if (found) return { chosen: essential.concat(pick), essential };
    }
    return { chosen: essential.concat(rest), essential };
  }

  function literal(p, nvars) {
    let s = '';
    for (let b = 0; b < nvars; b++) {
      const bit = 1 << (nvars - 1 - b);
      if (p.mask & bit) continue;
      s += NAMES[b] + ((p.value & bit) ? '' : "'");
    }
    return s || '1';
  }

  function simulate(values) {
    const nvars = Math.max(2, Math.min(4, values.vars | 0));
    const cells = 1 << nvars;
    const ones = parseList(values.minterms, cells);
    const dc = parseList(values.dontcares, cells).filter(m => ones.indexOf(m) === -1);

    const out = [];
    const base = { nvars, cells, ones, dc, groups: [], expr: '', focus: -1 };

    out.push(Object.assign({}, base, {
      caption: nvars + ' variables, so ' + cells + ' cells. Ones are marked 1, ' +
               "don't-cares X. Neighbouring cells differ in exactly one variable, " +
               'which is why the columns run 00, 01, 11, 10 rather than in order.',
    }));

    if (!ones.length) {
      out.push(Object.assign({}, base, {
        expr: '0',
        caption: 'No minterms, so the function is constant 0.',
      }));
      return out;
    }
    if (ones.length + dc.length === cells && ones.length) {
      out.push(Object.assign({}, base, {
        expr: '1', groups: [{ value: 0, mask: cells - 1 }],
        caption: 'Every cell is a one or a don\u2019t-care, so the whole map is one ' +
                 'group and the function is constant 1.',
      }));
      return out;
    }

    const primes = primeImplicants(ones.concat(dc).sort((a, b) => a - b));
    out.push(Object.assign({}, base, {
      groups: primes,
      caption: 'Combining adjacent cells repeatedly gives ' + primes.length +
               ' prime implicant(s): ' + primes.map(p => literal(p, nvars)).join(', ') +
               ". Don't-cares were allowed to join groups, which is what makes them " +
               'useful - they never have to be covered themselves.',
    }));

    const { chosen, essential } = minimalCover(primes, ones);

    essential.forEach((p, i) => {
      const mts = ones.filter(m => covers(p, m));
      out.push(Object.assign({}, base, {
        groups: essential.slice(0, i + 1),
        focus: i,
        caption: literal(p, nvars) + ' is essential: minterm ' +
                 mts.find(m => ones.filter(x => primes.filter(q => covers(q, x)).length === 1)
                                   .indexOf(m) !== -1) +
                 ' is covered by no other prime implicant, so this group must be in ' +
                 'the answer.',
      }));
    });

    const extra = chosen.filter(p => essential.indexOf(p) === -1);
    if (extra.length) {
      out.push(Object.assign({}, base, {
        groups: chosen,
        caption: 'The essentials leave some ones uncovered. The smallest set that ' +
                 'finishes the job is ' + extra.map(p => literal(p, nvars)).join(', ') + '.',
      }));
    }

    const expr = chosen.map(p => literal(p, nvars)).sort().join(' + ');
    out.push(Object.assign({}, base, {
      groups: chosen, expr,
      caption: 'Minimal sum of products: F = ' + expr + '. That is ' + chosen.length +
               ' term(s) and ' +
               chosen.reduce((a, p) => a + literal(p, nvars).replace(/'/g, '').length, 0) +
               ' literal(s).',
    }));
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  /* Cell -> (row, col) in Gray order. Rows take the high bits, columns the low. */
  function layout(nvars) {
    if (nvars === 2) return { rows: [0, 1], cols: [0, 1], rowBits: 1, colBits: 1 };
    if (nvars === 3) return { rows: [0, 1], cols: GRAY, rowBits: 1, colBits: 2 };
    return { rows: GRAY, cols: GRAY, rowBits: 2, colBits: 2 };
  }
  const bits = (v, n) => {
    let s = v.toString(2);
    while (s.length < n) s = '0' + s;
    return s;
  };

  function draw(host, frame) {
    const L = layout(frame.nvars);
    const rowVars = NAMES.slice(0, L.rowBits);
    const colVars = NAMES.slice(L.rowBits, L.rowBits + L.colBits);

    const table = el('div', { class: 'viz-kmap' });

    const head = el('div', { class: 'viz-krow' });
    head.appendChild(el('span', { class: 'viz-kcorner',
                                  text: rowVars + ' \\ ' + colVars }));
    L.cols.forEach(c => head.appendChild(
      el('span', { class: 'viz-khead', text: bits(c, L.colBits) })));
    table.appendChild(head);

    L.rows.forEach(r => {
      const row = el('div', { class: 'viz-krow' });
      row.appendChild(el('span', { class: 'viz-khead', text: bits(r, L.rowBits) }));
      L.cols.forEach(c => {
        const m = (r << L.colBits) | c;
        const isOne = frame.ones.indexOf(m) !== -1;
        const isDc = frame.dc.indexOf(m) !== -1;
        const inGroup = frame.groups.filter(p => covers(p, m));
        const cls = 'viz-kcell' + (isOne ? ' one' : isDc ? ' dc' : '') +
                    (inGroup.length ? ' grouped' : '') +
                    (inGroup.length > 1 ? ' shared' : '');
        row.appendChild(el('span', { class: cls }, [
          el('b', { text: isOne ? '1' : isDc ? 'X' : '0' }),
          el('i', { text: String(m) }),
        ]));
      });
      table.appendChild(row);
    });
    host.appendChild(table);

    if (frame.groups.length) {
      const list = el('div', { class: 'viz-terms' });
      frame.groups.forEach(p => list.appendChild(
        el('span', { class: 'viz-term', text: literal(p, frame.nvars) })));
      host.appendChild(list);
    }

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(frame.nvars + ' variables', 'mono'),
      chip(frame.ones.length + ' minterm(s)', 'mono'),
      frame.dc.length ? chip(frame.dc.length + " don't-care(s)", 'mono') : chip(''),
      frame.expr ? chip('F = ' + frame.expr, 'good') : chip(''),
    ]));
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('dl-kmap', {
    title: 'Karnaugh map',
    subtitle: 'Enter minterms and get the minimal sum of products, with the prime ' +
              'implicants and the essential ones called out on the way.',
    glyph: 'K',
    topic: 'kmap',
    note: '2 to 4 variables, exhaustive minimal cover',
    inputs: [
      { key: 'vars', label: 'Variables', type: 'select', value: 4,
        options: [{ value: '2', label: '2 (A B)' }, { value: '3', label: '3 (A B C)' },
                  { value: '4', label: '4 (A B C D)' }] },
      { key: 'minterms', label: 'Minterms', hint: '(space separated)', type: 'text',
        value: '0 1 2 5 6 7 8 9 10 14' },
      { key: 'dontcares', label: "Don't-cares", hint: '(optional)', type: 'text',
        value: '' },
    ],
    build: simulate,
    draw: draw,
  });
})();
