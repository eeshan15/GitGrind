/* ==========================================================================
   FIRST and FOLLOW.

   Both sets are fixed points: keep applying the rules until nothing changes.
   That is hard to see in a finished table, so every frame here is one rule
   application, and it says which rule fired and what it added.

   Grammar format, one production per line, | for alternatives, e for epsilon:
       E -> T E'
       E' -> + T E' | e
   The left side of the first line is the start symbol.
   ========================================================================== */
(function () {
  const { el } = GG;
  const EPS = 'e';

  function parseGrammar(text) {
    const prods = [];
    const nts = [];
    String(text || '').split(/\n+/).map(l => l.trim()).filter(Boolean).forEach((line, i) => {
      const m = line.match(/^(\S+)\s*(?:->|=>|:)\s*(.*)$/);
      if (!m) throw new Error('Line ' + (i + 1) + ': expected "A -> alpha".');
      const head = m[1];
      if (nts.indexOf(head) === -1) nts.push(head);
      m[2].split('|').forEach(alt => {
        const syms = alt.trim().split(/\s+/).filter(Boolean);
        prods.push({ head, body: syms.length ? syms : [EPS] });
      });
    });
    if (!prods.length) throw new Error('Write at least one production.');

    const terms = [];
    prods.forEach(p => p.body.forEach(s => {
      if (s !== EPS && nts.indexOf(s) === -1 && terms.indexOf(s) === -1) terms.push(s);
    }));
    return { prods, nts, terms, start: prods[0].head };
  }

  const isNT = (G, s) => G.nts.indexOf(s) !== -1;

  function simulate(values) {
    const G = parseGrammar(values.grammar);
    const FIRST = {}, FOLLOW = {};
    G.nts.forEach(n => { FIRST[n] = []; FOLLOW[n] = []; });
    G.terms.forEach(t => { FIRST[t] = [t]; });

    const out = [];
    const snap = (caption, focus, stage) => out.push({
      caption, G, focus, stage,
      FIRST: JSON.parse(JSON.stringify(FIRST)),
      FOLLOW: JSON.parse(JSON.stringify(FOLLOW)),
    });

    const add = (set, sym, v) => {
      if (set[sym].indexOf(v) === -1) { set[sym].push(v); set[sym].sort(); return true; }
      return false;
    };

    snap('Terminals are their own FIRST set. Non-terminals start empty and grow ' +
         'until nothing changes - both sets are least fixed points, which is why ' +
         'the rules are applied in a loop.', null, 'first');

    let changed = true, guard = 0;
    while (changed && guard++ < 60) {
      changed = false;
      G.prods.forEach(p => {
        if (p.body[0] === EPS) {
          if (add(FIRST, p.head, EPS)) {
            changed = true;
            snap(p.head + ' -> e directly puts e into FIRST(' + p.head + ').',
                 p.head, 'first');
          }
          return;
        }
        let allEps = true;
        for (const s of p.body) {
          const src = isNT(G, s) ? FIRST[s] : [s];
          let addedAny = false;
          src.forEach(x => { if (x !== EPS && add(FIRST, p.head, x)) addedAny = true; });
          if (addedAny) {
            changed = true;
            snap('From ' + p.head + ' -> ' + p.body.join(' ') + ': everything in FIRST(' +
                 s + ') except e goes into FIRST(' + p.head + '), because ' + s +
                 ' can start what ' + p.head + ' derives.', p.head, 'first');
          }
          if (src.indexOf(EPS) === -1) { allEps = false; break; }
        }
        if (allEps && add(FIRST, p.head, EPS)) {
          changed = true;
          snap('Every symbol on the right of ' + p.head + ' -> ' + p.body.join(' ') +
               ' can vanish, so ' + p.head + ' can too: add e to FIRST(' + p.head + ').',
               p.head, 'first');
        }
      });
    }

    add(FOLLOW, G.start, '$');
    snap('FOLLOW starts with the end marker $ in FOLLOW(' + G.start + '), the start ' +
         'symbol, because nothing follows the whole input.', G.start, 'follow');

    changed = true; guard = 0;
    while (changed && guard++ < 60) {
      changed = false;
      G.prods.forEach(p => {
        for (let i = 0; i < p.body.length; i++) {
          const B = p.body[i];
          if (!isNT(G, B)) continue;
          let allEps = true;
          for (let j = i + 1; j < p.body.length; j++) {
            const s = p.body[j];
            const src = isNT(G, s) ? FIRST[s] : [s];
            let addedAny = false;
            src.forEach(x => { if (x !== EPS && add(FOLLOW, B, x)) addedAny = true; });
            if (addedAny) {
              changed = true;
              snap('In ' + p.head + ' -> ' + p.body.join(' ') + ', ' + s + ' comes ' +
                   'right after ' + B + ', so FIRST(' + s + ') minus e goes into FOLLOW(' +
                   B + ').', B, 'follow');
            }
            if (src.indexOf(EPS) === -1) { allEps = false; break; }
          }
          if (allEps) {
            let addedAny = false;
            FOLLOW[p.head].forEach(x => { if (add(FOLLOW, B, x)) addedAny = true; });
            if (addedAny) {
              changed = true;
              snap('In ' + p.head + ' -> ' + p.body.join(' ') + ', nothing after ' + B +
                   ' has to appear, so whatever can follow ' + p.head +
                   ' can follow ' + B + ' too: FOLLOW(' + p.head + ') goes into FOLLOW(' +
                   B + ').', B, 'follow');
            }
          }
        }
      });
    }

    snap('Both sets have stopped changing, so they are complete. FIRST tells a parser ' +
         'which production can begin with the lookahead; FOLLOW tells it when an ' +
         'epsilon production is safe.', null, 'done');
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const G = frame.G;

    const gram = el('div', { class: 'viz-gram' });
    G.prods.forEach(p => gram.appendChild(el('span', { class: 'viz-prod',
      text: p.head + ' -> ' + p.body.join(' ') })));
    host.appendChild(gram);

    const table = el('div', { class: 'viz-results', style: 'margin-top:14px' });
    table.appendChild(el('div', { class: 'viz-rrow head' }, [
      el('span', { text: 'non-terminal' }), el('span', { text: 'FIRST' }),
      el('span', { text: 'FOLLOW' }),
    ]));
    G.nts.forEach(n => {
      table.appendChild(el('div', {
        class: 'viz-rrow' + (n === frame.focus ? ' live' : ''),
      }, [
        el('span', { text: n }),
        el('span', { text: '{ ' + (frame.FIRST[n] || []).join(', ') + ' }' }),
        el('span', { text: '{ ' + (frame.FOLLOW[n] || []).join(', ') + ' }' }),
      ]));
    });
    host.appendChild(table);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(frame.stage === 'first' ? 'computing FIRST'
           : frame.stage === 'follow' ? 'computing FOLLOW' : 'complete',
           frame.stage === 'done' ? 'good' : 'on'),
      chip(G.nts.length + ' non-terminal(s)', 'mono'),
      chip(G.terms.length + ' terminal(s)', 'mono'),
      chip('start ' + G.start, 'mono'),
    ]));
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('cd-firstfollow', {
    title: 'FIRST and FOLLOW',
    subtitle: 'Both sets built one rule at a time until they stop changing, with the ' +
              'production that caused each addition named.',
    glyph: 'R',
    topic: 'parsing-ll',
    note: 'fixed-point computation',
    inputs: [
      { key: 'grammar', label: 'Grammar', hint: '(| for alternatives, e for epsilon)',
        type: 'textarea',
        value: "E -> T E'\nE' -> + T E' | e\nT -> F T'\nT' -> * F T' | e\nF -> ( E ) | id" },
    ],
    build: simulate,
    draw: draw,
  });
})();
