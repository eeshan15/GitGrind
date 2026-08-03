/* ==========================================================================
   Disk scheduling.

   The number the exam wants is total head movement, so that is what accumulates
   in the corner while the head walks the track. Every move says where it went
   and why that request was chosen next.

   SCAN goes to the end of the disk before turning; LOOK turns at the last
   request. That one difference is worth several cylinders and is the most common
   place to lose a mark.
   ========================================================================== */
(function () {
  const { el } = GG;

  const POLICIES = {
    fcfs:  'FCFS (serve in arrival order)',
    sstf:  'SSTF (nearest request first)',
    scan:  'SCAN (sweep to the end, then reverse)',
    cscan: 'C-SCAN (sweep up, jump back, sweep up again)',
    look:  'LOOK (sweep to the last request, then reverse)',
    clook: 'C-LOOK (sweep up to the last request, jump back)',
  };

  function parseQueue(text, max) {
    const q = String(text || '').split(/[^0-9]+/).filter(Boolean).map(Number)
      .filter(n => n >= 0 && n <= max);
    if (!q.length) throw new Error('Give some cylinder requests, e.g. 98 183 37.');
    if (q.length > 20) throw new Error('Twenty requests is enough to see the pattern.');
    return q;
  }

  function simulate(values) {
    const max = Math.max(10, Math.min(9999, values.cylinders | 0)) - 1;
    const start = Math.max(0, Math.min(max, values.head | 0));
    const queue = parseQueue(values.queue, max);
    const policy = values.policy;
    const up = String(values.direction) === 'up';

    const path = [start];
    const served = [];
    let head = start, moved = 0;
    const pending = queue.slice();
    const out = [];

    const push = caption => out.push({
      caption, head, moved, path: path.slice(), served: served.slice(),
      pending: pending.slice(), queue, max, policy,
    });

    push('The head starts at cylinder ' + start + ' with ' + queue.length +
         ' request(s) waiting: ' + queue.join(', ') + '.');

    const go = (to, why) => {
      moved += Math.abs(to - head);
      head = to;
      path.push(to);
      if (pending.indexOf(to) !== -1) {
        pending.splice(pending.indexOf(to), 1);
        served.push(to);
      }
      push(why + ' Head movement so far: ' + moved + ' cylinder(s).');
    };

    if (policy === 'fcfs') {
      queue.forEach(t => go(t, 'Serve ' + t + ' next simply because it asked first.'));
    } else if (policy === 'sstf') {
      while (pending.length) {
        let best = pending[0];
        pending.forEach(t => {
          if (Math.abs(t - head) < Math.abs(best - head)) best = t;
        });
        go(best, 'The nearest waiting request is ' + best + ', ' +
                 Math.abs(best - head) + ' cylinder(s) away.');
      }
    } else {
      const above = () => pending.filter(t => t >= head).sort((a, b) => a - b);
      const below = () => pending.filter(t => t < head).sort((a, b) => b - a);
      let dir = up;

      for (let guard = 0; pending.length && guard < 100; guard++) {
        const ahead = dir ? above() : below();

        if (ahead.length) {
          go(ahead[0], 'Moving ' + (dir ? 'up' : 'down') + ', the next request in ' +
                       'that direction is ' + ahead[0] + '.');
          continue;
        }

        /* nothing left this way */
        if (policy === 'scan') {
          const edge = dir ? max : 0;
          if (head !== edge) {
            go(edge, 'No requests left going ' + (dir ? 'up' : 'down') +
                     ', but SCAN travels all the way to cylinder ' + edge +
                     ' before turning. Those are wasted cylinders that LOOK avoids.');
          }
          dir = !dir;
        } else if (policy === 'look') {
          dir = !dir;
          push('No requests left going ' + (dir ? 'down' : 'up') +
               ', so LOOK turns around here rather than walking to the edge.');
        } else if (policy === 'cscan') {
          if (head !== max) go(max, 'C-SCAN runs to the end of the disk at ' + max + '.');
          go(0, 'Then it jumps back to cylinder 0 without serving anything on the ' +
                'way. That jump still counts as head movement.');
          dir = true;
        } else {                                   /* c-look */
          const lowest = Math.min.apply(null, pending);
          go(lowest, 'C-LOOK jumps straight back to the lowest waiting request, ' +
                     lowest + ', without going to the edge.');
          dir = true;
        }
      }
    }

    out.push({
      caption: 'All ' + queue.length + ' request(s) served. Total head movement is ' +
               moved + ' cylinder(s), an average of ' +
               (moved / queue.length).toFixed(1) + ' per request.',
      head, moved, path: path.slice(), served: served.slice(),
      pending: [], queue, max, policy,
    });
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const W = 660, H = Math.max(150, 30 + frame.path.length * 22);
    const x = c => 40 + (c / frame.max) * (W - 80);

    const svg = ns('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'viz-svg',
                            role: 'img', 'aria-label': 'Head movement' });

    /* the cylinder axis */
    svg.appendChild(ns('line', { x1: 40, y1: 18, x2: W - 40, y2: 18,
                                 stroke: 'rgba(255,255,255,.25)' }));
    [0, Math.round(frame.max / 2), frame.max].forEach(c => {
      const t = ns('text', { x: x(c), y: 12, 'text-anchor': 'middle',
                             'font-family': 'ui-monospace, monospace',
                             'font-size': '10', fill: '#6f7d91' });
      t.textContent = String(c);
      svg.appendChild(t);
    });

    /* every waiting request as a tick */
    frame.queue.forEach(c => {
      const done = frame.served.indexOf(c) !== -1;
      svg.appendChild(ns('line', {
        x1: x(c), y1: 13, x2: x(c), y2: 23,
        stroke: done ? 'rgba(63,185,80,.8)' : 'rgba(232,180,62,.8)',
        'stroke-width': 2,
      }));
    });

    /* the walk, one row per move */
    for (let i = 1; i < frame.path.length; i++) {
      const y1 = 18 + (i - 1) * 22, y2 = 18 + i * 22;
      svg.appendChild(ns('line', {
        x1: x(frame.path[i - 1]), y1: y1, x2: x(frame.path[i]), y2: y2,
        stroke: '#e8b43e', 'stroke-width': 1.8,
      }));
      svg.appendChild(ns('circle', { cx: x(frame.path[i]), cy: y2, r: 4,
                                     fill: '#e8b43e' }));
      const t = ns('text', { x: x(frame.path[i]) + 8, y: y2 + 4,
                             'font-family': 'ui-monospace, monospace',
                             'font-size': '10', fill: '#95a1b3' });
      t.textContent = String(frame.path[i]);
      svg.appendChild(t);
    }
    svg.appendChild(ns('circle', { cx: x(frame.path[0]), cy: 18, r: 5,
                                   fill: 'none', stroke: '#fff', 'stroke-width': 1.5 }));
    host.appendChild(svg);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip('head at ' + frame.head, 'on'),
      chip('moved ' + frame.moved, 'mono'),
      chip('served ' + frame.served.length + '/' + frame.queue.length, 'mono'),
      chip(frame.pending.length ? 'waiting: ' + frame.pending.join(', ') : 'queue empty'),
    ]));
  }

  function ns(tag, attrs) {
    const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.keys(attrs || {}).forEach(k => n.setAttribute(k, attrs[k]));
    return n;
  }
  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('os-disk', {
    title: 'Disk scheduling',
    subtitle: 'Six policies over the same request queue, with total head movement ' +
              'counting up as the head walks. SCAN versus LOOK is the interesting pair.',
    glyph: 'D',
    topic: 'disk-scheduling',
    note: 'total head movement',
    inputs: [
      { key: 'policy', label: 'Policy', type: 'select', value: 'sstf',
        options: Object.keys(POLICIES).map(k => ({ value: k, label: POLICIES[k] })) },
      { key: 'cylinders', label: 'Cylinders', type: 'number', value: 200, min: 10, max: 9999 },
      { key: 'head', label: 'Head starts at', type: 'number', value: 53, min: 0 },
      { key: 'direction', label: 'Initial direction', type: 'select', value: 'up',
        options: [{ value: 'up', label: 'Towards higher cylinders' },
                  { value: 'down', label: 'Towards lower cylinders' }] },
      { key: 'queue', label: 'Request queue', hint: '(in arrival order)', type: 'text',
        value: '98 183 37 122 14 124 65 67' },
    ],
    build: simulate,
    draw: draw,
  });
})();
