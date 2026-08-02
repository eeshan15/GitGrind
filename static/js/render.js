/* Rendering for sidebar, overview, subjects, achievements, activity, detail. */
GG.render = (function () {
  'use strict';
  const { $, $$, el, hm, ago, nice, num, colorOf, countTo, growBars, bindTip } = GG;

  /* ============================== sidebar ============================== */
  function sidebar(st) {
    const p = st.profile, m = st.metrics;
    $('#displayName').textContent = p.display_name || 'GATE Aspirant';
    $('#handle').textContent = p.handle || '';
    $('#bio').textContent = p.bio || '';
    $('#mLocation').textContent = p.location || '--';
    $('#mExam').textContent = p.exam_name + (p.exam_date ? ' / ' + nice(p.exam_date) : '');

    const primary = (st.readiness.targets || []).find(t => t.is_primary);
    $('#mTarget').textContent = primary ? primary.name : '--';

    const initials = (p.display_name || 'GG').trim().split(/\s+/)
      .slice(0, 2).map(w => w[0]).join('').toUpperCase() || 'GG';
    $('#avatarGlyph').textContent = initials;

    $('#sSubjects').textContent = m.subjects_started + '/' + m.subjects_total;
    $('#sDays').textContent = m.active_days;

    const sp = $('#streakPill');
    $('#streakNum').textContent = m.current_streak;
    sp.classList.toggle('hot', m.current_streak >= 3);
    sp.title = 'Current streak ' + m.current_streak + 'd / longest ' + m.longest_streak + 'd';

    /* countdown */
    const cd = $('#cdNum');
    if (p.days_left === null || p.days_left === undefined) {
      cd.textContent = '--'; $('#cdLabel').textContent = 'set an exam date';
      $('#cdBar').style.width = '0%';
    } else if (p.days_left < 0) {
      cd.textContent = Math.abs(p.days_left); $('#cdLabel').textContent = 'days since exam';
      $('#cdBar').style.width = '100%';
    } else {
      countTo(cd, p.days_left);
      $('#cdLabel').textContent = 'days to ' + p.exam_name;
      cd.classList.toggle('warn', p.days_left <= 90 && p.days_left > 30);
      cd.classList.toggle('crit', p.days_left <= 30);
      const pct = Math.max(0, Math.min(100, (1 - p.days_left / 365) * 100));
      requestAnimationFrame(() => { $('#cdBar').style.width = pct + '%'; });
    }

    /* today ring */
    const target = p.daily_target_mins || 240;
    const pct = Math.min(1, st.today_minutes / target);
    const C = 2 * Math.PI * 35;
    const ring = $('#ringFg');
    requestAnimationFrame(() => { ring.style.strokeDashoffset = String(C * (1 - pct)); });
    ring.style.stroke = pct >= 1 ? 'var(--g4)' : pct >= .5 ? 'var(--g3)' : 'var(--warn)';
    $('#todayMins').textContent = hm(st.today_minutes);
    $('#todayOf').textContent = 'of ' + hm(target);
    const ab = $('#avatarBadge');
    ab.textContent = pct >= 1 ? 'MAX' : Math.round(pct * 100) + '%';
    ab.className = 'avatar-badge ' + (pct >= 1 ? 'done' : pct > 0 ? 'part' : '');

    /* mini readiness */
    const r = st.readiness;
    $('#miniReadiness').innerHTML = '';
    [['Index', r.index.toFixed(1)],
     ['Est. score', Math.round(r.est_score)],
     ['Percentile', r.position.percentile.toFixed(1) + '%']
    ].forEach(([k, v]) => {
      $('#miniReadiness').appendChild(el('div', { class: 'mr-row' }, [
        el('span', { text: k }), el('b', { text: String(v) }),
      ]));
    });

    /* badge strip */
    const strip = $('#badgeStrip');
    strip.innerHTML = '';
    const got = st.achievements.filter(a => a.unlocked).slice(-9).reverse();
    if (!got.length) strip.appendChild(el('span', { class: 'none', text: 'Nothing yet. Log a session.' }));
    got.forEach(a => {
      const b = el('div', { class: 'mini-badge', dataset: { t: a.tier }, text: a.glyph });
      bindTip(b, () => '<b>' + GG.esc(a.name) + '</b><br>' + GG.esc(a.desc));
      strip.appendChild(b);
    });
  }

  /* ============================ contribution =========================== */
  function graph(cal, weeksHost, monthsHost, onClick) {
    const wk = $(weeksHost), mo = $(monthsHost);
    wk.innerHTML = ''; mo.innerHTML = '';
    const today = new Date().toISOString().slice(0, 10);

    cal.months.forEach(m => {
      mo.appendChild(el('span', {
        text: m.name,
        style: 'left:' + (m.week * (11 + 3)) + 'px',
      }));
    });

    cal.weeks.forEach((week, wi) => {
      const col = el('div', { class: 'gw', style: '--d:' + wi });
      col.style.animationDelay = Math.min(wi * 7, 420) + 'ms';
      week.forEach(d => {
        const c = el('div', {
          class: 'cell l' + d.level + (d.future ? ' future' : '') + (d.day === today ? ' today' : ''),
          dataset: { day: d.day },
        });
        if (!d.future) {
          bindTip(c, () => {
            const bits = [d.minutes ? '<b>' + hm(d.minutes) + '</b>' : 'No session'];
            if (d.questions) bits.push(d.questions + ' question' + (d.questions > 1 ? 's' : ''));
            return bits.join(' / ') + '<br>' + d.label;
          });
          if (onClick) c.addEventListener('click', () => onClick(d.day));
        }
        col.appendChild(c);
      });
      wk.appendChild(col);
    });
    wk.classList.add('reveal');
  }

  /* ============================== overview ============================== */
  function overview(st) {
    const m = st.metrics;

    /* pinned subjects: highest exam weight that still has open topics */
    const pins = st.subjects.slice()
      .sort((a, b) => (b.marks * (100 - b.topic_progress)) - (a.marks * (100 - a.topic_progress)))
      .slice(0, 6);
    const grid = $('#pinGrid');
    grid.innerHTML = '';
    pins.forEach(s => grid.appendChild(pin(s)));
    if (!pins.length) grid.appendChild(emptyBox('No subjects', 'Check content/syllabus.json'));

    countTo($('#calHours'), m.year_minutes / 60, { dp: 0 });
    $('#calRange').textContent = nice(st.calendar.start) + ' -- ' + nice(st.today);
    graph(st.calendar, '#calWeeks', '#calMonths', day => GG.app.openLog(day));

    radar(st);
    kpis(st);

    /* The old flat "next actions" list is now the recommendation engine, which
       GG.plan renders with reasons and rating buttons. Keep the lookup guarded so
       render.js stays usable on its own. */
    const al = $('#actionList');
    if (al) al.innerHTML = '';

    feed($('#feedShort'), st.recent.slice(0, 8), st, false);
    growBars();
  }

  function pin(s) {
    const acc = s.accuracy === null ? '--' : s.accuracy + '%';
    return el('a', { class: 'pin', href: '#/subject/' + s.id }, [
      el('div', { class: 'pin-top' }, [
        el('span', { class: 'dot', style: 'background:' + colorOf(s.slug) }),
        el('span', { class: 'pin-name', text: s.name }),
        el('span', { class: 'tag', text: s.marks + 'm' }),
      ]),
      el('div', { class: 'bar' }, el('i', {
        dataset: { w: s.topic_progress },
        style: 'background:' + colorOf(s.slug),
      })),
      el('div', { class: 'pin-foot' }, [
        el('span', { text: s.topics_done + '/' + s.topic_count + ' topics' }),
        el('span', { text: hm(s.minutes) }),
        el('span', { text: 'acc ' + acc }),
      ]),
    ]);
  }

  function kpis(st) {
    const m = st.metrics;
    const rows = [
      [hm(m.total_minutes), 'total logged'],
      [m.longest_streak + 'd', 'longest streak'],
      [m.total_sessions, 'sessions'],
      [m.questions_attempted, 'questions done'],
      [m.accuracy + '%', 'accuracy'],
      [m.coverage_pct + '%', 'weighted coverage'],
      [m.topics_done + '/' + m.topics_total, 'topics closed'],
      [hm(m.avg_mins_per_active_day), 'avg active day'],
    ];
    const g = $('#kpiGrid');
    g.innerHTML = '';
    rows.forEach(([v, k]) => g.appendChild(
      el('div', { class: 'kpi' }, [el('b', { text: String(v) }), el('span', { text: k })])));
  }

  function radar(st) {
    const svg = $('#radar');
    const labels = st.kinds;
    const vals = labels.map(k => st.kind_minutes[k] || 0);
    const max = Math.max(1, ...vals);
    const cx = 130, cy = 108, R = 74, n = labels.length;
    const pt = (i, r) => {
      const a = (Math.PI * 2 * i) / n - Math.PI / 2;
      return [cx + Math.cos(a) * r, cy + Math.sin(a) * r];
    };
    let out = '';
    [1, .75, .5, .25].forEach(f => {
      const pts = labels.map((_, i) => pt(i, R * f).map(v => v.toFixed(1)).join(',')).join(' ');
      out += '<polygon class="radar-grid" points="' + pts + '"/>';
    });
    labels.forEach((_, i) => {
      const [x, y] = pt(i, R);
      out += '<line class="radar-grid radar-spoke" x1="' + cx + '" y1="' + cy + '" x2="' + x.toFixed(1) + '" y2="' + y.toFixed(1) + '"/>';
    });
    const area = vals.map((v, i) => pt(i, (v / max) * R).map(x => x.toFixed(1)).join(',')).join(' ');
    out += '<polygon class="radar-area" points="' + area + '"/>';
    vals.forEach((v, i) => {
      const [x, y] = pt(i, (v / max) * R);
      out += '<circle class="radar-pt" cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="2.6"/>';
    });
    labels.forEach((k, i) => {
      const [x, y] = pt(i, R + 19);
      const anchor = Math.abs(x - cx) < 8 ? 'middle' : x > cx ? 'start' : 'end';
      out += '<text class="radar-lab" x="' + x.toFixed(1) + '" y="' + y.toFixed(1) + '" text-anchor="' + anchor + '">' + GG.esc(k) + '</text>';
      out += '<text class="radar-val" x="' + x.toFixed(1) + '" y="' + (y + 10).toFixed(1) + '" text-anchor="' + anchor + '">' + hm(vals[i]) + '</text>';
    });
    svg.innerHTML = out;
  }

  /* ============================== subjects ============================== */
  const openSet = new Set();

  function subjects(st) {
    const host = $('#subjectList');
    const q = ($('#subjSearch').value || '').toLowerCase().trim();
    const sort = $('#subjSort').value;

    let list = st.subjects.slice();
    if (q) {
      list = list.filter(s => s.name.toLowerCase().includes(q) ||
        s.topics.some(t => t.name.toLowerCase().includes(q)));
    }
    const cmp = {
      coverage: (a, b) => a.topic_progress - b.topic_progress || b.marks - a.marks,
      marks: (a, b) => b.marks - a.marks,
      hours: (a, b) => b.minutes - a.minutes,
      recent: (a, b) => String(b.last || '').localeCompare(String(a.last || '')),
      accuracy: (a, b) => (a.accuracy === null ? 101 : a.accuracy) - (b.accuracy === null ? 101 : b.accuracy),
      name: (a, b) => a.name.localeCompare(b.name),
    }[sort] || ((a, b) => 0);
    list.sort(cmp);

    host.innerHTML = '';
    if (!list.length) { host.appendChild(emptyBox('Nothing matched', 'Try another search term.')); return; }
    list.forEach(s => host.appendChild(subjectCard(s, q)));
    growBars(host);
  }

  function subjectCard(s, q) {
    const isOpen = openSet.has(s.id) || (q && s.topics.some(t => t.name.toLowerCase().includes(q)));
    const card = el('div', { class: 'subj' + (isOpen ? ' open' : '') });

    const head = el('div', { class: 'subj-head' }, [
      el('div', {}, [
        el('div', { class: 'subj-title' }, [
          el('span', { class: 'dot', style: 'background:' + colorOf(s.slug) }),
          el('a', { href: '#/subject/' + s.id, text: s.name,
                    onclick: e => e.stopPropagation() }),
          el('span', { class: 'tag', text: s.marks + ' marks' }),
          s.topic_progress === 100 ? el('span', { class: 'tag ok', text: 'covered' }) : null,
        ]),
        el('div', { class: 'subj-meta' }, [
          el('span', { text: s.topics_done + '/' + s.topic_count + ' topics' }),
          el('span', { text: hm(s.minutes) }),
          el('span', { text: s.sessions + ' sessions' }),
          el('span', { text: s.attempts ? 'acc ' + s.accuracy + '% (' + s.attempts + 'q)' : 'no questions yet' }),
          el('span', { text: s.last ? ago(s.last) : 'not started' }),
        ]),
      ]),
      el('div', { class: 'subj-right' }, [
        el('div', { class: 'lab' }, [
          el('span', { text: 'coverage' }), el('span', { text: s.topic_progress + '%' })]),
        el('div', { class: 'bar tall' }, el('i', {
          dataset: { w: s.topic_progress }, style: 'background:' + colorOf(s.slug) })),
        el('div', { class: 'lab' }, [
          el('span', { text: 'hours' }), el('span', { text: s.hours_progress + '%' })]),
        el('div', { class: 'bar' }, el('i', {
          dataset: { w: s.hours_progress }, style: 'background:var(--accent)' })),
      ]),
      el('span', { class: 'caret', text: '>' }),
    ]);
    head.addEventListener('click', () => {
      card.classList.toggle('open');
      if (card.classList.contains('open')) openSet.add(s.id); else openSet.delete(s.id);
    });
    card.appendChild(head);

    const table = el('div', { class: 'topic-table' });
    s.topics.forEach(t => table.appendChild(topicRow(t)));
    if (!s.topics.length) table.appendChild(el('div', { class: 'empty', text: 'No topics listed for this subject.' }));
    card.appendChild(el('div', { class: 'subj-topics' }, el('div', {}, table)));
    return card;
  }

  function topicRow(t) {
    const tri = el('div', { class: 'tri' });
    [['pending', 'TODO'], ['learning', 'WIP'], ['done', 'DONE']].forEach(([s, label]) => {
      tri.appendChild(el('button', {
        class: t.status === s ? 'on' : '', dataset: { s },
        text: label,
        onclick: async ev => {
          ev.stopPropagation();
          try { await GG.app.setTopic(t.id, s); }
          catch (e) { GG.toast('Could not update', e.message, 'bad'); }
        },
      }));
    });
    const accCls = t.accuracy === null ? '' : t.accuracy >= 70 ? ' good' : t.accuracy < 50 ? ' poor' : '';
    return el('div', { class: 'topic' + (t.status === 'done' ? ' done' : '') }, [
      tri,
      el('div', { class: 'topic-name', text: t.name }),
      el('span', { class: 'topic-w', text: 'w' + t.weight + (t.bank ? ' / ' + t.bank + 'q' : '') }),
      el('span', {
        class: 'topic-acc' + accCls,
        text: t.attempts ? t.correct + '/' + t.attempts + ' (' + t.accuracy + '%)' : '--',
      }),
    ]);
  }

  /* ============================ achievements ============================ */
  function achievements(st) {
    const list = st.achievements;
    const got = list.filter(a => a.unlocked).length;
    $('#achCount').textContent = got + '/' + list.length;
    const wrap = $('#trackWrap');
    wrap.innerHTML = '';

    Object.keys(st.tracks).forEach(key => {
      const meta = st.tracks[key];
      const items = list.filter(a => a.track === key);
      const n = items.filter(a => a.unlocked).length;
      const sec = el('section', { class: 'track-sec' }, [
        el('div', { class: 'track-head' }, [
          el('span', { class: 'track-glyph', text: meta.glyph }),
          el('h3', { text: meta.label }),
          el('span', { class: 'track-count', text: n + '/' + items.length }),
        ]),
        el('p', { class: 'track-blurb', text: meta.blurb }),
      ]);
      const grid = el('div', { class: 'badge-grid stagger' });
      items.forEach(a => grid.appendChild(badge(a)));
      sec.appendChild(grid);
      wrap.appendChild(sec);
    });
    growBars(wrap);
  }

  function badge(a) {
    return el('div', { class: 'badge ' + (a.unlocked ? 'on' : 'off'), dataset: { t: a.tier } }, [
      el('span', { class: 'badge-tier', text: a.tier }),
      el('div', { class: 'hex' }, el('span', { text: a.glyph })),
      el('div', { class: 'badge-name', text: a.name }),
      el('div', { class: 'badge-desc', text: a.desc }),
      a.unlocked
        ? el('div', { class: 'badge-when', text: 'unlocked ' + ago((a.unlocked_at || '').slice(0, 10)) })
        : el('div', { class: 'badge-prog' }, [
            el('div', { class: 'bar' }, el('i', {
              dataset: { w: a.progress }, style: 'background:var(--line)' })),
            el('div', { class: 'lab', text: a.display_value + ' / ' + a.display_target }),
          ]),
    ]);
  }

  /* ============================== activity ============================== */
  function activity(st) {
    feed($('#feedFull'), st.recent, st, true);

    const log = $('#qotdLog');
    log.innerHTML = '';
    const items = st.qotd_history || [];
    if (!items.length) {
      log.appendChild(emptyBox('No daily questions yet', 'One appears each day you open the app.'));
    }
    items.forEach(q => {
      const mark = q.answered ? (q.correct ? '[+]' : '[x]') : '[ ]';
      log.appendChild(el('div', { class: 'row' }, [
        el('span', { class: 'mono', style: 'color:' + (q.correct ? 'var(--g4)' : q.answered ? 'var(--bad)' : 'var(--faint)'), text: mark }),
        el('div', { class: 'row-body' }, [
          el('div', { class: 'row-l1' }, [
            el('span', { class: 'row-name', text: q.subject || 'unknown' }),
            el('span', { class: 'chip-kind', text: q.topic || '' }),
          ]),
          el('div', { class: 'row-sub', text: q.reason }),
        ]),
        el('span', { class: 'row-num', text: q.answered ? (q.correct ? 'correct' : 'wrong') : 'skipped' }),
        el('span', { class: 'row-day', text: ago(q.day) }),
      ]));
    });
  }

  function feed(host, rows, st, deletable) {
    host.innerHTML = '';
    if (!rows.length) {
      host.appendChild(emptyBox('No sessions yet', 'Hit "Log session" and put the first square on the board.'));
      return;
    }
    rows.forEach(r => {
      const bits = [hm(r.minutes)];
      if (r.topics && r.topics.length) bits.push(r.topics.join(', '));
      if (r.note) bits.push(r.note);
      host.appendChild(el('div', { class: 'row' }, [
        el('span', { class: 'dot', style: 'background:' + colorOf(r.subject_slug) }),
        el('div', { class: 'row-body' }, [
          el('div', { class: 'row-l1' }, [
            el('a', { class: 'row-name', href: '#/subject/' + r.subject_id, text: r.subject_name }),
            el('span', { class: 'chip-kind ' + r.kind, text: st.kind_labels[r.kind] || r.kind }),
          ]),
          el('div', { class: 'row-sub', text: bits.join(' / '), title: bits.join(' / ') }),
        ]),
        el('span', { class: 'row-num', text: hm(r.minutes) }),
        el('span', { class: 'row-day' }, [
          document.createTextNode(ago(r.day)),
          deletable ? el('button', {
            class: 'x', title: 'Delete session', text: '\u00d7',
            onclick: () => GG.app.deleteSession(r.id),
          }) : null,
        ]),
      ]));
    });
  }

  const emptyBox = (title, sub) => el('div', { class: 'empty' }, [
    el('b', { text: title }), el('span', { text: sub || '' })]);

  /* =============================== detail =============================== */
  async function detail(id) {
    let data;
    try { data = await GG.api('/subjects/' + id); }
    catch (e) { GG.toast('Could not load subject', e.message, 'bad'); location.hash = '#/subjects'; return; }
    const s = data.subject;
    $('#dtDot').style.background = colorOf(s.slug);
    $('#dtName').textContent = s.name;
    $('#dtGroup').textContent = s.group || s.grp || '';

    const stats = [
      [hm(s.minutes), 'logged'],
      [s.sessions, 'sessions'],
      [s.days, 'active days'],
      [s.topics_done + '/' + s.topic_count, 'topics'],
      [s.topic_progress + '%', 'coverage'],
      [s.marks, 'exam marks'],
      [s.attempts, 'questions'],
      [s.accuracy === null ? '--' : s.accuracy + '%', 'accuracy'],
    ];
    const sh = $('#dtStats');
    sh.innerHTML = '';
    stats.forEach(([v, k]) => sh.appendChild(
      el('div', {}, [el('b', { text: String(v) }), el('span', { text: k })])));

    graph(data.calendar, '#dtWeeks', '#dtMonths', day => GG.app.openLog(day, s.id));

    const th = $('#dtTopics');
    th.innerHTML = '';
    const table = el('div', { class: 'topic-table' });
    s.topics.forEach(t => table.appendChild(topicRow(t)));
    th.appendChild(table);
    $('#dtQuiz').onclick = () => GG.practice.startSet(s.id, [], 5, '');

    feed($('#dtFeed'), data.sessions.map(x => Object.assign({}, x, {
      subject_name: s.name, subject_slug: s.slug, subject_id: s.id,
    })), GG.S.state, true);
  }

  return { sidebar, overview, subjects, achievements, activity, detail, graph, feed, emptyBox };
})();
