/* ==========================================================================
   GG.viz - the shell every topic visualiser plugs into.

   A visualiser supplies inputs, a build() that turns those inputs into a list of
   frames, and a draw() that paints one frame. Everything else - the dialog, the
   controls, the scrubber, the keyboard, reduced motion - lives here, so adding a
   topic is one small file rather than another copy of the plumbing.

   The rule these follow: every frame carries a caption saying *why* the step
   happened. An animation with no commentary is decoration; the sentence is the
   part that teaches.

     GG.viz.register('os-scheduling', {
       title, subtitle, topic,          // topic is a syllabus slug
       inputs: [ {key, label, type, ...} ],
       build(values) -> [ frame, ... ]  // each frame: { caption, ...your data }
       draw(host, frame, values, i)     // paint one frame into host
     });
   ========================================================================== */
window.GG = window.GG || {};
GG.viz = (function () {
  const { $, $$, el, modal } = GG;

  const REG = {};
  const V = { id: null, def: null, frames: [], i: 0, playing: false,
              timer: null, speed: 1, values: {} };

  const SPEEDS = [0.5, 1, 2, 4];
  const BASE_MS = 900;          /* one frame at 1x */

  function register(id, def) { REG[id] = Object.assign({ id: id }, def); }
  const list = () => Object.keys(REG).map(k => REG[k]);

  /* ------------------------------------------------------------ inputs --- */
  function defaults(def) {
    const out = {};
    (def.inputs || []).forEach(f => { out[f.key] = f.value; });
    return out;
  }

  function renderInputs() {
    const host = $('#vizInputs');
    host.innerHTML = '';
    (V.def.inputs || []).forEach(f => {
      let control;
      if (f.type === 'select') {
        control = el('select', {});
        (f.options || []).forEach(o =>
          control.appendChild(el('option', { value: o.value, text: o.label })));
        control.value = V.values[f.key];
      } else if (f.type === 'table') {
        control = tableInput(f);
      } else if (f.type === 'textarea') {
        control = el('textarea', { rows: '6', spellcheck: 'false' });
        control.value = V.values[f.key];
      } else {
        control = el('input', {
          type: f.type || 'number',
          value: String(V.values[f.key]),
          min: f.min !== undefined ? String(f.min) : null,
          max: f.max !== undefined ? String(f.max) : null,
          step: f.step !== undefined ? String(f.step) : null,
        });
      }
      control.classList.add('viz-in');
      control.dataset.key = f.key;
      control.addEventListener('change', () => {
        V.values[f.key] =
            f.type === 'table' ? readTable(control)
          : (f.type === 'select' || f.type === 'text' || f.type === 'textarea')
              ? control.value
          : Number(control.value);
        rebuild();
      });
      host.appendChild(el('label', { class: 'field viz-field' + (f.type === 'table' ? ' wide' : '') }, [
        el('span', {}, [f.label, f.hint ? el('em', { class: 'dim' }, [' ' + f.hint]) : '']),
        control,
      ]));
    });
  }

  /* A tiny editable grid: rows of processes, jobs, references, whatever the
     visualiser calls them. */
  function tableInput(f) {
    const wrap = el('div', { class: 'viz-table' });
    const head = el('div', { class: 'viz-trow viz-thead' });
    f.columns.forEach(c => head.appendChild(el('span', { text: c.label })));
    head.appendChild(el('span', {}));
    wrap.appendChild(head);

    const body = el('div', { class: 'viz-tbody' });
    wrap.appendChild(body);

    function addRow(values) {
      const row = el('div', { class: 'viz-trow' });
      f.columns.forEach(c => {
        const inp = el('input', { type: 'number', value: String(values[c.key] ?? c.value ?? 0),
                                  min: String(c.min ?? 0), 'data-col': c.key });
        inp.addEventListener('change', () => {
          V.values[f.key] = readTable(wrap);
          rebuild();
        });
        row.appendChild(inp);
      });
      const del = el('button', { class: 'viz-del', type: 'button', title: 'Remove' }, ['x']);
      del.onclick = () => {
        if (body.childElementCount <= 1) return;
        row.remove();
        V.values[f.key] = readTable(wrap);
        rebuild();
      };
      row.appendChild(del);
      body.appendChild(row);
    }

    (V.values[f.key] || []).forEach(addRow);

    const add = el('button', { class: 'btn btn-sm', type: 'button' }, ['+ row']);
    add.onclick = () => {
      if (body.childElementCount >= (f.max || 8)) return;
      const blank = {};
      f.columns.forEach(c => { blank[c.key] = c.value ?? 0; });
      addRow(blank);
      V.values[f.key] = readTable(wrap);
      rebuild();
    };
    wrap.appendChild(add);
    return wrap;
  }

  function readTable(wrap) {
    return $$('.viz-tbody .viz-trow', wrap).map(row => {
      const obj = {};
      $$('input', row).forEach(inp => { obj[inp.dataset.col] = Number(inp.value); });
      return obj;
    });
  }

  /* ------------------------------------------------------------ playback -- */
  function rebuild() {
    try {
      V.frames = V.def.build(V.values) || [];
      $('#vizErr').hidden = true;
    } catch (e) {
      V.frames = [];
      const box = $('#vizErr');
      box.hidden = false;
      box.textContent = e.message;
    }
    V.i = 0;
    pause();
    render();
  }

  function render() {
    const host = $('#vizStage');
    const frame = V.frames[V.i];
    host.innerHTML = '';
    if (!frame) return;
    try {
      V.def.draw(host, frame, V.values, V.i);
    } catch (e) {
      host.appendChild(el('p', { class: 'err' }, ['Draw failed: ' + e.message]));
    }
    $('#vizCaption').textContent = frame.caption || '';
    $('#vizStep').textContent = (V.i + 1) + ' / ' + V.frames.length;
    const bar = $('#vizScrub');
    bar.max = String(Math.max(0, V.frames.length - 1));
    bar.value = String(V.i);
    $('#vizPlay').textContent = V.playing ? 'Pause' : 'Play';
    $('#vizPrev').disabled = V.i === 0;
    $('#vizNext').disabled = V.i >= V.frames.length - 1;
  }

  function step(delta) {
    const next = V.i + delta;
    if (next < 0 || next >= V.frames.length) {
      if (V.playing) pause();
      return;
    }
    V.i = next;
    render();
  }

  function play() {
    if (!V.frames.length) return;
    if (V.i >= V.frames.length - 1) V.i = 0;
    V.playing = true;
    clearInterval(V.timer);
    /* Reduced motion still steps, it just does not animate between states. */
    V.timer = setInterval(() => step(1), BASE_MS / V.speed);
    render();
  }

  function pause() {
    V.playing = false;
    clearInterval(V.timer);
    V.timer = null;
    render();
  }

  const toggle = () => (V.playing ? pause() : play());

  /* --------------------------------------------------------------- open --- */
  function open(id) {
    const def = REG[id];
    if (!def) return;
    V.id = id;
    V.def = def;
    V.speed = 1;
    V.values = defaults(def);

    $('#vizTitle').textContent = def.title;
    $('#vizSubtitle').textContent = def.subtitle || '';
    $('#vizSpeed').textContent = '1x';
    renderInputs();
    rebuild();
    modal('#modalViz', true);

    /* Offer the drill straight afterwards: watching is not practising, and the
       gap between the two is where the learning leaks away. */
    const drill = $('#vizDrill');
    drill.hidden = !def.topic;
    drill.onclick = () => {
      modal('#modalViz', false);
      GG.practice.startSet({ purpose: 'weak', topic: def.topic });
    };
  }

  function close() {
    pause();
    modal('#modalViz', false);
  }

  /* ---------------------------------------------------------------- grid -- */
  function grid(hostSel) {
    const host = $(hostSel);
    if (!host) return;
    host.innerHTML = '';
    const items = list();
    if (!items.length) {
      host.appendChild(el('p', { class: 'dim small' }, ['No visualisers loaded.']));
      return;
    }
    items.forEach(def => {
      const card = el('button', { class: 'mode viz-card', type: 'button' }, [
        el('div', { class: 'mode-name' }, [
          el('span', { class: 'mode-glyph', text: def.glyph || '>' }), def.title,
        ]),
        el('p', { class: 'mode-why', text: def.subtitle || '' }),
        el('p', { class: 'mode-count', text: def.note || 'interactive' }),
      ]);
      card.onclick = () => open(def.id);
      host.appendChild(card);
    });
  }

  function wire() {
    const map = {
      '#vizPlay': toggle, '#vizNext': () => { pause(); step(1); },
      '#vizPrev': () => { pause(); step(-1); },
      '#vizReset': () => { pause(); V.i = 0; render(); },
      '#vizClose': close,
    };
    Object.keys(map).forEach(id => { const n = $(id); if (n) n.onclick = map[id]; });

    const sp = $('#vizSpeedBtn');
    if (sp) sp.onclick = () => {
      V.speed = SPEEDS[(SPEEDS.indexOf(V.speed) + 1) % SPEEDS.length];
      $('#vizSpeed').textContent = V.speed + 'x';
      if (V.playing) play();
    };

    const scrub = $('#vizScrub');
    if (scrub) scrub.addEventListener('input', () => {
      pause();
      V.i = Number(scrub.value);
      render();
    });

    document.addEventListener('keydown', e => {
      if ($('#modalViz').hidden) return;
      const t = (document.activeElement || {}).tagName;
      if (t === 'INPUT' || t === 'SELECT') return;
      if (e.key === ' ') { e.preventDefault(); toggle(); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); pause(); step(1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); pause(); step(-1); }
    });
  }

  document.addEventListener('DOMContentLoaded', wire);

  return { register, open, close, list, grid };
})();
