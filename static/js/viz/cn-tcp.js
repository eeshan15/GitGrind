/* ==========================================================================
   TCP congestion control.

   One graph, three regimes. Slow start doubles the window every round trip until
   it hits the threshold; congestion avoidance then adds one segment per RTT; a
   loss cuts everything back. Which cutback depends on how the loss was detected,
   and that is the distinction the exam tests.

   Timeout means the network is badly congested: window back to 1, threshold to
   half. Three duplicate ACKs mean packets are still flowing, so Reno only halves
   the window and keeps going, while Tahoe restarts from 1 either way.
   ========================================================================== */
(function () {
  const { el } = GG;

  function parseEvents(text) {
    const ev = {};
    String(text || '').split(/[\s,]+/).filter(Boolean).forEach(tok => {
      const m = tok.match(/^(\d+)\s*:?\s*([td])$/i);
      if (!m) throw new Error('"' + tok + '" should look like 8:t (timeout) or 12:d ' +
                              '(three duplicate ACKs).');
      ev[Number(m[1])] = m[2].toLowerCase();
    });
    return ev;
  }

  function simulate(values) {
    const rounds = Math.max(4, Math.min(40, values.rounds | 0));
    const events = parseEvents(values.events);
    const reno = String(values.variant) === 'reno';
    let cwnd = 1, ssthresh = Math.max(2, values.ssthresh | 0);

    const series = [];
    const out = [];

    const push = caption => out.push({
      caption, series: series.map(p => Object.assign({}, p)),
      cwnd, ssthresh, rounds, reno,
    });

    series.push({ t: 0, cwnd, ssthresh, phase: 'ss' });
    push('Start with cwnd = 1 segment and ssthresh = ' + ssthresh +
         '. TCP has no idea what the network can take, so it probes.');

    for (let t = 1; t <= rounds; t++) {
      const ev = events[t];

      if (ev === 't') {
        ssthresh = Math.max(2, Math.floor(cwnd / 2));
        cwnd = 1;
        series.push({ t, cwnd, ssthresh, phase: 'loss' });
        push('Round ' + t + ': TIMEOUT. Nothing is getting through, so TCP assumes ' +
             'serious congestion: ssthresh drops to half the old window (' + ssthresh +
             ') and cwnd restarts at 1. This is the expensive kind of loss.');
        continue;
      }
      if (ev === 'd') {
        ssthresh = Math.max(2, Math.floor(cwnd / 2));
        cwnd = reno ? ssthresh : 1;
        series.push({ t, cwnd, ssthresh, phase: 'loss' });
        push('Round ' + t + ': three duplicate ACKs. Packets are still arriving, so ' +
             'the loss was probably isolated. ssthresh becomes ' + ssthresh +
             (reno
               ? ' and Reno halves cwnd to ' + cwnd +
                 ' rather than restarting - that is fast recovery.'
               : ' and Tahoe restarts cwnd at 1 regardless of how the loss was found.'));
        continue;
      }

      if (cwnd < ssthresh) {
        cwnd = Math.min(cwnd * 2, ssthresh);
        series.push({ t, cwnd, ssthresh, phase: 'ss' });
        push('Round ' + t + ': still below ssthresh, so slow start doubles cwnd to ' +
             cwnd + '. "Slow" refers to the starting point, not the growth - this is ' +
             'exponential.');
      } else {
        cwnd = cwnd + 1;
        series.push({ t, cwnd, ssthresh, phase: 'ca' });
        push('Round ' + t + ': at or above ssthresh, so congestion avoidance adds one ' +
             'segment per RTT. cwnd = ' + cwnd + '. Linear from here until something ' +
             'breaks.');
      }
    }

    const peak = Math.max.apply(null, series.map(p => p.cwnd));
    push('After ' + rounds + ' round trip(s) cwnd is ' + cwnd + ', ssthresh is ' +
         ssthresh + ', and the window peaked at ' + peak + ' segment(s).');
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const S = frame.series;
    const maxY = Math.max(4, Math.max.apply(null, S.map(p => Math.max(p.cwnd, p.ssthresh))) + 1);
    const W = 660, H = 240, L = 36, B = 28;
    const x = t => L + (t / frame.rounds) * (W - L - 14);
    const y = v => H - B - (v / maxY) * (H - B - 14);

    const svg = ns('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'viz-svg',
                            role: 'img', 'aria-label': 'Congestion window' });

    svg.appendChild(ns('line', { x1: L, y1: H - B, x2: W - 10, y2: H - B,
                                 stroke: 'rgba(255,255,255,.25)' }));
    svg.appendChild(ns('line', { x1: L, y1: 10, x2: L, y2: H - B,
                                 stroke: 'rgba(255,255,255,.25)' }));
    for (let v = 0; v <= maxY; v += Math.ceil(maxY / 5)) {
      const t = ns('text', { x: L - 6, y: y(v) + 4, 'text-anchor': 'end',
        'font-family': 'ui-monospace, monospace', 'font-size': '10', fill: '#6f7d91' });
      t.textContent = String(v);
      svg.appendChild(t);
    }

    /* ssthresh as a step line */
    let d = '';
    S.forEach((p, i) => { d += (i ? ' L' : 'M') + x(p.t) + ',' + y(p.ssthresh); });
    svg.appendChild(ns('path', { d: d, fill: 'none', stroke: 'rgba(229,83,75,.6)',
                                 'stroke-width': 1.4, 'stroke-dasharray': '5 4' }));

    /* cwnd */
    let c = '';
    S.forEach((p, i) => { c += (i ? ' L' : 'M') + x(p.t) + ',' + y(p.cwnd); });
    svg.appendChild(ns('path', { d: c, fill: 'none', stroke: '#e8b43e',
                                 'stroke-width': 2.2 }));

    S.forEach(p => {
      svg.appendChild(ns('circle', { cx: x(p.t), cy: y(p.cwnd), r: 3.4,
        fill: p.phase === 'loss' ? '#e5534b' : p.phase === 'ss' ? '#e8b43e' : '#3fb950' }));
    });

    host.appendChild(svg);
    host.appendChild(el('div', { class: 'viz-state' }, [
      chip('cwnd ' + frame.cwnd, 'on'),
      chip('ssthresh ' + frame.ssthresh, 'mono'),
      chip(frame.reno ? 'TCP Reno' : 'TCP Tahoe', 'mono'),
      chip('gold = slow start, green = avoidance, red = loss'),
    ]));
  }

  function ns(tag, attrs) {
    const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.keys(attrs || {}).forEach(k => n.setAttribute(k, attrs[k]));
    return n;
  }
  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('cn-tcp', {
    title: 'TCP congestion control',
    subtitle: 'The cwnd sawtooth, round trip by round trip. Put a timeout and a ' +
              'triple-duplicate-ACK in and watch Tahoe and Reno diverge.',
    glyph: 'C',
    topic: 'tcp',
    note: 'slow start, avoidance, loss recovery',
    inputs: [
      { key: 'variant', label: 'Variant', type: 'select', value: 'reno',
        options: [{ value: 'reno', label: 'TCP Reno (fast recovery on 3 dup ACKs)' },
                  { value: 'tahoe', label: 'TCP Tahoe (always restart at 1)' }] },
      { key: 'ssthresh', label: 'Initial ssthresh', type: 'number', value: 8, min: 2, max: 64 },
      { key: 'rounds', label: 'Round trips', type: 'number', value: 20, min: 4, max: 40 },
      { key: 'events', label: 'Loss events', hint: '(8:t = timeout, 14:d = 3 dup ACKs)',
        type: 'text', value: '8:t 15:d' },
    ],
    build: simulate,
    draw: draw,
  });
})();
