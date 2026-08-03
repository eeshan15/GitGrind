/* ==========================================================================
   Hash tables.

   Collisions are the whole subject, so the probe count is on screen the entire
   time and every insertion says how many slots it had to look at. Chaining never
   probes; open addressing does, and clustering is what makes that number grow.

   Primary clustering under linear probing is easy to see here: insert keys that
   hash near each other and watch later insertions walk over the whole run.
   ========================================================================== */
(function () {
  const { el } = GG;

  const METHODS = {
    chaining:  'Separate chaining (a list per slot)',
    linear:    'Linear probing (h + i)',
    quadratic: 'Quadratic probing (h + i^2)',
    double:    'Double hashing (h1 + i * h2)',
  };

  const isPrime = n => {
    if (n < 2) return false;
    for (let i = 2; i * i <= n; i++) if (n % i === 0) return false;
    return true;
  };
  const primeBelow = n => { let p = n - 1; while (p > 1 && !isPrime(p)) p--; return Math.max(2, p); };

  function simulate(values) {
    const m = Math.max(3, Math.min(23, values.size | 0));
    const method = values.method;
    const keys = String(values.keys || '').split(/[^0-9]+/).filter(Boolean).map(Number);
    if (!keys.length) throw new Error('Give some keys, e.g. 50 700 76 85.');
    if (keys.length > 24) throw new Error('Twenty-four keys is plenty.');

    const R = primeBelow(m);
    const table = new Array(m).fill(null).map(() => (method === 'chaining' ? [] : null));
    let probes = 0, stored = 0;
    const out = [];

    const push = (caption, hit, path) => out.push({
      caption, m, method, R, hit, path: path || [],
      table: table.map(c => (Array.isArray(c) ? c.slice() : c)),
      probes, stored, load: stored / m,
    });

    push('Table of ' + m + ' slot(s). h(k) = k mod ' + m +
         (method === 'double' ? ', and h2(k) = ' + R + ' - (k mod ' + R + ')' : '') + '.',
         -1);

    keys.forEach(key => {
      const h = key % m;

      if (method === 'chaining') {
        table[h].push(key);
        stored++;
        probes++;
        push('h(' + key + ') = ' + key + ' mod ' + m + ' = ' + h + '. ' +
             (table[h].length > 1
               ? 'Slot ' + h + ' already held ' + table[h].slice(0, -1).join(', ') +
                 ', so ' + key + ' joins the chain - chaining never probes elsewhere.'
               : 'Slot ' + h + ' was empty.'), h, [h]);
        return;
      }

      if (stored >= m) {
        push('The table is full, so ' + key + ' cannot be inserted. Open addressing ' +
             'cannot hold more keys than it has slots.', -1);
        return;
      }

      const h2 = method === 'double' ? (R - (key % R)) : 0;
      const path = [];
      let i = 0, slot = h;
      for (; i < m; i++) {
        slot = method === 'linear' ? (h + i) % m
             : method === 'quadratic' ? (h + i * i) % m
             : (h + i * h2) % m;
        path.push(slot);
        probes++;
        if (table[slot] === null) break;
        if (table[slot] === key) break;
      }

      if (table[slot] !== null && table[slot] !== key) {
        push('h(' + key + ') = ' + h + ', but after ' + m + ' probe(s) no free slot ' +
             'was found. Quadratic probing can fail like this even when the table is ' +
             'not full, which is why the table size matters.', -1, path);
        return;
      }

      const wasFree = table[slot] === null;
      table[slot] = key;
      if (wasFree) stored++;

      push('h(' + key + ') = ' + key + ' mod ' + m + ' = ' + h + '. ' +
           (i === 0
             ? 'Slot ' + h + ' was free, so one probe was enough.'
             : 'Slot ' + h + ' was taken, so it probed ' + path.join(' -> ') +
               ' and landed in ' + slot + ' after ' + (i + 1) + ' probe(s).'),
           slot, path);
    });

    push('Done. ' + stored + ' key(s) stored, load factor ' +
         (stored / m).toFixed(2) + ', ' + probes + ' probe(s) in total - an average ' +
         'of ' + (probes / Math.max(1, keys.length)).toFixed(2) + ' per insertion.', -1);
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const grid = el('div', { class: 'viz-hash' });
    for (let i = 0; i < frame.m; i++) {
      const cell = frame.table[i];
      const filled = Array.isArray(cell) ? cell.length : cell !== null;
      const onPath = frame.path.indexOf(i) !== -1;
      const row = el('div', {
        class: 'viz-hrow' + (i === frame.hit ? ' at' : '') +
               (onPath && i !== frame.hit ? ' probed' : '') + (filled ? ' full' : ''),
      }, [
        el('span', { class: 'viz-hi', text: String(i) }),
        el('span', { class: 'viz-hv',
          text: Array.isArray(cell) ? (cell.length ? cell.join(' -> ') : '-')
                                    : (cell === null ? '-' : String(cell)) }),
      ]);
      grid.appendChild(row);
    }
    host.appendChild(grid);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(METHODS[frame.method].split(' (')[0], 'on'),
      chip('load ' + frame.load.toFixed(2), frame.load > 0.75 ? 'bad' : 'mono'),
      chip('probes ' + frame.probes, 'mono'),
      chip('stored ' + frame.stored + '/' + frame.m, 'mono'),
    ]));
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('ds-hashing', {
    title: 'Hash tables',
    subtitle: 'Four collision strategies over the same keys, with the probe count ' +
              'running. Watch clustering build under linear probing.',
    glyph: 'H',
    topic: 'hashing',
    note: 'probes, clustering, load factor',
    inputs: [
      { key: 'method', label: 'Method', type: 'select', value: 'linear',
        options: Object.keys(METHODS).map(k => ({ value: k, label: METHODS[k] })) },
      { key: 'size', label: 'Table size', type: 'number', value: 7, min: 3, max: 23 },
      { key: 'keys', label: 'Keys', hint: '(in this order)', type: 'text',
        value: '50 700 76 85 92 73 101' },
    ],
    build: simulate,
    draw: draw,
  });
})();
