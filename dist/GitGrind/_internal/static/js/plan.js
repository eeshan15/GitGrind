/* ==========================================================================
   GG.plan - the command centre.

   This module owns everything that answers "what do I do next?": the hero card,
   today's missions, the generated plan, the revision queue, the risk/payback
   pair, the mastery map and the recommendation list.

   Design rule followed throughout: never show a number without saying what it
   means and what to do about it. Every card carries a reason line.
   ========================================================================== */
window.GG = window.GG || {};
GG.plan = (function () {
  const { $, el, esc, hm, num, api, toast, band, clamp, empty, growBars, announce } = GG;

  /* --------------------------------------------------------------- hero --- */
  function hero(st) {
    const host = $('#heroAction');
    const side = $('#heroSide');
    if (!host) return;
    host.innerHTML = '';
    side.innerHTML = '';

    const a = st.next_action;
    if (!a) {
      host.appendChild(el('div', { class: 'next-card calm' }, [
        el('div', { class: 'next-kicker' }, ['Nothing urgent']),
        el('h3', { class: 'next-title', text: 'You are on top of it' }),
        el('p', { class: 'next-detail' }, ['Coverage, accuracy, volume and retention are all ' +
          'tracking. Pick any subject and keep the streak alive.']),
        el('div', { class: 'next-foot' }, [
          el('button', { class: 'btn btn-primary', onclick: () => GG.app.openLog() },
            ['Log a session']),
        ]),
      ]));
    } else {
      const urgent = a.band === 'now';
      const card = el('div', { class: 'next-card' + (urgent ? ' urgent' : '') });
      card.appendChild(el('div', { class: 'next-kicker' }, [
        el('span', { class: 'state ' + a.band }, [
          el('i', {}, [urgent ? '!' : a.band === 'soon' ? '~' : '.']),
          a.band === 'now' ? 'do this now' : a.band === 'soon' ? 'do this today' : 'when you can',
        ]),
        el('span', {}, ['next action']),
      ]));
      card.appendChild(el('h3', { class: 'next-title', text: a.title }));
      card.appendChild(el('p', { class: 'next-detail', text: a.detail }));
      if (a.reason) {
        card.appendChild(el('p', { class: 'why' }, [el('b', {}, ['Why: ']), a.reason]));
      }
      const foot = el('div', { class: 'next-foot' });
      foot.appendChild(el('button', {
        class: 'btn btn-primary',
        onclick: () => act(a),
      }, [a.action_label || 'Start']));
      if (a.expected) {
        foot.appendChild(el('span', { class: 'dim small' }, ['Expected: ' + a.expected]));
      }
      card.appendChild(foot);

      /* The runner-up, so the ranking is auditable rather than magic. */
      if (a.why_not) {
        card.appendChild(el('p', { class: 'next-alt', text: a.why_not }));
      }
      card.appendChild(voteRow(a, true));
      host.appendChild(card);
    }

    /* three tiles: today's minutes, retention pressure, readiness */
    const m = st.metrics || {};
    const target = (st.profile && st.profile.daily_target_minutes) || 240;
    side.appendChild(tile(
      hm(st.today_minutes || 0),
      st.today_minutes >= target ? 'good' : st.today_minutes ? 'mid' : 'bad',
      'Today', 'target ' + hm(target) + ' - ' + Math.round((st.today_minutes || 0) / target * 100) + '% there'));

    const debt = st.debt || {};
    side.appendChild(tile(
      String(debt.due_today || 0),
      debt.pressure > 65 ? 'bad' : debt.pressure > 30 ? 'mid' : 'good',
      'Due for revision',
      debt.overdue ? debt.overdue + ' overdue, oldest ' + debt.oldest_days + 'd'
                   : 'schedule is clear'));

    const r = st.readiness || {};
    side.appendChild(tile(
      String(Math.round(r.index || 0)),
      (r.index || 0) >= 65 ? 'good' : (r.index || 0) >= 40 ? 'mid' : 'bad',
      'Readiness index',
      (r.band && r.band.label ? r.band.label + ' - ' : '') + 'est. score ' +
        (r.est_score === undefined ? '--' : Math.round(r.est_score))));
  }

  function tile(number, tone, label, sub) {
    return el('div', { class: 'hero-tile' }, [
      el('div', { class: 'ht-num ' + tone, text: number }),
      el('div', { class: 'ht-body' }, [
        el('div', { class: 'ht-label', text: label }),
        el('div', { class: 'ht-sub', text: sub }),
      ]),
    ]);
  }

  /* Route a recommendation's action to the right part of the app. */
  function act(a) {
    const action = a.action || {};
    if (action.route === 'quiz' || action.mode) {
      GG.practice.startSet({ purpose: action.mode || 'mixed', subject: a.subject_slug || '',
                             topic: a.topic_slug || '' });
      rate(a, 'followed');
      return;
    }
    if (action.route === 'plan-block') { startBlock(action.key || ''); rate(a, 'followed'); return; }
    if (action.route === 'log') { GG.app.openLog(a.subject_slug || ''); rate(a, 'followed'); return; }
    if (action.route === 'subject' && a.subject_slug) {
      const s = (GG.S.state.subjects || []).find(x => x.slug === a.subject_slug);
      if (s) { location.hash = '#/subject/' + s.id; rate(a, 'followed'); return; }
    }
    if (action.route) { location.hash = '#/' + action.route; rate(a, 'followed'); return; }
    GG.app.openLog(a.subject_slug || '');
  }

  /* --------------------------------------------------------- feedback ----- */
  /* Rating a suggestion is the whole learning loop. Keep it to one click. */
  function voteRow(a, compact) {
    const labels = ((GG.S.state.feedback || {}).answer_labels) || {};
    const opts = compact
      ? [['helpful', 'Useful'], ['wrong_priority', 'Not the priority'], ['chose_other', 'Doing something else']]
      : [['helpful', 'Useful'], ['not_helpful', 'Not useful'], ['wrong_priority', 'Wrong priority']];
    const row = el('div', { class: 'vote' });
    row.appendChild(el('span', { class: 'dim small', style: 'margin-right:4px' }, ['Was this right?']));
    opts.forEach(([key, text]) => {
      const b = el('button', { type: 'button', title: labels[key] || text }, [text]);
      b.onclick = () => {
        row.querySelectorAll('button').forEach(x => x.classList.remove('picked', 'neg'));
        b.classList.add('picked');
        if (key !== 'helpful') b.classList.add('neg');
        rate(a, key);
      };
      row.appendChild(b);
    });
    return row;
  }

  async function rate(a, answer) {
    try {
      await api('/feedback', {
        method: 'POST',
        body: {
          rec_id: a.id || null, kind: 'recommendation', slug: a.slug || '',
          answer: answer, rec_kind: a.kind || '', topic: a.topic_slug || '',
        },
      });
      if (answer !== 'followed') {
        toast('Noted', 'Similar suggestions will be ranked ' +
          (answer === 'helpful' ? 'higher' : 'lower') + ' from now on.');
      }
    } catch (e) { /* a failed rating must never block the actual study action */ }
  }

  /* ----------------------------------------------------------- missions --- */
  function missions(st, hostId) {
    const host = $(hostId || '#missionStrip');
    if (!host) return;
    const ms = st.missions || { items: [] };
    host.innerHTML = '';
    const sum = $('#missionSummary');
    if (sum && hostId !== '#missionStripFull') sum.textContent = ms.headline || '';

    (ms.items || []).forEach(m => {
      /* progress arrives as a 0-1 fraction; fall back to value/target so a
         mission without one still draws a bar. */
      const frac = m.target ? (m.value || 0) / m.target : (m.progress || 0);
      const pctDone = clamp(Math.round(frac * 100), 0, 100);
      host.appendChild(el('div', { class: 'mission' + (m.done ? ' done' : '') }, [
        el('span', { class: 'mission-tick', text: 'OK' }),
        el('div', { class: 'mission-scope', text: m.scope === 'week' ? 'this week' : 'today' }),
        el('div', { class: 'mission-top' }, [
          el('span', { class: 'mission-label', text: m.label }),
          el('span', { class: 'mission-num',
                       text: (m.value || 0) + '/' + (m.target || 0) + (m.unit ? ' ' + m.unit : '') }),
        ]),
        el('div', { class: 'track' }, [el('i', { dataset: { w: String(pctDone) } })]),
        m.reward ? el('div', { class: 'dim small', style: 'margin-top:8px', text: m.reward }) : '',
      ]));
    });

    if (!(ms.items || []).length) {
      host.appendChild(empty('--', 'No missions yet',
        'Missions appear once the app knows your daily target. Set one in your profile.'));
    }
  }

  /* --------------------------------------------------------------- plan --- */
  function plan(st) {
    const host = $('#planCard');
    if (!host) return;
    const p = st.plan;
    host.innerHTML = '';

    const meta = $('#planMeta');
    if (meta && p) {
      meta.textContent = hm(p.total_minutes || 0) + ' / ' + (p.total_questions || 0) + 'q';
    }

    if (!p || !(p.blocks || []).length) {
      host.appendChild(el('div', { class: 'plan-shell' }, [
        empty('[]', 'No plan for today',
          'The planner builds a plan from your revision schedule, weakest topics and ' +
          'remaining syllabus. Press Rebuild to generate one.',
          el('button', { class: 'btn btn-primary', onclick: regenerate }, ['Build today\u2019s plan'])),
      ]));
      return;
    }

    const shell = el('div', { class: 'plan-shell' });
    shell.appendChild(el('div', { class: 'plan-head' }, [
      el('p', { class: 'plan-why', text: p.reason || '' }),
      el('div', { class: 'plan-prog' }, [
        el('b', { text: p.done_count + '/' + p.block_count }),
        el('div', { class: 'plan-bar' }, [el('i', { dataset: { w: String(p.progress_pct || 0) } })]),
      ]),
    ]));

    (p.blocks || []).forEach(b => shell.appendChild(blockRow(b, p)));

    /* Rating the plan as a whole is a separate, coarser signal from rating each
       recommendation, and it is what tunes plan length. */
    if (p.done_count >= p.block_count && p.block_count) {
      shell.appendChild(el('div', { class: 'block' }, [
        el('div', { class: 'block-when' }, ['--']),
        el('div', {}, [
          el('div', { class: 'block-title' }, ['Plan finished. Was it the right size?']),
          el('p', { class: 'block-reason' }, ['This tunes how much the planner gives you tomorrow.']),
        ]),
        el('div', { class: 'block-act' }, [
          el('button', { class: 'btn btn-sm', onclick: () => ratePlan('too_long') }, ['Too much']),
          el('button', { class: 'btn btn-sm', onclick: () => ratePlan('helpful') }, ['Just right']),
          el('button', { class: 'btn btn-sm', onclick: () => ratePlan('too_short') }, ['Too little']),
        ]),
      ]));
    }
    host.appendChild(shell);
  }

  function blockRow(b, p) {
    const done = !!b.done;
    const act = el('div', { class: 'block-act' });
    if (done) {
      act.appendChild(el('span', { class: 'state ok' }, [el('i', {}, ['#']), 'done']));
    } else if (b.count > 0) {
      act.appendChild(el('button', {
        class: 'btn btn-primary btn-sm', onclick: () => startBlock(b.key),
      }, ['Start']));
      act.appendChild(el('button', {
        class: 'btn btn-sm', onclick: () => completeBlock(b.key),
      }, ['Mark done']));
    } else {
      act.appendChild(el('button', {
        class: 'btn btn-sm', onclick: () => GG.app.openLog(b.subject_slug || ''),
      }, ['Log it']));
      act.appendChild(el('button', {
        class: 'btn btn-sm', onclick: () => completeBlock(b.key),
      }, ['Mark done']));
    }

    const title = el('div', { class: 'block-title' }, [b.label]);
    if (b.purpose) {
      title.appendChild(el('span', { class: 'state later' }, [
        el('i', {}, ['>']), (GG.S.state.purposes || {})[b.purpose] || b.purpose,
      ]));
    }

    const body = el('div', {}, [
      title,
      el('div', { class: 'block-meta' }, [
        hm(b.minutes) + (b.count ? ' - ' + b.count + ' questions' : ' - reading and notes'),
      ]),
    ]);
    if (b.reason) body.appendChild(el('p', { class: 'block-reason', text: b.reason }));
    if (b.fixing || b.aim) {
      body.appendChild(el('p', { class: 'block-aim' }, [
        b.fixing ? 'Fixing: ' + b.fixing + '. ' : '',
        b.aim ? el('b', {}, ['Aim: ' + b.aim]) : '',
      ]));
    }

    return el('div', { class: 'block' + (done ? ' done' : '') }, [
      el('div', { class: 'block-when' }, [
        el('b', { text: b.slot || String((p.blocks || []).indexOf(b) + 1) }),
        b.slot ? '' : 'block',
      ]),
      body, act,
    ]);
  }

  async function regenerate() {
    try {
      await api('/plan/generate', { method: 'POST', body: { force: true } });
      toast('Plan rebuilt', 'Built from your current revision debt and weak topics.');
      GG.app.reload();
    } catch (e) { toast('Could not rebuild', e.message, 'bad'); }
  }

  async function startBlock(key) {
    try {
      const out = await api('/plan/block/start', { method: 'POST', body: { key: key } });
      if (out.quiz) {
        GG.practice.open(out.quiz, { planKey: key });
      } else {
        toast('Nothing to serve', 'That block has no questions in the bank yet. ' +
          'Log it manually once you have studied it.', 'warn');
      }
    } catch (e) { toast('Could not start', e.message, 'bad'); }
  }

  async function completeBlock(key) {
    try {
      await api('/plan/block/complete', { method: 'POST', body: { key: key } });
      announce('Block marked done.');
      GG.app.reload();
    } catch (e) { toast('Could not update', e.message, 'bad'); }
  }

  async function ratePlan(answer) {
    try {
      await api('/plan/rate', { method: 'POST', body: { answer: answer } });
      toast('Thanks', 'Tomorrow\u2019s plan will be sized accordingly.');
      GG.app.reload();
    } catch (e) { toast('Could not save', e.message, 'bad'); }
  }

  /* ----------------------------------------------------- revision queue --- */
  function revision(st) {
    const host = $('#revisionPanel');
    if (!host) return;
    const q = st.revision_queue || [];
    const debt = st.debt || {};
    host.innerHTML = '';

    const shell = el('div', { class: 'queue-shell' });
    shell.appendChild(el('div', { class: 'queue-head' }, [
      el('h3', {}, ['Revision queue']),
      el('div', { class: 'row-gap' }, [
        el('span', { class: 'dim small mono' }, [debt.due_today + ' due, ' + debt.overdue + ' overdue']),
        q.length ? el('button', {
          class: 'btn btn-sm btn-primary',
          onclick: () => GG.practice.startSet({ purpose: 'review' }),
        }, ['Revise now']) : '',
      ]),
    ]));

    if (!q.length) {
      shell.appendChild(empty('OK', 'Schedule is clear',
        'Nothing is due. Items enter this queue when you mark a topic done or get a ' +
        'question wrong, and come back on a spacing schedule that stretches as you ' +
        'keep getting them right.'));
      host.appendChild(shell);
      return;
    }

    const list = el('div', { class: 'queue-list' });
    q.slice(0, 12).forEach(it => {
      const b = band(it.strength_pct);
      const sub = it.state === 'overdue'
        ? 'overdue by ' + it.overdue_days + 'd'
        : it.is_due ? 'due today'
        : 'in ' + it.due_in_days + 'd';
      list.appendChild(el('div', { class: 'qrow' }, [
        el('div', {}, [
          el('div', { class: 'qrow-name', text: it.topic_name || it.label }),
          el('div', { class: 'qrow-sub' }, [
            (it.subject_name || '') + ' - ' + sub + ' - rep ' + it.reps +
            (it.lapses ? ', ' + it.lapses + ' lapse' + (it.lapses > 1 ? 's' : '') : ''),
          ]),
        ]),
        el('div', { class: 'qrow-strength' }, [
          el('span', { class: 'state ' + b.cls, title: 'Estimated retention' },
            [el('i', {}, [b.glyph]), it.strength_pct + '%']),
          el('div', { class: 'strength-bar ' + (it.strength_pct < 40 ? 'low' : it.strength_pct < 70 ? 'mid' : '') },
            [el('i', { dataset: { w: String(it.strength_pct) } })]),
          el('button', {
            class: 'btn btn-sm', title: 'Push this back a day',
            onclick: () => skip(it.id),
          }, ['Later']),
        ]),
      ]));
    });
    shell.appendChild(list);

    if (q.length > 12) {
      shell.appendChild(el('div', { class: 'queue-head', style: 'border-top:1px solid var(--line-soft);border-bottom:0' }, [
        el('span', { class: 'dim small' }, ['+' + (q.length - 12) + ' more scheduled']),
      ]));
    }
    host.appendChild(shell);
  }

  async function skip(id) {
    try {
      await api('/revision/skip', { method: 'POST', body: { id: id } });
      GG.app.reload();
    } catch (e) { toast('Could not postpone', e.message, 'bad'); }
  }

  /* --------------------------------------------------- risk and payback --- */
  function risk(st) {
    const host = $('#riskPanel');
    if (!host) return;
    const r = st.readiness || {};
    host.innerHTML = '';

    const rows = [];
    if (r.risk && r.risk.name) {
      rows.push(el('div', { class: 'risk-card' }, [
        el('div', { class: 'risk-kicker' }, ['Biggest risk right now']),
        el('h3', { class: 'risk-name', text: r.risk.name }),
        el('p', { class: 'risk-why', text: r.risk.why || '' }),
        el('button', {
          class: 'btn btn-primary btn-sm',
          onclick: () => GG.practice.startSet({ purpose: 'weak', topic: r.risk.topic || '' }),
        }, ['Drill this topic']),
      ]));
    }
    if (r.recovery && r.recovery.name) {
      rows.push(el('div', { class: 'risk-card payback' }, [
        el('div', { class: 'risk-kicker' }, ['Cheapest points on the table']),
        el('h3', { class: 'risk-name', text: r.recovery.name }),
        el('p', { class: 'risk-why', text: r.recovery.why || '' }),
        el('button', {
          class: 'btn btn-sm',
          onclick: () => GG.app.openLog(r.recovery.subject || ''),
        }, ['Study it next']),
      ]));
    }
    if (!rows.length) {
      rows.push(el('div', { class: 'card' }, [
        empty('--', 'Not enough data yet',
          'Once you have a few graded questions the app can name your riskiest topic ' +
          'and the one with the cheapest payback.'),
      ]));
    }
    rows.forEach((n, i) => { if (i) n.style.marginTop = 'var(--s3)'; host.appendChild(n); });
  }

  /* ------------------------------------------------------ mastery map ----- */
  function heatmap(st) {
    const host = $('#heatmapHost');
    if (!host) return;
    host.innerHTML = '';
    const rows = st.heatmap || [];
    if (!rows.length) {
      host.appendChild(empty('##', 'Mastery map is empty',
        'Every square is one syllabus topic. They fill in as you study and answer ' +
        'questions, so this is your syllabus at a glance.'));
      return;
    }
    const note = $('#heatLegendNote');
    if (note) note.textContent = 'One square per topic, darkest problem first';

    rows.forEach(sub => {
      const cells = el('div', { class: 'heat-cells' });
      (sub.cells || []).forEach(c => {
        const b = band(c.health);
        /* The heat level is derived from the health band rather than sent down,
           so the map and every other band indicator can never disagree. */
        const level = c.level !== undefined ? c.level
          : c.attempts === 0 && !c.strength ? 0
          : b.cls === 'critical' ? 1 : b.cls === 'weak' ? 2 : b.cls === 'ok' ? 3 : 4;
        const cell = el('button', {
          class: 'heat h' + level, type: 'button',
          dataset: { g: b.glyph },
          'aria-label': c.name + ': ' + b.label + ', health ' + c.health + '%',
        });
        GG.bindTip(cell, () =>
          '<b>' + esc(c.name) + '</b><br>' + b.label + ' - health ' + c.health + '%' +
          '<br>' + (c.attempts ? (c.accuracy === null ? '--' : c.accuracy) + '% over ' + c.attempts + ' questions'
                               : 'no questions attempted') +
          (c.bank ? '<br>' + c.bank + ' in bank' : '<br>no questions in bank') +
          '<br><span class="dim">click to drill</span>');
        cell.onclick = () => GG.practice.startSet({ purpose: 'weak', topic: c.topic });
        cells.appendChild(cell);
      });
      host.appendChild(el('div', { class: 'heat-row' }, [
        el('div', { class: 'heat-name' }, [
          sub.name, ' ', el('span', {}, [sub.marks + 'm - ' + sub.avg_health + '%']),
        ]),
        cells,
      ]));
    });

    host.appendChild(el('div', { class: 'heat-legend' }, [
      el('span', { class: 'dim small' }, ['Bands:']),
      legend('critical', '!', 'critical'), legend('weak', '~', 'weak'),
      legend('ok', '+', 'ok'), legend('strong', '#', 'strong'),
      el('span', { class: 'dim small' }, ['- click any square to practise that topic']),
    ]));
  }

  const legend = (cls, glyph, label) =>
    el('span', { class: 'state ' + cls }, [el('i', {}, [glyph]), label]);

  /* -------------------------------------------------- recommendations ----- */
  function recommendations(st) {
    const host = $('#recList');
    if (!host) return;
    host.innerHTML = '';
    const recs = st.recommendations || [];
    if (!recs.length) {
      host.appendChild(el('div', { class: 'card' }, [
        empty('--', 'Nothing flagged',
          'Coverage, accuracy, volume, consistency and retention are all tracking. ' +
          'Keep logging and this list will fill in when something slips.'),
      ]));
      return;
    }
    recs.forEach(r => {
      const card = el('div', { class: 'rec' });
      card.appendChild(el('div', { class: 'rec-top' }, [
        el('span', { class: 'state ' + r.band }, [
          el('i', {}, [r.band === 'now' ? '!' : r.band === 'soon' ? '~' : '.']), r.band,
        ]),
        el('h3', { class: 'rec-title', text: r.title }),
      ]));
      card.appendChild(el('p', { class: 'rec-detail', text: r.detail }));
      if (r.reason) card.appendChild(el('p', { class: 'why' }, [el('b', {}, ['Why: ']), r.reason]));
      if (r.expected) {
        card.appendChild(el('p', { class: 'rec-expect' }, ['Expected: ', el('b', {}, [r.expected])]));
      }
      if (r.learned_weight && Math.abs(r.learned_weight - 1) > 0.04) {
        card.appendChild(el('p', { class: 'why-picked' }, [
          'Ranked ' + (r.learned_weight > 1 ? 'up' : 'down') + ' (x' +
          Number(r.learned_weight || 1).toFixed(2) + ') from how you have rated this kind of advice.',
        ]));
      }
      card.appendChild(el('div', { class: 'rec-foot' }, [
        el('button', { class: 'btn btn-sm btn-primary', onclick: () => act(r) },
          [r.action_label || 'Do it']),
        voteRow(r, false),
      ]));
      host.appendChild(card);
    });
  }

  /* --------------------------------------------------------- side panels -- */
  function side(st) {
    const debt = st.debt || {};
    const host = $('#miniDebt');
    if (host) {
      host.innerHTML = '';
      const cls = debt.pressure > 65 ? '' : debt.pressure > 30 ? 'mid' : 'low';
      host.appendChild(el('div', { class: 'row' }, [
        'Due today', el('b', { text: String(debt.due_today || 0) })]));
      host.appendChild(el('div', { class: 'row' }, [
        'Overdue', el('b', { text: String(debt.overdue || 0) })]));
      host.appendChild(el('div', { class: 'row' }, [
        'Oldest', el('b', { text: (debt.oldest_days || 0) + 'd' })]));
      host.appendChild(el('div', { class: 'pressure ' + cls },
        [el('i', { dataset: { w: String(debt.pressure || 0) } })]));
      host.appendChild(el('div', { class: 'dim small', style: 'margin-top:6px' }, [
        debt.worst && debt.worst.name
          ? 'Worst: ' + debt.worst.name + ' (' + debt.worst.days + 'd late)'
          : 'Nothing overdue.',
      ]));
    }

    const q = st.session_quality || {};
    const ql = $('#qualityLine');
    if (ql) {
      ql.textContent = q.available
        ? 'Session quality ' + q.score + '/100 - ' + (q.note || '')
        : 'Log a session to see today\u2019s quality score.';
    }

    const due = $('#duePill');
    if (due) {
      due.hidden = !(debt.due_today > 0);
      $('#dueNum').textContent = debt.due_today || 0;
    }
  }

  /* ------------------------------------------------------------- paint ---- */
  function paint(st) {
    hero(st);
    missions(st);
    plan(st);
    revision(st);
    risk(st);
    heatmap(st);
    recommendations(st);
    side(st);
    growBars();
  }

  return { paint, missions, startBlock, regenerate, rate, voteRow, act };
})();
