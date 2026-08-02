/* Doubt desk: prompt composer, handoff links, optional inline answer. */
GG.doubts = (function () {
  'use strict';
  const { $, $$, el, ago } = GG;

  let lastPrompt = '';
  let ctx = { subject_slug: '', topic_slug: '', question_id: '' };

  function tab(st) {
    const sSel = $('#dSubject');
    if (sSel.dataset.built !== String(st.subjects.length)) {
      sSel.innerHTML = '<option value="">Not specified</option>';
      st.subjects.forEach(s => sSel.appendChild(
        el('option', { value: s.slug, text: s.name })));
      sSel.dataset.built = String(st.subjects.length);
    }
    sSel.onchange = () => fillTopics(st);
    fillTopics(st);

    $('#dBuild').onclick = () => build(false);
    $('#dAsk').onclick = () => build(true);

    refreshStatus();
    history(st);
  }

  function fillTopics(st) {
    const tSel = $('#dTopic');
    const slug = $('#dSubject').value;
    tSel.innerHTML = '<option value="">Not specified</option>';
    const subj = st.subjects.find(s => s.slug === slug);
    if (subj) subj.topics.forEach(t => tSel.appendChild(
      el('option', { value: t.slug, text: t.name })));
  }

  async function refreshStatus() {
    let s;
    try { s = await GG.api('/doubts/status'); } catch (e) { return; }
    const line = $('#dStatusLine');
    if (s.inline_available) {
      line.innerHTML = 'Inline answers ready via <b>' +
        (s.ollama.available ? 'local Ollama' : GG.esc(s.provider)) + '</b>';
    } else {
      line.textContent = 'No inline source set up. Handoff links below work with no setup.';
    }
    providers(s);
    return s;
  }

  function providers(s) {
    const host = $('#dProviders');
    host.innerHTML = '';

    /* local */
    const ol = s.ollama;
    host.appendChild(el('div', { style: 'margin-bottom:18px' }, [
      el('div', { class: 'row-end', style: 'margin:0 0 10px' }, [
        el('b', { style: 'font-size:13px', text: 'Route 1 - local model (free, offline)' }),
        el('span', { class: 'state-key ' + (ol.available ? 'live' : 'off'),
                     text: ol.available ? 'DETECTED' : 'NOT RUNNING' }),
      ]),
      el('p', { class: 'dim small', style: 'margin:0 0 10px',
        text: ol.available
          ? (ol.models && ol.models.length
              ? 'Ollama is up at ' + ol.base_url + ' with: ' + ol.models.join(', ')
              : 'Ollama is up but has no model pulled yet.')
          : 'Install Ollama from ollama.com, then run "ollama pull qwen2.5:3b". ' +
            'It runs on your own machine, costs nothing and works without internet.' }),
      el('div', { class: 'row-gap' }, [
        el('button', { class: 'btn btn-sm', text: 'Recheck', onclick: refreshStatus }),
        el('button', { class: 'btn btn-sm', text: 'Configure', onclick: () => aiModal(s) }),
      ]),
      el('div', { class: 'prov-grid', style: 'margin-top:12px' },
        (ol.suggested || []).map(m => el('div', { class: 'prov' }, [
          el('span', { class: 'prov-name mono', text: m.name }),
          el('span', { class: 'prov-note', text: m.note }),
          el('span', { class: 'state-key', text: m.size }),
        ]))),
    ]));

    /* hosted */
    host.appendChild(el('div', { style: 'margin-bottom:18px' }, [
      el('div', { class: 'row-end', style: 'margin:0 0 10px' }, [
        el('b', { style: 'font-size:13px', text: 'Route 2 - hosted free tier (optional key)' }),
        el('span', { class: 'state-key ' + (s.has_key ? 'live' : 'off'),
                     text: s.has_key ? 'KEY SAVED' : 'NO KEY' }),
      ]),
      el('div', { class: 'prov-grid' },
        Object.keys(s.hosted).map(k => {
          const h = s.hosted[k];
          return el('div', { class: 'prov' }, [
            el('span', { class: 'prov-name', text: h.label }),
            el('span', { class: 'prov-note', text: h.note }),
            el('div', { class: 'prov-foot' }, [
              el('a', { class: 'link', href: h.signup, target: '_blank',
                        rel: 'noopener', text: 'Get a free key' }),
              h.configured ? el('span', { class: 'state-key live', text: 'ACTIVE' }) : null,
            ]),
          ]);
        })),
    ]));

    /* handoff */
    host.appendChild(el('div', {}, [
      el('div', { class: 'row-end', style: 'margin:0 0 10px' }, [
        el('b', { style: 'font-size:13px', text: 'Route 3 - handoff (always available, no setup)' }),
        el('span', { class: 'state-key live', text: 'READY' }),
      ]),
      el('p', { class: 'dim small', style: 'margin:0',
        text: 'Build a prompt above and these open with it pre-filled, in whatever free ' +
              'account you already have. Nothing leaves this machine until you click.' }),
    ]));
  }

  async function build(inline) {
    const body = $('#dBody').value.trim();
    if (!body) { GG.toast('Write the doubt first', 'Even one line is enough.', 'bad'); return; }
    ctx.subject_slug = $('#dSubject').value;
    ctx.topic_slug = $('#dTopic').value;

    const btn = inline ? $('#dAsk') : $('#dBuild');
    const label = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> working';

    try {
      const built = await GG.api('/doubts/prompt', {
        body: Object.assign({ body }, ctx),
      });
      lastPrompt = built.prompt;
      render(built);
      if (inline) {
        const out = await GG.api('/doubts/ask', {
          body: Object.assign({ body, prompt: built.prompt }, ctx),
        });
        showAnswer(out);
        GG.toast('Answered', 'via ' + out.provider);
      }
    } catch (e) {
      GG.toast(inline ? 'Inline answer failed' : 'Could not build prompt', e.message, 'bad');
    } finally {
      btn.disabled = false;
      btn.textContent = label;
    }
  }

  function render(built) {
    const host = $('#dResult');
    host.innerHTML = '';
    const card = el('div', { class: 'card', style: 'margin-top:16px' });
    card.appendChild(el('div', { class: 'row-end', style: 'margin:0 0 12px' }, [
      el('b', { style: 'font-size:13px', text: 'Composed prompt' }),
      el('div', { class: 'row-gap' }, [
        el('button', {
          class: 'btn btn-sm', text: 'Copy prompt',
          onclick: async ev => {
            try {
              await navigator.clipboard.writeText(built.prompt);
              ev.currentTarget.textContent = 'Copied';
              setTimeout(() => (ev.currentTarget.textContent = 'Copy prompt'), 1600);
            } catch (e) { GG.toast('Copy blocked', 'Select the text manually.', 'bad'); }
          },
        }),
      ]),
    ]));
    card.appendChild(el('div', { class: 'prompt-box', text: built.prompt }));
    card.appendChild(el('p', { class: 'dim small', style: 'margin:14px 0 8px',
      text: 'Open it somewhere free:' }));
    card.appendChild(el('div', { class: 'prov-grid' },
      built.links.map(l => el('div', { class: 'prov' }, [
        el('span', { class: 'prov-name', text: l.name }),
        el('span', { class: 'prov-note', text: l.note }),
        el('a', { class: 'btn btn-sm', href: l.ready_url, target: '_blank', rel: 'noopener',
                  text: l.prefill ? 'Open with prompt' : 'Open (paste it)' }),
      ]))));
    host.appendChild(card);
    host.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function showAnswer(out) {
    const host = $('#dResult');
    host.appendChild(el('div', { class: 'card', style: 'margin-top:16px' }, [
      el('div', { class: 'row-end', style: 'margin:0 0 12px' }, [
        el('b', { style: 'font-size:13px', text: 'Answer' }),
        el('span', { class: 'state-key live', text: out.provider.toUpperCase() }),
      ]),
      el('div', { class: 'answer-box', text: out.answer }),
      el('p', { class: 'dim small', style: 'margin:12px 0 0',
        text: 'A language model wrote this. Check it against a standard text before you ' +
              'trust it on exam day.' }),
    ]));
    if (out.items) historyRows(out.items);
  }

  function history(st) {
    GG.api('/doubts').then(d => historyRows(d.items)).catch(() => {});
  }

  function historyRows(items) {
    const host = $('#dHistory');
    host.innerHTML = '';
    if (!items || !items.length) {
      host.appendChild(GG.render.emptyBox('No doubts logged',
        'Anything you ask gets kept here with its answer.'));
      return;
    }
    items.forEach(d => {
      host.appendChild(el('div', { class: 'row' }, [
        el('span', { class: 'mono dim', text: d.answer ? '[+]' : '[?]' }),
        el('div', { class: 'row-body' }, [
          el('div', { class: 'row-l1' }, [
            el('span', { class: 'row-name', text: (d.body || '').slice(0, 80) }),
            d.provider ? el('span', { class: 'chip-kind', text: d.provider }) : null,
          ]),
          el('div', { class: 'row-sub',
                      text: [d.subject_slug, d.topic_slug].filter(Boolean).join(' / ') || 'general' }),
        ]),
        el('span', { class: 'row-num', text: d.answer ? 'answered' : 'prompt only' }),
        el('span', { class: 'row-day' }, [
          document.createTextNode(ago((d.created_at || '').slice(0, 10))),
          el('button', { class: 'x', text: '\u00d7', title: 'Delete',
            onclick: async () => {
              try { const r = await GG.api('/doubts/' + d.id, { method: 'DELETE' });
                    historyRows(r.items); } catch (e) {}
            } }),
        ]),
      ]));
    });
  }

  /* jump here from a quiz result */
  function prefill(q) {
    location.hash = '#/doubts';
    setTimeout(() => {
      ctx = { subject_slug: q.subject, topic_slug: q.topic, question_id: q.id };
      const sSel = $('#dSubject');
      sSel.value = q.subject;
      sSel.dispatchEvent(new Event('change'));
      setTimeout(() => { $('#dTopic').value = q.topic; }, 30);
      $('#dBody').value = 'I got this one wrong. Walk me through it from the start.';
      $('#dBody').focus();
    }, 120);
  }

  function aiModal(s) {
    const body = $('#aiBody');
    body.innerHTML = '';
    const providerSel = el('select', { id: 'aiProvider' }, [
      el('option', { value: 'none', text: 'Auto (local Ollama if running, else handoff)' }),
      el('option', { value: 'ollama', text: 'Ollama - local, free' }),
      el('option', { value: 'groq', text: 'Groq - hosted free tier' }),
      el('option', { value: 'gemini', text: 'Google AI Studio - hosted free tier' }),
      el('option', { value: 'openrouter', text: 'OpenRouter - hosted, :free models' }),
    ]);
    providerSel.value = s.provider || 'none';
    body.appendChild(el('label', { class: 'field' }, [
      el('span', { text: 'Source' }), providerSel]));
    body.appendChild(el('label', { class: 'field' }, [
      el('span', { text: 'Model', html: '' }),
      el('input', { type: 'text', id: 'aiModel', value: s.model || '',
                    placeholder: 'e.g. qwen2.5:3b or llama-3.3-70b-versatile' })]));
    body.appendChild(el('label', { class: 'field' }, [
      el('span', { text: 'API key (only for hosted sources)' }),
      el('input', { type: 'password', id: 'aiKey', placeholder: s.has_key ? 'saved - leave blank to keep' : '' })]));
    body.appendChild(el('label', { class: 'field' }, [
      el('span', { text: 'Ollama address' }),
      el('input', { type: 'text', id: 'aiOllama', value: s.ollama.base_url || 'http://127.0.0.1:11434' })]));
    body.appendChild(el('p', { class: 'dim small', style: 'margin:0',
      text: 'The key is stored in your local database and stripped from any backup you export. ' +
            'You never need one - the handoff links work without it.' }));

    $('#saveAi').onclick = async () => {
      const payload = {
        ai_provider: $('#aiProvider').value,
        ai_model: $('#aiModel').value.trim(),
        ollama_url: $('#aiOllama').value.trim(),
      };
      const k = $('#aiKey').value.trim();
      if (k) payload.ai_key = k;
      try {
        await GG.api('/settings/ai', { body: payload });
        GG.modal('#modalAi', false);
        GG.toast('Saved', 'Answer source updated.');
        refreshStatus();
      } catch (e) { GG.toast('Could not save', e.message, 'bad'); }
    };
    GG.modal('#modalAi', true);
  }

  return { tab, prefill, refreshStatus };
})();

/* ==========================================================================
   v3 additions - the "did it actually help?" loop.

   A doubt is only resolved when the topic sticks, so there are two signals here:
   an immediate helped / did-not-help button, and a delayed one the engine sets
   by itself when you later answer that topic correctly.
   ========================================================================== */
(function () {
  const { $, el, api, toast, empty, growBars } = GG;
  const base = GG.doubts;

  function pressure(st) {
    const host = $('#dPressure');
    if (!host) return;
    host.innerHTML = '';
    const rows = (st.doubt_pressure || (st.doubts || {}).pressure || []);
    if (!rows.length) {
      host.appendChild(el('p', { class: 'dim small' }, [
        'Asking about the same topic twice is a stronger weak-topic signal than a single ' +
        'wrong answer. Once that happens, the topic shows up here and gets pushed up in ' +
        'your plan.',
      ]));
      return;
    }
    rows.forEach(r => {
      host.appendChild(el('div', { class: 'bar-row' }, [
        el('span', { text: r.name || r.topic }),
        el('div', { class: 'bar-track' }, [
          el('i', { dataset: { w: String(Math.min(100, r.count * 25)) } })]),
        el('span', { class: 'bar-val', text: r.count + 'x' }),
      ]));
    });
  }

  async function rate(id, helped, node) {
    try {
      await api('/doubts/rate', { method: 'POST', body: { id: id, helped: helped } });
      toast(helped ? 'Good' : 'Noted',
        helped ? 'Marked as resolved.'
               : 'That topic has been pushed up your weak list.');
      if (node) {
        node.innerHTML = '';
        node.appendChild(el('span', { class: 'state ' + (helped ? 'ok' : 'weak') }, [
          el('i', {}, [helped ? '#' : '~']), helped ? 'helped' : 'did not help',
        ]));
      }
    } catch (e) { toast('Could not save', e.message, 'bad'); }
  }

  /* Attach rating buttons to every logged doubt that has no verdict yet. */
  function decorate() {
    GG.$$('#dHistory .row').forEach(row => {
      if (row.dataset.rated) return;
      const id = row.dataset.doubtId;
      if (!id) return;
      row.dataset.rated = '1';
      const box = el('div', { class: 'row-gap' });
      box.appendChild(el('button', { class: 'btn btn-sm', onclick: () => rate(id, true, box) },
        ['Helped']));
      box.appendChild(el('button', { class: 'btn btn-sm', onclick: () => rate(id, false, box) },
        ['Still stuck']));
      row.appendChild(box);
    });
  }

  const originalTab = base.tab;
  base.tab = function (st) {
    originalTab(st);
    pressure(st);
    decorate();
    growBars();
  };
  base.rate = rate;
})();
