/* ==========================================================================
   Page replacement.

   Four policies over the same reference string, one reference at a time. The
   fault count is counted by the simulation, not asserted, so the frame table and
   the totals can never disagree.

   Belady's anomaly is worth finding yourself: run FIFO on 1 2 3 4 1 2 5 1 2 3 4 5
   with three frames, then with four, and watch the faults go up.
   ========================================================================== */
(function () {
  const { el } = GG;

  const POLICIES = {
    fifo:    'FIFO (oldest arrival leaves)',
    lru:     'LRU (least recently used leaves)',
    optimal: 'Optimal (furthest future use leaves)',
    clock:   'Clock / second chance',
  };

  function parseRefs(text) {
    const refs = String(text || '').split(/[^0-9]+/).filter(Boolean).map(Number);
    if (!refs.length) throw new Error('Give a reference string, e.g. 7 0 1 2 0 3.');
    if (refs.length > 40) throw new Error('Keep it under 40 references so the table stays readable.');
    return refs;
  }

  function simulate(values) {
    const refs = parseRefs(values.refs);
    const n = Math.max(1, Math.min(8, values.frames | 0));
    const policy = values.policy;

    const frames = new Array(n).fill(null);
    const loadedAt = new Array(n).fill(-1);   /* FIFO order        */
    const usedAt = new Array(n).fill(-1);     /* LRU recency       */
    const refBit = new Array(n).fill(0);      /* clock second chance */
    let hand = 0, faults = 0, hits = 0;

    const out = [];

    refs.forEach((page, step) => {
      const at = frames.indexOf(page);
      let victim = -1, why;

      if (at !== -1) {
        hits++;
        usedAt[at] = step;
        refBit[at] = 1;
        why = 'Page ' + page + ' is already in frame ' + at + '. Hit, nothing is evicted.';
      } else {
        faults++;
        const free = frames.indexOf(null);
        if (free !== -1) {
          victim = free;
          why = 'Page ' + page + ' is not resident and frame ' + free +
                ' is empty. Fault, but no eviction yet.';
        } else if (policy === 'fifo') {
          victim = loadedAt.indexOf(Math.min.apply(null, loadedAt));
          why = 'Page ' + page + ' faults. FIFO evicts ' + frames[victim] +
                ', loaded earliest of everything resident.';
        } else if (policy === 'lru') {
          victim = usedAt.indexOf(Math.min.apply(null, usedAt));
          why = 'Page ' + page + ' faults. LRU evicts ' + frames[victim] +
                ', untouched the longest.';
        } else if (policy === 'optimal') {
          let far = -1;
          frames.forEach((p, i) => {
            let next = refs.indexOf(p, step + 1);
            if (next === -1) next = Infinity;
            if (far === -1 || next > (refs.indexOf(frames[far], step + 1) === -1
                ? Infinity : refs.indexOf(frames[far], step + 1))) far = i;
          });
          victim = far;
          const nxt = refs.indexOf(frames[victim], step + 1);
          why = 'Page ' + page + ' faults. Optimal evicts ' + frames[victim] +
                (nxt === -1 ? ', which is never referenced again.'
                            : ', not needed again until position ' + nxt + '.');
        } else {                                  /* clock */
          let guard = 0;
          while (guard++ < n * 3) {
            if (refBit[hand] === 0) break;
            refBit[hand] = 0;
            hand = (hand + 1) % n;
          }
          victim = hand;
          why = 'Page ' + page + ' faults. The clock hand cleared reference bits and ' +
                'stopped on ' + frames[victim] + ', which had its second chance used up.';
          hand = (hand + 1) % n;
        }

        frames[victim] = page;
        loadedAt[victim] = step;
        usedAt[victim] = step;
        refBit[victim] = 1;
      }

      out.push({
        caption: why,
        step: step,
        page: page,
        hit: at !== -1,
        placed: at !== -1 ? at : victim,
        frames: frames.slice(),
        refBits: refBit.slice(),
        hand: policy === 'clock' ? hand : -1,
        faults: faults,
        hits: hits,
        refs: refs,
      });
    });

    const last = out[out.length - 1];
    out.push(Object.assign({}, last, {
      caption: 'Done. ' + faults + ' page fault(s) and ' + hits + ' hit(s) over ' +
               refs.length + ' references - a hit ratio of ' +
               (hits / refs.length * 100).toFixed(1) + '%.',
      step: refs.length,
      page: null,
      placed: -1,
    }));
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame, values) {
    const refs = frame.refs;
    const cell = Math.max(22, Math.min(40, 620 / refs.length));

    /* the reference string, with the cursor on the current one */
    const strip = el('div', { class: 'viz-refs' });
    refs.forEach((r, i) => {
      strip.appendChild(el('span', {
        class: 'viz-ref' + (i === frame.step ? ' at' : '') + (i < frame.step ? ' past' : ''),
        text: String(r),
        style: 'min-width:' + cell + 'px',
      }));
    });
    host.appendChild(strip);

    /* the frame table */
    const table = el('div', { class: 'viz-frames' });
    frame.frames.forEach((p, i) => {
      const live = i === frame.placed;
      const row = el('div', { class: 'viz-frow' + (live ? ' live' : '') }, [
        el('span', { class: 'viz-fname', text: 'frame ' + i }),
        el('span', { class: 'viz-fval' + (p === null ? ' empty' : ''),
                     text: p === null ? '-' : String(p) }),
      ]);
      if (values.policy === 'clock') {
        row.appendChild(el('span', { class: 'viz-fbit', text: 'R=' + frame.refBits[i] }));
        row.appendChild(el('span', { class: 'viz-fhand',
                                     text: frame.hand === i ? '<- hand' : '' }));
      }
      table.appendChild(row);
    });
    host.appendChild(table);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(frame.page === null ? 'finished' : 'reference ' + frame.page, 'mono'),
      chip(frame.page === null ? '' : (frame.hit ? 'HIT' : 'FAULT'),
           frame.page === null ? '' : (frame.hit ? 'good' : 'bad')),
      chip('faults ' + frame.faults, 'mono'),
      chip('hits ' + frame.hits, 'mono'),
      chip('hit ratio ' +
           (frame.step ? (frame.hits / frame.step * 100).toFixed(0) : '0') + '%', 'mono'),
    ]));
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('os-paging', {
    title: 'Page replacement',
    subtitle: 'Step through a reference string and watch which page gets evicted ' +
              'and why. Change the frame count to hunt for Belady anomalies.',
    glyph: 'P',
    topic: 'virtual-memory',
    note: 'four policies, fault counter',
    inputs: [
      { key: 'policy', label: 'Policy', type: 'select', value: 'lru',
        options: Object.keys(POLICIES).map(k => ({ value: k, label: POLICIES[k] })) },
      { key: 'frames', label: 'Frames', type: 'number', value: 3, min: 1, max: 8 },
      { key: 'refs', label: 'Reference string', type: 'text',
        hint: '(space separated)',
        value: '7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1' },
    ],
    build: simulate,
    draw: draw,
  });
})();
