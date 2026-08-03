/* ==========================================================================
   Pipelining and hazards.

   Five stages, one instruction per row, one cycle per column. What the exam
   cares about is where the bubbles come from, so every stall carries the reason:
   which register, produced by which instruction, needed by which.

   Turn forwarding off and the same program grows by several cycles. That
   difference is the whole argument for forwarding, and it is easier to believe
   when you watch it happen to your own instruction sequence.
   ========================================================================== */
(function () {
  const { el } = GG;

  const STAGES = ['IF', 'ID', 'EX', 'MEM', 'WB'];

  /* A deliberately small instruction language: enough for hazards, no more.
       add  rd rs rt      arithmetic, result ready after EX
       lw   rd rs         load, result only ready after MEM
       sw   rs rt         store, reads two registers, writes none
       beq  rs rt         branch, reads two registers  */
  function parse(text) {
    const lines = String(text || '').split(/\n+/).map(l => l.trim()).filter(Boolean);
    if (!lines.length) throw new Error('Write at least one instruction.');
    if (lines.length > 10) throw new Error('Ten instructions is plenty to see the point.');

    return lines.map((line, i) => {
      const parts = line.replace(/,/g, ' ').split(/\s+/).filter(Boolean);
      const op = (parts[0] || '').toLowerCase();
      const regs = parts.slice(1).map(r => r.toLowerCase());
      let dest = null, srcs = [];

      if (op === 'add' || op === 'sub' || op === 'and' || op === 'or') {
        if (regs.length < 3) throw new Error('Line ' + (i + 1) + ': ' + op + ' needs three registers.');
        dest = regs[0]; srcs = [regs[1], regs[2]];
      } else if (op === 'lw') {
        if (regs.length < 2) throw new Error('Line ' + (i + 1) + ': lw needs a destination and a base.');
        dest = regs[0]; srcs = [regs[1]];
      } else if (op === 'sw') {
        if (regs.length < 2) throw new Error('Line ' + (i + 1) + ': sw needs two registers.');
        srcs = [regs[0], regs[1]];
      } else if (op === 'beq' || op === 'bne') {
        if (regs.length < 2) throw new Error('Line ' + (i + 1) + ': ' + op + ' needs two registers.');
        srcs = [regs[0], regs[1]];
      } else {
        throw new Error('Line ' + (i + 1) + ': "' + op + '" is not one of add, sub, and, or, lw, sw, beq.');
      }
      return { i, text: line, op, dest, srcs, load: op === 'lw' };
    });
  }

  function simulate(values) {
    const prog = parse(values.program);
    const forwarding = String(values.forwarding) === '1';

    /* schedule[i] = {stage -> cycle}; bubbles[i] = number of stall cycles */
    const idAt = [];         /* cycle in which each instruction sits in ID */
    const exAt = [], memAt = [], wbAt = [], ifAt = [];
    const stalls = [];
    const notes = [];

    prog.forEach((ins, i) => {
      let ifc = i === 0 ? 1 : Math.max(ifAt[i - 1] + 1, 1);
      let idc = i === 0 ? ifc + 1 : Math.max(ifc + 1, idAt[i - 1] + 1);

      /* a RAW hazard delays ID until the value can be had */
      let wait = 0, reason = '';
      ins.srcs.forEach(src => {
        for (let p = i - 1; p >= 0; p--) {
          const prod = prog[p];
          if (prod.dest !== src) continue;
          /* earliest cycle this instruction can read src */
          /* The earliest cycle this instruction may sit in ID and still have the
             value by the time it needs it in EX. With forwarding an ALU result is
             ready at the end of the producer's EX; a load result only at the end
             of its MEM, which is why load-use still costs a cycle. Without
             forwarding the value is not in the register file until WB. */
          const ready = forwarding
            ? (prod.load ? memAt[p] : exAt[p])
            : wbAt[p];
          if (ready > idc + wait) {
            wait = ready - idc;
            reason = src + ' is produced by instruction ' + (p + 1) + ' (' + prod.op + ')' +
                     (forwarding
                       ? (prod.load
                          ? ' and a load result is only available after MEM, so even ' +
                            'with forwarding this costs a cycle'
                          : ' and is forwarded from EX')
                       : ' and without forwarding it is not in the register file until WB');
          }
          break;                                          /* nearest producer wins */
        }
      });

      idc += wait;
      stalls[i] = wait;
      notes[i] = wait ? reason : '';

      ifAt[i] = ifc;
      idAt[i] = idc;
      exAt[i] = idc + 1;
      memAt[i] = idc + 2;
      wbAt[i] = idc + 3;
    });

    const totalCycles = Math.max.apply(null, wbAt);
    const bubbles = stalls.reduce((a, b) => a + b, 0);

    /* one frame per cycle */
    const out = [];
    for (let c = 1; c <= totalCycles; c++) {
      const grid = prog.map((ins, i) => {
        const cells = {};
        cells[ifAt[i]] = 'IF';
        for (let s = ifAt[i] + 1; s < idAt[i]; s++) cells[s] = '--';
        cells[idAt[i]] = 'ID';
        cells[exAt[i]] = 'EX';
        cells[memAt[i]] = 'MEM';
        cells[wbAt[i]] = 'WB';
        return cells;
      });

      const active = prog
        .map((ins, i) => ({ i, stage: grid[i][c] }))
        .filter(x => x.stage && x.stage !== '--');
      const stalling = prog
        .map((ins, i) => ({ i, stage: grid[i][c] }))
        .filter(x => x.stage === '--');

      let caption;
      if (stalling.length) {
        const s = stalling[0];
        caption = 'Cycle ' + c + ': instruction ' + (s.i + 1) + ' is stalled. ' +
                  notes[s.i] + '.';
      } else if (active.length) {
        caption = 'Cycle ' + c + ': ' +
          active.map(a => 'instruction ' + (a.i + 1) + ' in ' + a.stage).join(', ') + '.';
      } else {
        caption = 'Cycle ' + c + '.';
      }

      out.push({ caption, cycle: c, totalCycles, bubbles, grid, prog, stalls,
                 forwarding });
    }

    const ideal = prog.length + 4;
    out.push({
      caption: 'Finished in ' + totalCycles + ' cycles. A hazard-free run would take ' +
               ideal + ', so ' + bubbles + ' cycle(s) went to stalls' +
               (forwarding ? ' even with forwarding on.' : ' because forwarding is off.'),
      cycle: totalCycles, totalCycles, bubbles, grid: out.length ? out[out.length - 1].grid : [],
      prog, stalls, forwarding,
    });
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    const table = el('div', { class: 'viz-pipe' });

    const head = el('div', { class: 'viz-prow head' });
    head.appendChild(el('span', { class: 'viz-pins', text: 'instruction' }));
    for (let c = 1; c <= frame.totalCycles; c++) {
      head.appendChild(el('span', { class: 'viz-pc' + (c === frame.cycle ? ' at' : ''),
                                    text: String(c) }));
    }
    table.appendChild(head);

    frame.prog.forEach((ins, i) => {
      const row = el('div', { class: 'viz-prow' });
      row.appendChild(el('span', { class: 'viz-pins mono',
                                   text: (i + 1) + '. ' + ins.text }));
      for (let c = 1; c <= frame.totalCycles; c++) {
        const stage = frame.grid[i] ? frame.grid[i][c] : '';
        const cls = stage === '--' ? ' stall'
                  : stage ? ' s' + stage.toLowerCase() : '';
        row.appendChild(el('span', {
          class: 'viz-pcell' + cls + (c === frame.cycle && stage ? ' now' : ''),
          text: stage || '',
        }));
      }
      table.appendChild(row);
    });
    host.appendChild(table);

    host.appendChild(el('div', { class: 'viz-state' }, [
      chip('cycle ' + frame.cycle + '/' + frame.totalCycles, 'mono'),
      chip('stall cycles ' + frame.bubbles, frame.bubbles ? 'bad' : 'good'),
      chip('ideal ' + (frame.prog.length + 4), 'mono'),
      chip(frame.forwarding ? 'forwarding on' : 'forwarding off', 'on'),
    ]));
  }

  const chip = (text, cls) => el('span', { class: 'viz-chip ' + (cls || ''), text: text });

  GG.viz.register('coa-pipeline', {
    title: 'Pipelining and hazards',
    subtitle: 'A five-stage pipeline over your own instruction sequence, with the ' +
              'reason printed for every bubble. Toggle forwarding to see what it buys.',
    glyph: 'F',
    topic: 'pipelining',
    note: 'RAW hazards, stalls, forwarding',
    inputs: [
      { key: 'forwarding', label: 'Forwarding', type: 'select', value: '1',
        options: [{ value: '1', label: 'On (EX/MEM and MEM/WB bypass)' },
                  { value: '0', label: 'Off (wait for write-back)' }] },
      { key: 'program', label: 'Program', type: 'textarea',
        hint: '(add/sub/and/or rd rs rt, lw rd rs, sw rs rt, beq rs rt)',
        value: 'lw r1 r0\nadd r2 r1 r1\nsub r3 r2 r1\nadd r4 r3 r2' },
    ],
    build: simulate,
    draw: draw,
  });
})();
