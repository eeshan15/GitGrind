/* ==========================================================================
   LL(1) parsing.

   The table is built from FIRST and FOLLOW, then the stack is driven through an
   input string one move at a time. Two conflicting entries in the same cell mean
   the grammar is not LL(1), and the frame says which productions clashed - that
   is usually the actual exam question.

   Same grammar format as the FIRST/FOLLOW visualiser.
   ========================================================================== */
(function () {
  const { el } = GG;
  const EPS = 'e', END = '$';

  function parseGrammar(text) {
    const prods = [];
    const nts = [];
    String(text || '').split(/\n+/).map(l => l.trim()).filter(Boolean).forEach((line, i) => {
      const m = line.match(/^(\S+)\s*(?:->|=>|:)\s*(.*)$/);
      if (!m) throw new Error('Line ' + (i + 1) + ': expected "A -> alpha".');
      if (nts.indexOf(m[1]) === -1) nts.push(m[1]);
      m[2].split('|').forEach(alt => {
        const syms = alt.trim().split(/\s+/).filter(Boolean);
        prods.push({ head: m[1], body: syms.length ? syms : [EPS] });
      });
    });
    if (!prods.length) throw new Error('Write at least one production.');
    const terms = [];
    prods.forEach(p => p.body.forEach(s => {
      if (s !== EPS && nts.indexOf(s) === -1 && terms.indexOf(s) === -1) terms.push(s);
    }));
    return { prods, nts, terms, start: prods[0].head };
  }

  function sets(G) {
    const isNT = s => G.nts.indexOf(s) !== -1;
    const FIRST = {}, FOLLOW = {};
    G.nts.forEach(n => { FIRST[n] = []; FOLLOW[n] = []; });
    const add = (S, k, v) => (S[k].indexOf(v) === -1 ? (S[k].push(v), true) : false);
    const firstOf = s => (isNT(s) ? FIRST[s] : [s]);

    let go = true, guard = 0;
    while (go && guard++ < 80) {
      go = false;
      G.prods.forEach(p => {
        if (p.body[0] === EPS) { if (add(FIRST, p.head, EPS)) go = true; return; }
        let allEps = true;
        for (const s of p.body) {
          firstOf(s).forEach(x => { if (x !== EPS && add(FIRST, p.head, x)) go = true; });
          if (firstOf(s).indexOf(EPS) === -1) { allEps = false; break; }
        }
        if (allEps && add(FIRST, p.head, EPS)) go = true;
      });
    }

    add(FOLLOW, G.start, END);
    go = true; guard = 0;
    while (go && guard++ < 80) {
      go = false;
      G.prods.forEach(p => {
        for (let i = 0; i < p.body.length; i++) {
          const B = p.body[i];
          if (!isNT(B)) continue;
          let allEps = true;
          for (let j = i + 1; j < p.body.length; j++) {
            firstOf(p.body[j]).forEach(x => {
              if (x !== EPS && add(FOLLOW, B, x)) go = true;
            });
            if (firstOf(p.body[j]).indexOf(EPS) === -1) { allEps = false; break; }
          }
          if (allEps) FOLLOW[p.head].forEach(x => { if (add(FOLLOW, B, x)) go = true; });
        }
      });
    }

    /* FIRST of a string of symbols */
    const firstSeq = body => {
      const r = [];
      let allEps = true;
      for (const s of body) {
        if (s === EPS) continue;
        firstOf(s).forEach(x => { if (x !== EPS && r.indexOf(x) === -1) r.push(x); });
        if (firstOf(s).indexOf(EPS) === -1) { allEps = false; break; }
      }
      if (allEps) r.push(EPS);
      return r;
    };
    return { FIRST, FOLLOW, firstSeq };
  }

  function simulate(values) {
    const G = parseGrammar(values.grammar);
    const { FIRST, FOLLOW, firstSeq } = sets(G);

    const table = {};
    const conflicts = [];
    G.nts.forEach(n => { table[n] = {}; });

    G.prods.forEach(p => {
      const f = firstSeq(p.body);
      const cols = f.filter(x => x !== EPS);
      if (f.indexOf(EPS) !== -1) FOLLOW[p.head].forEach(x => {
        if (cols.indexOf(x) === -1) cols.push(x);
      });
      cols.forEach(t => {
        if (table[p.head][t] && table[p.head][t] !== p) {
          conflicts.push({ nt: p.head, t, a: table[p.head][t], b: p });
        } else {
          table[p.head][t] = p;
        }
      });
    });

    const cols = G.terms.concat([END]);
    const out = [];
    const base = { G, FIRST, FOLLOW, table, cols, conflicts, stack: [], input: [], at: 0 };

    out.push(Object.assign({}, base, {
      caption: 'The parse table: for A -> alpha, the entry M[A, t] is set for every t ' +
               'in FIRST(alpha), and if alpha can vanish, for every t in FOLLOW(A) too.',
    }));

    if (conflicts.length) {
      const c = conflicts[0];
      out.push(Object.assign({}, base, {
        caption: 'M[' + c.nt + ', ' + c.t + '] wants two productions at once: ' +
                 c.a.head + ' -> ' + c.a.body.join(' ') + ' and ' +
                 c.b.head + ' -> ' + c.b.body.join(' ') + '. A single lookahead ' +
                 'cannot choose between them, so this grammar is NOT LL(1). Left ' +
                 'factoring or removing left recursion usually fixes it.',
      }));
      return out;
    }

    const input = String(values.input || '').trim().split(/\s+/).filter(Boolean).concat([END]);
    const stack = [END, G.start];
    let at = 0, guard = 0;

    const push = caption => out.push(Object.assign({}, base, {
      caption, stack: stack.slice(), input, at,
    }));

    push('Stack holds ' + stack.slice().reverse().join(' ') + ' with the start symbol ' +
         'on top; the input is ' + input.join(' ') + '.');

    while (stack.length && guard++ < 200) {
      const top = stack[stack.length - 1];
      const look = input[at];

      if (top === END && look === END) {
        stack.pop();
        push('Stack and input both reduce to $, so the string is ACCEPTED.');
        out[out.length - 1].accepted = true;
        return out;
      }
      if (G.nts.indexOf(top) === -1) {
        if (top === look) {
          stack.pop(); at++;
          push('Top of stack is the terminal ' + top + ' and the lookahead matches, ' +
               'so both are consumed.');
        } else {
          push('Top of stack is ' + top + ' but the lookahead is ' + look +
               '. They do not match, so the string is REJECTED.');
          out[out.length - 1].accepted = false;
          return out;
        }
        continue;
      }

      const p = table[top][look];
      if (!p) {
        push('M[' + top + ', ' + look + '] is empty - no production can start with ' +
             look + ' here, so the string is REJECTED.');
        out[out.length - 1].accepted = false;
        return out;
      }
      stack.pop();
      if (p.body[0] !== EPS) {
        for (let i = p.body.length - 1; i >= 0; i--) stack.push(p.body[i]);
      }
      push('Lookahead ' + look + ' selects ' + p.head + ' -> ' + p.body.join(' ') +
           '. Pop ' + top + ' and push the right side in reverse so the leftmost ' +
           'symbol ends up on top.');
    }

    push('The parser ran too long, which means the grammar loops on this input.');
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const G = frame.G;

    const table = el('div', { class: 'viz-results' });
    const head = el('div', { class: 'viz-rrow head' });
    head.appendChild(el('span', { text: '' }));
    frame.cols.forEach(c => head.appendChild(el('span', { text: c })));
    table.appendChild(head);

    G.nts.forEach(n => {
      const row = el('div', { class: 'viz-rrow' });
      row.appendChild(el('span', { text: n }));
      frame.cols.forEach(c => {
        const p = frame.table[n][c];
        const bad = frame.conflicts.some(x => x.nt === n && x.t === c);
        const cell = el('span', { text: p ? p.head + '->' + p.body.join('') : '' });
        if (bad) cell.style.color = 'var(--bad)';
        row.appendChild(cell);
      });
      table.appendChild(row);
    });
    host.appendChild(table);

    if (frame.input.length) {
      const trace = el('div', { class: 'viz-trace' }, [
        el('div', {}, [
          el('span', { class: 'k', text: 'stack' }),
          el('span', { class: 'v mono', text: frame.stack.slice().reverse().join(' ') }),
        ]),
        el('div', {}, [
          el('span', { class: 'k', text: 'input' }),
          el('span', { class: 'v mono',
                       text: frame.input.slice(frame.at).join(' ') }),
        ]),
      ]);
      host.appendChild(trace);
    }

    host.appendChild(el('div', { class: 'viz-state' }, [
      frame.conflicts.length
        ? chip(frame.conflicts.length + ' conflict(s) - not LL(1)', 'bad')
        : chip('conflict free', 'good'),
      frame.accepted === true ? chip('ACCEPTED', 'good')
        : frame.accepted === false ? chip('REJECTED', 'bad') : chip(''),
    ]));
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('cd-ll1', {
    title: 'LL(1) parsing',
    subtitle: 'Build the parse table from FIRST and FOLLOW, then drive the stack ' +
              'through an input. Conflicting cells are named, not just flagged.',
    glyph: 'L',
    topic: 'parsing-ll',
    note: 'parse table, stack trace, conflicts',
    inputs: [
      { key: 'grammar', label: 'Grammar', hint: '(| for alternatives, e for epsilon)',
        type: 'textarea',
        value: "E -> T E'\nE' -> + T E' | e\nT -> F T'\nT' -> * F T' | e\nF -> ( E ) | id" },
      { key: 'input', label: 'Input', hint: '(space separated tokens)', type: 'text',
        value: 'id + id * id' },
    ],
    build: simulate,
    draw: draw,
  });
})();
