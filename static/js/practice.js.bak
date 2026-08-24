/* Question of the day, quiz runner and results. */
GG.practice = (function () {
  'use strict';
  const { $, $$, el, esc, ago, growBars, figures, mathText, codeBlocks } = GG;

  const LETTER = i => String.fromCharCode(65 + i);
  let quiz = null;      /* { id, questions, responses, idx, startedAt } */

  /* ========================= question rendering ======================== */
  function questionBlock(q, opts) {
    const o = Object.assign({ selected: null, locked: false, reveal: null, onPick: null }, opts);
    const wrap = el('div', {});

    wrap.appendChild(el('div', { class: 'qotd-meta' }, [
      el('span', { class: 'chip-kind ' + q.kind, text: q.kind === 'pyq' ? 'previous year' : 'practice' }),
      el('span', { class: 'chip-kind', text: q.type.toUpperCase() }),
      el('span', { class: 'chip-kind', text: q.marks + ' mark' + (q.marks > 1 ? 's' : '') }),
      el('span', { class: 'chip-kind', text: q.difficulty }),
      q.topic ? el('span', { class: 'chip-kind', text: q.topic }) : null,
    ]));
    wrap.appendChild(el('div', { class: 'q-text' }, [mathText(q.text)]));
    /* Figures go below the stem, above the options: that is the reading order
       of the printed paper, and a diagram-dependent question is unanswerable
       until it is on screen. */
    /* Listing first, then figure: that is the printed order, and the code is
       usually what the question is asking about. */
    const code = codeBlocks(q);
    if (code) wrap.appendChild(code);
    const figs = figures(q);
    if (figs) wrap.appendChild(figs);

    if (q.type === 'nat') {
      const input = el('input', {
        type: 'number', step: 'any', placeholder: 'numeric answer',
        value: o.selected === null || o.selected === undefined ? '' : o.selected,
        disabled: o.locked,
      });
      input.addEventListener('input', () => o.onPick && o.onPick(input.value === '' ? null : parseFloat(input.value)));
      wrap.appendChild(el('div', { class: 'nat-input' }, [
        input, el('span', { class: 'dim small', text: 'No negative marking on NAT.' }),
      ]));
    } else {
      const multi = q.type === 'msq';
      const box = el('div', { class: 'q-opts' });
      const sel = Array.isArray(o.selected) ? o.selected.slice() : [];
      (q.options || []).forEach((text, i) => {
        let cls = 'opt';
        if (sel.includes(i)) cls += ' sel';
        if (o.reveal) {
          const key = o.reveal.answer || [];
          if (key.includes(i)) cls = 'opt right';
          else if (sel.includes(i)) cls = 'opt wrong';
        }
        const row = el('div', { class: cls }, [
          el('span', { class: 'opt-key', text: LETTER(i) }),
          el('span', { class: 'opt-txt' }, [mathText(text)]),
        ]);
        if (!o.locked) {
          row.addEventListener('click', () => {
            let next;
            if (multi) {
              next = sel.includes(i) ? sel.filter(x => x !== i) : sel.concat([i]).sort();
            } else {
              next = [i];
            }
            o.onPick && o.onPick(next);
          });
        }
        box.appendChild(row);
      });
      wrap.appendChild(box);
      if (multi) wrap.appendChild(el('p', { class: 'dim small', style: 'margin:9px 0 0',
        text: 'Multiple correct. All-or-nothing, but no negative marking.' }));
      else wrap.appendChild(el('p', { class: 'dim small', style: 'margin:9px 0 0',
        text: 'Single correct. A wrong answer costs ' + (q.marks / 3).toFixed(2) + ' marks, GATE style.' }));
    }
    return wrap;
  }

  function verdict(res) {
    const q = res.question;
    const right = res.correct;
    const box = el('div', { class: 'q-verdict ' + (right ? 'right' : 'wrong') });
    let answerText;
    if (q.type === 'nat') answerText = String(q.answer_value);
    else answerText = (q.answer || []).map(LETTER).join(', ');

    box.appendChild(el('div', { class: 'head-line' }, [
      el('span', { class: 'mono', style: 'color:' + (right ? 'var(--g4)' : 'var(--bad)'),
                   text: right ? '[+] correct' : '[x] wrong' }),
      el('b', { text: (res.marks_got > 0 ? '+' : '') + res.marks_got + ' marks' }),
      el('span', { class: 'dim small', text: 'answer: ' + answerText }),
    ]));
    if (q.explain) box.appendChild(el('div', { class: 'q-explain' }, [mathText(q.explain)]));
    if (res.peer) box.appendChild(el('div', { class: 'solve-rate',
      text: 'Modelled solve rate for this difficulty: ' + res.peer.solve_rate + '% (simulated, not live data)' }));
    box.appendChild(el('button', {
      class: 'btn btn-sm', style: 'margin-top:12px', text: 'Ask about this',
      onclick: () => GG.doubts.prefill(q),
    }));
    return box;
  }

  /* ============================== QOTD ================================= */
  function renderQotd(st, host, compact) {
    const qd = st.qotd;
    const h = $(host);
    h.innerHTML = '';
    if (!qd) {
      h.appendChild(GG.render.emptyBox('No question available',
        'The bank under content/questions is empty.'));
      return;
    }

    const card = el('div', { class: 'qotd' });
    card.appendChild(el('div', { class: 'qotd-top' }, [
      el('span', { class: 'qotd-key', text: 'DAILY' }),
      el('span', { class: 'qotd-why', text: qd.subject_name + ' / ' + qd.reason }),
      el('span', { class: 'qotd-right' }, [
        qd.streak ? el('span', { class: 'chip-kind', text: qd.streak + 'd answered' }) : null,
        compact ? el('a', { class: 'link', href: '#/practice', text: 'Practice tab' }) : null,
      ]),
    ]));

    const body = el('div', { class: 'qotd-body' });
    let picked = qd.answered ? (qd.your_response !== undefined ? qd.your_response : null) : null;

    const block = questionBlock(qd.question, {
      selected: picked,
      locked: qd.answered,
      reveal: qd.answered ? qd.question : null,
      onPick: v => { picked = v; submitBtn.disabled = v === null || (Array.isArray(v) && !v.length); },
    });
    body.appendChild(block);

    const submitBtn = el('button', {
      class: 'btn btn-primary', text: 'Submit answer', disabled: true,
      onclick: async () => {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> checking';
        try {
          const out = await GG.api('/qotd/answer', { body: { response: picked } });
          GG.app.apply(out.state);
          GG.toast(out.correct ? 'Correct' : 'Not this time',
                   out.correct ? 'Daily question cleared.' : 'Explanation is on the card.',
                   out.correct ? '' : 'bad');
        } catch (e) {
          GG.toast('Could not submit', e.message, 'bad');
          submitBtn.disabled = false;
          submitBtn.textContent = 'Submit answer';
        }
      },
    });

    if (qd.answered) {
      /* MCQ carries a one-third penalty; MSQ and NAT do not. Mirrors quiz.grade_one. */
      const penalty = qd.question.type === 'mcq'
        ? -Math.round((qd.question.marks / 3) * 100) / 100
        : 0;
      body.appendChild(verdict({
        question: qd.question,
        correct: qd.correct,
        marks_got: qd.correct ? qd.question.marks : penalty,
        peer: null,
      }));
    } else {
      body.appendChild(el('div', { class: 'row-end' }, [
        el('span', { class: 'dim small', text: 'Answer once. It is logged either way.' }),
        submitBtn,
      ]));
    }
    card.appendChild(body);
    h.appendChild(card);
  }

  /* ============================ quiz runner ============================ */
  async function startSet(subjectId, topicIds, count, kind) {
    try {
      const built = await GG.api('/quiz', {
        body: {
          subject_id: subjectId || null,
          topic_ids: topicIds || [],
          count: count || 5,
          kinds: kind ? [kind] : null,
        },
      });
      open(built, 'Practice set');
    } catch (e) {
      GG.toast('Could not build the set', e.message, 'bad');
    }
  }

  function open(built, title) {
    quiz = {
      id: built.id,
      questions: built.questions,
      responses: built.questions.map(() => null),
      // Per-question timing and confidence. The backend has always read these
      // off each response (quiz._record_attempt), but the UI never sent them, so
      // attempts.seconds was the set duration divided evenly - a column that
      // looked complete and carried no information.
      times: built.questions.map(() => 0),
      conf: built.questions.map(() => null),
      shownAt: Date.now(),
      idx: 0,
      total: built.total_marks,
      startedAt: Date.now(),
      title: title || 'Quiz',
    };
    GG.modal('#modalQuiz', true);
    draw();
  }

  /* Bank the time spent on the question now on screen. Called before every
     move, so revisiting a question accumulates rather than overwrites. */
  function stamp() {
    if (!quiz) return;
    const now = Date.now();
    quiz.times[quiz.idx] += Math.max(0, Math.round((now - quiz.shownAt) / 1000));
    quiz.shownAt = now;
  }

  function go(i) {
    stamp();
    quiz.idx = i;
    draw();
  }

  function draw() {
    const q = quiz.questions[quiz.idx];
    quiz.shownAt = Date.now();
    $('#quizTitle').textContent = quiz.title;
    $('#quizProgress').textContent = (quiz.idx + 1) + ' / ' + quiz.questions.length +
      '  |  ' + quiz.total + ' marks';

    const body = $('#quizBody');
    body.innerHTML = '';

    body.appendChild(el('div', { class: 'quiz-bar' }, el('i', {
      style: 'width:' + ((quiz.idx + 1) / quiz.questions.length * 100) + '%' })));

    const nav = el('div', { class: 'quiz-nav' });
    quiz.questions.forEach((_, i) => {
      const done = quiz.responses[i] !== null &&
        !(Array.isArray(quiz.responses[i]) && !quiz.responses[i].length);
      nav.appendChild(el('button', {
        class: 'qn' + (done ? ' done' : '') + (i === quiz.idx ? ' now' : ''),
        text: String(i + 1),
        onclick: () => go(i),
      }));
    });
    body.appendChild(nav);

    const holder = el('div', { class: 'quiz-q' });
    holder.appendChild(questionBlock(q, {
      selected: quiz.responses[quiz.idx],
      onPick: v => { stamp(); quiz.responses[quiz.idx] = v; draw(); },
    }));

    /* Confidence is asked for, not inferred. A wrong answer given confidently is
       a different problem from a wrong guess, and only the person answering
       knows which it was. Optional: skipping it logs null, not a fake value. */
    const conf = el('div', { class: 'row-end', style: 'gap:6px;margin-top:10px' }, [
      el('span', { class: 'dim small', style: 'margin-right:auto',
        text: 'How sure are you?' }),
    ]);
    /* 1-5, matching the clamp in quiz._record_attempt. A 0-1 float would be
       squashed to 1 by int() and every rating would read as "no idea". */
    [['No idea', 1], ['Guess', 2], ['Unsure', 3], ['Fairly sure', 4], ['Certain', 5]]
      .forEach(([label, v]) => {
        const on = quiz.conf[quiz.idx] === v;
        conf.appendChild(el('button', {
          class: 'btn btn-sm' + (on ? ' btn-primary' : ''),
          text: label,
          onclick: () => {
            stamp();
            quiz.conf[quiz.idx] = on ? null : v;
            draw();
          },
        }));
      });
    holder.appendChild(conf);
    body.appendChild(holder);

    const foot = $('#quizFoot');
    foot.innerHTML = '';
    const answered = quiz.responses.filter(r =>
      r !== null && !(Array.isArray(r) && !r.length)).length;
    foot.appendChild(el('span', {
      class: 'dim small', style: 'margin-right:auto',
      text: answered + ' of ' + quiz.questions.length + ' answered',
    }));
    if (quiz.idx > 0) foot.appendChild(el('button', {
      class: 'btn', text: '< Back', onclick: () => go(quiz.idx - 1) }));
    if (quiz.idx < quiz.questions.length - 1) {
      foot.appendChild(el('button', {
        class: 'btn', text: 'Next >', onclick: () => go(quiz.idx + 1) }));
    }
    foot.appendChild(el('button', {
      class: 'btn btn-primary', text: 'Submit set', onclick: submit }));
  }

  async function submit() {
    stamp();
    const payload = quiz.questions.map((q, i) => ({
      question_id: q.id,
      response: quiz.responses[i],
      seconds: quiz.times[i],
      confidence: quiz.conf[i],
    }));
    const btns = $$('#quizFoot .btn');
    btns.forEach(b => (b.disabled = true));
    try {
      const out = await GG.api('/quiz/' + quiz.id + '/submit', {
        body: { responses: payload, duration_s: Math.round((Date.now() - quiz.startedAt) / 1000) },
      });
      GG.app.apply(out.state);
      results(out);
    } catch (e) {
      GG.toast('Could not submit', e.message, 'bad');
      btns.forEach(b => (b.disabled = false));
    }
  }

  function results(out) {
    $('#quizTitle').textContent = 'Result';
    $('#quizProgress').textContent = '';
    const body = $('#quizBody');
    body.innerHTML = '';

    const pct = out.total_marks ? Math.max(0, out.scored_marks) / out.total_marks * 100 : 0;
    body.appendChild(el('div', { class: 'result-hero' }, [
      el('div', { class: 'rh' }, [
        el('b', { style: 'color:' + (pct >= 60 ? 'var(--g4)' : pct >= 35 ? 'var(--warn)' : 'var(--bad)'),
                  text: out.scored_marks + ' / ' + out.total_marks }),
        el('span', { text: 'marks scored (GATE marking, negatives included)' }),
      ]),
      el('div', { class: 'rh' }, [
        el('b', { text: out.correct_count + ' / ' + out.question_count }),
        el('span', { text: 'questions correct  (' + out.accuracy + '%)' }),
      ]),
    ]));

    if (out.peer) body.appendChild(peerBox(out.peer));

    const list = el('div', { class: 'res-list' });
    out.results.forEach((r, i) => {
      const card = el('div', { class: 'res ' + (r.correct ? 'right' : 'wrong') });
      card.style.animationDelay = Math.min(i * 55, 400) + 'ms';
      card.appendChild(el('div', { class: 'res-top' }, [
        el('span', { text: 'Q' + (i + 1) + '  ' + r.question.topic }),
        el('span', { text: (r.marks_got > 0 ? '+' : '') + r.marks_got + ' / ' + r.question.marks }),
      ]));
      card.appendChild(questionBlock(r.question, {
        selected: r.your_response, locked: true, reveal: r.question,
      }));
      card.appendChild(verdict(r));
      list.appendChild(card);
    });
    body.appendChild(list);

    const foot = $('#quizFoot');
    foot.innerHTML = '';
    foot.appendChild(el('button', { class: 'btn btn-primary', text: 'Done',
      onclick: () => GG.modal('#modalQuiz', false) }));
  }

  function peerBox(p) {
    const box = el('div', { class: 'peer-box' });
    box.appendChild(el('div', { class: 'row-end', style: 'margin:0 0 4px' }, [
      el('b', { style: 'font-size:13px', text: 'Where this score sits' }),
      el('span', { class: 'state-key', text: 'SIMULATED' }),
    ]));
    box.appendChild(el('p', { class: 'dim small', style: 'margin:6px 0 0',
      text: 'You scored better than ' + GG.num(p.beat_count) + ' of ' + GG.num(p.sample) +
            ' virtual attempts on this exact paper -- the ' + p.percentile + 'th percentile.' }));

    const range = Math.max(p.total_marks, p.your_score, p.top_decile, 1);
    const pos = v => Math.max(0, Math.min(100, (v / range) * 100));
    const scale = el('div', { class: 'peer-scale' }, [
      el('div', { class: 'peer-track' }),
      el('div', { class: 'peer-marker median', dataset: { l: 'median ' + p.median },
                  style: 'left:' + pos(p.median) + '%' }),
      el('div', { class: 'peer-marker', dataset: { l: 'you ' + p.your_score },
                  style: 'left:0%' }),
    ]);
    box.appendChild(scale);
    requestAnimationFrame(() => {
      scale.querySelectorAll('.peer-marker:not(.median)')
        .forEach(m => (m.style.left = pos(p.your_score) + '%'));
    });

    box.appendChild(el('div', { class: 'row-gap', style: 'margin-top:6px' }, [
      el('span', { class: 'dim small', text: 'median ' + p.median },),
      el('span', { class: 'dim small', text: 'top decile ' + p.top_decile }),
      el('span', { class: 'dim small', text: 'paper total ' + p.total_marks }),
    ]));
    box.appendChild(el('div', { class: 'peer-note', text: p.note }));
    return box;
  }

  /* ============================ practice tab =========================== */
  function tab(st) {
    renderQotd(st, '#qotdPanel', false);
    $('#qotdStreak').textContent = st.qotd && st.qotd.streak
      ? st.qotd.streak + ' day answering streak' : '';

    const sel = $('#pqSubject');
    if (sel.dataset.built !== String(st.subjects.length)) {
      sel.innerHTML = '<option value="">Any subject</option>';
      st.subjects.forEach(s => sel.appendChild(
        el('option', { value: s.id, text: s.name + ' (' + s.bank + 'q)' })));
      sel.dataset.built = String(st.subjects.length);
    }
    sel.onchange = () => topicPicker(st);
    topicPicker(st);

    $('#pqStart').onclick = () => {
      const sid = $('#pqSubject').value ? parseInt($('#pqSubject').value, 10) : null;
      const tids = $$('#pqTopics .tp.on').map(n => parseInt(n.dataset.id, 10));
      startSet(sid, tids, parseInt($('#pqCount').value, 10), $('#pqKind').value);
    };

    /* history */
    const host = $('#quizHistory');
    host.innerHTML = '';
    const hist = st.quiz_history || [];
    if (!hist.length) host.appendChild(GG.render.emptyBox('No sets yet',
      'Finish a session with a quiz, or build a set above.'));
    hist.forEach(q => {
      const pct = q.total_marks ? Math.round(Math.max(0, q.scored_marks) / q.total_marks * 100) : 0;
      host.appendChild(el('div', { class: 'row' }, [
        el('span', { class: 'mono dim', text: q.source === 'session' ? '[S]' : '[P]' }),
        el('div', { class: 'row-body' }, [
          el('div', { class: 'row-l1' }, [
            el('span', { class: 'row-name', text: q.subject_name || 'Mixed' }),
            el('span', { class: 'chip-kind', text: q.source }),
          ]),
          el('div', { class: 'row-sub',
                      text: (q.topic_slugs || '').split(',').filter(Boolean).join(', ') || 'mixed topics' }),
        ]),
        el('span', { class: 'row-num',
                     style: 'color:' + (pct >= 60 ? 'var(--g4)' : pct >= 35 ? 'var(--warn)' : 'var(--bad)'),
                     text: q.scored_marks + '/' + q.total_marks }),
        el('span', { class: 'row-day', text: ago(q.day) }),
      ]));
    });

    /* bank panel */
    const bp = $('#bankPanel');
    bp.innerHTML = '';
    const b = st.bank;
    bp.appendChild(el('p', { class: 'dim small', style: 'margin:0 0 12px',
      text: b.total + ' questions across ' + b.files.length + ' files in content/questions/. ' +
            'These are authored for this tracker -- add your own by dropping another JSON file in ' +
            'the same shape. Nothing is scraped from any paid platform.' }));
    const grid = el('div', { class: 'kpi-grid' });
    Object.keys(b.subjects).sort().forEach(k => {
      const s = st.subjects.find(x => x.slug === k);
      grid.appendChild(el('div', { class: 'kpi' }, [
        el('b', { text: String(b.subjects[k]) }),
        el('span', { text: s ? s.name : k }),
      ]));
    });
    bp.appendChild(grid);
  }

  function topicPicker(st) {
    const host = $('#pqTopics');
    host.innerHTML = '';
    const sid = $('#pqSubject').value ? parseInt($('#pqSubject').value, 10) : null;
    const subj = st.subjects.find(s => s.id === sid);
    if (!subj) {
      $('#pqAvail').textContent = 'Pick a subject to narrow by topic.';
      return;
    }
    subj.topics.forEach(t => {
      const node = el('label', {
        class: 'tp' + (t.status === 'done' ? ' was-done' : ''),
        dataset: { id: t.id },
      }, [
        el('span', { class: 'box', text: '[ ]' }),
        el('span', { text: t.name + (t.bank ? ' (' + t.bank + ')' : ' (0)') }),
      ]);
      node.addEventListener('click', e => {
        e.preventDefault();
        node.classList.toggle('on');
        node.querySelector('.box').textContent = node.classList.contains('on') ? '[x]' : '[ ]';
        avail(st);
      });
      host.appendChild(node);
    });
    avail(st);
  }

  function avail(st) {
    const sid = $('#pqSubject').value ? parseInt($('#pqSubject').value, 10) : null;
    const subj = st.subjects.find(s => s.id === sid);
    const on = $$('#pqTopics .tp.on').map(n => parseInt(n.dataset.id, 10));
    let n;
    if (!subj) n = st.bank.total;
    else if (!on.length) n = subj.bank;
    else n = subj.topics.filter(t => on.includes(t.id)).reduce((a, t) => a + t.bank, 0);
    $('#pqAvail').textContent = n + ' question' + (n === 1 ? '' : 's') + ' available for this selection';
  }

  return { tab, renderQotd, startSet, open, questionBlock, verdict };
})();

/* ==========================================================================
   v3 additions - adaptive modes, confidence logging, mistake tagging,
   save-for-later and the retry loop.

   These are appended rather than folded in so the v2 quiz runner stays exactly
   as it was; the wrappers below extend it instead of replacing it.
   ========================================================================== */
(function () {
  const { $, el, api, toast, empty, growBars, hm } = GG;
  const base = GG.practice;

  /* Purpose-driven set. This is what every "Start", "Drill this", "Revise now"
     button in the app calls, so the selector reason travels with the quiz. */
  async function startPurpose(opts) {
    const o = opts || {};
    try {
      const built = await api('/quiz', {
        method: 'POST',
        body: {
          purpose: o.purpose || 'mixed',
          subject: o.subject || '',
          topic: o.topic || '',
          topics: o.topics || [],
          count: o.count || 0,
          kind: o.kind || '',
          question_ids: o.questionIds || [],
          paper: o.paper || '',
          mode: o.mode || o.purpose || 'mixed',
          reason: o.reason || '',
        },
      });
      if (!built || !(built.questions || []).length) {
        toast('No questions available',
          'The bank has nothing that fits those filters yet. Import more, or widen ' +
          'the selection.', 'warn');
        return null;
      }
      base.open(built, built.title || 'Practice set');
      return built;
    } catch (e) {
      toast('Could not build the set', e.message, 'bad');
      return null;
    }
  }

  /* Accept both the v2 call style (subjectId, topicIds, count, kind) and the v3
     object style, so nothing that already worked breaks. */
  const originalStartSet = base.startSet;
  base.startSet = function (a, b, c, d) {
    if (a && typeof a === 'object' && !Array.isArray(a)) return startPurpose(a);
    return originalStartSet(a, b, c, d);
  };
  base.startPurpose = startPurpose;

  /* --------------------------------------------------------- mode grid ---- */
  const MODES = [
    ['review', 'R', 'Revision due', 'Only what your spacing schedule says is due. This is ' +
      'the highest-value practice there is, because it stops what you already learnt ' +
      'from leaking away.'],
    ['weak', 'W', 'Weak-topic drill', 'Concentrated on the topics where your accuracy is ' +
      'lowest relative to their exam weight.'],
    ['mixed', 'M', 'Mixed PYQ set', 'Previous-year questions across subjects, the way the ' +
      'real paper mixes them.'],
    ['speed', 'S', 'Speed drill', 'One-mark questions with a tight clock, to fix the ' +
      'time-per-question problem before it costs marks.'],
    ['boss', 'B', 'Boss question', 'One hard two-mark question on a topic you have covered. ' +
      'Win or lose, it tells you where you actually stand.'],
    ['fresh', 'F', 'Unseen questions', 'Only questions you have never been served, for when ' +
      'you want a clean read on a topic.'],
  ];

  function modes(st) {
    const host = $('#modeGrid');
    if (!host) return;
    host.innerHTML = '';
    const due = (st.debt || {}).due_today || 0;
    MODES.forEach(([purpose, glyph, name, why]) => {
      const disabled = purpose === 'review' && !due;
      const btn = el('button', {
        class: 'mode' + (purpose === 'boss' ? ' boss' : ''),
        type: 'button', disabled: disabled,
      }, [
        el('div', { class: 'mode-name' }, [el('span', { class: 'mode-glyph', text: glyph }), name]),
        el('p', { class: 'mode-why', text: why }),
        el('p', { class: 'mode-count' }, [
          purpose === 'review' ? (due ? due + ' due now' : 'nothing due')
            : purpose === 'boss' ? '1 question'
            : 'adaptive size',
        ]),
      ]);
      btn.onclick = () => startPurpose({ purpose: purpose });
      host.appendChild(btn);
    });
  }

  /* ------------------------------------------------ mistakes and confidence */
  function mistakes(st) {
    const host = $('#mistakePanel');
    if (!host) return;
    host.innerHTML = '';
    const m = st.mistakes || {};
    const items = m.items || [];
    if (!items.length) {
      host.appendChild(el('p', { class: 'dim small' }, [
        'After a wrong answer you can tag why you got it wrong. Once a few are tagged, ' +
        'the pattern shows up here - and "silly" mistakes need a very different fix from ' +
        '"concept" ones.',
      ]));
      return;
    }
    const total = items.reduce((a, x) => a + x.count, 0);
    items.forEach(x => {
      host.appendChild(el('div', { class: 'bar-row' }, [
        el('span', { text: x.label }),
        el('div', { class: 'bar-track' }, [
          el('i', { dataset: { w: String(Math.round(x.count / total * 100)) } })]),
        el('span', { class: 'bar-val', text: x.count + ' (' + Math.round(x.count / total * 100) + '%)' }),
      ]));
    });
    if (m.untagged) {
      host.appendChild(el('p', { class: 'dim small', style: 'margin-top:12px' }, [
        m.untagged + ' wrong answer(s) still untagged.',
      ]));
    }
    if (m.headline) {
      host.appendChild(el('p', { class: 'why', style: 'margin-top:12px' }, [m.headline]));
    }
  }

  function confidence(st) {
    const host = $('#confidencePanel');
    if (!host) return;
    host.innerHTML = '';
    const c = st.confidence || {};
    if (!c.available) {
      host.appendChild(el('p', { class: 'dim small' }, [
        c.note || 'Rate your confidence after each answer and this panel will show whether ' +
        'you can trust your own gut. Confidently wrong is the most expensive state to be in, ' +
        'because you will not revise it.',
      ]));
      return;
    }
    (c.buckets || []).forEach(b => {
      host.appendChild(el('div', { class: 'bar-row' }, [
        el('span', { text: b.label }),
        el('div', { class: 'bar-track' }, [el('i', { dataset: { w: String(b.accuracy) } })]),
        el('span', { class: 'bar-val', text: b.accuracy + '% / ' + b.n }),
      ]));
    });
    if (c.note) host.appendChild(el('p', { class: 'why', style: 'margin-top:12px' }, [c.note]));
  }

  function saved(st) {
    const host = $('#savedList');
    if (!host) return;
    host.innerHTML = '';
    const items = st.saved_questions || [];
    if (!items.length) {
      host.appendChild(empty('--', 'Nothing saved',
        'Press Save while reviewing an answer and the question lands here, so a hard ' +
        'one is never lost in a finished set.'));
      return;
    }
    items.forEach(q => {
      host.appendChild(el('div', { class: 'row' }, [
        el('div', { class: 'row-main' }, [
          el('div', { class: 'row-title', text: (q.text || '').slice(0, 120) }),
          el('div', { class: 'row-sub mono small' }, [
            [q.subject_name || q.subject, q.topic_name || q.topic, q.marks + 'm']
              .filter(Boolean).join(' - '),
          ]),
        ]),
        el('button', {
          class: 'btn btn-sm',
          onclick: () => startPurpose({ questionIds: [q.question_id || q.id], purpose: 'fresh' }),
        }, ['Retry']),
      ]));
    });
  }

  /* Extend the existing tab() rather than replacing it. */
  const originalTab = base.tab;
  base.tab = function (st) {
    originalTab(st);
    if (GG.viz) GG.viz.grid('#vizGrid');
    mistakes(st);
    modes(st);
    mistakes(st);
    confidence(st);
    saved(st);
    growBars();
  };
})();
