/* ==========================================================================
   CPU scheduling.

   Five policies over the same process table, simulated one time unit at a time.
   The numbers GATE actually asks for - completion, turnaround, waiting - are
   computed from the simulation itself rather than from a formula, so the Gantt
   chart and the table can never disagree.

   Type your own burst times in and it doubles as a way to check your answer to
   a paper question.
   ========================================================================== */
(function () {
  const { el, esc } = GG;

  const POLICIES = {
    fcfs:     'FCFS (first come, first served)',
    sjf:      'SJF (shortest job first, non-preemptive)',
    srtf:     'SRTF (shortest remaining time, preemptive)',
    rr:       'Round robin',
    priority: 'Priority (non-preemptive, lower number wins)',
  };

  const COLOURS = ['#e8b43e', '#3fb950', '#79c0ff', '#e5534b', '#c77dff',
                   '#e08c3a', '#56d4dd', '#f0883e'];

  function simulate(values) {
    const procs = (values.procs || []).map((p, i) => ({
      id: 'P' + (i + 1),
      idx: i,
      arrival: Math.max(0, p.arrival | 0),
      burst: Math.max(1, p.burst | 0),
      priority: p.priority | 0,
      left: Math.max(1, p.burst | 0),
      start: null,
      done: null,
    }));
    if (!procs.length) throw new Error('Add at least one process.');
    if (procs.length > 8) throw new Error('Eight processes is the sensible limit here.');

    const policy = values.policy;
    const quantum = Math.max(1, values.quantum | 0);
    const total = procs.reduce((a, p) => a + p.burst, 0);
    const limit = total + Math.max(...procs.map(p => p.arrival)) + 2;

    const frames = [];
    const gantt = [];               /* [{id, from, to}] */
    let t = 0, running = null, sliceLeft = 0, guard = 0;
    let rrQueue = [];

    const arrived = () => procs.filter(p => p.arrival <= t && p.left > 0);

    while (procs.some(p => p.left > 0) && guard++ < limit * 4) {
      const ready = arrived();

      /* keep the round-robin queue fed in arrival order */
      if (policy === 'rr') {
        ready.forEach(p => {
          if (p !== running && rrQueue.indexOf(p) === -1) rrQueue.push(p);
        });
      }

      let why = '';
      if (!ready.length && !running) {
        gantt.push({ id: 'idle', from: t, to: t + 1 });
        why = 'Nothing has arrived yet, so the CPU idles.';
        frames.push(snapshot(t, null, ready, procs, gantt, why));
        t++;
        continue;
      }

      /* choose, or keep going */
      if (policy === 'fcfs') {
        if (!running || running.left === 0) {
          running = ready.slice().sort((a, b) => a.arrival - b.arrival || a.idx - b.idx)[0];
          why = running.id + ' runs: it arrived first among the waiting processes.';
        }
      } else if (policy === 'sjf') {
        if (!running || running.left === 0) {
          running = ready.slice().sort((a, b) => a.burst - b.burst || a.arrival - b.arrival)[0];
          why = running.id + ' runs: shortest burst (' + running.burst + ') of everything that has arrived.';
        }
      } else if (policy === 'srtf') {
        const best = ready.slice().sort((a, b) => a.left - b.left || a.arrival - b.arrival)[0];
        if (running && best !== running && best.left < running.left) {
          why = best.id + ' preempts ' + running.id + ': ' + best.left +
                ' left versus ' + running.left + '.';
        } else if (!running || running.left === 0) {
          why = best.id + ' runs: least remaining time (' + best.left + ').';
        }
        running = best;
      } else if (policy === 'priority') {
        if (!running || running.left === 0) {
          running = ready.slice().sort((a, b) => a.priority - b.priority ||
                                                 a.arrival - b.arrival)[0];
          why = running.id + ' runs: priority ' + running.priority + ' beats the rest.';
        }
      } else if (policy === 'rr') {
        if (!running || running.left === 0 || sliceLeft === 0) {
          if (running && running.left > 0) {
            rrQueue.push(running);
            why = running.id + ' used its full quantum and goes to the back of the queue.';
          }
          rrQueue = rrQueue.filter(p => p.left > 0);
          running = rrQueue.shift() || ready[0];
          sliceLeft = quantum;
          if (!why && running) why = running.id + ' takes the CPU for up to ' + quantum + ' unit(s).';
        }
      }

      if (!running) { t++; continue; }
      if (running.start === null) running.start = t;

      const last = gantt[gantt.length - 1];
      if (last && last.id === running.id && last.to === t) last.to = t + 1;
      else gantt.push({ id: running.id, from: t, to: t + 1 });

      running.left--;
      if (policy === 'rr') sliceLeft--;

      if (!why) why = running.id + ' continues, ' + running.left + ' unit(s) of work left.';

      if (running.left === 0) {
        running.done = t + 1;
        why = running.id + ' finishes at t=' + running.done + '. Turnaround ' +
              (running.done - running.arrival) + ', waiting ' +
              (running.done - running.arrival - running.burst) + '.';
      }

      frames.push(snapshot(t + 1, running, arrived().filter(p => p !== running),
                           procs, gantt, why));
      if (running.left === 0) running = null;
      t++;
    }

    frames.push(snapshot(t, null, [], procs, gantt, summary(procs)));
    return frames;
  }

  function summary(procs) {
    const n = procs.length;
    const tat = procs.reduce((a, p) => a + (p.done - p.arrival), 0) / n;
    const wt = procs.reduce((a, p) => a + (p.done - p.arrival - p.burst), 0) / n;
    return 'All done. Average turnaround ' + tat.toFixed(2) +
           ', average waiting ' + wt.toFixed(2) + '.';
  }

  function snapshot(t, running, ready, procs, gantt, caption) {
    return {
      t: t,
      caption: caption,
      running: running ? running.id : null,
      ready: ready.map(p => p.id),
      gantt: gantt.map(g => Object.assign({}, g)),
      rows: procs.map(p => ({
        id: p.id, arrival: p.arrival, burst: p.burst, priority: p.priority,
        left: p.left,
        done: p.done,
        tat: p.done === null ? null : p.done - p.arrival,
        wait: p.done === null ? null : p.done - p.arrival - p.burst,
      })),
    };
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame, values) {
    const span = Math.max(1, frame.gantt.length ? frame.gantt[frame.gantt.length - 1].to : 1);
    const W = 640, unit = Math.max(14, Math.min(46, (W - 40) / span));
    const width = 40 + span * unit;

    const svg = ns('svg', { viewBox: '0 0 ' + width + ' 150', class: 'viz-svg',
                            role: 'img', 'aria-label': 'Gantt chart' });

    frame.gantt.forEach(g => {
      const x = 20 + g.from * unit, w = (g.to - g.from) * unit;
      const idle = g.id === 'idle';
      svg.appendChild(ns('rect', {
        x: x, y: 30, width: w, height: 44, rx: 4,
        fill: idle ? 'rgba(255,255,255,.05)' : colourOf(g.id, frame.rows),
        stroke: g.id === frame.running ? '#fff' : 'rgba(0,0,0,.35)',
        'stroke-width': g.id === frame.running ? 2 : 1,
      }));
      if (w > 16) {
        const label = ns('text', { x: x + w / 2, y: 58, 'text-anchor': 'middle',
                                   class: 'viz-bar-label',
                                   fill: idle ? '#8b949e' : '#0b0f16' });
        label.textContent = idle ? '' : g.id;
        svg.appendChild(label);
      }
    });

    /* time axis: every tick when there is room, else every fifth */
    const stepEvery = unit >= 24 ? 1 : 5;
    for (let i = 0; i <= span; i++) {
      const x = 20 + i * unit;
      svg.appendChild(ns('line', { x1: x, y1: 74, x2: x, y2: 80,
                                   stroke: 'rgba(255,255,255,.25)' }));
      if (i % stepEvery === 0) {
        const tx = ns('text', { x: x, y: 94, 'text-anchor': 'middle', class: 'viz-tick' });
        tx.textContent = String(i);
        svg.appendChild(tx);
      }
    }

    const now = ns('line', { x1: 20 + frame.t * unit, y1: 22, x2: 20 + frame.t * unit,
                             y2: 82, stroke: '#e8b43e', 'stroke-width': 2 });
    svg.appendChild(now);

    host.appendChild(svg);

    /* live state */
    host.appendChild(el('div', { class: 'viz-state' }, [
      chip('t = ' + frame.t, 'mono'),
      chip('running: ' + (frame.running || 'idle'), frame.running ? 'on' : ''),
      chip('ready: ' + (frame.ready.length ? frame.ready.join(', ') : 'empty')),
    ]));

    /* results table */
    const head = ['', 'AT', 'BT'];
    if (values.policy === 'priority') head.push('Pr');
    head.push('Left', 'CT', 'TAT', 'WT');

    const table = el('div', { class: 'viz-results' });
    table.appendChild(row(head, true));
    frame.rows.forEach(r => {
      const cells = [r.id, r.arrival, r.burst];
      if (values.policy === 'priority') cells.push(r.priority);
      cells.push(r.left, r.done ?? '-', r.tat ?? '-', r.wait ?? '-');
      table.appendChild(row(cells, false, colourOf(r.id, frame.rows),
                            r.id === frame.running));
    });

    const done = frame.rows.filter(r => r.done !== null);
    if (done.length === frame.rows.length) {
      const n = done.length;
      table.appendChild(row(
        ['avg', '', '', ...(values.policy === 'priority' ? [''] : []), '', '',
         (done.reduce((a, r) => a + r.tat, 0) / n).toFixed(2),
         (done.reduce((a, r) => a + r.wait, 0) / n).toFixed(2)], true));
    }
    host.appendChild(table);
  }

  function row(cells, headish, colour, live) {
    const r = el('div', { class: 'viz-rrow' + (headish ? ' head' : '') +
                                 (live ? ' live' : '') });
    cells.forEach((c, i) => {
      const span = el('span', { text: String(c) });
      if (i === 0 && colour) span.style.borderLeft = '3px solid ' + colour;
      r.appendChild(span);
    });
    return r;
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  function colourOf(id, rows) {
    const i = rows.findIndex(r => r.id === id);
    return COLOURS[(i < 0 ? 0 : i) % COLOURS.length];
  }

  function ns(tag, attrs) {
    const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.keys(attrs || {}).forEach(k => n.setAttribute(k, attrs[k]));
    return n;
  }

  GG.viz.register('os-scheduling', {
    title: 'CPU scheduling',
    subtitle: 'Watch the Gantt chart build one tick at a time, then read the ' +
              'turnaround and waiting times off the same simulation.',
    glyph: 'S',
    topic: 'cpu-scheduling',
    note: 'five policies, your own numbers',
    inputs: [
      { key: 'policy', label: 'Policy', type: 'select',
        value: 'srtf',
        options: Object.keys(POLICIES).map(k => ({ value: k, label: POLICIES[k] })) },
      { key: 'quantum', label: 'Quantum', hint: '(round robin only)',
        type: 'number', value: 2, min: 1, max: 10 },
      { key: 'procs', label: 'Processes', type: 'table', max: 8,
        columns: [
          { key: 'arrival', label: 'Arrival', value: 0 },
          { key: 'burst', label: 'Burst', value: 4 },
          { key: 'priority', label: 'Priority', value: 1 },
        ],
        value: [
          { arrival: 0, burst: 7, priority: 2 },
          { arrival: 2, burst: 4, priority: 1 },
          { arrival: 4, burst: 1, priority: 3 },
          { arrival: 5, burst: 4, priority: 2 },
        ] },
    ],
    build: simulate,
    draw: draw,
  });
})();
