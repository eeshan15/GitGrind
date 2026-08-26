/* ==========================================================================
   GG.live - one crash-safe checkpoint of whatever is in flight, and the prompt
   that offers it back.

   Providers, not values. timer.js and practice.js each register a function that
   returns their current state or null; a flush calls every provider and writes
   the merged result. Two consequences worth the indirection:

     - a checkpoint written by the ten-second tick is exactly as fresh as one
       written by a click, so a crash loses at most a few seconds,
     - neither module can overwrite the other's half of the row, which a
       naive "post my state" call would do every time.

   Nothing here is allowed to interrupt the person using the app: a failed
   checkpoint is dropped and retried on the next tick, never surfaced.
   ========================================================================== */
window.GG = window.GG || {};
GG.live = (function () {
  const IDLE_MS = 1200;     /* settle after a change before writing        */
  const FORCE_MS = 10000;   /* never go longer than this while something runs */

  const sources = {};
  let idle = null;
  let ticker = null;
  let sending = false;
  let again = false;
  let lastKind = '';
  let offered = false;

  /* ----------------------------------------------------------- transport --- */
  function collect() {
    const out = {};
    Object.keys(sources).forEach(name => {
      let v = null;
      try {
        v = sources[name]();
      } catch (e) {
        v = null;   /* a broken provider must not stop the others saving */
      }
      if (v) out[name] = v;
    });
    return out;
  }

  function kindOf(payload) {
    const on = Object.keys(payload);
    if (!on.length) return '';
    return on.length > 1 ? 'both' : on[0];
  }

  async function flush() {
    if (idle) { clearTimeout(idle); idle = null; }
    if (sending) { again = true; return; }

    const payload = collect();
    const kind = kindOf(payload);
    /* Nothing in flight and nothing left on the server: no reason to talk. */
    if (!kind && !lastKind) return;

    sending = true;
    again = false;
    try {
      await GG.api('/live', { body: { kind: kind, payload: payload } });
      lastKind = kind;
    } catch (e) {
      /* Deliberately silent. The next tick tries again, and a toast about a
         failed background write is noise in the middle of a question. */
    } finally {
      sending = false;
      if (again) flush();
    }
  }

  function touch() {
    if (idle) clearTimeout(idle);
    idle = setTimeout(flush, IDLE_MS);
    if (!ticker) {
      ticker = setInterval(() => {
        if (kindOf(collect()) || lastKind) flush();
      }, FORCE_MS);
    }
  }

  function register(name, fn) {
    sources[name] = fn;
  }

  /* The last chance before this page goes away. fetch() is cancelled on unload;
     sendBeacon is handed to the browser and survives it. */
  function beacon() {
    const payload = collect();
    const kind = kindOf(payload);
    if (!kind || !navigator.sendBeacon) return;
    try {
      navigator.sendBeacon('/api/live', new Blob(
        [JSON.stringify({ kind: kind, payload: payload })],
        { type: 'application/json' }));
    } catch (e) { /* nothing further we can do at this point */ }
  }

  async function clear() {
    try {
      await GG.api('/live/clear', { body: {} });
      lastKind = '';
    } catch (e) { /* the age check on the server will drop it eventually */ }
  }

  /* -------------------------------------------------------------- prompt --- */
  /* GG.ago works in whole days, which is the wrong unit for "when did we
     crash". This one is minutes and hours. */
  function since(iso) {
    if (!iso) return 'a moment ago';
    const ms = Date.now() - new Date(iso).getTime();
    if (!isFinite(ms) || ms < 0) return 'a moment ago';
    const mins = Math.floor(ms / 60000);
    if (mins < 1) return 'seconds ago';
    if (mins < 60) return mins + (mins === 1 ? ' minute ago' : ' minutes ago');
    const hours = Math.floor(mins / 60);
    if (hours < 24) return hours + (hours === 1 ? ' hour ago' : ' hours ago');
    const days = Math.floor(hours / 24);
    return days + (days === 1 ? ' day ago' : ' days ago');
  }

  const answered = arr => (arr || []).filter(
    r => r !== null && r !== undefined && !(Array.isArray(r) && !r.length)).length;

  function rows(payload) {
    const out = [];
    if (payload.timer) {
      const mins = Math.floor((payload.timer.elapsed || 0) / 60000);
      const st = GG.S.state || {};
      const subj = (st.subjects || []).find(s => s.id === payload.timer.subjectId);
      out.push((subj ? subj.name : 'Session') + ' \u2014 ' +
        (mins ? GG.hm(mins) + ' on the clock' : 'under a minute on the clock'));
    }
    if (payload.quiz) {
      const total = (payload.quiz.responses || []).length;
      out.push('Practice set \u2014 ' + answered(payload.quiz.responses) +
        ' of ' + total + ' answered');
    }
    return out;
  }

  function offer(info) {
    const payload = (info.saved || {}).payload || {};
    if (!Object.keys(payload).length) return;

    const body = GG.$('#resumeBody');
    const foot = GG.$('#resumeFoot');
    if (!body || !foot) return;

    body.innerHTML = '';
    body.appendChild(GG.el('p', { class: 'dim small', style: 'margin:0 0 12px',
      text: info.unclean_exit
        ? 'GitGrind closed without shutting down properly. This is where you were.'
        : 'You left this running when you last closed GitGrind.' }));

    rows(payload).forEach(text =>
      body.appendChild(GG.el('div', { class: 'resume-row', text: text })));

    if (payload.timer) {
      body.appendChild(GG.el('p', { class: 'dim small', style: 'margin:12px 0 0',
        text: 'Last saved ' + since((info.saved || {}).beat_at) +
          '. The time since then is not counted \u2014 the app was not running.' }));
    }

    foot.innerHTML = '';

    foot.appendChild(GG.el('button', {
      class: 'btn btn-primary', text: 'Resume',
      onclick: async () => {
        GG.modal('#modalResume', false);
        /* Only one dialog can have the foreground. When both halves come back
           the quiz takes it - that is the thing that was actually in front of
           you - and the clock goes to the topbar pill, where a paused timer is
           already legible. Opening both stacks them, which reads as a bug. */
        const both = !!(payload.timer && payload.quiz);
        const mins = payload.timer
          ? Math.floor((payload.timer.elapsed || 0) / 60000) : 0;

        if (payload.timer && GG.timer.restore) {
          GG.timer.restore(payload.timer, { open: !both, quiet: both });
        }

        if (payload.quiz && GG.practice.restore) {
          const reopened = await GG.practice.restore(payload.quiz);
          if (!reopened && payload.timer && GG.timer.open) {
            /* The set could not be rebuilt, so nothing is holding the screen.
               Hand it back to the clock rather than leaving the person on an
               empty page wondering what was restored. */
            GG.timer.open();
          } else if (reopened && both) {
            GG.toast('Session restored',
              GG.hm(mins) + ' is paused in the topbar, and your answers are back.');
          }
        }
        touch();
      },
    }));

    /* Only worth offering when there is something loggable: the session writer
       rejects anything under a minute anyway. */
    const mins = payload.timer ? Math.floor((payload.timer.elapsed || 0) / 60000) : 0;
    if (mins >= 1) {
      foot.appendChild(GG.el('button', {
        class: 'btn', text: 'Log ' + GG.hm(mins) + ' and clear',
        onclick: async () => {
          GG.modal('#modalResume', false);
          if (!GG.timer.restore) return;
          /* open:true here even though the dialog is closed a moment later:
             stop() reads the ticked topics out of #tmTopics rather than from
             timer state, so skipping the build would silently drop them from
             the logged session. */
          GG.timer.restore(payload.timer, { quiet: true });
          await GG.timer.stop();
        },
      }));
    }

    foot.appendChild(GG.el('button', {
      class: 'btn btn-danger', text: 'Discard',
      onclick: async () => {
        GG.modal('#modalResume', false);
        await clear();
        GG.toast('Discarded', 'Nothing was logged.');
      },
    }));

    GG.modal('#modalResume', true);
  }

  /* Called from app.apply on the first state of the load. */
  function restore(state) {
    if (offered) return;
    const info = (state || {}).live;
    if (!info || !info.resumable) return;
    offered = true;
    offer(info);
  }

  document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener('pagehide', beacon);
    /* Hiding covers the case the beacon does not: a window closed to the tray
       in the app-mode path is hidden, then killed, with no pagehide in between. */
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') flush();
    });
  });

  return { register: register, touch: touch, flush: flush, clear: clear,
           restore: restore, since: since };
})();