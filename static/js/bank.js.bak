/* ==========================================================================
   GG.bank - question bank operations: health, coverage gaps, sources, the
   import log, the human review queue and bank search.

   The review queue is the important part. Imported questions never go straight
   into practice; they sit here until a person approves them, which is why a bad
   PDF cannot poison your quizzes.
   ========================================================================== */
window.GG = window.GG || {};
GG.bank = (function () {
  const { $, el, esc, api, toast, num, nice, empty, growBars } = GG;

  function strip(st) {
    const b = st.bank || {};
    const rv = st.review || {};
    const host = $('#bankStrip');
    if (!host) return;
    host.innerHTML = '';
    const tiles = [
      [num(b.total), 'questions'],
      [b.health_pct + '%', 'usable'],
      [b.coverage_pct + '%', 'topic coverage'],
      [num(rv.pending), 'awaiting review'],
      [num(b.missing_explanation), 'no explanation'],
      [num((st.sources || []).length), 'sources'],
    ];
    tiles.forEach(([n, label]) => host.appendChild(
      el('div', { class: 'stat-tile' }, [el('b', { text: String(n) }), el('span', { text: label })])));
  }

  /* Practice's existing renderer fills #bankPanel with the health breakdown, so
     this module only adds what it does not cover. */
  function gaps(st) {
    const host = $('#bankGaps');
    if (!host) return;
    host.innerHTML = '';
    const health = st.bank_health || st.bank || {};
    const emptyTopics = health.empty_topics || [];
    const thin = health.thin_topics || [];

    if (!emptyTopics.length && !thin.length) {
      host.appendChild(el('p', { class: 'dim small' },
        ['Every syllabus topic has at least four questions. That is unusually good.']));
      return;
    }
    if (emptyTopics.length) {
      host.appendChild(el('p', { class: 'dim small', style: 'margin:0 0 10px' }, [
        emptyTopics.length + ' topic(s) have no questions at all. Highest exam weight first, ' +
        'because those are the ones worth importing next.',
      ]));
      emptyTopics.slice(0, 8).forEach(t => {
        host.appendChild(el('div', { class: 'bar-row' }, [
          el('span', { text: t.topic }),
          el('div', { class: 'bar-track' }, [el('i', { dataset: { w: String(Math.min(100, t.marks * 8)) } })]),
          el('span', { class: 'bar-val', text: t.marks + 'm' }),
        ]));
      });
    }
    if (thin.length) {
      host.appendChild(el('p', { class: 'dim small', style: 'margin:14px 0 0' }, [
        thin.length + ' topic(s) have fewer than four questions: ' +
        thin.slice(0, 6).map(t => t.topic).join(', ') +
        (thin.length > 6 ? ' and ' + (thin.length - 6) + ' more' : '') + '.',
      ]));
    }
    host.appendChild(el('p', { class: 'dim small', style: 'margin:14px 0 0' }, [
      'Fill gaps with: ', el('code', {}, ['python tools/import_questions.py <file> --dry-run']),
    ]));
  }

  function sources(st) {
    const host = $('#bankSources');
    if (!host) return;
    host.innerHTML = '';
    const rows = st.sources || [];
    if (!rows.length) {
      host.appendChild(empty('--', 'No sources registered',
        'A source records where questions came from and how much you trust it. ' +
        'Register one with tools/ingest.py --register.'));
      return;
    }
    host.appendChild(el('div', { class: 'src-row head-row' }, [
      el('span', {}, ['source']), el('span', {}, ['kind']),
      el('span', {}, ['questions']), el('span', {}, ['last import']),
    ]));
    rows.forEach(s => {
      host.appendChild(el('div', { class: 'src-row' }, [
        el('div', { class: 'src-name' }, [
          el('b', { text: s.name }),
          el('span', { text: s.slug + (s.url ? ' - ' + s.url.replace(/^https?:\/\//, '') : '') }),
        ]),
        el('span', { class: 'dim small mono', text: s.kind }),
        el('span', { class: 'mono small', text: num(s.questions) }),
        el('span', { class: 'dim small mono', text: s.last_import_at ? nice(s.last_import_at) : 'never' }),
      ]));
    });
    host.appendChild(el('p', { class: 'dim small', style: 'margin:14px 0 0' },
      ['Trust is stored per source but never used to hide questions; it only ' +
       'influences how strictly an import is reviewed.']));
  }

  function imports(st) {
    const host = $('#bankImports');
    if (!host) return;
    host.innerHTML = '';
    const rows = st.imports || [];
    if (!rows.length) {
      host.appendChild(empty('--', 'No imports yet',
        'Every import writes a manifest to content/imports/ and a row here, so you ' +
        'can always see what a past run did.'));
      return;
    }
    host.appendChild(el('div', { class: 'imp-row head-row' }, [
      el('span', {}, ['when']), el('span', {}, ['input']),
      el('span', {}, ['found']), el('span', {}, ['ok']),
      el('span', {}, ['review']), el('span', {}, ['dupes']),
    ]));
    rows.slice(0, 12).forEach(r => {
      host.appendChild(el('div', { class: 'imp-row' }, [
        el('span', { class: 'dim small mono', text: (r.started_at || '').slice(0, 16).replace('T', ' ') }),
        el('span', { class: 'small', style: 'overflow:hidden;text-overflow:ellipsis;white-space:nowrap',
                     title: r.input_path }, [
          (r.input_path || '').split('/').pop() + (r.dry_run ? ' (dry run)' : ''),
        ]),
        el('span', { class: 'mono small', text: String(r.found) }),
        el('span', { class: 'mono small', text: String(r.matched) }),
        el('span', { class: 'mono small', text: String(r.needs_review) }),
        el('span', { class: 'mono small', text: String(r.duplicates) }),
      ]));
    });
  }

  /* ------------------------------------------------------- review queue --- */
  async function review() {
    const host = $('#reviewList');
    if (!host) return;
    host.innerHTML = '<p class="dim small">Loading...</p>';
    let items = [];
    try {
      const out = await api('/review');
      items = out.items || [];
      const c = $('#reviewCount');
      if (c) {
        c.textContent = out.counts
          ? out.counts.pending + ' pending, ' + out.counts.approved + ' approved, ' +
            out.counts.rejected + ' rejected'
          : '';
      }
    } catch (e) {
      host.innerHTML = '';
      host.appendChild(el('p', { class: 'err' }, ['Could not load the review queue: ' + e.message]));
      return;
    }

    host.innerHTML = '';
    if (!items.length) {
      host.appendChild(el('div', { class: 'card' }, [
        empty('OK', 'Nothing waiting',
          'Imported questions the parser was not confident about land here. Approving ' +
          'one copies it into content/banks/reviewed/ and makes it live; rejecting ' +
          'leaves the raw import untouched.'),
      ]));
      return;
    }

    items.forEach(it => {
      const q = it.payload || {};
      const conf = it.confidence || 0;
      const cls = conf < 0.4 ? 'low' : conf < 0.7 ? 'mid' : 'high';
      const card = el('div', { class: 'review-card' });
      card.appendChild(el('div', { class: 'row-gap' }, [
        el('span', { class: 'conf-pill ' + cls, text: 'confidence ' + Number(conf).toFixed(2) }),
        el('span', { class: 'dim small mono', text: it.question_id || '' }),
        el('span', { class: 'dim small mono', text: (q.subject || '?') + '/' + (q.topic || '?') }),
        q.marks ? el('span', { class: 'dim small mono', text: q.marks + ' mark' }) : '',
      ]));
      if ((it.issues || []).length) {
        card.appendChild(el('p', { class: 'review-issues', text: it.issues.join(' | ') }));
      }
      card.appendChild(el('div', { class: 'review-q' }, [GG.mathText(q.text || '(no text)')]));
      const rCode = GG.codeBlocks(q);
      if (rCode) card.appendChild(rCode);
      const rFigs = GG.figures(q);
      if (rFigs) card.appendChild(rFigs);
      if ((q.options || []).length) {
        const opts = el('div', { class: 'review-opts' });
        q.options.forEach((o, i) => opts.appendChild(el('div', { class: 'review-opt' }, [
          el('b', {}, ['ABCD'[i] || String(i + 1)]),
          String(o).trim() ? GG.mathText(String(o))
            : el('i', { class: 'opt-missing', text: 'not extracted' }),
        ])));
        card.appendChild(opts);
      }
      card.appendChild(el('p', { class: 'dim small' }, [
        'Answer: ' + (q.answer || (q.answer_value !== undefined ? q.answer_value : '(none parsed)')),
      ]));
      card.appendChild(el('div', { class: 'row-end' }, [
        el('button', { class: 'btn btn-sm btn-danger', onclick: () => decide(it.id, false) }, ['Reject']),
        el('button', { class: 'btn btn-sm btn-primary', onclick: () => decide(it.id, true) }, ['Approve']),
      ]));
      host.appendChild(card);
    });
  }

  async function decide(id, approve) {
    try {
      await api(approve ? '/review/approve' : '/review/reject',
        { method: 'POST', body: { id: id } });
      toast(approve ? 'Approved' : 'Rejected',
        approve ? 'Copied into the reviewed bank and live from now on.'
                : 'Left out of the bank. The raw import file is untouched.');
      review();
      GG.app.reload();
    } catch (e) { toast('Could not save', e.message, 'bad'); }
  }

  /* ------------------------------------------------------------ papers ---- */
  function papers(st) {
    const host = $('#bankPapers');
    if (!host) return;
    host.innerHTML = '';
    const rows = st.papers || [];
    if (!rows.length) {
      host.appendChild(empty('--', 'No papers reconstructed',
        'A paper groups questions into one examination unit. They are derived ' +
        'from each question\'s origin block, so importing a GO volume creates them.'));
      return;
    }
    host.appendChild(el('div', { class: 'src-row head-row' }, [
      el('span', {}, ['paper']), el('span', {}, ['sections']),
      el('span', {}, ['questions']), el('span', {}, ['']),
    ]));
    rows.forEach(p => {
      const secs = (p.sections || [])
        .map(x => x.section.toUpperCase() + ' ' + x.question_count + '/' + x.total_marks + 'm')
        .join('  ');
      host.appendChild(el('div', { class: 'src-row' }, [
        el('div', { class: 'src-name' }, [
          el('b', { text: p.name }),
          el('span', { text: p.slug + (p.code ? ' - ' + p.code : '') }),
        ]),
        el('span', { class: 'dim small mono', text: secs }),
        // An incomplete paper must say so: the bank is subject-sliced, so most
        // papers arrive short of what they printed. Showing "62" next to a
        // 100-mark total without a caveat would misrepresent a mock score.
        el('span', { class: 'mono small', text: num(p.question_count) +
          (p.printed_questions ? ' / ' + p.printed_questions : '') +
          (p.complete ? '' : ' (partial)') }),
        el('button', {
          class: 'btn btn-sm',
          onclick: () => GG.practice.startSet({ paper: p.slug, purpose: 'mock' }),
        }, ['Sit it']),
      ]));
    });
    host.appendChild(el('p', { class: 'dim small', style: 'margin:14px 0 0' },
      ['Marked (partial) when the bank holds fewer questions than the paper ' +
       'printed. A partial paper still practises fine; its total is not a real score.']));
  }

  /* ------------------------------------------------------------ search ---- */
  function fillSelects(st) {
    const sel = $('#qsSubject');
    if (sel && !sel.dataset.filled) {
      sel.appendChild(el('option', { value: '' }, ['Any subject']));
      (st.subjects || []).forEach(s =>
        sel.appendChild(el('option', { value: s.slug }, [s.name])));
      sel.dataset.filled = '1';
    }
    const psel = $('#qsPaper');
    if (psel && !psel.dataset.filled) {
      psel.appendChild(el('option', { value: '' }, ['Any paper']));
      (st.papers || []).forEach(p =>
        psel.appendChild(el('option', { value: p.slug }, [p.name])));
      psel.dataset.filled = '1';
    }
  }

  async function search() {
    const host = $('#qsResults');
    host.innerHTML = '<p class="dim small">Searching...</p>';
    const params = new URLSearchParams({
      q: $('#qsQuery').value.trim(),
      subject: $('#qsSubject').value,
      paper: $('#qsPaper') ? $('#qsPaper').value : '',
      type: $('#qsType').value,
      difficulty: $('#qsDiff').value,
      limit: '40',
    });
    try {
      const out = await api('/questions?' + params.toString());
      host.innerHTML = '';
      const items = out.items || [];
      if (!items.length) {
        host.appendChild(el('div', { class: 'card' }, [
          empty('--', 'No matches', 'Nothing in the bank matches those filters.'),
        ]));
        return;
      }
      host.appendChild(el('p', { class: 'dim small' }, [items.length + ' match(es)']));
      items.forEach(q => {
        host.appendChild(el('div', { class: 'row' }, [
          el('div', { class: 'row-main' }, [
            el('div', { class: 'row-title', text: (q.text || '').slice(0, 130) }),
            el('div', { class: 'row-sub mono small' }, [
              [q.subject, q.topic, q.type, q.difficulty, q.marks + 'm',
               q.paper || q.year || '',
               q.position_in_paper ? 'Q' + q.position_in_paper : ''
              ].filter(Boolean).join(' - '),
            ]),
          ]),
          el('button', {
            class: 'btn btn-sm',
            onclick: () => GG.practice.startSet({ questionIds: [q.id], purpose: 'fresh' }),
          }, ['Try it']),
        ]));
      });
    } catch (e) {
      host.innerHTML = '';
      host.appendChild(el('p', { class: 'err' }, ['Search failed: ' + e.message]));
    }
  }

  async function reload() {
    try {
      const out = await api('/bank/reload', { method: 'POST', body: {} });
      toast('Bank reloaded', (out.total || 0) + ' questions, ' +
        (out.health_pct || 0) + '% usable.');
      GG.app.reload();
    } catch (e) { toast('Reload failed', e.message, 'bad'); }
  }

  function tab(st) {
    strip(st);
    gaps(st);
    sources(st);
    papers(st);
    imports(st);
    fillSelects(st);
    review();
    growBars();
  }

  return { tab, review, search, reload, papers };
})();

/* ==========================================================================
   Pending answers.

   The GO volumes contain thousands of questions with no answer printed. Rather
   than throw them away, they sit in the bank marked answer_pending: counted in
   coverage, listed here, and never served in a quiz until an answer exists.

   Filling one in writes it back into its bank file, so the fix is permanent.
   ========================================================================== */
(function () {
  const { $, el, api, toast, empty, esc } = GG;
  const base = GG.bank;

  const state = { offset: 0, subject: '', items: [] };

  function fillSubjectFilter(st) {
    const sel = $('#pendingSubject');
    if (!sel || sel.dataset.filled) return;
    sel.appendChild(el('option', { value: '' }, ['All subjects']));
    (st.subjects || []).forEach(s => sel.appendChild(el('option', { value: s.slug }, [s.name])));
    sel.dataset.filled = '1';
    sel.onchange = () => { state.offset = 0; state.items = []; load(true); };
  }

  async function load(replace) {
    const host = $('#pendingList');
    if (!host) return;
    if (replace) host.innerHTML = '<p class="dim small">Loading...</p>';
    const params = new URLSearchParams({
      subject: state.subject || ($('#pendingSubject') ? $('#pendingSubject').value : ''),
      limit: '25',
      offset: String(state.offset),
    });
    let out;
    try {
      out = await api('/questions/pending?' + params.toString());
    } catch (e) {
      host.innerHTML = '';
      host.appendChild(el('p', { class: 'err' }, ['Could not load: ' + e.message]));
      return;
    }
    const c = out.counts || {};
    const label = $('#pendingCount');
    if (label) {
      label.textContent = c.total
        ? c.total + ' waiting' + (c.needs_options ? ', ' + c.needs_options + ' also missing options' : '')
        : 'none waiting';
    }
    if (replace) host.innerHTML = '';
    const items = out.items || [];
    if (!items.length && replace) {
      host.appendChild(el('div', { class: 'card' }, [
        empty('OK', 'Nothing waiting',
          'Every question in the bank has an answer. Import more material to add to it.'),
      ]));
      return;
    }
    items.forEach(q => host.appendChild(card(q)));
    state.offset += items.length;
    const more = $('#pendingMore');
    if (more) more.hidden = items.length < 25;
  }

  function card(q) {
    const wrap = el('div', { class: 'review-card', dataset: { qid: q.id } });

    wrap.appendChild(el('div', { class: 'row-gap' }, [
      el('span', { class: 'state weak' }, [el('i', {}, ['~']), 'answer needed']),
      q.needs_options ? el('span', { class: 'state critical' },
        [el('i', {}, ['!']), 'options missing too']) : '',
      el('span', { class: 'dim small mono', text: q.subject + '/' + q.topic }),
      el('span', { class: 'dim small mono', text: q.type.toUpperCase() + ' - ' + q.marks + 'm' }),
      q.exam ? el('span', { class: 'dim small mono', text: q.exam }) : '',
    ]));

    wrap.appendChild(el('div', { class: 'review-q' }, [GG.mathText(q.text || '(no text extracted)')]));
    /* The figure is often the whole reason this one is pending, so show it here
       too - the answer cannot be looked up from the stem alone. */
    const pCode = GG.codeBlocks(q);
    if (pCode) wrap.appendChild(pCode);
    const pFigs = GG.figures(q);
    if (pFigs) wrap.appendChild(pFigs);

    if ((q.options || []).length) {
      const opts = el('div', { class: 'review-opts' });
      q.options.forEach((o, i) => opts.appendChild(el('div', { class: 'review-opt' }, [
        el('b', {}, ['ABCD'[i] || String(i + 1)]),
        String(o).trim() ? GG.mathText(String(o))
          : el('i', { class: 'opt-missing', text: 'not extracted' }),
      ])));
      wrap.appendChild(opts);
    }

    if (q.note) wrap.appendChild(el('p', { class: 'dim small', text: q.note }));
    if (q.source_ref) {
      wrap.appendChild(el('p', { class: 'dim small mono' }, [
        'source: ' + (q.source_file || '') + ' ref ' + q.source_ref,
      ]));
    }

    /* One click to go and look it up. */
    const tools = el('div', { class: 'row-gap', style: 'margin:12px 0' }, [
      el('a', { class: 'btn btn-sm', href: q.search_url, target: '_blank', rel: 'noopener' },
        ['Search for the answer']),
    ]);
    wrap.appendChild(tools);

    /* The form. Options box only appears when the extraction lost them. */
    const needOpts = q.needs_options || (q.options || []).length < 2;
    const form = el('div', {});
    if (needOpts) {
      form.appendChild(el('label', { class: 'field' }, [
        el('span', {}, ['Options, one per line (leave blank for a numeric answer)']),
        el('textarea', { rows: '4', class: 'pa-opts',
                         placeholder: '2\n4\n8\n16' }),
      ]));
    }
    form.appendChild(el('div', { class: 'field-row' }, [
      el('label', { class: 'field' }, [
        el('span', {}, ['Answer (A, B, C, D or B,D for multiple)']),
        el('input', { type: 'text', class: 'pa-ans', placeholder: 'B' }),
      ]),
      el('label', { class: 'field' }, [
        el('span', {}, ['or numeric answer (NAT)']),
        el('input', { type: 'text', class: 'pa-val', placeholder: '12.5' }),
      ]),
    ]));
    form.appendChild(el('label', { class: 'field' }, [
      el('span', {}, ['Explanation (optional, but future you will thank you)']),
      el('textarea', { rows: '2', class: 'pa-exp' }),
    ]));
    wrap.appendChild(form);

    const err = el('p', { class: 'err', hidden: true });
    wrap.appendChild(err);

    wrap.appendChild(el('div', { class: 'row-end' }, [
      el('button', { class: 'btn btn-sm', onclick: () => wrap.remove() }, ['Skip for now']),
      el('button', {
        class: 'btn btn-sm btn-primary',
        onclick: ev => save(wrap, q, err, ev.target),
      }, ['Save answer']),
    ]));
    return wrap;
  }

  async function save(wrap, q, err, btn) {
    const pick = sel => { const n = wrap.querySelector(sel); return n ? n.value.trim() : ''; };
    const optsRaw = pick('.pa-opts');
    const body = {
      id: q.id,
      answer: pick('.pa-ans'),
      answer_value: pick('.pa-val'),
      explain: pick('.pa-exp'),
    };
    if (optsRaw) body.options = optsRaw.split('\n').map(x => x.trim()).filter(Boolean);
    if (!body.answer && !body.answer_value) {
      err.hidden = false;
      err.textContent = 'Give either a letter answer or a numeric value.';
      return;
    }
    err.hidden = true;
    btn.disabled = true;
    try {
      const out = await api('/questions/answer', { method: 'POST', body: body });
      toast('Answer saved', q.id + ' is now gradable. ' +
        ((out.counts || {}).total || 0) + ' still waiting.');
      wrap.style.opacity = '0.35';
      wrap.innerHTML = '';
      wrap.appendChild(el('p', { class: 'dim small' }, ['Saved: ' + q.id]));
      const label = $('#pendingCount');
      if (label && out.counts) label.textContent = out.counts.total + ' waiting';
    } catch (e) {
      btn.disabled = false;
      err.hidden = false;
      err.textContent = e.message;
    }
  }

  const originalTab = base.tab;
  base.tab = function (st) {
    originalTab(st);
    fillSubjectFilter(st);
    state.offset = 0;
    load(true);
  };

  document.addEventListener('DOMContentLoaded', () => {
    const more = $('#pendingMore');
    if (more) more.onclick = () => load(false);
  });

  base.pending = load;
})();
