/* ==========================================================================
   Sliding window: Go-Back-N and Selective Repeat.

   The difference between the two only shows up when something is lost, so the
   lost-frames box is the point of the whole thing: drop frame 2 and watch GBN
   throw away 3, 4 and 5 as well while Selective Repeat keeps them.

   Time is in round-trip ticks, not seconds, which is how the exam counts it.
   ========================================================================== */
(function () {
  const { el } = GG;

  const MODES = {
    gbn: 'Go-Back-N (cumulative ACK, discard out of order)',
    sr:  'Selective Repeat (individual ACK, buffer out of order)',
  };

  function parseLost(text, total) {
    const set = {};
    String(text || '').split(/[^0-9]+/).filter(Boolean).forEach(t => {
      const n = Number(t);
      if (n >= 0 && n < total) set[n] = true;
    });
    return set;
  }

  function simulate(values) {
    const total = Math.max(1, Math.min(16, values.total | 0));
    const win = Math.max(1, Math.min(total, values.window | 0));
    const timeout = Math.max(2, Math.min(12, values.timeout | 0));
    const mode = values.mode;
    const willDrop = parseLost(values.lost, total);

    /* One tick is one propagation step. A frame put on the wire at tick t either
       arrives at t+1 or is lost; an acknowledgement takes another tick. That is
       coarse, but it is the same granularity the exam uses when it counts
       "how many transmissions did this take". */
    const state = new Array(total).fill('pending');   /* pending|sent|acked|lost */
    const sentAt = new Array(total).fill(-1);
    const buffered = {};
    let base = 0, expected = 0, delivered = 0, sends = 0, t = 0;

    const out = [];
    const push = caption => out.push({
      caption, t, base, win, total, mode,
      state: state.slice(),
      buffered: Object.keys(buffered).map(Number),
      delivered, sends,
    });

    push('Window covers frames ' + base + ' to ' + (Math.min(base + win, total) - 1) +
         '. Nothing has been sent yet.');

    let guard = 0;
    while (delivered < total && guard++ < 500) {
      /* 1. fill the window */
      const justSent = [];
      for (let i = base; i < Math.min(base + win, total); i++) {
        if (state[i] !== 'pending') continue;
        state[i] = 'sent';
        sentAt[i] = t;
        sends++;
        justSent.push(i);
      }
      if (justSent.length) {
        push('Sent frame' + (justSent.length > 1 ? 's ' : ' ') + justSent.join(', ') +
             '. The window allows ' + win + ' unacknowledged frame(s) at once.');
      }

      t++;

      /* 2. everything in flight either arrives or is lost */
      for (let i = base; i < Math.min(base + win, total); i++) {
        if (state[i] !== 'sent' || sentAt[i] !== t - 1) continue;

        if (willDrop[i]) {
          delete willDrop[i];                       /* lost only the first time */
          state[i] = 'lost';
          push('Frame ' + i + ' is lost in transit. No acknowledgement comes back, ' +
               'so the sender can only find out by timing out.');
          continue;
        }

        if (i === expected) {
          state[i] = 'acked';
          expected++;
          delivered++;
          let extra = 0;
          if (mode === 'sr') {
            while (buffered[expected]) {
              delete buffered[expected];
              state[expected] = 'acked';
              expected++;
              delivered++;
              extra++;
            }
          }
          push('Frame ' + i + ' arrives in order and is acknowledged' +
               (extra ? ', releasing ' + extra + ' buffered frame(s) behind it' : '') +
               '.');
        } else if (mode === 'gbn') {
          state[i] = 'pending';                     /* discarded, will be resent */
          push('Frame ' + i + ' arrives, but the receiver still wants ' + expected +
               '. Go-Back-N discards anything out of order, so this frame is thrown ' +
               'away even though it made it across.');
        } else {
          buffered[i] = true;
          state[i] = 'acked';                       /* individually acknowledged */
          push('Frame ' + i + ' arrives out of order. Selective Repeat buffers it and ' +
               'acknowledges it individually, so it never needs sending again.');
        }
      }

      /* 3. the window slides over everything acknowledged from the base */
      let moved = 0;
      while (base < total && state[base] === 'acked' &&
             (mode === 'gbn' ? base < expected : true) && !buffered[base]) {
        base++;
        moved++;
      }
      if (moved) {
        push('The window slides to ' + base + '. It now covers ' + base + ' to ' +
             (Math.min(base + win, total) - 1) + '.');
      }

      /* 4. timeout on the oldest unacknowledged frame */
      if (base < total && state[base] === 'lost' && t - sentAt[base] >= timeout) {
        if (mode === 'gbn') {
          let n = 0;
          for (let i = base; i < Math.min(base + win, total); i++) {
            if (state[i] === 'acked') continue;
            state[i] = 'pending';
            n++;
          }
          push('Timeout on frame ' + base + '. Go-Back-N resends it and the ' +
               (n - 1) + ' frame(s) after it, because the receiver threw those away.');
        } else {
          state[base] = 'pending';
          push('Timeout on frame ' + base + '. Selective Repeat resends only that ' +
               'frame; everything already buffered stays put.');
        }
      }
    }

    out.push({
      caption: 'All ' + total + ' frames delivered in ' + t + ' tick(s) using ' +
               sends + ' transmission(s). ' +
               (sends > total ? (sends - total) + ' of those were retransmissions.'
                              : 'No retransmissions were needed.'),
      t, base, win, total, mode,
      state: state.slice(), buffered: [], delivered, sends,
    });
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  const CLS = { pending: '', sent: ' sent', acked: ' acked', lost: ' lost' };

  function draw(host, frame) {
    const strip = el('div', { class: 'viz-win' });
    for (let i = 0; i < frame.total; i++) {
      const inWindow = i >= frame.base && i < frame.base + frame.win;
      strip.appendChild(el('span', {
        class: 'viz-fr' + CLS[frame.state[i]] + (inWindow ? ' inwin' : '') +
               (frame.buffered.indexOf(i) !== -1 ? ' buf' : ''),
        text: String(i),
        title: frame.state[i],
      }));
    }
    host.appendChild(strip);

    host.appendChild(el('div', { class: 'viz-winbar' }, [
      el('span', { class: 'dim small',
                   text: 'window covers ' + frame.base + ' .. ' +
                         Math.min(frame.base + frame.win, frame.total) - 1 }),
    ]));

    host.appendChild(el('div', { class: 'viz-legend' }, [
      key('', 'not sent'), key('sent', 'in flight'), key('acked', 'acknowledged'),
      key('lost', 'lost'), key('buf', 'buffered'),
    ]));

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip('tick ' + frame.t, 'mono'),
      chip('delivered ' + frame.delivered + '/' + frame.total, 'mono'),
      chip('transmissions ' + frame.sends, 'mono'),
      chip(frame.mode === 'gbn' ? 'Go-Back-N' : 'Selective Repeat', 'on'),
    ]));
  }

  const key = (cls, label) => el('span', { class: 'viz-key' }, [
    el('i', { class: 'viz-fr ' + cls }), label,
  ]);
  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('cn-window', {
    title: 'Sliding window',
    subtitle: 'Go-Back-N versus Selective Repeat on the same losses. Drop a frame ' +
              'and watch how differently the two protocols recover.',
    glyph: 'W',
    topic: 'sliding-window',
    note: 'loss, timeout, retransmission',
    inputs: [
      { key: 'mode', label: 'Protocol', type: 'select', value: 'gbn',
        options: Object.keys(MODES).map(k => ({ value: k, label: MODES[k] })) },
      { key: 'window', label: 'Window size', type: 'number', value: 4, min: 1, max: 15 },
      { key: 'total', label: 'Frames to send', type: 'number', value: 8, min: 1, max: 16 },
      { key: 'timeout', label: 'Timeout', hint: '(ticks)', type: 'number',
        value: 3, min: 2, max: 12 },
      { key: 'lost', label: 'Lost frames', hint: '(space separated)', type: 'text',
        value: '2' },
    ],
    build: simulate,
    draw: draw,
  });
})();
