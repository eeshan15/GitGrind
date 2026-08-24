/* Profile: who you are, and the three things about your practice that are worth
   seeing at a glance rather than digging for.

   Everything here reads from state. Nothing is computed in the browser beyond
   turning numbers into geometry, so the page cannot disagree with the rest of
   the app about what your week looked like. */
window.GG = window.GG || {};
GG.profile = (function () {
  const { $, el, num } = GG;

  /* ------------------------------- identity ------------------------------ */
  const SOCIALS = [
    ['github', 'GitHub', 'https://github.com/'],
    ['linkedin', 'LinkedIn', 'https://www.linkedin.com/in/'],
    ['x', 'X', 'https://x.com/'],
    ['website', 'Website', ''],
  ];

  function socialUrl(kind, value) {
    const v = String(value || '').trim();
    if (!v) return '';
    if (/^https?:\/\//i.test(v)) return v;
    const base = (SOCIALS.find(s => s[0] === kind) || [])[2] || '';
    if (!base) return 'https://' + v.replace(/^\/+/, '');
    return base + v.replace(/^@/, '');
  }

  function identity(st) {
    const host = $('#profIdentity');
    if (!host) return;
    const p = st.profile || {};
    host.innerHTML = '';

    const avatar = el('div', { class: 'prof-avatar' });
    if (p.avatar) {
      avatar.appendChild(el('img', { src: p.avatar, alt: '' }));
      avatar.classList.add('has-photo');
      avatar.title = 'Click to enlarge';
      avatar.onclick = () => GG.avatarZoom(p.avatar, avatar);
    } else {
      /* Initials rather than a stock silhouette: it is obvious that nothing has
         been uploaded, and it still looks deliberate. */
      const initials = (p.display_name || 'You')
        .split(/\s+/).filter(Boolean).slice(0, 2)
        .map(w => w[0].toUpperCase()).join('');
      avatar.appendChild(el('span', { class: 'prof-initials', text: initials }));
    }

    const lines = el('div', { class: 'prof-lines' }, [
      el('h2', { text: p.display_name || 'Unnamed' }),
      el('p', { class: 'dim', text: [p.handle && '@' + p.handle, p.location]
        .filter(Boolean).join('  ·  ') }),
    ]);
    if (p.bio) lines.appendChild(el('p', { class: 'prof-bio', text: p.bio }));

    const socials = el('div', { class: 'prof-socials' });
    SOCIALS.forEach(([kind, label]) => {
      const raw = (p.socials || {})[kind];
      if (!raw) return;
      socials.appendChild(el('a', {
        class: 'chip', href: socialUrl(kind, raw),
        target: '_blank', rel: 'noopener noreferrer',
      }, [label]));
    });
    if (socials.childNodes.length) lines.appendChild(socials);

    host.appendChild(avatar);
    host.appendChild(lines);
    host.appendChild(el('button', {
      class: 'btn', text: 'Edit profile', onclick: () => GG.app.openProfile(),
    }));
  }

  /* ---------------------------- weekly minutes --------------------------- */
  function weekly(st) {
    const host = $('#profWeekly');
    if (!host) return;
    host.innerHTML = '';
    const rows = (st.profile_stats || {}).weekly_minutes || [];
    if (!rows.length) {
      host.appendChild(el('p', { class: 'dim',
        text: 'No sessions logged yet. Log one and this fills in.' }));
      return;
    }
    const peak = Math.max.apply(null, rows.map(r => r.minutes)) || 1;
    const target = (st.profile || {}).daily_target_mins || 0;
    const weekTarget = target * 7;

    /* Scale against whichever is larger. If the target is off the top of the
       chart the bars have nothing to be short *of*, and a bad week looks the
       same as a good one. */
    const top = Math.max(peak, weekTarget || 0) || 1;

    const chart = el('div', { class: 'pbar-chart', role: 'img',
      'aria-label': 'Minutes studied per week over the last ' + rows.length + ' weeks' });

    if (weekTarget) {
      /* The plot band runs from 1.4rem off the bottom (week label) up to
         2.25rem off the top (chart padding + the value label), so the line has
         to be placed inside that band rather than against the whole card. */
      const frac = Math.min(1, weekTarget / top);
      chart.appendChild(el('div', {
        class: 'pbar-goal',
        style: 'bottom:calc(1.4rem + (100% - 3.65rem) * ' + frac.toFixed(4) + ')',
      }, [el('span', { text: 'target ' + num(weekTarget) + 'm' })]));
    }

    rows.forEach(r => {
      const pct = r.minutes ? Math.max(1.5, (r.minutes / top) * 100) : 0;
      const col = el('div', { class: 'pbar-col' + (r.minutes === peak ? ' best' : '') }, [
        el('span', { class: 'pbar-val', text: r.minutes ? num(r.minutes) : '' }),
        el('div', { class: 'pbar-track' }, [
          el('div', {
            class: 'pbar-fill' + (weekTarget && r.minutes >= weekTarget ? ' hit' : ''),
            style: 'height:' + pct.toFixed(2) + '%',
            title: r.week_start + ': ' + r.minutes + ' min',
          }),
        ]),
        el('span', { class: 'pbar-label', text: r.label }),
      ]);
      chart.appendChild(col);
    });
    host.appendChild(chart);

    const total = rows.reduce((a, r) => a + r.minutes, 0);
    const active = rows.filter(r => r.minutes > 0).length;
    const hit = weekTarget ? rows.filter(r => r.minutes >= weekTarget).length : 0;
    host.appendChild(el('p', { class: 'dim small', text:
      num(Math.round(total / 60)) + ' h across ' + active + ' active week(s)' +
      (weekTarget
        ? '. ' + hit + ' of ' + rows.length + ' weeks cleared the ' +
          num(weekTarget) + ' min target.'
        : '.') }));
  }

  /* -------------------------- difficulty split --------------------------- */
  function difficulty(st) {
    const host = $('#profDifficulty');
    if (!host) return;
    host.innerHTML = '';
    const rows = ((st.profile_stats || {}).difficulty || [])
      .filter(r => r.attempts > 0);
    const total = rows.reduce((a, r) => a + r.attempts, 0);
    if (!total) {
      host.appendChild(el('p', { class: 'dim',
        text: 'No attempts yet. Practise a set and this fills in.' }));
      return;
    }

    /* An SVG ring drawn from stroke-dasharray: no canvas, no library, and it
       scales with the card instead of being a fixed bitmap. */
    const R = 54, C = 2 * Math.PI * R;
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 140 140');
    svg.setAttribute('class', 'donut');
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label',
      rows.map(r => r.band + ' ' + r.share + '%').join(', '));
    let offset = 0;
    rows.forEach(r => {
      const len = (r.attempts / total) * C;
      const seg = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      seg.setAttribute('cx', '70');
      seg.setAttribute('cy', '70');
      seg.setAttribute('r', String(R));
      seg.setAttribute('class', 'donut-seg band-' + r.band);
      seg.setAttribute('stroke-dasharray', len + ' ' + (C - len));
      seg.setAttribute('stroke-dashoffset', String(-offset));
      svg.appendChild(seg);
      offset += len;
    });
    const mid = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    mid.setAttribute('x', '70');
    mid.setAttribute('y', '76');
    mid.setAttribute('class', 'donut-mid');
    mid.textContent = num(total);
    svg.appendChild(mid);

    const legend = el('ul', { class: 'donut-legend' });
    rows.forEach(r => {
      legend.appendChild(el('li', { class: 'band-' + r.band }, [
        el('b', { text: r.band }),
        el('span', { text: num(r.attempts) + '  ·  ' + r.share + '%' }),
        /* Accuracy alongside share, because "most of my practice is medium" and
           "I am weakest on medium" are different facts and both matter. */
        el('span', { class: 'dim', text: r.accuracy + '% correct' }),
      ]));
    });

    host.appendChild(svg);
    host.appendChild(legend);
    if (rows.some(r => r.band === 'unknown')) {
      host.appendChild(el('p', { class: 'dim small', text:
        'Unknown means the question has left the bank since you answered it.' }));
    }
  }

  /* ----------------------------- revision list --------------------------- */
  /* Reads state.revision_list, NOT state.revision_queue. The queue is the
     spacing engine and holds every topic you have started plus every question
     you have got wrong; this list is only what you bookmarked. */
  function revision(st) {
    const host = $('#profRevision');
    if (!host) return;
    host.innerHTML = '';
    const rows = st.revision_list || [];

    if (!rows.length) {
      host.appendChild(el('p', { class: 'dim', text:
        'Nothing bookmarked yet. Press the bookmark on any question - in Practice, ' +
        'in the daily question or in the Bank - and it lands here.' }));
      return;
    }

    const due = rows.filter(r => r.is_due).length;
    const head = el('div', { class: 'rev-head' }, [
      el('span', { class: 'dim small', text:
        rows.length + ' bookmarked' + (due ? '  \u00b7  ' + due + ' due today or earlier' : '') }),
      el('button', {
        class: 'btn btn-sm btn-primary',
        onclick: () => GG.practice.startSet({
          questionIds: rows.filter(r => !r.missing).map(r => r.question_id),
          purpose: 'review',
          reason: 'Your bookmarked questions',
        }),
      }, ['Revise these']),
    ]);
    host.appendChild(head);

    const list = el('ul', { class: 'rev-list' });
    rows.forEach(r => {
      const overdue = r.is_due && r.due_day;
      const meta = [r.subject_slug, r.topic_slug, r.difficulty,
        r.marks ? r.marks + 'm' : ''].filter(Boolean).join('  \u00b7  ');

      /* Three different states, and saying which is which matters: scheduled,
         retired by two clean solves, or gone from the bank entirely. */
      let when, whenCls;
      if (r.missing) { when = 'not in bank'; whenCls = 'dim small'; }
      else if (!r.scheduled) { when = 'mastered'; whenCls = 'dim small'; }
      else { when = r.due_day || ''; whenCls = 'mono small'; }

      const li = el('li', { class: overdue ? 'overdue' : '' }, [
        el('div', { class: 'rev-main' }, [
          el('b', { text: r.label }),
          el('span', { class: 'dim small', text: meta }),
        ]),
        el('span', { class: whenCls, text: when }),
        el('span', { class: 'dim small', text:
          'rep ' + (r.reps || 0) + (r.lapses ? ', ' + r.lapses + ' lapse(s)' : '') }),
        el('button', {
          class: 'btn btn-sm rev-drop', title: 'Remove from the revision list',
          onclick: async ev => {
            const btn = ev.currentTarget;
            btn.disabled = true;
            try {
              const out = await GG.api('/questions/save',
                { body: { question_id: r.question_id, saved: false } });
              if (out && out.state) { GG.S.state = out.state; GG.profile.tab(out.state); }
              GG.toast('Removed from revision list');
            } catch (e) {
              btn.disabled = false;
              GG.toast('Could not remove', e.message, 'bad');
            }
          },
        }, ['Remove']),
      ]);
      list.appendChild(li);
    });
    host.appendChild(list);
  }

  function tab(st) {
    identity(st);
    weekly(st);
    difficulty(st);
    revision(st);
  }

  return { tab, socialUrl };
})();