/* ==========================================================================
   Finite automaton simulation.

   Type a transition table, type a string, and step the machine through it. The
   state diagram is laid out on a circle, so any machine you write draws itself
   without you positioning anything.

   NFAs are handled by tracking a set of current states rather than one, which is
   the subset construction happening live: watch the set grow and collapse.

   Table format, one line per transition:
       q0, 0 -> q1
   plus  start: q0   and   accept: q1 q2
   ========================================================================== */
(function () {
  const { el } = GG;

  function parseMachine(text) {
    const lines = String(text || '').split(/\n+/).map(l => l.trim()).filter(Boolean);
    const delta = {};                 /* delta[state][symbol] = [states] */
    const states = [];
    let start = null;
    const accept = [];

    const see = s => { if (states.indexOf(s) === -1) states.push(s); };

    lines.forEach((line, i) => {
      let m;
      if ((m = line.match(/^start\s*:\s*(\S+)/i))) {
        start = m[1]; see(start); return;
      }
      if ((m = line.match(/^accept\s*:\s*(.+)$/i))) {
        m[1].split(/[\s,]+/).filter(Boolean).forEach(s => { see(s); accept.push(s); });
        return;
      }
      m = line.match(/^(\S+)\s*,\s*(\S+)\s*(?:->|=>)\s*(.+)$/);
      if (!m) throw new Error('Line ' + (i + 1) + ': expected "state, symbol -> state".');
      const from = m[1], sym = m[2];
      const to = m[3].split(/[\s,|]+/).filter(Boolean);
      see(from); to.forEach(see);
      delta[from] = delta[from] || {};
      delta[from][sym] = (delta[from][sym] || []).concat(to);
    });

    if (!start) throw new Error('Add a "start: q0" line.');
    if (!accept.length) throw new Error('Add an "accept: ..." line.');

    const alphabet = [];
    Object.keys(delta).forEach(s => Object.keys(delta[s]).forEach(a => {
      if (alphabet.indexOf(a) === -1) alphabet.push(a);
    }));

    const nondeterministic = Object.keys(delta).some(s =>
      Object.keys(delta[s]).some(a => delta[s][a].length > 1));

    return { delta, states, start, accept, alphabet, nondeterministic };
  }

  function simulate(values) {
    const M = parseMachine(values.machine);
    const input = String(values.input || '').replace(/\s+/g, '');
    if (input.length > 30) throw new Error('Keep the input under 30 symbols.');

    let current = [M.start];
    const out = [];

    const isAccepting = set => set.some(s => M.accept.indexOf(s) !== -1);

    out.push({
      caption: 'Start in ' + M.start + ' with the head before the first symbol.',
      pos: 0, current: current.slice(), input, M,
      reading: null, dead: false,
      accepted: input.length === 0 && isAccepting(current),
    });

    for (let i = 0; i < input.length; i++) {
      const sym = input[i];
      const next = [];
      current.forEach(s => {
        const to = (M.delta[s] || {})[sym] || [];
        to.forEach(x => { if (next.indexOf(x) === -1) next.push(x); });
      });

      let caption;
      if (!next.length) {
        caption = 'Reading "' + sym + '" from ' + current.join(', ') +
                  ' has no transition. The machine is stuck, so the string is rejected.';
        current = [];
        out.push({ caption, pos: i + 1, current: [], input, M, reading: sym,
                   dead: true, accepted: false });
        break;
      }

      caption = 'Read "' + sym + '": ' + current.join(', ') + ' -> ' + next.join(', ') +
                (M.nondeterministic && next.length > 1
                  ? '. Several states are possible at once, so all of them are tracked.'
                  : '.');
      current = next;
      out.push({
        caption, pos: i + 1, current: current.slice(), input, M,
        reading: sym, dead: false, accepted: isAccepting(current),
      });
    }

    const last = out[out.length - 1];
    if (!last.dead) {
      const ok = isAccepting(current);
      out.push(Object.assign({}, last, {
        caption: 'Input finished in ' + (current.join(', ') || 'nothing') + '. ' +
                 (ok ? 'That is an accepting state, so the string is ACCEPTED.'
                     : 'No accepting state among them, so the string is REJECTED.'),
        accepted: ok, done: true,
      }));
    } else {
      out.push(Object.assign({}, last, {
        caption: 'The machine died part way through, so the string is REJECTED.',
        done: true,
      }));
    }
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const M = frame.M;

    /* the tape */
    const tape = el('div', { class: 'viz-tape' });
    for (let i = 0; i < frame.input.length; i++) {
      tape.appendChild(el('span', {
        class: 'viz-cellt' + (i === frame.pos - 1 ? ' at' : '') + (i < frame.pos - 1 ? ' past' : ''),
        text: frame.input[i],
      }));
    }
    if (!frame.input.length) {
      tape.appendChild(el('span', { class: 'viz-cellt dim', text: 'e' }));
    }
    host.appendChild(tape);

    /* the diagram, states on a circle */
    const n = M.states.length;
    const R = Math.min(120, 40 + n * 12);
    const size = (R + 46) * 2;
    const svg = ns('svg', { viewBox: '0 0 ' + size + ' ' + size, class: 'viz-svg',
                            role: 'img', 'aria-label': 'State diagram' });
    const cx = size / 2, cy = size / 2;
    const pos = {};
    M.states.forEach((s, i) => {
      const a = (i / n) * Math.PI * 2 - Math.PI / 2;
      pos[s] = { x: cx + R * Math.cos(a), y: cy + R * Math.sin(a) };
    });

    /* edges */
    Object.keys(M.delta).forEach(from => {
      Object.keys(M.delta[from]).forEach(sym => {
        M.delta[from][sym].forEach(to => {
          const a = pos[from], b = pos[to];
          if (!a || !b) return;
          const live = frame.current.indexOf(to) !== -1 && frame.reading === sym;
          if (from === to) {
            const loop = ns('path', {
              d: 'M' + (a.x - 10) + ',' + (a.y - 20) + ' q 10,-22 20,0',
              fill: 'none', stroke: live ? '#e8b43e' : 'rgba(255,255,255,.22)',
              'stroke-width': live ? 2.5 : 1.5,
            });
            svg.appendChild(loop);
            svg.appendChild(text(a.x, a.y - 30, sym, live));
          } else {
            svg.appendChild(ns('line', {
              x1: a.x, y1: a.y, x2: b.x, y2: b.y,
              stroke: live ? '#e8b43e' : 'rgba(255,255,255,.18)',
              'stroke-width': live ? 2.5 : 1.2,
            }));
            svg.appendChild(text((a.x + b.x) / 2, (a.y + b.y) / 2 - 4, sym, live));
          }
        });
      });
    });

    /* states */
    M.states.forEach(s => {
      const p = pos[s];
      const live = frame.current.indexOf(s) !== -1;
      const acc = M.accept.indexOf(s) !== -1;
      if (acc) {
        svg.appendChild(ns('circle', { cx: p.x, cy: p.y, r: 22, fill: 'none',
          stroke: live ? '#e8b43e' : 'rgba(255,255,255,.4)', 'stroke-width': 1.5 }));
      }
      svg.appendChild(ns('circle', {
        cx: p.x, cy: p.y, r: 18,
        fill: live ? '#e8b43e' : '#1a212c',
        stroke: live ? '#fff' : 'rgba(255,255,255,.35)',
        'stroke-width': live ? 2 : 1.2,
      }));
      const t = text(p.x, p.y + 4, s, false);
      t.setAttribute('fill', live ? '#0b0f16' : '#e9eef5');
      t.setAttribute('font-weight', '700');
      svg.appendChild(t);
      if (s === M.start) {
        svg.appendChild(ns('line', { x1: p.x - 40, y1: p.y, x2: p.x - 20, y2: p.y,
          stroke: 'rgba(255,255,255,.5)', 'stroke-width': 1.5 }));
      }
    });
    host.appendChild(svg);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(M.nondeterministic ? 'NFA' : 'DFA', 'on'),
      chip('current: ' + (frame.current.join(', ') || 'dead'), 'mono'),
      chip('read ' + frame.pos + '/' + frame.input.length, 'mono'),
      frame.done ? chip(frame.accepted ? 'ACCEPTED' : 'REJECTED',
                        frame.accepted ? 'good' : 'bad') : chip(''),
    ]));
  }

  function text(x, y, str, live) {
    const t = ns('text', { x: x, y: y, 'text-anchor': 'middle',
                           fill: live ? '#e8b43e' : '#95a1b3',
                           'font-family': 'ui-monospace, monospace', 'font-size': '12' });
    t.textContent = str;
    return t;
  }

  function ns(tag, attrs) {
    const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.keys(attrs || {}).forEach(k => n.setAttribute(k, attrs[k]));
    return n;
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('toc-dfa', {
    title: 'Automaton simulation',
    subtitle: 'Write a transition table and run a string through it one symbol at ' +
              'a time. The default machine accepts any string containing "10". Give a ' +
              'state two targets for one symbol and it becomes an NFA, tracked as a set.',
    glyph: 'A',
    topic: 'finite-automata',
    note: 'DFA and NFA, live state set',
    inputs: [
      { key: 'machine', label: 'Transition table', type: 'textarea',
        hint: '(state, symbol -> state)',
        value: 'start: q0\naccept: q2\nq0, 0 -> q0\nq0, 1 -> q1\nq1, 0 -> q2\nq1, 1 -> q1\nq2, 0 -> q2\nq2, 1 -> q2' },
      { key: 'input', label: 'Input string', type: 'text', value: '11010' },
    ],
    build: simulate,
    draw: draw,
  });
})();
