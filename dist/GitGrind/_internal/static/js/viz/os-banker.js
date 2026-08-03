/* ==========================================================================
   Banker's algorithm.

   Safety is not a property of the allocation table on its own - it is a question
   about whether some order exists in which everybody can finish. So the frames
   walk that search: available resources, who can be satisfied right now, and
   what is released when they finish.

   If no process can proceed and some still need resources, the state is unsafe,
   and the frame says which processes are stuck and what they were short of.
   ========================================================================== */
(function () {
  const { el } = GG;

  function grid(rows, cols, label) {
    return rows.map((r, i) => {
      if (r.length !== cols) {
        throw new Error(label + ': row ' + (i + 1) + ' has ' + r.length +
                        ' number(s), expected ' + cols + '.');
      }
      return r.slice();
    });
  }

  function parseMatrix(text, label) {
    const rows = String(text || '').split(/\n+/).map(l => l.trim()).filter(Boolean)
      .map(l => l.split(/[\s,]+/).filter(Boolean).map(Number));
    if (!rows.length) throw new Error(label + ' is empty.');
    if (rows.some(r => r.some(isNaN))) throw new Error(label + ' has a non-number in it.');
    return rows;
  }

  function simulate(values) {
    const alloc = parseMatrix(values.allocation, 'Allocation');
    const maxm = parseMatrix(values.maximum, 'Maximum');
    const avail = parseMatrix(values.available, 'Available')[0];

    const n = alloc.length, m = avail.length;
    if (maxm.length !== n) throw new Error('Allocation has ' + n + ' process(es) but ' +
                                           'Maximum has ' + maxm.length + '.');
    grid(alloc, m, 'Allocation');
    grid(maxm, m, 'Maximum');

    const need = alloc.map((row, i) => row.map((v, j) => {
      const d = maxm[i][j] - v;
      if (d < 0) throw new Error('Process P' + i + ' already holds more of resource ' +
                                 j + ' than its maximum.');
      return d;
    }));

    const work = avail.slice();
    const finish = new Array(n).fill(false);
    const order = [];
    const out = [];

    const push = (caption, focus) => out.push({
      caption, focus, n, m,
      alloc: alloc.map(r => r.slice()),
      maxm: maxm.map(r => r.slice()),
      need: need.map(r => r.slice()),
      work: work.slice(), finish: finish.slice(), order: order.slice(),
      safe: null,
    });

    push('Need = Maximum - Allocation, computed for every process. Available is ' +
         work.join(' ') + '. The question is whether some order lets all ' + n +
         ' process(es) finish.', -1);

    let guard = 0;
    while (order.length < n && guard++ < n * n + 5) {
      let picked = -1;
      for (let i = 0; i < n; i++) {
        if (finish[i]) continue;
        if (need[i].every((v, j) => v <= work[j])) { picked = i; break; }
      }

      if (picked === -1) {
        const stuck = [];
        for (let i = 0; i < n; i++) {
          if (finish[i]) continue;
          const short = [];
          need[i].forEach((v, j) => { if (v > work[j]) short.push('R' + j); });
          stuck.push('P' + i + ' is short of ' + short.join(', '));
        }
        push('No remaining process can be satisfied from ' + work.join(' ') + '. ' +
             stuck.join('; ') + '. The state is UNSAFE - there is no order in which ' +
             'everyone finishes, so this request must not be granted.', -1);
        out[out.length - 1].safe = false;
        return out;
      }

      push('P' + picked + ' needs ' + need[picked].join(' ') + ' and available is ' +
           work.join(' '), picked);
      out[out.length - 1].caption += ', so it can run to completion.';

      need[picked].forEach((v, j) => { work[j] += alloc[picked][j]; });
      finish[picked] = true;
      order.push(picked);

      push('P' + picked + ' finishes and releases everything it held (' +
           alloc[picked].join(' ') + '). Available becomes ' + work.join(' ') + '.',
           picked);
    }

    push('Every process finished. The state is SAFE, and one safe sequence is ' +
         order.map(i => 'P' + i).join(' -> ') + '. Others may exist; one is enough.', -1);
    out[out.length - 1].safe = true;
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const cols = [];
    for (let j = 0; j < frame.m; j++) cols.push('R' + j);

    const table = el('div', { class: 'viz-bank' });
    const head = el('div', { class: 'viz-brow head' });
    head.appendChild(el('span', { class: 'viz-bp', text: '' }));
    ['Allocation', 'Maximum', 'Need'].forEach(g =>
      head.appendChild(el('span', { class: 'viz-bg', text: g })));
    head.appendChild(el('span', { class: 'viz-bp', text: '' }));
    table.appendChild(head);

    const sub = el('div', { class: 'viz-brow head' });
    sub.appendChild(el('span', { class: 'viz-bp', text: 'process' }));
    for (let g = 0; g < 3; g++) {
      sub.appendChild(el('span', { class: 'viz-bg mono', text: cols.join(' ') }));
    }
    sub.appendChild(el('span', { class: 'viz-bp', text: 'state' }));
    table.appendChild(sub);

    for (let i = 0; i < frame.n; i++) {
      const row = el('div', { class: 'viz-brow' + (i === frame.focus ? ' at' : '') +
                                     (frame.finish[i] ? ' done' : '') });
      row.appendChild(el('span', { class: 'viz-bp mono', text: 'P' + i }));
      [frame.alloc[i], frame.maxm[i], frame.need[i]].forEach(v =>
        row.appendChild(el('span', { class: 'viz-bg mono', text: v.join(' ') })));
      row.appendChild(el('span', { class: 'viz-bp small',
        text: frame.finish[i] ? 'finished' : 'waiting' }));
      table.appendChild(row);
    }
    host.appendChild(table);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip('available ' + frame.work.join(' '), 'on'),
      chip('finished ' + frame.order.length + '/' + frame.n, 'mono'),
      frame.order.length
        ? chip('sequence ' + frame.order.map(i => 'P' + i).join(' -> '), 'mono')
        : chip(''),
      frame.safe === null ? chip('')
        : chip(frame.safe ? 'SAFE' : 'UNSAFE', frame.safe ? 'good' : 'bad'),
    ]));
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('os-banker', {
    title: "Banker's algorithm",
    subtitle: 'Work out whether a state is safe by finding an order in which every ' +
              'process can finish. If none exists, the frames say who is stuck and why.',
    glyph: 'K',
    topic: 'deadlock',
    note: 'safe sequence or proof of none',
    inputs: [
      { key: 'available', label: 'Available', hint: '(one row)', type: 'text',
        value: '3 3 2' },
      { key: 'allocation', label: 'Allocation', hint: '(one row per process)',
        type: 'textarea', value: '0 1 0\n2 0 0\n3 0 2\n2 1 1\n0 0 2' },
      { key: 'maximum', label: 'Maximum', hint: '(one row per process)',
        type: 'textarea', value: '7 5 3\n3 2 2\n9 0 2\n2 2 2\n4 3 3' },
    ],
    build: simulate,
    draw: draw,
  });
})();
