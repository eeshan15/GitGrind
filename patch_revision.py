#!/usr/bin/env python3
"""
patch_revision_list.py  --  make the profile's revision list strictly bookmarks.

THE PROBLEM
    The profile page rendered state.revision_queue. That table is the spacing
    engine, not a user list: revision.sync_from_activity() enrols every topic you
    have started, and revision.record_attempt() enrols every question you get
    wrong. Hence 318 due and a page full of rows nobody asked for.

WHY NOT JUST FILTER revision_queue
    Because four other things read it:
        planner.py            builds the daily plan from queue(include_future=False)
        revision.debt()       the DUE pill, and readiness
        revision.strength_map()  topic health / the heatmap
        plan.js               the Today page's own "Revision queue" panel
    Narrowing that table to bookmarks would quietly break all of them.

THE FIX
    Two separate things with two separate names.

      Revision QUEUE  - the spacing engine. Unchanged. Shown on Today.
      Revision LIST   - your bookmarks. New. Shown on Profile.

    quiz.revision_list() reads question_stats.saved as the source of truth and
    LEFT JOINs revision_queue for the schedule, so a bookmark that has been
    retired by two clean solves still appears - marked "mastered" - because it
    is still bookmarked.

Run from the repo root, AFTER fix_profile_appjs.py and patch_profile_v2.py.
Safe to run twice. Writes a .bak beside each file.
"""

import io
import os
import shutil
import sys

EDITS = [
    # ------------------------------------------------------------- quiz.py
    ('core/quiz.py',
     'def saved_ids(conn):',
     '''def revision_list(conn, day=None):
    """The user's revision list: bookmarked questions, and nothing else.

    Deliberately built from question_stats.saved rather than from
    revision_queue. The queue is the spacing engine - it also holds every topic
    you have started and every question you have got wrong, because the planner,
    the debt figure and the readiness score are all computed from it. Reading
    the list off the queue is what made the profile page show 300-odd rows the
    user never asked for.

    The schedule is still shown where one exists, via a LEFT JOIN: a bookmark
    that has been answered correctly twice has been retired from the queue, but
    it is still bookmarked, so it still belongs on this list.
    """
    day = day or date.today().isoformat()
    bank = content.question_bank()
    out = []
    for r in conn.execute(
        "SELECT qs.question_id AS qid, qs.updated_at AS saved_at,"
        "       rq.due_day, rq.reps, rq.lapses, rq.active, rq.interval_days"
        "  FROM question_stats qs"
        "  LEFT JOIN revision_queue rq"
        "    ON rq.item_type = 'question' AND rq.item_key = qs.question_id"
        " WHERE qs.saved = 1"
        " ORDER BY COALESCE(rq.due_day, '9999-12-31') ASC, qs.updated_at DESC"
    ):
        q = bank.get(r["qid"])
        if not q:
            # Bookmarked, then the question left the bank on a re-import. Say so
            # rather than dropping the row silently.
            out.append(
                dict(
                    question_id=r["qid"],
                    label=r["qid"],
                    missing=True,
                    subject_slug="",
                    topic_slug="",
                    difficulty="",
                    marks=0,
                    due_day=r["due_day"] or "",
                    reps=r["reps"] or 0,
                    lapses=r["lapses"] or 0,
                    scheduled=bool(r["active"]),
                    is_due=False,
                )
            )
            continue
        due = r["due_day"] or ""
        out.append(
            dict(
                question_id=r["qid"],
                label=(q.get("text") or r["qid"]).strip()[:110],
                missing=False,
                subject_slug=q.get("subject", ""),
                topic_slug=q.get("topic", ""),
                difficulty=q.get("difficulty", ""),
                marks=q.get("marks", 0),
                due_day=due,
                reps=r["reps"] or 0,
                lapses=r["lapses"] or 0,
                scheduled=bool(r["active"]),
                is_due=bool(due and r["active"] and due <= day),
            )
        )
    return out


def saved_ids(conn):'''),

    # -------------------------------------------------------------- api.py
    ('core/api.py',
     "        saved_ids=quiz.saved_ids(conn),",
     "        saved_ids=quiz.saved_ids(conn),\n"
     "        # The bookmark list, kept separate from revision_queue: that table is\n"
     "        # the spacing engine and also feeds the planner, the debt figure and\n"
     "        # readiness, so it cannot be narrowed to bookmarks.\n"
     "        revision_list=quiz.revision_list(conn),"),

    # ---------------------------------------------------------- index.html
    ('static/index.html',
     '      <div class="head mt"><h2>Revision queue</h2></div>\n'
     '      <div class="card" id="profRevision"></div>',
     '      <div class="head mt"><h2>Revision list</h2></div>\n'
     '      <p class="dim small" style="margin:-4px 0 10px">Only questions you have '
     'bookmarked. The spacing queue that drives your daily plan lives on the Today page.</p>\n'
     '      <div class="card" id="profRevision"></div>'),

    # ------------------------------------------------------------ style.css
    ('static/css/style.css',
     ".rev-list { list-style: none; margin: 0; padding: 0; }",
     """.rev-head { display: flex; align-items: center; justify-content: space-between;
  gap: .8rem; flex-wrap: wrap; margin-bottom: .7rem; }
.rev-drop { opacity: 0; transition: opacity var(--fast); }
.rev-list li:hover .rev-drop, .rev-drop:focus { opacity: 1; }
.rev-list { list-style: none; margin: 0; padding: 0; }"""),

    ('static/css/style.css',
     ".rev-list li { display: grid; grid-template-columns: 1fr auto auto; gap: .8rem;",
     ".rev-list li { display: grid; grid-template-columns: 1fr auto auto auto; gap: .8rem;"),
]

# profile.js revision() is a whole-function swap.
REV_START = "  /* ----------------------------- revision list --------------------------- */"
REV_END = "  function tab(st) {"
REV_NEW = """  /* ----------------------------- revision list --------------------------- */
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
        rows.length + ' bookmarked' + (due ? '  \\u00b7  ' + due + ' due today or earlier' : '') }),
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
        r.marks ? r.marks + 'm' : ''].filter(Boolean).join('  \\u00b7  ');

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

"""


def read(p):
    return io.open(p, encoding="utf-8", newline="").read()


def main():
    if not os.path.isfile("app.py") or not os.path.isdir("static"):
        sys.exit("run this from the repo root (the folder with app.py and static/)")
    if "def saved_ids(conn):" not in read("core/quiz.py"):
        sys.exit("core/quiz.py has no saved_ids() - run patch_profile_v2.py first.")

    changed = skipped = 0
    bufs = {}

    for path, old, new in EDITS:
        if not os.path.isfile(path):
            sys.exit("missing %s" % path)
        bufs.setdefault(path, read(path))
        s = bufs[path]
        crlf = "\r\n" in s
        o = old.replace("\n", "\r\n") if crlf else old
        n = new.replace("\n", "\r\n") if crlf else new
        if n in s:
            print("  skip    %-24s already applied" % path)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d time(s), expected 1" % (path, s.count(o)))
        bufs[path] = s.replace(o, n, 1)
        print("  patched %-24s ok" % path)
        changed += 1

    p = "static/js/profile.js"
    bufs.setdefault(p, read(p))
    s = bufs[p]
    crlf = "\r\n" in s
    a = REV_START.replace("\n", "\r\n") if crlf else REV_START
    b = REV_END.replace("\n", "\r\n") if crlf else REV_END
    body = REV_NEW.replace("\n", "\r\n") if crlf else REV_NEW
    if "revision_list" in s:
        print("  skip    %-24s revision() already rewritten" % p)
        skipped += 1
    elif a in s and b in s:
        i, j = s.index(a), s.index(b)
        bufs[p] = s[:i] + body + s[j:]
        print("  patched %-24s revision() rewritten" % p)
        changed += 1
    else:
        sys.exit("  ERROR   %s: could not find the revision() section markers" % p)

    for path, text in bufs.items():
        if text != read(path):
            if not os.path.exists(path + ".bak2"):
                shutil.copyfile(path, path + ".bak2")
            io.open(path, "w", encoding="utf-8", newline="").write(text)

    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    print("\n  Restart the app, then hard-refresh (Ctrl+Shift+R).")
    print("  Your existing revision_queue rows are left alone - they still drive")
    print("  the daily plan. The profile list simply no longer reads from them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())