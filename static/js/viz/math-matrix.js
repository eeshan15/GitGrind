/* ==========================================================================
   Gaussian elimination.

   Row reduction is a sequence of three moves - swap, scale, subtract - and every
   frame here is exactly one of them, named. The rank falls out at the end as the
   number of non-zero rows, and for a square matrix the determinant comes free
   from the product of the pivots.

   Rows go one per line, numbers separated by spaces.
   ========================================================================== */
(function () {
  const { el } = GG;

  const round = v => (Math.abs(v) < 1e-9 ? 0 : Math.round(v * 1000) / 1000);
  const show = v => {
    const r = round(v);
    return Number.isInteger(r) ? String(r) : r.toFixed(3).replace(/0+$/, '');
  };

  function parse(text) {
    const rows = String(text || '').split(/\n+/).map(l => l.trim()).filter(Boolean)
      .map(l => l.split(/[\s,]+/).filter(Boolean).map(Number));
    if (!rows.length) throw new Error('Give at least one row.');
    const w = rows[0].length;
    rows.forEach((r, i) => {
      if (r.length !== w) throw new Error('Row ' + (i + 1) + ' has ' + r.length +
                                          ' entries but row 1 has ' + w + '.');
      if (r.some(isNaN)) throw new Error('Row ' + (i + 1) + ' has a non-number.');
    });
    if (rows.length > 6 || w > 7) throw new Error('Six rows by seven columns is the limit here.');
    return rows;
  }

  function simulate(values) {
    const M = parse(values.matrix).map(r => r.slice());
    const rref = String(values.mode) === 'rref';
    const rows = M.length, cols = M[0].length;
    const out = [];
    const pivots = [];
    let swaps = 0, detScale = 1;

    const push = (caption, mark) => out.push({
      M: M.map(r => r.map(round)), caption, mark: mark || {},
      pivots: pivots.slice(), rows, cols,
    });

    push('Starting matrix. Row reduction only ever does three things: swap two ' +
         'rows, multiply a row by a non-zero constant, or subtract a multiple of ' +
         'one row from another.');

    let r = 0;
    for (let c = 0; c < cols && r < rows; c++) {
      /* find a pivot */
      let best = -1;
      for (let i = r; i < rows; i++) {
        if (Math.abs(M[i][c]) > 1e-9 && (best === -1 || Math.abs(M[i][c]) > Math.abs(M[best][c]))) {
          best = i;
        }
      }
      if (best === -1) {
        push('Column ' + (c + 1) + ' is all zeros from row ' + (r + 1) +
             ' down, so there is no pivot here. Move to the next column - this is ' +
             'exactly where rank drops below the number of columns.', { col: c });
        continue;
      }

      if (best !== r) {
        const t = M[best]; M[best] = M[r]; M[r] = t;
        swaps++;
        detScale = -detScale;
        push('Swap rows ' + (r + 1) + ' and ' + (best + 1) + ' to bring the largest ' +
             'entry in column ' + (c + 1) + ' to the pivot position. Each swap flips ' +
             'the sign of the determinant.', { row: r, col: c });
      }

      const p = M[r][c];
      if (rref && Math.abs(p - 1) > 1e-9) {
        detScale *= p;
        for (let j = 0; j < cols; j++) M[r][j] /= p;
        push('Divide row ' + (r + 1) + ' by its pivot ' + show(p) +
             ' so the pivot becomes 1.', { row: r, col: c });
      }

      const start = rref ? 0 : r + 1;
      for (let i = start; i < rows; i++) {
        if (i === r) continue;
        if (Math.abs(M[i][c]) < 1e-9) continue;
        const f = M[i][c] / M[r][c];
        for (let j = 0; j < cols; j++) M[i][j] -= f * M[r][j];
        push('Row ' + (i + 1) + ' <- row ' + (i + 1) + ' - (' + show(f) + ') x row ' +
             (r + 1) + ', which clears the entry in column ' + (c + 1) + '.',
             { row: i, col: c });
      }

      pivots.push({ r, c });
      r++;
    }

    const rank = pivots.length;
    const nonZero = M.filter(row => row.some(v => Math.abs(v) > 1e-9)).length;
    let det = null;
    if (rows === cols) {
      det = rank < rows ? 0
        : pivots.reduce((a, p) => a * M[p.r][p.c], 1) * detScale * (rref ? 1 : 1);
      if (rref) det = rank < rows ? 0 : detScale;
    }

    push('Done. ' + rank + ' pivot(s), so the rank is ' + rank +
         '. That equals the number of non-zero rows (' + nonZero + '), and the ' +
         'nullity is ' + (cols - rank) + ' by rank-nullity.' +
         (det !== null ? ' The matrix is square, and the determinant is ' +
                         show(det) + '.' : ''));
    out[out.length - 1].rank = rank;
    out[out.length - 1].det = det;
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const grid = el('div', { class: 'viz-matrix' });
    frame.M.forEach((row, i) => {
      const r = el('div', {
        class: 'viz-mrow' + (frame.mark.row === i ? ' at' : '') +
               (frame.pivots.some(p => p.r === i) ? ' pivotrow' : ''),
      });
      row.forEach((v, j) => {
        r.appendChild(el('span', {
          class: 'viz-mcell' + (frame.mark.col === j ? ' col' : '') +
                 (frame.pivots.some(p => p.r === i && p.c === j) ? ' pivot' : '') +
                 (Math.abs(v) < 1e-9 ? ' zero' : ''),
          text: show(v),
        }));
      });
      grid.appendChild(r);
    });
    host.appendChild(grid);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip(frame.rows + ' x ' + frame.cols, 'mono'),
      chip('pivots ' + frame.pivots.length, 'mono'),
      frame.rank !== undefined ? chip('rank ' + frame.rank, 'good') : chip(''),
      frame.det !== undefined && frame.det !== null
        ? chip('det ' + show(frame.det), 'mono') : chip(''),
    ]));
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('math-matrix', {
    title: 'Gaussian elimination',
    subtitle: 'Row reduce a matrix one operation at a time and read off the rank, ' +
              'nullity and determinant at the end.',
    glyph: 'M',
    topic: 'matrices',
    note: 'rank, nullity, determinant',
    inputs: [
      { key: 'mode', label: 'Reduce to', type: 'select', value: 'ref',
        options: [{ value: 'ref', label: 'Row echelon form (forward elimination)' },
                  { value: 'rref', label: 'Reduced row echelon form' }] },
      { key: 'matrix', label: 'Matrix', hint: '(one row per line)', type: 'textarea',
        value: '2 1 -1 8\n-3 -1 2 -11\n-2 1 2 -3' },
    ],
    build: simulate,
    draw: draw,
  });
})();
