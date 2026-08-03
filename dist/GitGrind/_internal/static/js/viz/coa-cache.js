/* ==========================================================================
   Cache mapping.

   The part GATE actually tests is the address split: how many bits go to the
   offset, the index and the tag, and which set an address therefore lands in.
   So that is what this shows first - the address in binary, cut into its three
   fields - and then where the block goes.

   Direct mapped, n-way set associative and fully associative are the same
   machine with associativity set to 1, n, or "all blocks in one set".
   ========================================================================== */
(function () {
  const { el } = GG;

  const log2 = n => Math.log(n) / Math.LN2;
  const isPow2 = n => n > 0 && (n & (n - 1)) === 0;

  function geometry(values) {
    const addrBits = Math.max(8, Math.min(32, values.addrBits | 0));
    const blockSize = values.blockSize | 0;
    const cacheSize = values.cacheSize | 0;
    let ways = values.ways | 0;

    if (!isPow2(blockSize)) throw new Error('Block size must be a power of two.');
    if (!isPow2(cacheSize)) throw new Error('Cache size must be a power of two.');
    if (cacheSize < blockSize) throw new Error('The cache cannot be smaller than one block.');

    const blocks = cacheSize / blockSize;
    if (ways === 0) ways = blocks;                       /* fully associative */
    if (!isPow2(ways)) throw new Error('Associativity must be a power of two, or 0 for fully associative.');
    if (ways > blocks) throw new Error('More ways than the cache has blocks.');

    const sets = blocks / ways;
    const offsetBits = Math.round(log2(blockSize));
    const indexBits = Math.round(log2(sets));
    const tagBits = addrBits - offsetBits - indexBits;
    if (tagBits < 1) throw new Error('No bits left for the tag. Use a wider address or a smaller cache.');

    return { addrBits, blockSize, cacheSize, blocks, ways, sets,
             offsetBits, indexBits, tagBits };
  }

  function parseAddrs(text) {
    const raw = String(text || '').split(/[\s,]+/).filter(Boolean);
    if (!raw.length) throw new Error('Give some addresses, e.g. 0 4 16 132.');
    if (raw.length > 30) throw new Error('Keep it under 30 accesses so the table stays readable.');
    return raw.map(t => {
      const v = /^0x/i.test(t) ? parseInt(t, 16) : parseInt(t, 10);
      if (isNaN(v) || v < 0) throw new Error('"' + t + '" is not an address.');
      return v;
    });
  }

  function simulate(values) {
    const g = geometry(values);
    const addrs = parseAddrs(values.addrs);
    const limit = Math.pow(2, g.addrBits);

    /* sets[s] = array of {tag, lastUsed} of length ways */
    const sets = [];
    for (let s = 0; s < g.sets; s++) sets.push(new Array(g.ways).fill(null));
    const used = sets.map(() => new Array(g.ways).fill(-1));

    let hits = 0, misses = 0;
    const out = [];

    addrs.forEach((addr, step) => {
      if (addr >= limit) throw new Error('Address ' + addr + ' does not fit in ' +
                                         g.addrBits + ' bits.');
      const offset = addr % g.blockSize;
      const blockNo = Math.floor(addr / g.blockSize);
      const index = g.sets > 1 ? blockNo % g.sets : 0;
      const tag = Math.floor(blockNo / g.sets);

      const set = sets[index];
      const at = set.indexOf(tag);
      let placed, evicted = null, why;

      if (at !== -1) {
        hits++;
        used[index][at] = step;
        placed = at;
        why = 'Address ' + addr + ' -> set ' + index + ', tag ' + tag +
              '. Tag already in way ' + at + ', so this is a hit.';
      } else {
        misses++;
        const free = set.indexOf(null);
        if (free !== -1) {
          placed = free;
          why = 'Address ' + addr + ' -> set ' + index + ', tag ' + tag +
                '. Miss, and way ' + free + ' was free.';
        } else {
          placed = used[index].indexOf(Math.min.apply(null, used[index]));
          evicted = set[placed];
          why = 'Address ' + addr + ' -> set ' + index + ', tag ' + tag +
                '. Miss and the set is full, so LRU evicts tag ' + evicted +
                ' from way ' + placed + '.';
        }
        set[placed] = tag;
        used[index][placed] = step;
      }

      out.push({
        caption: why, step, addr, offset, blockNo, index, tag,
        hit: at !== -1, placed, evicted, hits, misses,
        sets: sets.map(s => s.slice()),
        g: g,
        addrs: addrs,
      });
    });

    const last = out[out.length - 1];
    out.push(Object.assign({}, last, {
      caption: 'Done. ' + hits + ' hit(s) and ' + misses + ' miss(es) over ' +
               addrs.length + ' accesses - a hit ratio of ' +
               (hits / addrs.length * 100).toFixed(1) + '%.',
      step: addrs.length, addr: null, placed: -1,
    }));
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function bits(value, count) {
    let s = (value >>> 0).toString(2);
    while (s.length < count) s = '0' + s;
    return s.slice(-count);
  }

  function draw(host, frame) {
    const g = frame.g;

    /* the geometry, stated once */
    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(g.cacheSize + ' B cache', 'mono'),
      chip(g.blockSize + ' B blocks', 'mono'),
      chip(g.blocks + ' blocks', 'mono'),
      chip(g.ways === g.blocks ? 'fully associative'
           : g.ways === 1 ? 'direct mapped' : g.ways + '-way', 'on'),
      chip(g.sets + ' set(s)', 'mono'),
      chip('tag ' + g.tagBits + ' | index ' + g.indexBits + ' | offset ' + g.offsetBits, 'mono'),
    ]));

    /* the address, cut into its three fields */
    if (frame.addr !== null) {
      const split = el('div', { class: 'viz-addr' });
      const field = (label, value, bitstr, cls) => el('div', { class: 'viz-af ' + cls }, [
        el('span', { class: 'viz-af-k', text: label }),
        el('span', { class: 'viz-af-b', text: bitstr || '-' }),
        el('span', { class: 'viz-af-v', text: String(value) }),
      ]);
      split.appendChild(field('tag', frame.tag,
        bits(frame.tag, g.tagBits), 'tag'));
      if (g.indexBits > 0) {
        split.appendChild(field('index', frame.index,
          bits(frame.index, g.indexBits), 'idx'));
      }
      split.appendChild(field('offset', frame.offset,
        bits(frame.offset, g.offsetBits), 'off'));
      host.appendChild(split);
      host.appendChild(el('p', { class: 'viz-addr-note dim small' }, [
        'address ' + frame.addr + '  =  0b' +
        bits(frame.addr, g.addrBits) + '  (block ' + frame.blockNo + ')',
      ]));
    }

    /* the cache itself */
    const grid = el('div', { class: 'viz-cache' });
    frame.sets.forEach((set, s) => {
      const row = el('div', { class: 'viz-set' + (s === frame.index && frame.addr !== null ? ' at' : '') });
      row.appendChild(el('span', { class: 'viz-set-k', text: 'set ' + s }));
      set.forEach((tag, w) => {
        const live = s === frame.index && w === frame.placed && frame.addr !== null;
        row.appendChild(el('span', {
          class: 'viz-way' + (tag === null ? ' empty' : '') + (live ? ' live' : '') +
                 (live && frame.hit ? ' good' : '') + (live && !frame.hit ? ' bad' : ''),
          text: tag === null ? '-' : 'tag ' + tag,
        }));
      });
      grid.appendChild(row);
    });
    host.appendChild(grid);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(frame.addr === null ? 'finished' : (frame.hit ? 'HIT' : 'MISS'),
           frame.addr === null ? '' : (frame.hit ? 'good' : 'bad')),
      chip('hits ' + frame.hits, 'mono'),
      chip('misses ' + frame.misses, 'mono'),
      chip('hit ratio ' +
           (frame.step ? (frame.hits / frame.step * 100).toFixed(0) : '0') + '%', 'mono'),
    ]));
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('coa-cache', {
    title: 'Cache mapping',
    subtitle: 'See the address split into tag, index and offset, then watch the ' +
              'block land in its set. Direct mapped, n-way, or fully associative.',
    glyph: 'C',
    topic: 'cache',
    note: 'address split + hit ratio',
    inputs: [
      { key: 'addrBits', label: 'Address bits', type: 'number', value: 16, min: 8, max: 32 },
      { key: 'cacheSize', label: 'Cache size', hint: '(bytes)', type: 'number',
        value: 128, min: 16, max: 65536 },
      { key: 'blockSize', label: 'Block size', hint: '(bytes)', type: 'number',
        value: 16, min: 2, max: 1024 },
      { key: 'ways', label: 'Associativity', hint: '(1 = direct, 0 = fully)',
        type: 'number', value: 2, min: 0, max: 32 },
      { key: 'addrs', label: 'Addresses', hint: '(decimal or 0x hex)', type: 'text',
        value: '0 4 16 132 232 160 1024 30 140 3100 180 2180' },
    ],
    build: simulate,
    draw: draw,
  });
})();
