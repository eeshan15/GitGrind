#!/usr/bin/env python3
"""
patch_profile_v2.py  --  three fixes on top of the profile page.

1. WEEKLY CHART GEOMETRY
   The profile chart borrowed the class names .bar-track and .bar-val, which
   were already taken further up style.css by an 8px pill:

       .bar-track { height:8px; border-radius:999px;
                    background:var(--surface-2); overflow:hidden }

   The profile rule overrode `height` but not `border-radius`, so a ~150px tall
   track kept a 999px radius and rendered as a grey ellipse that clipped its own
   fill. Renamed to pbar-* so the two can never collide again, and while the
   chart was open: bars are now scaled against max(peak, weekly target) with a
   dashed target line, so a short bar reads as "under target" rather than just
   "short".

2. AVATAR LIGHTBOX
   The sidebar showed initials even when a picture was set, which made the
   upload look broken. It now shows the photo, and clicking either avatar opens
   it full size - growing out of the thumbnail you clicked and shrinking back
   into it on close.

3. BOOKMARK -> REVISION LIST
   /api/questions/save only flipped question_stats.saved, which nothing user
   facing ever read. It now also enrols the question in revision_queue (and
   deactivates it on un-bookmark, without resetting an interval you have already
   earned), and every question card carries a bookmark control.

Run from the repo root. Safe to run twice. Writes a .bak beside each file.

Requires fix_profile_appjs.py to have been run first.
"""

import io
import os
import shutil
import sys

# (path, old, new) - each `old` must appear exactly once.
EDITS = [
    # ------------------------------------------------------------------ CSS
    ('static/css/style.css',
     """/* Bars are a flex row of columns rather than absolute positioning, so a week
   with nothing logged still occupies its slot and the gap stays visible. */
.bar-chart { display: flex; align-items: flex-end; gap: .45rem; height: 190px;
  padding-top: 1.1rem; }
.bar-col { flex: 1 1 0; display: flex; flex-direction: column; align-items: center;
  height: 100%; min-width: 0; }
.bar-track { flex: 1 1 auto; width: 100%; display: flex; align-items: flex-end; }
.bar-fill { width: 100%; border-radius: 3px 3px 0 0;
  background: var(--accent-soft, #2f6f5f); transition: height .25s ease; }
.bar-fill.hit { background: var(--accent, #3fbf8f); }
.bar-val { font-size: .68rem; color: var(--dim, #8b95a7); height: 1rem; }
.bar-label { font-size: .68rem; color: var(--dim, #8b95a7); margin-top: .3rem;
  white-space: nowrap; }""",
     """/* Prefixed pbar-* rather than bar-*: the old .bar-track further up this file is
   an 8px pill with border-radius 999px and overflow:hidden, and a 150px-tall
   element wearing that rule renders as an ellipse that clips its own fill. */
.pbar-chart { position: relative; display: flex; align-items: flex-end;
  gap: .5rem; height: 210px; padding: 1.2rem .2rem 0; }
.pbar-col { flex: 1 1 0; display: flex; flex-direction: column; align-items: center;
  height: 100%; min-width: 0; }
.pbar-track { flex: 1 1 auto; width: 100%; display: flex; align-items: flex-end;
  justify-content: center; border-radius: 0; background: none; overflow: visible; }
.pbar-fill { width: 78%; max-width: 64px; min-height: 2px; border-radius: 4px 4px 0 0;
  background: linear-gradient(180deg, #4a5568, #333c4c);
  transition: height .3s var(--ease, ease), filter .12s; }
.pbar-fill.hit { background: linear-gradient(180deg, var(--accent, #e8b43e), #b8862a); }
.pbar-col:hover .pbar-fill { filter: brightness(1.25); }
.pbar-val { font-family: var(--mono); font-size: 11px; text-align: center;
  color: var(--dim); height: 1.05rem; letter-spacing: -.02em; }
.pbar-label { font-family: var(--mono); font-size: 11px; color: var(--faint, #6c7684);
  margin-top: .35rem; white-space: nowrap; }
.pbar-col.best .pbar-val { color: var(--fg); font-weight: 700; }

/* The weekly target drawn across the plot, so a short bar reads as "under
   target" instead of just "short". Bars are scaled against max(peak, target)
   so this line is always on screen. */
.pbar-goal { position: absolute; left: .2rem; right: .2rem; height: 0;
  border-top: 1px dashed rgba(232,180,62,.45); pointer-events: none; }
.pbar-goal span { position: absolute; right: 0; top: -1.05rem;
  font: 10px var(--mono); color: rgba(232,180,62,.75); letter-spacing: .04em; }

/* ---------------------------- avatar lightbox ---------------------------- */
/* The picture grows out of the thumbnail you clicked and shrinks back into it,
   so it stays obvious which avatar is open. */
.avatar-zoom { position: fixed; inset: 0; z-index: 60; display: grid;
  place-items: center; background: #010409ee; cursor: zoom-out; }
.avatar-zoom img { width: min(62vmin, 400px); height: min(62vmin, 400px);
  border-radius: 50%; object-fit: cover; border: 2px solid var(--line);
  box-shadow: 0 24px 70px #000c; }
.avatar-zoom .zoom-hint { position: absolute; bottom: 9%; color: var(--dim);
  font-size: 12px; font-family: var(--mono); }
.avatar-zoom img.in  { animation: avatar-pop .26s cubic-bezier(.16,.84,.44,1) both; }
.avatar-zoom img.out { animation: avatar-pop .17s ease-in reverse both; }
@keyframes avatar-pop {
  from { transform: translate(var(--from-x,0), var(--from-y,0)) scale(var(--from-s,.2));
         opacity: 0; }
  to   { transform: translate(0,0) scale(1); opacity: 1; }
}
body.reduced-motion .avatar-zoom img.in,
body.reduced-motion .avatar-zoom img.out { animation: none; }

.avatar.has-photo, .prof-avatar.has-photo { cursor: zoom-in; }
.avatar.has-photo .avatar-photo { position: absolute; inset: 0; width: 100%;
  height: 100%; object-fit: cover; z-index: 2; }
.avatar.has-photo .avatar-glyph { display: none; }

/* ------------------------------- bookmark -------------------------------- */
/* Sits in the question's chip row. Outline means "not saved", filled means
   "in the revision queue" - the same two states the server stores. */
.bookmark { margin-left: auto; background: none; border: 1px solid var(--line);
  border-radius: 6px; padding: 3px 6px; line-height: 0; cursor: pointer;
  color: var(--dim); transition: color var(--fast), border-color var(--fast),
  background var(--fast); }
.bookmark svg { width: 15px; height: 15px; display: block; }
.bookmark:hover { color: var(--accent); border-color: var(--accent); }
.bookmark.on { color: var(--accent); border-color: rgba(232,180,62,.5);
  background: var(--accent-soft); }
.bookmark.on svg { fill: currentColor; }
.bookmark[disabled] { opacity: .5; cursor: default; }
.row .bookmark { margin-left: 0; }"""),

    # -------------------------------------------------------------- index
    ('static/index.html',
     '<div class="scrim" id="scrim" hidden></div>',
     '<div class="scrim" id="scrim" hidden></div>\n'
     '\n'
     '<div class="avatar-zoom" id="avatarZoom" hidden>\n'
     '  <img id="avatarZoomImg" alt="Profile picture">\n'
     '  <span class="zoom-hint">click anywhere or press Esc to close</span>\n'
     '</div>'),

    # ------------------------------------------------------------- core.js
    ('static/js/core.js',
     "  const closeAll = () => {",
     """  /* --------------------------- avatar lightbox -------------------------- */
  /* Deliberately not a .modal: there is no dialog chrome, no focus trap worth
     the name and no scrim to share - it is a picture and a way out. It reads
     the thumbnail's box so the image can grow out of exactly where you clicked,
     which is what makes the gesture legible. */
  let zoomWired = false;

  function avatarZoom(src, from) {
    if (!src) return;
    const box = $('#avatarZoom');
    const img = $('#avatarZoomImg');
    if (!box || !img) return;

    if (!zoomWired) {
      box.addEventListener('click', avatarZoomClose);
      zoomWired = true;
    }

    img.src = src;
    const r = from && from.getBoundingClientRect ? from.getBoundingClientRect() : null;
    const side = Math.min(Math.min(window.innerWidth, window.innerHeight) * 0.62, 400);
    if (r && r.width) {
      img.style.setProperty('--from-x', (r.left + r.width / 2 - window.innerWidth / 2).toFixed(1) + 'px');
      img.style.setProperty('--from-y', (r.top + r.height / 2 - window.innerHeight / 2).toFixed(1) + 'px');
      img.style.setProperty('--from-s', Math.max(0.05, r.width / side).toFixed(3));
    } else {
      img.style.setProperty('--from-x', '0px');
      img.style.setProperty('--from-y', '0px');
      img.style.setProperty('--from-s', '0.2');
    }

    box.hidden = false;
    /* Restart the animation even when the same picture is opened twice. */
    img.classList.remove('in', 'out');
    void img.offsetWidth;
    img.classList.add('in');
    document.body.classList.add('modal-open');
  }

  function avatarZoomClose() {
    const box = $('#avatarZoom');
    if (!box || box.hidden) return;
    const img = $('#avatarZoomImg');
    img.classList.remove('in');
    img.classList.add('out');
    const done = () => {
      box.hidden = true;
      img.classList.remove('out');
      if (!$$('.modal').some(x => !x.hidden)) document.body.classList.remove('modal-open');
    };
    if (document.body.classList.contains('reduced-motion')) done();
    else setTimeout(done, 180);
  }

  const closeAll = () => {
    avatarZoomClose();"""),

    ('static/js/core.js',
     "    modal, closeAll, show, parseHash, markNav, ROUTES,",
     "    modal, closeAll, show, parseHash, markNav, ROUTES,\n"
     "    avatarZoom, avatarZoomClose,"),

    # ----------------------------------------------------------- render.js
    ('static/js/render.js',
     """    const initials = (p.display_name || 'GG').trim().split(/\\s+/)
      .slice(0, 2).map(w => w[0]).join('').toUpperCase() || 'GG';
    $('#avatarGlyph').textContent = initials;""",
     """    const initials = (p.display_name || 'GG').trim().split(/\\s+/)
      .slice(0, 2).map(w => w[0]).join('').toUpperCase() || 'GG';
    $('#avatarGlyph').textContent = initials;

    /* The sidebar showed initials even when a picture was set, which made the
       upload look like it had not worked. Show the photo, and let it open. */
    const av = $('.avatar');
    if (av) {
      let photo = $('.avatar-photo', av);
      if (p.avatar) {
        if (!photo) {
          photo = el('img', { class: 'avatar-photo', alt: '' });
          av.appendChild(photo);
        }
        if (photo.getAttribute('src') !== p.avatar) photo.src = p.avatar;
        av.classList.add('has-photo');
        av.title = 'Click to enlarge';
        av.onclick = () => GG.avatarZoom(p.avatar, av);
      } else {
        if (photo) photo.remove();
        av.classList.remove('has-photo');
        av.title = '';
        av.onclick = null;
      }
    }"""),

    # ---------------------------------------------------------- profile.js
    ('static/js/profile.js',
     """    const avatar = el('div', { class: 'prof-avatar' });
    if (p.avatar) {
      avatar.appendChild(el('img', { src: p.avatar, alt: '' }));
    } else {""",
     """    const avatar = el('div', { class: 'prof-avatar' });
    if (p.avatar) {
      avatar.appendChild(el('img', { src: p.avatar, alt: '' }));
      avatar.classList.add('has-photo');
      avatar.title = 'Click to enlarge';
      avatar.onclick = () => GG.avatarZoom(p.avatar, avatar);
    } else {"""),

    # ---------------------------------------------------------- practice.js
    ('static/js/practice.js',
     """  const LETTER = i => String.fromCharCode(65 + i);
  let quiz = null;      /* { id, questions, responses, idx, startedAt } */
""",
     """  const LETTER = i => String.fromCharCode(65 + i);
  let quiz = null;      /* { id, questions, responses, idx, startedAt } */

  /* ============================= bookmark ============================== */
  /* Outline when unsaved, filled when saved - one glyph, so the two states
     cannot be confused with two different buttons. */
  const BOOKMARK_SVG =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>';

  const isSaved = id => ((GG.S.state || {}).saved_ids || []).indexOf(id) !== -1;

  function bookmark(q) {
    const id = q.id || q.question_id;
    const btn = el('button', { class: 'bookmark', type: 'button' });
    btn.innerHTML = BOOKMARK_SVG;

    const paint = on => {
      btn.classList.toggle('on', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.title = on
        ? 'In your revision list - click to remove'
        : 'Save to your revision list';
    };
    paint(isSaved(id));

    btn.onclick = async ev => {
      /* The whole question card is clickable in some views. */
      ev.stopPropagation();
      ev.preventDefault();
      const want = !btn.classList.contains('on');
      /* Paint first: the round trip rebuilds the entire state and the delay is
         long enough to feel like the click was dropped. Reverted on failure. */
      paint(want);
      btn.disabled = true;
      try {
        const out = await GG.api('/questions/save',
          { body: { question_id: id, saved: want } });
        if (out && out.state) {
          GG.S.state = out.state;
          /* Only repaint views that actually show this list. A quiz in a modal
             must not be torn down underneath the person answering it. */
          if (GG.S.route === 'profile' || GG.S.route === 'practice') GG.app.paint();
        }
        GG.toast(want ? 'Saved for revision' : 'Removed from revision',
          want ? 'It is in the revision queue on your profile.' : '');
      } catch (e) {
        paint(!want);
        GG.toast('Could not save', e.message, 'bad');
      } finally {
        btn.disabled = false;
      }
    };
    return btn;
  }
"""),

    ('static/js/practice.js',
     """      q.topic ? el('span', { class: 'chip-kind', text: q.topic }) : null,
    ]));""",
     """      q.topic ? el('span', { class: 'chip-kind', text: q.topic }) : null,
      /* Last in the row and pushed right by margin-left:auto, so it reads as an
         action on the question rather than another label about it. */
      bookmark(q),
    ]));"""),

    ('static/js/practice.js',
     "  return { tab, renderQotd, startSet, open, questionBlock, verdict };",
     "  return { tab, renderQotd, startSet, open, questionBlock, verdict, bookmark };"),

    # -------------------------------------------------------------- bank.js
    ('static/js/bank.js',
     """          el('button', {
            class: 'btn btn-sm',
            onclick: () => GG.practice.startSet({ questionIds: [q.id], purpose: 'fresh' }),
          }, ['Try it']),
        ]));""",
     """          GG.practice.bookmark(q),
          el('button', {
            class: 'btn btn-sm',
            onclick: () => GG.practice.startSet({ questionIds: [q.id], purpose: 'fresh' }),
          }, ['Try it']),
        ]));"""),

    # ------------------------------------------------------------- quiz.py
    ('core/quiz.py',
     '''def save_question(conn, question_id, saved=True):
    q = content.question_bank().get(question_id)
    if not q:
        raise LookupError("Unknown question.")
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "INSERT INTO question_stats (question_id, subject_slug, topic_slug, saved,"
            " updated_at) VALUES (?,?,?,?,?)"
            " ON CONFLICT(question_id) DO UPDATE SET saved = excluded.saved,"
            " updated_at = excluded.updated_at",
            (question_id, q["subject"], q.get("topic", ""), 1 if saved else 0, now),
        )
    return dict(question_id=question_id, saved=bool(saved))''',
     '''def save_question(conn, question_id, saved=True):
    """Bookmark a question, and put it in (or take it out of) the revision queue.

    Bookmarking and enrolling used to be two separate things, which meant the
    star did nothing you could see later. There is only one thing a person means
    when they press it - "show me this again" - so the two now move together.
    Un-bookmarking deactivates the queue row rather than deleting it, so an
    accidental double-click does not throw away an interval you have earned.
    """
    q = content.question_bank().get(question_id)
    if not q:
        raise LookupError("Unknown question.")
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "INSERT INTO question_stats (question_id, subject_slug, topic_slug, saved,"
            " updated_at) VALUES (?,?,?,?,?)"
            " ON CONFLICT(question_id) DO UPDATE SET saved = excluded.saved,"
            " updated_at = excluded.updated_at",
            (question_id, q["subject"], q.get("topic", ""), 1 if saved else 0, now),
        )
        if saved:
            row = conn.execute(
                "SELECT id FROM revision_queue WHERE item_type = 'question'"
                " AND item_key = ?",
                (question_id,),
            ).fetchone()
            if row:
                # Already scheduled - reactivate without resetting the interval.
                conn.execute(
                    "UPDATE revision_queue SET active = 1, updated_at = ?"
                    " WHERE item_type = 'question' AND item_key = ?",
                    (now, question_id),
                )
            else:
                revision.enrol_question(conn, q)
        else:
            revision.drop(conn, "question", question_id)
    return dict(question_id=question_id, saved=bool(saved))


def saved_ids(conn):
    """Every bookmarked question id, so the UI can draw the star correctly.

    A flat list rather than the full rows: the practice view only needs to know
    which stars are filled, and the payload already carries this state once.
    """
    return [
        r["question_id"]
        for r in conn.execute(
            "SELECT question_id FROM question_stats WHERE saved = 1"
        )
    ]'''),

    # -------------------------------------------------------------- api.py
    ('core/api.py',
     "        saved_questions=quiz.saved_questions(conn, 20),",
     "        saved_questions=quiz.saved_questions(conn, 20),\n"
     "        saved_ids=quiz.saved_ids(conn),"),

    ('core/api.py',
     '''        if path == "/api/questions/save":
            return (
                quiz.save_question(
                    conn, body.get("question_id"), bool(body.get("saved", True))
                ),
                200,
            )''',
     '''        if path == "/api/questions/save":
            # Bookmarking now moves the revision queue, so the client needs the
            # whole state back or the profile page would keep showing the old
            # list until the next full refresh.
            outcome = quiz.save_question(
                conn, body.get("question_id"), bool(body.get("saved", True))
            )
            outcome["state"] = build_state(conn)
            return outcome, 200'''),
]

# The weekly() rewrite is a whole-function swap, handled separately because the
# body is long enough that an anchor diff would be harder to read than this.
WEEKLY_START = "  /* ---------------------------- weekly minutes --------------------------- */"
WEEKLY_END = "  /* -------------------------- difficulty split --------------------------- */"
WEEKLY_NEW = """  /* ---------------------------- weekly minutes --------------------------- */
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

"""


def read(path):
    return io.open(path, encoding="utf-8", newline="").read()


def write(path, text):
    if not os.path.exists(path + ".bak"):
        shutil.copyfile(path, path + ".bak")
    io.open(path, "w", encoding="utf-8", newline="").write(text)


def main():
    if not os.path.isfile("app.py") or not os.path.isdir("static"):
        sys.exit("run this from the repo root (the folder with app.py and static/)")

    changed = skipped = 0
    buffers = {}

    for path, old, new in EDITS:
        if not os.path.isfile(path):
            sys.exit("missing %s" % path)
        if path not in buffers:
            buffers[path] = read(path)
        s = buffers[path]
        crlf = "\r\n" in s
        o = old.replace("\n", "\r\n") if crlf else old
        n = new.replace("\n", "\r\n") if crlf else new
        if n in s:
            print("  skip    %-24s already applied" % path)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d time(s), expected 1.\n"
                     "          Did you run fix_profile_appjs.py first?" % (path, s.count(o)))
        buffers[path] = s.replace(o, n, 1)
        print("  patched %-24s ok" % path)
        changed += 1

    # ---- profile.js weekly() whole-function swap --------------------------
    p = "static/js/profile.js"
    if p not in buffers:
        buffers[p] = read(p)
    s = buffers[p]
    crlf = "\r\n" in s
    start = WEEKLY_START.replace("\n", "\r\n") if crlf else WEEKLY_START
    end = WEEKLY_END.replace("\n", "\r\n") if crlf else WEEKLY_END
    body = WEEKLY_NEW.replace("\n", "\r\n") if crlf else WEEKLY_NEW
    if "pbar-chart" in s:
        print("  skip    %-24s weekly() already rewritten" % p)
        skipped += 1
    elif start in s and end in s:
        i, j = s.index(start), s.index(end)
        buffers[p] = s[:i] + body + s[j:]
        print("  patched %-24s weekly() rewritten" % p)
        changed += 1
    else:
        sys.exit("  ERROR   %s: could not find the weekly() section markers" % p)

    for path, text in buffers.items():
        if text != read(path):
            write(path, text)

    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    if changed:
        print("  backups written as <file>.bak")
    print("\n  Restart the app, then hard-refresh the browser (Ctrl+Shift+R) -")
    print("  style.css and the js files are cached aggressively.")
    return 0


if __name__ == "__main__":
    sys.exit(main())