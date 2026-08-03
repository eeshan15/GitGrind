/* Readiness tab: index hero, movement, target cards, trend line. */
GG.readiness = (function () {
  'use strict';
  const { $, el, num, signed, countTo, growBars } = GG;

  function tab(st) {
    const r = st.readiness;

    countTo($('#rIndex'), r.index, { dp: 1 });
    $('#rScore').textContent = 'estimated GATE score ' + Math.round(r.est_score) +
      ' / ' + r.score_max;

    /* component bars */
    const host = $('#rComponents');
    host.innerHTML = '';
    const rows = [
      ['Coverage', r.components.coverage, r.weights.coverage, 'topics ticked, weighted by exam marks'],
      ['Accuracy', r.components.accuracy, r.weights.accuracy,
        r.components.accuracy_confidence < 100
          ? 'raw ' + r.components.accuracy_raw + '%, only ' + r.components.accuracy_confidence + '% confident yet'
          : 'raw ' + r.components.accuracy_raw + '% over a solid sample'],
      ['Volume', r.components.volume, r.weights.volume,
        'against a ' + r.volume_reference_hours + 'h reference'],
      ['Consistency', r.components.consistency, r.weights.consistency, 'streak and active days'],
    ];
    rows.forEach(([name, val, w, note]) => {
      host.appendChild(el('div', { class: 'rb' }, [
        el('span', { class: 'rb-name', text: name, title: note }),
        el('div', { class: 'bar tall' }, el('i', {
          dataset: { w: Math.min(100, val) },
          style: 'background:' + (val >= 70 ? 'var(--g4)' : val >= 40 ? 'var(--warn)' : 'var(--bad)'),
        })),
        el('span', { class: 'rb-val' }, [
          el('b', { text: val.toFixed(1) }),
          document.createTextNode(' \u00b7 ' + Math.round(w * 100) + '%'),
        ]),
      ]));
    });

    movement(r);
    targets(r);
    trend(st.readiness_history || []);
    growBars($('#view-readiness'));
  }

  function movement(r) {
    const host = $('#rMovement');
    host.innerHTML = '';
    const mv = r.movement;

    if (!mv.available) {
      host.appendChild(el('div', { class: 'move' }, [
        el('b', { class: 'flat', text: '--' }),
        el('span', { text: mv.note || 'Baseline being recorded.' }),
        el('span', { class: 'sim', text: 'SIMULATED COHORT' }),
      ]));
    } else {
      const cls = v => (v > 0 ? 'up' : v < 0 ? 'down' : 'flat');
      const cards = [
        [signed(num(mv.passed_today)), 'virtual candidates you moved past since ' + mv.since, mv.passed_today],
        [num(mv.still_ahead), 'still ahead of you in the model', 0],
        [signed(mv.index_delta.toFixed(2)), 'readiness index change', mv.index_delta],
        [signed(Math.round(mv.score_delta)), 'estimated score change', mv.score_delta],
      ];
      cards.forEach(([big, label, delta]) => {
        host.appendChild(el('div', { class: 'move' }, [
          el('b', { class: cls(delta), text: String(big) }),
          el('span', { text: label }),
          el('span', { class: 'sim', text: 'SIMULATED COHORT' }),
        ]));
      });
    }

    host.appendChild(el('div', { class: 'move' }, [
      el('b', { class: 'flat', text: r.position.percentile.toFixed(2) + '%' }),
      el('span', { text: 'percentile against ' + num(r.position.sample) + ' modelled profiles' }),
      el('span', { class: 'sim', text: 'SIMULATED COHORT' }),
    ]));
  }

  function targets(r) {
    const host = $('#rTargets');
    host.innerHTML = '';
    r.targets.forEach(t => {
      const card = el('div', {
        class: 'target' + (t.is_primary ? ' primary' : '') + (t.cleared ? ' cleared' : ''),
      });

      card.appendChild(el('div', { class: 'target-top' }, [
        el('div', {}, [
          el('div', { class: 'target-name', text: t.name }),
          el('div', { class: 'target-org', text: t.org.toUpperCase() }),
        ]),
        t.is_primary ? el('span', { class: 'state-key live', text: 'PRIMARY' }) : null,
      ]));

      if (t.comparable) {
        card.appendChild(el('div', { class: 'target-nums' }, [
          el('span', { class: 'now', style: 'color:' + (t.cleared ? 'var(--g4)' : 'var(--fg)'),
                       text: Math.round(t.your_value) }),
          el('span', { class: 'of', text: '/ cutoff ' + Math.round(t.cutoff) }),
        ]));
        card.appendChild(el('div', { class: 'bar tall' }, el('i', {
          dataset: { w: t.progress },
          style: 'background:' + (t.cleared ? 'var(--g4)' : t.progress > 80 ? 'var(--warn)' : 'var(--accent)'),
        })));
        card.appendChild(el('div', {
          class: 'target-gap' + (t.cleared ? ' done' : t.gap < 80 ? ' short' : ''),
          text: t.cleared
            ? 'Model puts you past the reported cutoff. Keep the margin.'
            : t.gap + ' score points short. Needs readiness index ' + t.index_needed +
              ' (you are ' + t.index_gap + ' below).',
        }));
      } else {
        card.appendChild(el('div', { class: 'target-nums' }, [
          el('span', { class: 'now dim', text: Math.round(t.cutoff) }),
          el('span', { class: 'of', text: '/ ' + (t.out_of || 300) + ' on BARC CBT' }),
        ]));
        card.appendChild(el('div', { class: 'target-gap', text: t.hint }));
      }

      if (t.history && t.history.length) {
        card.appendChild(el('div', { class: 'hist' },
          t.history.map(h => el('span', { text: h.year + ': ' + h.value }))));
      }
      if (t.note) card.appendChild(el('div', { class: 'target-note', text: t.note }));
      card.appendChild(el('div', { class: 'target-src', text: 'SOURCE: ' + (t.source || 'unspecified') }));
      host.appendChild(card);
    });
  }

  function trend(rows) {
    const svg = $('#rTrend');
    if (rows.length < 2) {
      svg.innerHTML = '<text class="trend-lab" x="14" y="26">' +
        'Not enough history yet. A point is recorded each day you use the app.</text>';
      return;
    }
    const W = 720, H = 200, pad = 34;
    const vals = rows.map(r => r.index_value);
    const lo = Math.max(0, Math.min(...vals) - 4);
    const hi = Math.min(100, Math.max(...vals) + 4);
    const span = (hi - lo) || 1;
    const x = i => pad + (i / (rows.length - 1)) * (W - pad * 2);
    const y = v => H - pad - ((v - lo) / span) * (H - pad * 2);

    let out = '';
    [0, .5, 1].forEach(f => {
      const yy = y(lo + span * f);
      out += '<line class="trend-axis" x1="' + pad + '" y1="' + yy.toFixed(1) +
             '" x2="' + (W - pad) + '" y2="' + yy.toFixed(1) + '"/>';
      out += '<text class="trend-lab" x="4" y="' + (yy + 3).toFixed(1) + '">' +
             (lo + span * f).toFixed(0) + '</text>';
    });
    const pts = rows.map((r, i) => x(i).toFixed(1) + ',' + y(r.index_value).toFixed(1));
    out += '<polygon class="trend-area" points="' + pad + ',' + (H - pad) + ' ' +
           pts.join(' ') + ' ' + (W - pad) + ',' + (H - pad) + '"/>';
    out += '<polyline class="trend-line" points="' + pts.join(' ') + '"/>';
    out += '<text class="trend-lab" x="' + pad + '" y="' + (H - 10) + '">' + rows[0].day + '</text>';
    out += '<text class="trend-lab" x="' + (W - pad) + '" y="' + (H - 10) +
           '" text-anchor="end">' + rows[rows.length - 1].day + '</text>';
    svg.innerHTML = out;
  }

  return { tab };
})();

/* ==========================================================================
   v3 additions - explainability. The index on its own is a vanity number; what
   makes it useful is being able to see which term is holding it down, what
   moved it since last time, and what finishing today's plan is arithmetically
   worth.
   ========================================================================== */
(function () {
  const { $, el, api, empty, growBars, hm } = GG;
  const base = GG.readiness;

  function contributions(st) {
    const host = $('#rContrib');
    if (!host) return;
    const rows = (st.readiness || {}).contributions || [];
    host.innerHTML = '';
    if (!rows.length) {
      host.appendChild(el('p', { class: 'dim small' }, ['Log a session to populate this.']));
      return;
    }
    host.appendChild(el('p', { class: 'dim small', style: 'margin:0 0 14px' }, [
      'The index is a weighted sum. The solid bar is what you have earned; the hatched ' +
      'part is the headroom still available in that term. The widest hatched bar is ' +
      'where your next hour buys the most.',
    ]));
    rows.forEach(c => {
      /* max_points is the cap for this term; guard every division so a missing
         field degrades to an empty bar instead of throwing. */
      const cap = Number(c.max_points || c.max || 0) || 1;
      const got = Number(c.points || 0);
      const gap = Math.max(0, Number(c.headroom === undefined ? cap - got : c.headroom));
      host.appendChild(el('div', { class: 'contrib' }, [
        el('div', { class: 'contrib-name' }, [
          c.label, el('em', {}, [c.measured || 'estimated']),
        ]),
        el('div', { class: 'contrib-track' }, [
          el('i', { class: 'got', dataset: { w: String(Math.round(got / cap * 100)) } }),
          el('i', { class: 'gap', dataset: { w: String(Math.round(gap / cap * 100)) } }),
        ]),
        el('div', { class: 'contrib-val' }, [
          el('b', { text: got.toFixed(1) }), ' / ' + cap.toFixed(0),
        ]),
      ]));
    });
  }

  function moved(st) {
    const host = $('#rMoved');
    if (!host) return;
    const mv = (st.readiness || {}).movement || {};
    host.innerHTML = '';
    host.appendChild(el('p', { class: 'headline', text: mv.headline || 'First reading recorded.' }));
    const rows = mv.why_moved || [];
    if (!rows.length) {
      host.appendChild(el('p', { class: 'dim small' }, [
        'Once there are two readings, this panel breaks the change down term by term, so ' +
        'a drop is never a mystery.',
      ]));
      return;
    }
    rows.forEach(r => {
      const dir = r.delta > 0.05 ? 'up' : r.delta < -0.05 ? 'down' : 'flat';
      host.appendChild(el('div', { class: 'moved' }, [
        el('span', { class: 'delta ' + dir },
          [(r.delta > 0 ? '+' : '') + Number(r.delta || 0).toFixed(2)]),
        el('span', {}, [el('b', {}, [r.label]), ' - ' + (r.note || '')]),
      ]));
    });
  }

  function projection(st) {
    const host = $('#rProjection');
    if (!host) return;
    const p = (st.readiness || {}).projection;
    host.innerHTML = '';
    if (!p || !(p.estimate || p.available)) {
      host.appendChild(el('p', { class: 'dim small' }, [
        (p && p.note) || 'Build today\u2019s plan and this shows what completing it is worth.',
      ]));
      return;
    }
    host.appendChild(el('div', { class: 'proj' }, [
      el('div', { class: 'proj-cell' }, [
        el('b', { class: 'delta up', text: '+' + Number(p.index_delta || 0).toFixed(2) }),
        el('span', {}, ['readiness index']),
      ]),
      el('div', { class: 'proj-cell' }, [
        el('b', { class: 'delta up', text: '+' + Math.round(p.score_delta || 0) }),
        el('span', {}, ['estimated score']),
      ]),
      el('div', { class: 'proj-cell' }, [
        el('b', { text: hm(p.minutes || 0) }),
        el('span', {}, ['time it asks for']),
      ]),
      el('div', { class: 'proj-cell' }, [
        el('b', { text: String(p.questions || 0) }),
        el('span', {}, ['questions']),
      ]),
    ]));
    host.appendChild(el('p', { class: 'why', style: 'margin-top:16px' }, [
      p.note || 'This is arithmetic on the same formula, not a forecast. It assumes you ' +
      'finish the plan and that your accuracy holds.',
    ]));
  }

  function feedback(st) {
    const host = $('#rFeedback');
    if (!host) return;
    const f = st.feedback || {};
    host.innerHTML = '';

    host.appendChild(el('p', { class: 'dim small', style: 'margin:0 0 14px' }, [
      'This is a preference-learning loop, not a language model. Every time you rate a ' +
      'suggestion the app nudges a weight, and those weights re-rank future advice. ' +
      'With no ratings at all, every weight is 1.0 and you get the plain rules engine.',
    ]));

    if (!f.active) {
      host.appendChild(el('p', { class: 'dim small' }, [
        f.note || 'No ratings yet. Use the buttons under any suggestion on the Today page.',
      ]));
      return;
    }

    host.appendChild(el('div', { class: 'proj' }, [
      el('div', { class: 'proj-cell' }, [el('b', { text: String(f.total) }), el('span', {}, ['ratings given'])]),
      el('div', { class: 'proj-cell' }, [
        el('b', { text: (f.helpful_pct === null ? '--' : f.helpful_pct + '%') }),
        el('span', {}, ['rated useful'])]),
      el('div', { class: 'proj-cell' }, [
        el('b', { text: (f.followed_pct === null ? '--' : f.followed_pct + '%') }),
        el('span', {}, ['actually followed'])]),
      el('div', { class: 'proj-cell' }, [
        el('b', { text: Number(f.difficulty_dial || 1).toFixed(2) + 'x' }),
        el('span', {}, ['difficulty dial'])]),
    ]));

    const learned = f.learned || [];
    if (learned.length) {
      host.appendChild(el('p', { class: 'dim small', style: 'margin:18px 0 8px' }, [
        'Learned weights. Above 1.0 means "show me more of this".',
      ]));
      learned.forEach(w => {
        const pos = Math.round(Math.min(100, (Number(w.weight || 1) / 1.9) * 100));
        host.appendChild(el('div', { class: 'learned' }, [
          el('span', {}, [w.label || (w.scope + ': ' + w.key)]),
          el('span', { class: 'mono small dim', text: (w.samples || 0) + ' rating(s)' }),
          el('div', { class: 'weight-bar' }, [
            el('i', { dataset: { w: String(pos) } }), el('b', {}),
          ]),
        ]));
      });
    }
    host.appendChild(el('p', { class: 'why', style: 'margin-top:16px' }, [
      'Weights are clamped between 0.35 and 1.90 and the step size shrinks as samples ' +
      'grow, so one grumpy afternoon cannot permanently break the recommendations.',
    ]));
  }

  const originalTab = base.tab;
  base.tab = function (st) {
    originalTab(st);
    const r = st.readiness || {};

    const bandHost = $('#rBand');
    if (bandHost) {
      bandHost.innerHTML = '';
      if (r.band) {
        bandHost.appendChild(el('span', { class: 'state ' + (r.band.cls || 'ok') }, [
          el('i', {}, ['#']), r.band.label,
        ]));
      }
      if (r.estimate_confidence) {
        bandHost.appendChild(el('span', {
          class: 'state later', title: r.estimate_confidence.note || '',
        }, [el('i', {}, ['?']), r.estimate_confidence.band + ' confidence']));
      }
    }

    contributions(st);
    moved(st);
    projection(st);
    feedback(st);
    growBars();
  };
})();
