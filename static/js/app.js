/* Boot, routing and the session-logging flow. */
GG.app = (function () {
  'use strict';
  const { $, $$, el, hm } = GG;

  let badgeSnapshot = null;

  /* ============================== render =============================== */
  function apply(state) {
    GG.S.state = state;
    GG.adoptServerPrefs(state.prefs);
    celebrate(state);
    GG.render.sidebar(state);
    paint();
    GG.splashDone();
  }

  function paint() {
    const st = GG.S.state;
    if (!st) return;
    const r = GG.S.route;
    if (r === 'overview') {
      GG.render.overview(st);
      GG.plan.paint(st);
      GG.practice.renderQotd(st, '#qotdInline', true);
    } else if (r === 'subjects') GG.render.subjects(st);
    else if (r === 'practice') GG.practice.tab(st);
    else if (r === 'readiness') GG.readiness.tab(st);
    else if (r === 'bank') GG.bank.tab(st);
    else if (r === 'achievements') {
      GG.render.achievements(st);
      GG.plan.missions(st, '#missionStripFull');
    } else if (r === 'doubts') GG.doubts.tab(st);
    else if (r === 'profile') GG.profile.tab(st);
    else if (r === 'activity') GG.render.activity(st);
    else if (r === 'detail') GG.render.detail(GG.S.detailId);
  }

  function celebrate(state) {
    const now = new Set(state.achievements.filter(a => a.unlocked).map(a => a.code));
    if (badgeSnapshot) {
      state.achievements.forEach(a => {
        if (a.unlocked && !badgeSnapshot.has(a.code)) {
          GG.toast('Sticker unlocked: ' + a.name, a.tier.toUpperCase() + ' / ' + a.desc, 'trophy');
        }
      });
    }
    badgeSnapshot = now;
  }

  async function reload() {
    try {
      apply(await GG.api('/state'));
    } catch (e) {
      GG.toast('Could not reach the server', e.message, 'bad');
    }
  }

  /* ============================== routing ============================== */
  function route() {
    const { route, id } = GG.parseHash();
    GG.show(route, id);
    paint();
  }

  /* =========================== session logging ========================= */
  function openLog(day, subjectId) {
    const st = GG.S.state;
    if (!st) return;

    const sel = $('#fSubject');
    sel.innerHTML = '';
    st.subjects.forEach(s => sel.appendChild(el('option', {
      value: s.id, text: s.name + '  (' + s.topics_done + '/' + s.topic_count + ')' })));

    /* default to whatever was studied most recently */
    const recent = st.recent[0];
    sel.value = subjectId || (recent ? recent.subject_id : st.subjects[0] && st.subjects[0].id);

    const kind = $('#fKind');
    kind.innerHTML = '';
    st.kinds.forEach(k => kind.appendChild(el('option', {
      value: k, text: st.kind_labels[k] || k })));

    $('#fDay').value = day || st.today;
    $('#fDay').max = st.today;
    $('#fMinutes').value = 60;
    $('#fHour').value = new Date().getHours();
    $('#fNote').value = '';
    $('#logErr').hidden = true;

    const quick = $('#fQuick');
    quick.innerHTML = '';
    [30, 45, 60, 90, 120, 180, 240].forEach(m => {
      quick.appendChild(el('button', {
        class: 'chip' + (m === 60 ? ' on' : ''), text: hm(m),
        onclick: e => {
          e.preventDefault();
          $('#fMinutes').value = m;
          $$('#fQuick .chip').forEach(c => c.classList.remove('on'));
          e.currentTarget.classList.add('on');
        },
      }));
    });

    sel.onchange = () => logTopics();
    logTopics();
    GG.modal('#modalLog', true);
  }

  function logTopics() {
    const st = GG.S.state;
    const host = $('#fTopics');
    host.innerHTML = '';
    const sid = parseInt($('#fSubject').value, 10);
    const subj = st.subjects.find(s => s.id === sid);
    if (!subj || !subj.topics.length) {
      host.appendChild(el('span', { class: 'dim small', text: 'No topics listed for this subject.' }));
      return;
    }
    subj.topics.forEach(t => {
      const node = el('label', {
        class: 'tp' + (t.status === 'done' ? ' was-done' : ''),
        dataset: { id: t.id, slug: t.slug },
        title: t.status === 'done' ? 'Already marked done' : t.status,
      }, [
        el('span', { class: 'box', text: t.status === 'done' ? '[+]' : '[ ]' }),
        el('span', { text: t.name }),
      ]);
      node.addEventListener('click', e => {
        e.preventDefault();
        node.classList.toggle('on');
        node.querySelector('.box').textContent = node.classList.contains('on')
          ? '[x]' : (t.status === 'done' ? '[+]' : '[ ]');
      });
      host.appendChild(node);
    });
  }

  async function saveLog() {
    const btn = $('#saveLog');
    const payload = {
      subject_id: parseInt($('#fSubject').value, 10),
      day: $('#fDay').value,
      minutes: parseInt($('#fMinutes').value, 10),
      kind: $('#fKind').value,
      hour: parseInt($('#fHour').value, 10),
      note: $('#fNote').value,
      topic_ids: $$('#fTopics .tp.on').map(n => parseInt(n.dataset.id, 10)),
      mark_topics_done: $('#fMarkDone').checked,
      with_quiz: $('#fWithQuiz').checked,
      quiz_count: 4,
    };
    if (!payload.minutes) {
      const err = $('#logErr');
      err.textContent = 'Put some minutes on the session.';
      err.hidden = false;
      return;
    }
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> saving';
    try {
      const out = await GG.api('/sessions', { body: payload });
      GG.modal('#modalLog', false);
      apply(out.state);
      const n = payload.topic_ids.length;
      GG.toast('Session committed',
        hm(payload.minutes) + (n ? ' / ' + n + ' topic' + (n > 1 ? 's' : '') + ' marked' : ''));

      if (out.quiz && out.quiz.questions && out.quiz.questions.length) {
        setTimeout(() => GG.practice.open(out.quiz, 'Quiz on what you just studied'), 340);
      } else if (payload.with_quiz && out.quiz_error) {
        GG.toast('No quiz generated', out.quiz_error, 'bad');
      }
    } catch (e) {
      const err = $('#logErr');
      err.textContent = e.message;
      err.hidden = false;
    } finally {
      btn.disabled = false;
      btn.textContent = 'Commit session';
    }
  }

  async function setTopic(topicId, status) {
    const st = await GG.api('/topics/status', { body: { topic_id: topicId, status } });
    apply(st);
  }

  async function deleteSession(id) {
    if (!confirm('Delete this session? The squares and hours go with it.')) return;
    try { apply(await GG.api('/sessions/' + id, { method: 'DELETE' })); GG.toast('Session removed'); }
    catch (e) { GG.toast('Could not delete', e.message, 'bad'); }
  }

  /* ============================== profile ============================== */
  function openProfile() {
    const p = GG.S.state.profile;
    $('#pName').value = p.display_name || '';
    $('#pHandle').value = p.handle || '';
    $('#pBio').value = p.bio || '';
    $('#pLoc').value = p.location || '';
    $('#pExam').value = p.exam_name || '';
    $('#pExamDate').value = p.exam_date || '';
    $('#pTarget').value = p.daily_target_mins || 240;
    const sel = $('#pPrimary');
    sel.innerHTML = '';
    (GG.S.state.readiness.targets || []).forEach(t => sel.appendChild(
      el('option', { value: t.slug, text: t.name })));
    sel.value = p.primary_target || '';
    const soc = p.socials || {};
    $('#pGithub').value = soc.github || '';
    $('#pLinkedin').value = soc.linkedin || '';
    $('#pX').value = soc.x || '';
    $('#pSite').value = soc.website || '';
    /* Hold the picked image here rather than in the form: a file input cannot be
       set programmatically, so re-opening the dialog would otherwise look like
       the picture had been cleared. */
    pendingAvatar = null;
    $('#pAvatar').value = '';
    $('#pAvatarNote').textContent = p.avatar
      ? 'A picture is set. Choose a file to replace it, or clear it below.'
      : 'Stored in your own database, resized to 256px. Nothing is uploaded anywhere.';
    GG.modal('#modalProfile', true);
  }

  let pendingAvatar = null;

  /* Downscale in the browser so the database holds a thumbnail, not a 4MB phone
     photo. Settings values are text, and a data URL is the one shape that needs
     no upload endpoint, no static file serving and no cleanup on delete. */
  function readAvatar(file) {
    return new Promise((resolve, reject) => {
      if (!file) return resolve(null);
      if (!/^image\//.test(file.type)) return reject(new Error('That is not an image.'));
      if (file.size > 8 * 1024 * 1024) return reject(new Error('Image is over 8MB.'));
      const reader = new FileReader();
      reader.onerror = () => reject(new Error('Could not read that file.'));
      reader.onload = () => {
        const img = new Image();
        img.onerror = () => reject(new Error('Could not decode that image.'));
        img.onload = () => {
          const side = Math.min(img.width, img.height);
          const cv = document.createElement('canvas');
          cv.width = cv.height = 256;
          const ctx = cv.getContext('2d');
          ctx.drawImage(img, (img.width - side) / 2, (img.height - side) / 2,
                        side, side, 0, 0, 256, 256);
          resolve(cv.toDataURL('image/jpeg', 0.82));
        };
        img.src = reader.result;
      };
      reader.readAsDataURL(file);
    });
  }

  async function saveProfile() {
    try {
      const st = await GG.api('/profile', {
        body: {
          display_name: $('#pName').value, handle: $('#pHandle').value,
          bio: $('#pBio').value, location: $('#pLoc').value,
          exam_name: $('#pExam').value, exam_date: $('#pExamDate').value,
          daily_target_mins: $('#pTarget').value, primary_target: $('#pPrimary').value,
          social_github: $('#pGithub').value.trim(),
          social_linkedin: $('#pLinkedin').value.trim(),
          social_x: $('#pX').value.trim(),
          social_website: $('#pSite').value.trim(),
          ...(pendingAvatar === null ? {} : { avatar: pendingAvatar }),
        },
      });
      GG.modal('#modalProfile', false);
      apply(st);
      GG.toast('Profile saved');
    } catch (e) { GG.toast('Could not save', e.message, 'bad'); }
  }

  /* ========================== backup / restore ========================= */
  async function exportBackup() {
    try {
      const data = await GG.api('/export');
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const a = el('a', {
        href: URL.createObjectURL(blob),
        download: 'gitgrind-backup-' + new Date().toISOString().slice(0, 10) + '.json',
      });
      document.body.appendChild(a); a.click(); a.remove();
      GG.toast('Backup downloaded', 'Your API key is not included.');
    } catch (e) { GG.toast('Export failed', e.message, 'bad'); }
  }

  function importBackup(file) {
    const fr = new FileReader();
    fr.onload = async () => {
      try {
        const payload = JSON.parse(fr.result);
        if (!confirm('This replaces everything currently in the tracker. Continue?')) return;
        const state = await GG.api('/import', { body: payload });
        apply(state);
        /* A backup from an older bank carries question ids that have since been
           replaced. Say what was reconnected and what was not, because silence
           here reads as data loss. */
        const r = state.import_repair || {};
        const stuck = (r.unresolved || []).length;
        if (r.rows) {
          GG.toast('Backup restored',
            r.rows + ' history row(s) reconnected to the current question bank' +
            (stuck ? ', ' + stuck + ' question(s) no longer in the bank' : ''));
        } else if (stuck) {
          GG.toast('Backup restored',
            stuck + ' question(s) in your history are no longer in the bank. ' +
            'Those attempts are kept but will not show under a topic.');
        } else {
          GG.toast('Backup restored');
        }
      } catch (e) { GG.toast('Import failed', e.message, 'bad'); }
    };
    fr.readAsText(file);
  }

  async function resetActivity() {
    const typed = prompt('This deletes every session, quiz and sticker. Type RESET to confirm.');
    if (typed !== 'RESET') {
      if (typed !== null) GG.toast('Nothing cleared', 'You need to type RESET exactly.');
      return;
    }
    try { apply(await GG.api('/reset', { body: { scope: 'activity' } })); GG.toast('Activity cleared'); }
    catch (e) { GG.toast('Could not reset', e.message, 'bad'); }
  }

  /* =============================== wiring ============================== */
  function init() {
    window.addEventListener('hashchange', route);
    window.addEventListener('resize', GG.markNav);

    $('#btnLog').onclick = () => openLog();
    $('#saveLog').onclick = saveLog;
    /* The sidebar button is now a link to #/profile; the modal is opened from
       the profile page instead. Guard it so a missing element cannot abort init.*/
    const btnProfile = $('#btnProfile');
    if (btnProfile) btnProfile.onclick = openProfile;
    $('#saveProfile').onclick = saveProfile;
    const avatarInput = $('#pAvatar');
    if (avatarInput) avatarInput.onchange = async () => {
      try {
        pendingAvatar = await readAvatar(avatarInput.files[0]);
        $('#pAvatarNote').textContent = pendingAvatar
          ? 'Ready. Save to keep it.'
          : 'Picture cleared on save.';
      } catch (e) {
        avatarInput.value = '';
        pendingAvatar = null;
        GG.toast('Could not use that image', e.message);
      }
    };
    const clearAvatar = $('#pAvatarClear');
    if (clearAvatar) clearAvatar.onclick = () => {
      pendingAvatar = '';
      if (avatarInput) avatarInput.value = '';
      $('#pAvatarNote').textContent = 'Picture cleared on save.';
    };
    $('#quizClose').onclick = () => {
      if (confirm('Close the quiz? Unsubmitted answers are lost.')) GG.modal('#modalQuiz', false);
    };
    $('#btnExport').onclick = exportBackup;
    $('#btnImport').onclick = () => $('#fileImport').click();
    $('#fileImport').onchange = e => { if (e.target.files[0]) importBackup(e.target.files[0]); };
    $('#btnReset').onclick = resetActivity;

    $('#subjSearch').addEventListener('input', () => GG.render.subjects(GG.S.state));
    $('#subjSort').addEventListener('change', () => GG.render.subjects(GG.S.state));

    $$('[data-close]').forEach(b => b.addEventListener('click', () => {
      const m = b.closest('.modal');
      if (m) GG.modal('#' + m.id, false);
    }));
    $('#scrim').addEventListener('click', () => {
      if (!$('#modalQuiz').hidden) return;   /* quizzes need an explicit close */
      GG.closeAll();
    });

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        if (!$('#modalQuiz').hidden) return;
        GG.closeAll();
        GG.hideTip();
      }
      const typing = /^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName);
      if (typing || e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === 'l' || e.key === 'L') { e.preventDefault(); openLog(); }
      if (e.key === 'd' || e.key === 'D') { location.hash = '#/doubts'; }
      if (e.key === 'p' || e.key === 'P') { location.hash = '#/practice'; }
      if (e.key === '?') { location.hash = '#/readiness'; }
    });

    route();
    reload();
  }

  document.addEventListener('DOMContentLoaded', init);

  return { apply, reload, openLog, setTopic, deleteSession, paint, openProfile };
})();

/* ==========================================================================
   v3 wiring - the command centre, the bank view, engine settings, and a
   keyboard layer that makes the whole app usable without a mouse.
   ========================================================================== */
(function () {
  const { $, $$, el, api, toast, key } = GG;
  const base = GG.app;
  /* openLog is called from plan cards with a subject slug rather than a date, so
     accept either and translate. */
  const originalOpenLog = base.openLog;
  base.openLog = function (a, b) {
    if (typeof a === 'string' && a && !/^\d{4}-\d{2}-\d{2}$/.test(a)) {
      const st = GG.S.state || {};
      const s = (st.subjects || []).find(x => x.slug === a);
      return originalOpenLog(null, s ? s.id : undefined);
    }
    return originalOpenLog(a, b);
  };

  /* --------------------------------------------------------- settings ----- */
  /* Only the values the engine declares tunable are shown, so the UI can never
     drift from what the backend will accept. */
  const SETTING_COPY = {
    weak_accuracy_threshold: ['Weak-topic threshold (%)',
      'Accuracy below this counts as weak, which drives drills and the plan.'],
    revision_grace_days: ['Revision grace (days)',
      'How late an item can be before it is treated as overdue rather than due.'],
    repeat_cooldown_days: ['Repeat cooldown (days)',
      'How long before a question you have already seen can be served again.'],
    plan_auto_generate: ['Build the daily plan automatically',
      'Off means the plan only appears when you press Rebuild.'],
    adaptive_difficulty: ['Adapt question difficulty',
      'Off means difficulty is picked at random rather than tracking your accuracy.'],
    reduced_motion: ['Reduced motion',
      'Removes transitions and the staggered entrance. Your operating system ' +
      'setting is honoured regardless of this box.'],
  };

  function openSettings() {
    const body = $('#settingsBody');
    const prefs = (GG.S.state || {}).prefs || {};
    body.innerHTML = '';
    body.appendChild(el('p', { class: 'dim small', style: 'margin:0 0 16px' }, [
      'These change how the engines behave, and are stored in the database next to ' +
      'your sessions. Defaults are sensible; change them only if the app is being ' +
      'too soft or too harsh with you.',
    ]));
    Object.keys(prefs).forEach(k => {
      const [label, help] = SETTING_COPY[k] || [k, ''];
      const v = prefs[k];
      if (typeof v === 'boolean') {
        body.appendChild(el('label', { class: 'check' }, [
          el('input', { type: 'checkbox', id: 'set_' + k, checked: v }),
          el('span', {}, [el('b', {}, [label]), help ? el('em', { class: 'dim' }, [' ' + help]) : '']),
        ]));
      } else {
        body.appendChild(el('label', { class: 'field' }, [
          el('span', {}, [label, help ? el('em', { class: 'dim' }, [' ' + help]) : '']),
          el('input', { type: 'number', id: 'set_' + k, value: String(v) }),
        ]));
      }
    });
    GG.modal('#modalSettings', true);
  }

  async function saveSettings() {
    const prefs = (GG.S.state || {}).prefs || {};
    const body = {};
    Object.keys(prefs).forEach(k => {
      const f = $('#set_' + k);
      if (!f) return;
      body[k] = f.type === 'checkbox' ? (f.checked ? 1 : 0) : Number(f.value);
    });
    try {
      await api('/settings', { method: 'POST', body: body });
      GG.setReducedMotion(!!body.reduced_motion);
      GG.modal('#modalSettings', false);
      toast('Settings saved', 'The engines will use these from the next refresh.');
      base.reload();
    } catch (e) { toast('Could not save', e.message, 'bad'); }
  }

  /* --------------------------------------------------------- shortcuts ---- */
  function registerShortcuts() {
    key('l', 'Log a session', () => base.openLog());
    key('t', 'Jump to Today', () => { location.hash = '#/overview'; });
    key('s', 'Jump to Subjects', () => { location.hash = '#/subjects'; });
    key('p', 'Jump to Practice', () => { location.hash = '#/practice'; });
    key('r', 'Jump to Readiness', () => { location.hash = '#/readiness'; });
    key('b', 'Jump to the question Bank', () => { location.hash = '#/bank'; });
    key('a', 'Jump to Activity', () => { location.hash = '#/activity'; });
    key('d', 'Jump to Doubts', () => { location.hash = '#/doubts'; });
    key('n', 'Do the next action', () => {
      const st = GG.S.state;
      if (st && st.next_action) GG.plan.act(st.next_action);
    });
    key('v', 'Start the revision set that is due', () => {
      GG.practice.startSet({ purpose: 'review' });
    });
    key('g', 'Rebuild today\u2019s plan', () => GG.plan.regenerate());
    key('m', 'Toggle reduced motion', () => {
      const off = !GG.S.ui.reducedMotion;
      GG.setReducedMotion(off);
      toast(off ? 'Motion reduced' : 'Motion restored', '');
    });
    key('?', 'Show this list', () => GG.shortcutHelp());
  }

  /* ------------------------------------------------------------- boot ----- */
  function wire() {
    GG.loadPrefs();
    registerShortcuts();

    const keysBtn = $('#btnKeys');
    if (keysBtn) keysBtn.onclick = () => GG.shortcutHelp();

    const setBtn = $('#btnSettings');
    if (setBtn) setBtn.onclick = openSettings;
    const setSave = $('#saveSettings');
    if (setSave) setSave.onclick = saveSettings;

    const regen = $('#planRegen');
    if (regen) regen.onclick = () => GG.plan.regenerate();

    const reloadBtn = $('#bankReload');
    if (reloadBtn) reloadBtn.onclick = () => GG.bank.reload();
    const searchBtn = $('#qsGo');
    if (searchBtn) searchBtn.onclick = () => GG.bank.search();
    const qsQuery = $('#qsQuery');
    if (qsQuery) qsQuery.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); GG.bank.search(); }
    });

    /* Keep whatever is half-typed in the log dialog, so an accidental Escape or a
       stray click does not cost you the entry. */
    const logModal = $('#modalLog');
    if (logModal) {
      logModal.addEventListener('input', () => GG.draft('log', GG.snapshot(logModal)));
      const btn = $('#btnLog');
      if (btn) {
        btn.addEventListener('click', () => setTimeout(() => {
          const d = GG.draft('log');
          if (d && d.fNote) GG.restore(logModal, { fNote: d.fNote });
        }, 90));
      }
    }
  }

  document.addEventListener('DOMContentLoaded', wire);
  base.openSettings = openSettings;
})();