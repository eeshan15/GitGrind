/* ==========================================================================
   Sorting algorithms.

   The bars are the easy part; the counters are the point. Comparisons and swaps
   run in the corner so the difference between an O(n^2) sort and an O(n log n)
   one is a number you can watch grow rather than a claim.

   Try an already-sorted array: insertion sort barely moves, bubble sort with the
   early exit stops after one pass, and quicksort with a first-element pivot has
   its worst case.
   ========================================================================== */
(function () {
  const { el } = GG;

  const ALGOS = {
    bubble:    'Bubble sort (with early exit)',
    selection: 'Selection sort',
    insertion: 'Insertion sort',
    merge:     'Merge sort',
    quick:     'Quicksort (last element as pivot)',
  };

  function simulate(values) {
    const arr = String(values.data || '').split(/[^0-9]+/).filter(Boolean).map(Number);
    if (arr.length < 2) throw new Error('Give at least two numbers.');
    if (arr.length > 16) throw new Error('Sixteen values keeps the bars readable.');
    const algo = values.algo;

    const a = arr.slice();
    const out = [];
    let cmp = 0, swaps = 0;

    const push = (caption, mark, done) => out.push({
      caption, a: a.slice(), mark: mark || {}, cmp, swaps,
      done: done || [], max: Math.max.apply(null, arr),
    });

    push('Starting array. Comparisons and swaps are counted as they happen.', {});

    if (algo === 'bubble') {
      for (let i = 0; i < a.length - 1; i++) {
        let moved = false;
        for (let j = 0; j < a.length - 1 - i; j++) {
          cmp++;
          push('Compare ' + a[j] + ' and ' + a[j + 1] + '.', { cmp: [j, j + 1] },
               range(a.length - i, a.length));
          if (a[j] > a[j + 1]) {
            const t = a[j]; a[j] = a[j + 1]; a[j + 1] = t;
            swaps++;
            moved = true;
            push('Out of order, so swap them. The largest value keeps bubbling right.',
                 { swap: [j, j + 1] }, range(a.length - i, a.length));
          }
        }
        if (!moved) {
          push('A whole pass with no swaps means the array is already sorted, so ' +
               'bubble sort stops early.', {}, range(0, a.length));
          break;
        }
      }
    } else if (algo === 'selection') {
      for (let i = 0; i < a.length - 1; i++) {
        let min = i;
        for (let j = i + 1; j < a.length; j++) {
          cmp++;
          push('Looking for the smallest in the unsorted part: compare ' + a[j] +
               ' against the current smallest ' + a[min] + '.',
               { cmp: [j, min] }, range(0, i));
          if (a[j] < a[min]) min = j;
        }
        if (min !== i) {
          const t = a[i]; a[i] = a[min]; a[min] = t;
          swaps++;
        }
        push('The smallest remaining value is ' + a[i] + ', so it moves to position ' +
             i + '. Selection sort always does exactly one swap per pass.',
             { swap: [i, min] }, range(0, i + 1));
      }
      push('Sorted.', {}, range(0, a.length));
    } else if (algo === 'insertion') {
      for (let i = 1; i < a.length; i++) {
        const key = a[i];
        let j = i - 1;
        push('Take ' + key + ' and slide it left until it sits in the right place.',
             { cmp: [i] }, range(0, i));
        while (j >= 0) {
          cmp++;
          if (a[j] <= key) break;
          a[j + 1] = a[j];
          swaps++;
          push(a[j] + ' is bigger than ' + key + ', so it shifts right.',
               { swap: [j, j + 1] }, range(0, i + 1));
          j--;
        }
        a[j + 1] = key;
        push(key + ' settles at position ' + (j + 1) + '.', { cmp: [j + 1] },
             range(0, i + 1));
      }
    } else if (algo === 'merge') {
      const work = a.slice();
      const sort = (lo, hi, d) => {
        if (hi - lo < 2) return;
        const mid = (lo + hi) >> 1;
        push('Split [' + lo + '..' + (hi - 1) + '] into [' + lo + '..' + (mid - 1) +
             '] and [' + mid + '..' + (hi - 1) + '].', { range: [lo, hi - 1] });
        sort(lo, mid, d + 1);
        sort(mid, hi, d + 1);
        let i = lo, j = mid, k = lo;
        const tmp = [];
        while (i < mid && j < hi) {
          cmp++;
          tmp.push(a[i] <= a[j] ? a[i++] : a[j++]);
        }
        while (i < mid) tmp.push(a[i++]);
        while (j < hi) tmp.push(a[j++]);
        tmp.forEach(v => { a[k++] = v; });
        swaps += tmp.length;
        push('Merge those two sorted halves back together. Merging is where all the ' +
             'work happens - the splitting is free.', { range: [lo, hi - 1] });
      };
      sort(0, a.length, 0);
      push('Sorted. Merge sort did the same amount of work regardless of the input, ' +
           'which is why it is always n log n.', {}, range(0, a.length));
    } else {
      const sort = (lo, hi) => {
        if (lo >= hi) return;
        const pivot = a[hi];
        push('Partition [' + lo + '..' + hi + '] around the pivot ' + pivot + '.',
             { pivot: hi, range: [lo, hi] });
        let i = lo - 1;
        for (let j = lo; j < hi; j++) {
          cmp++;
          push('Is ' + a[j] + ' below the pivot ' + pivot + '?',
               { cmp: [j], pivot: hi, range: [lo, hi] });
          if (a[j] < pivot) {
            i++;
            if (i !== j) {
              const t = a[i]; a[i] = a[j]; a[j] = t;
              swaps++;
              push('Yes, so it moves to the left side.', { swap: [i, j], pivot: hi });
            }
          }
        }
        const t = a[i + 1]; a[i + 1] = a[hi]; a[hi] = t;
        swaps++;
        push('The pivot ' + pivot + ' takes its final place at ' + (i + 1) +
             '. Everything left of it is smaller, everything right is larger.',
             { swap: [i + 1, hi] }, [i + 1]);
        sort(lo, i);
        sort(i + 2, hi);
      };
      sort(0, a.length - 1);
      push('Sorted.', {}, range(0, a.length));
    }

    out.push({
      caption: 'Finished in ' + cmp + ' comparison(s) and ' + swaps +
               ' move(s) for ' + arr.length + ' element(s). ' +
               'For reference, n^2/2 would be ' +
               Math.round(arr.length * arr.length / 2) + ' and n log n about ' +
               Math.round(arr.length * Math.log(arr.length) / Math.LN2) + '.',
      a: a.slice(), mark: {}, cmp, swaps,
      done: range(0, a.length), max: Math.max.apply(null, arr),
    });
    return out;
  }

  const range = (lo, hi) => {
    const r = [];
    for (let i = lo; i < hi; i++) r.push(i);
    return r;
  };

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const n = frame.a.length;
    const W = 640, BW = Math.min(46, (W - 20) / n), Hgt = 190;
    const svg = ns('svg', { viewBox: '0 0 ' + (n * BW + 20) + ' ' + Hgt,
                            class: 'viz-svg', role: 'img', 'aria-label': 'Array' });

    frame.a.forEach((v, i) => {
      const h = Math.max(6, (v / frame.max) * 140);
      const x = 10 + i * BW, y = 160 - h;
      let fill = 'rgba(255,255,255,.14)';
      if (frame.done.indexOf(i) !== -1) fill = 'rgba(63,185,80,.55)';
      if (frame.mark.range && i >= frame.mark.range[0] && i <= frame.mark.range[1]) {
        fill = 'rgba(121,192,255,.3)';
      }
      if (frame.mark.cmp && frame.mark.cmp.indexOf(i) !== -1) fill = '#e8b43e';
      if (frame.mark.swap && frame.mark.swap.indexOf(i) !== -1) fill = '#e5534b';
      if (frame.mark.pivot === i) fill = '#c77dff';

      svg.appendChild(ns('rect', { x: x + 2, y: y, width: BW - 4, height: h,
                                   rx: 3, fill: fill }));
      const t = ns('text', { x: x + BW / 2, y: 176, 'text-anchor': 'middle',
        'font-family': 'ui-monospace, monospace', 'font-size': '11', fill: '#95a1b3' });
      t.textContent = String(v);
      svg.appendChild(t);
    });
    host.appendChild(svg);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip('comparisons ' + frame.cmp, 'mono'),
      chip('moves ' + frame.swaps, 'mono'),
      chip('sorted ' + frame.done.length + '/' + n, 'mono'),
      chip('gold = comparing, red = moving, purple = pivot'),
    ]));
  }

  function ns(tag, attrs) {
    const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.keys(attrs || {}).forEach(k => n.setAttribute(k, attrs[k]));
    return n;
  }
  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('algo-sort', {
    title: 'Sorting algorithms',
    subtitle: 'Five sorts over your own array with comparisons and moves counted. ' +
              'Feed it a sorted array to see best and worst cases diverge.',
    glyph: 'S',
    topic: 'searching-sorting',
    note: 'comparison and move counts',
    inputs: [
      { key: 'algo', label: 'Algorithm', type: 'select', value: 'quick',
        options: Object.keys(ALGOS).map(k => ({ value: k, label: ALGOS[k] })) },
      { key: 'data', label: 'Array', hint: '(space separated)', type: 'text',
        value: '5 2 9 1 7 3' },
    ],
    build: simulate,
    draw: draw,
  });
})();
