/* ==========================================================================
   Normalisation.

   Everything follows from attribute closure, so that is computed first and shown
   step by step. Candidate keys come from closures; the normal form then falls out
   of testing every functional dependency against those keys.

   Format:
       R: A B C D E
       A B -> C
       C -> D
   ========================================================================== */
(function () {
  const { el } = GG;

  function parse(text) {
    let attrs = [];
    const fds = [];
    String(text || '').split(/\n+/).map(l => l.trim()).filter(Boolean).forEach((l, i) => {
      let m = l.match(/^R\s*:\s*(.+)$/i);
      if (m) { attrs = m[1].split(/[\s,]+/).filter(Boolean); return; }
      m = l.match(/^(.+?)\s*(?:->|=>)\s*(.+)$/);
      if (!m) throw new Error('Line ' + (i + 1) + ': expected "R: A B C" or "A B -> C".');
      fds.push({
        lhs: m[1].split(/[\s,]+/).filter(Boolean),
        rhs: m[2].split(/[\s,]+/).filter(Boolean),
      });
    });
    if (!attrs.length) throw new Error('Start with a relation line, e.g. "R: A B C D".');
    if (!fds.length) throw new Error('Add at least one functional dependency.');
    if (attrs.length > 8) throw new Error('Eight attributes keeps the key search quick.');
    return { attrs, fds };
  }

  const has = (set, xs) => xs.every(x => set.indexOf(x) !== -1);
  const key = xs => xs.slice().sort().join('');

  function closure(start, fds, trace) {
    const out = start.slice();
    let go = true;
    while (go) {
      go = false;
      fds.forEach(f => {
        if (!has(out, f.lhs)) return;
        const added = f.rhs.filter(r => out.indexOf(r) === -1);
        if (!added.length) return;
        added.forEach(r => out.push(r));
        go = true;
        if (trace) trace.push({ fd: f, added: added.slice(), now: out.slice() });
      });
    }
    return out;
  }

  function subsets(arr, size) {
    const res = [];
    (function pick(start, cur) {
      if (cur.length === size) { res.push(cur.slice()); return; }
      for (let i = start; i < arr.length; i++) { cur.push(arr[i]); pick(i + 1, cur); cur.pop(); }
    })(0, []);
    return res;
  }

  function simulate(values) {
    const R = parse(values.schema);
    const out = [];
    const base = { R, closureOf: null, trace: [], keys: [], prime: [], nf: null, why: [] };

    out.push(Object.assign({}, base, {
      caption: 'Relation R(' + R.attrs.join(', ') + ') with ' + R.fds.length +
               ' functional dependenc(ies). Everything below is derived from ' +
               'attribute closure, so that comes first.',
    }));

    /* demonstrate one closure in detail */
    const demo = R.fds[0].lhs;
    const trace = [];
    const cl = closure(demo, R.fds, trace);
    out.push(Object.assign({}, base, {
      closureOf: demo, trace: [], 
      caption: 'Take {' + demo.join(', ') + '}+. Start with the attributes themselves ' +
               'and keep applying any dependency whose left side is already inside.',
    }));
    trace.forEach((t, i) => {
      out.push(Object.assign({}, base, {
        closureOf: demo, trace: trace.slice(0, i + 1),
        caption: t.fd.lhs.join('') + ' -> ' + t.fd.rhs.join('') +
                 ' applies because {' + t.fd.lhs.join(', ') + '} is already in the ' +
                 'closure, so ' + t.added.join(', ') + ' joins it. Closure is now {' +
                 t.now.join(', ') + '}.',
      }));
    });
    out.push(Object.assign({}, base, {
      closureOf: demo, trace,
      caption: '{' + demo.join(', ') + '}+ = {' + cl.join(', ') + '}' +
               (cl.length === R.attrs.length
                 ? ', which is every attribute - so this is a superkey.'
                 : ', which is not everything, so this is not a superkey on its own.'),
    }));

    /* candidate keys: smallest attribute sets whose closure is everything */
    const keys = [];
    for (let size = 1; size <= R.attrs.length; size++) {
      subsets(R.attrs, size).forEach(s => {
        if (keys.some(k => has(s, k))) return;          /* not minimal */
        if (closure(s, R.fds).length === R.attrs.length) keys.push(s);
      });
      if (keys.length) break;
    }
    /* also catch larger minimal keys the size sweep missed */
    for (let size = keys.length ? keys[0].length + 1 : 1; size <= R.attrs.length; size++) {
      subsets(R.attrs, size).forEach(s => {
        if (keys.some(k => has(s, k))) return;
        if (closure(s, R.fds).length === R.attrs.length) keys.push(s);
      });
    }

    const prime = [];
    keys.forEach(k => k.forEach(a => { if (prime.indexOf(a) === -1) prime.push(a); }));

    out.push(Object.assign({}, base, {
      keys, prime,
      caption: keys.length
        ? 'Candidate key(s): ' + keys.map(k => '{' + k.join(', ') + '}').join(', ') +
          '. Prime attributes (those in some key): ' + prime.join(', ') + '.'
        : 'No candidate key found, which means the dependencies do not determine every ' +
          'attribute.',
    }));

    /* normal form */
    const why = [];
    let bcnf = true, third = true, second = true;

    R.fds.forEach(f => {
      const lhsClosure = closure(f.lhs, R.fds);
      const superkey = lhsClosure.length === R.attrs.length;
      const nonTrivial = f.rhs.some(r => f.lhs.indexOf(r) === -1);
      if (!nonTrivial) return;

      if (!superkey) {
        bcnf = false;
        const rhsAllPrime = f.rhs.every(r => prime.indexOf(r) !== -1 ||
                                             f.lhs.indexOf(r) !== -1);
        if (!rhsAllPrime) {
          third = false;
          why.push(f.lhs.join('') + ' -> ' + f.rhs.join('') + ' breaks 3NF: the left ' +
                   'side is not a superkey and the right side is not prime.');
          const partial = keys.some(k => has(k, f.lhs) && f.lhs.length < k.length);
          if (partial) {
            second = false;
            why.push('It is also a partial dependency - ' + f.lhs.join('') +
                     ' is only part of a candidate key - so it breaks 2NF as well.');
          }
        } else {
          why.push(f.lhs.join('') + ' -> ' + f.rhs.join('') + ' breaks BCNF (left side ' +
                   'is not a superkey) but survives 3NF, because the right side is prime.');
        }
      }
    });

    const nf = bcnf ? 'BCNF' : third ? '3NF' : second ? '2NF' : '1NF';
    out.push(Object.assign({}, base, {
      keys, prime, nf, why,
      caption: why.length
        ? 'Highest normal form: ' + nf + '. ' + why.join(' ')
        : 'Every non-trivial dependency has a superkey on the left, so R is already ' +
          'in BCNF.',
    }));
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const R = frame.R;

    const g = el('div', { class: 'viz-gram' });
    g.appendChild(el('span', { class: 'viz-prod',
      text: 'R(' + R.attrs.join(', ') + ')' }));
    R.fds.forEach(f => g.appendChild(el('span', { class: 'viz-prod',
      text: f.lhs.join('') + ' -> ' + f.rhs.join('') })));
    host.appendChild(g);

    if (frame.closureOf) {
      const now = frame.trace.length
        ? frame.trace[frame.trace.length - 1].now : frame.closureOf;
      const strip = el('div', { class: 'viz-closure' });
      R.attrs.forEach(a => strip.appendChild(el('span', {
        class: 'viz-attr' + (now.indexOf(a) !== -1 ? ' in' : '') +
               (frame.closureOf.indexOf(a) !== -1 ? ' seed' : ''),
        text: a,
      })));
      host.appendChild(el('p', { class: 'dim small', style: 'margin:14px 0 6px' },
        ['{' + frame.closureOf.join(', ') + '}+']));
      host.appendChild(strip);
    }

    if (frame.keys.length) {
      const t = el('div', { class: 'viz-results', style: 'margin-top:14px' });
      t.appendChild(el('div', { class: 'viz-rrow head' }, [
        el('span', { text: 'candidate keys' }), el('span', { text: 'prime attributes' }),
      ]));
      t.appendChild(el('div', { class: 'viz-rrow' }, [
        el('span', { text: frame.keys.map(k => '{' + k.join('') + '}').join('  ') }),
        el('span', { text: frame.prime.join(', ') }),
      ]));
      host.appendChild(t);
    }

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(R.attrs.length + ' attribute(s)', 'mono'),
      chip(R.fds.length + ' dependenc(ies)', 'mono'),
      frame.nf ? chip('highest normal form: ' + frame.nf,
                      frame.nf === 'BCNF' ? 'good' : 'bad') : chip(''),
    ]));
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('dbms-normal', {
    title: 'Normalisation',
    subtitle: 'Attribute closure step by step, then candidate keys, then the highest ' +
              'normal form with the offending dependency named.',
    glyph: 'F',
    topic: 'normalization',
    note: 'closure, keys, 2NF/3NF/BCNF',
    inputs: [
      { key: 'schema', label: 'Relation and dependencies', type: 'textarea',
        hint: '(R: A B C, then A -> B)',
        value: 'R: A B C D E\nA -> B C\nC D -> E\nB -> D\nE -> A' },
    ],
    build: simulate,
    draw: draw,
  });
})();
