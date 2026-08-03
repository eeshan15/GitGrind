/* ==========================================================================
   GG.timer - stopwatch logging.

   The manual dialog is still there and unchanged: it is the right tool for
   entering a session after the fact. This is the other half - press start before
   you begin, and the session writes itself when you stop.

   The clock lives in memory on GG.S, not in the modal, so closing the dialog or
   moving between tabs does not stop it. A pill in the topbar keeps the elapsed
   time visible from anywhere in the app.
   ========================================================================== */
window.GG = window.GG || {};
GG.timer = (function () {
  const { $, $$, el, api, toast, hm, modal, announce } = GG;

  const T = {
    running: false,
    startedAt: null,      /* epoch ms of the current run          */
    accrued: 0,           /* ms banked from before the last pause */
    subjectId: null,
    topicIds: [],
    kind: 'concept',
    tick: null,
  };

  const elapsedMs = () =>
    T.accrued + (T.running && T.startedAt ? Date.now() - T.startedAt : 0);
  const elapsedMin = () => Math.floor(elapsedMs() / 60000);

  function clock(ms) {
    const s = Math.floor(ms / 1000);
    const pad = n => String(n).padStart(2, '0');
    return pad(Math.floor(s / 3600)) + ':' + pad(Math.floor(s / 60) % 60) + ':' + pad(s % 60);
  }

  /* ------------------------------------------------------------- topbar --- */
  function paintPill() {
    const pill = $('#timerPill');
    if (!pill) return;
    const on = T.running || T.accrued > 0;
    pill.hidden = !on;
    if (!on) return;
    pill.classList.toggle('live', T.running);
    $('#timerPillTime').textContent = clock(elapsedMs());
    pill.title = T.running ? 'Session running - click to open' : 'Session paused - click to open';
  }

  function paintDialog() {
    const face = $('#timerFace');
    if (!face) return;
    face.textContent = clock(elapsedMs());
    face.classList.toggle('live', T.running);

    const mins = elapsedMin();
    $('#timerMins').textContent = mins
      ? 'will log as ' + hm(mins)
      : 'anything under a minute is not logged';

    $('#timerStart').hidden = T.running;
    $('#timerStart').textContent = T.accrued > 0 ? 'Resume' : 'Start';
    $('#timerPause').hidden = !T.running;
    $('#timerStop').disabled = mins < 1;
    $('#timerDiscard').hidden = !(T.running || T.accrued > 0);

    /* Locking the subject once the clock is running stops a half-hour of
       algebra being filed under operating systems by accident. */
    $('#tmSubject').disabled = T.running || T.accrued > 0;
  }

  function paint() {
    paintPill();
    if (!$('#modalTimer').hidden) paintDialog();
  }

  function startTicking() {
    if (T.tick) return;
    T.tick = setInterval(paint, 1000);
  }
  function stopTicking() {
    if (!T.tick) return;
    clearInterval(T.tick);
    T.tick = null;
  }

  /* -------------------------------------------------------------- clock --- */
  function start() {
    const sel = $('#tmSubject');
    if (!sel.value) {
      err('Pick a subject first.');
      return;
    }
    T.subjectId = parseInt(sel.value, 10);
    T.kind = $('#tmKind').value;
    T.running = true;
    T.startedAt = Date.now();
    startTicking();
    paint();
    announce('Timer started.');
  }

  function pause() {
    if (!T.running) return;
    T.accrued = elapsedMs();
    T.running = false;
    T.startedAt = null;
    stopTicking();
    paint();
    announce('Timer paused at ' + clock(T.accrued));
  }

  function reset() {
    T.running = false;
    T.startedAt = null;
    T.accrued = 0;
    T.subjectId = null;
    T.topicIds = [];
    stopTicking();
    paint();
  }

  function discard() {
    if (elapsedMin() >= 1 &&
        !confirm('Throw away ' + clock(elapsedMs()) + ' without logging it?')) return;
    reset();
    modal('#modalTimer', false);
    toast('Timer cleared', 'Nothing was logged.');
  }

  async function stop() {
    const mins = elapsedMin();
    if (mins < 1) {
      err('Less than a minute on the clock.');
      return;
    }
    const topicIds = $$('#tmTopics .tp.on').map(n => parseInt(n.dataset.id, 10));
    const btn = $('#timerStop');
    btn.disabled = true;
    try {
      const out = await api('/sessions', {
        method: 'POST',
        body: {
          subject_id: T.subjectId,
          day: GG.S.state.today,
          minutes: mins,
          kind: T.kind,
          hour: new Date().getHours(),
          topic_ids: topicIds,
          mark_done: $('#tmMarkDone').checked,
          with_quiz: $('#tmWithQuiz').checked,
          quiz_count: 4,
          note: $('#tmNote').value.trim(),
        },
      });
      reset();
      modal('#modalTimer', false);
      toast('Logged ' + hm(mins), 'Timed session saved.');
      if (out.state) GG.app.apply(out.state);
      else GG.app.reload();
      if (out.quiz && out.quiz.questions && out.quiz.questions.length) {
        setTimeout(() => GG.practice.open(out.quiz, 'Quiz on what you just studied'), 340);
      }
    } catch (e) {
      btn.disabled = false;
      err(e.message);
    }
  }

  function err(msg) {
    const box = $('#timerErr');
    box.hidden = false;
    box.textContent = msg;
    setTimeout(() => { box.hidden = true; }, 4000);
  }

  /* --------------------------------------------------------------- open --- */
  function topics(st) {
    const host = $('#tmTopics');
    host.innerHTML = '';
    const sid = $('#tmSubject').value ? parseInt($('#tmSubject').value, 10) : null;
    const subj = (st.subjects || []).find(s => s.id === sid);
    if (!subj) {
      host.appendChild(el('p', { class: 'dim small' },
        ['Pick a subject to tick off the topics you get through.']));
      return;
    }
    subj.topics.forEach(t => {
      const node = el('label', {
        class: 'tp' + (t.status === 'done' ? ' was-done' : '') +
               (T.topicIds.includes(t.id) ? ' on' : ''),
        dataset: { id: t.id },
      }, [
        el('span', { class: 'box', text: T.topicIds.includes(t.id) ? '[x]' : '[ ]' }),
        el('span', { text: t.name }),
      ]);
      node.addEventListener('click', e => {
        e.preventDefault();
        node.classList.toggle('on');
        const on = node.classList.contains('on');
        node.querySelector('.box').textContent = on ? '[x]' : '[ ]';
        T.topicIds = $$('#tmTopics .tp.on').map(n => parseInt(n.dataset.id, 10));
      });
      host.appendChild(node);
    });
  }

  function open() {
    const st = GG.S.state;
    if (!st) return;

    const sel = $('#tmSubject');
    if (sel.dataset.built !== String((st.subjects || []).length)) {
      sel.innerHTML = '<option value="">Choose a subject</option>';
      (st.subjects || []).forEach(s =>
        sel.appendChild(el('option', { value: s.id, text: s.name })));
      sel.dataset.built = String((st.subjects || []).length);
    }
    if (T.subjectId) sel.value = String(T.subjectId);

    const kind = $('#tmKind');
    if (!kind.dataset.built) {
      (st.kinds || ['concept', 'pyq', 'dpp', 'revision', 'mock', 'notes']).forEach(k =>
        kind.appendChild(el('option', { value: k, text: (st.kind_labels || {})[k] || k })));
      kind.dataset.built = '1';
    }
    if (T.kind) kind.value = T.kind;

    sel.onchange = () => { T.topicIds = []; topics(st); };
    topics(st);
    modal('#modalTimer', true);
    paintDialog();
    if (T.running) startTicking();
  }

  function wire() {
    const b = $('#btnTimer');
    if (b) b.onclick = open;
    const pill = $('#timerPill');
    if (pill) pill.onclick = open;
    const map = {
      '#timerStart': start, '#timerPause': pause,
      '#timerStop': stop, '#timerDiscard': discard,
    };
    Object.keys(map).forEach(id => { const n = $(id); if (n) n.onclick = map[id]; });

    /* A running clock should survive an accidental tab close. */
    window.addEventListener('beforeunload', e => {
      if (T.running || T.accrued > 0) {
        e.preventDefault();
        e.returnValue = '';
      }
    });
    GG.key('s', 'Start or open the session timer', open, { hidden: false });
  }

  document.addEventListener('DOMContentLoaded', wire);

  return { open, start, pause, stop, paint, get running() { return T.running; },
           get minutes() { return elapsedMin(); } };
})();