#!/usr/bin/env python3
"""Render the session-end data the backend has been sending all along.

quiz.submit_quiz returns breakdown (per-topic accuracy for the set), wrong_ids
and retry_available, and /api/quiz/retry plus quiz.retry_set have existed the
whole time. practice.js results() renders the score hero, the peer box and the
per-question cards, then puts a single "Done" button in the footer and drops
all three. So after finishing a set the app knows exactly which topic just went
badly and offers nothing to do about it.

That is the original complaint - nothing relevant comes back after a session -
and most of it is a missing twenty lines of frontend, not a matching problem.

Three edits:

  1. breakdownBox()   per-topic accuracy for the set just finished, weakest
                      first, so the ordering itself is the recommendation
  2. nextActions()    "Retry the N you missed" from wrong_ids, and "Practise 5
                      more on <weakest topic>" - the API resolves subject and
                      topic slugs itself, so neither needs a new endpoint
  3. results()        call both, and keep Done as the last button

Styling uses only classes practice.js already uses (rh, res-list, peer-box,
row-end, dim small, btn, btn-primary) plus the CSS variables it already reads
(--g4, --warn, --bad). Nothing here needs a stylesheet change.

Run patch_subtopic.py first if you have not - not because this depends on it,
but because the weakest-topic button is far more useful once subtopics exist.

CRLF-safe and idempotent. Run from the repo root:  python patch_results.py
"""
import io
import os
import sys

EDITS = [
    # ---- 1 + 2. the two new builders, before peerBox --------------------
    ('static/js/practice.js',
     '  function peerBox(p) {',

     '''  function breakdownBox(rows) {
    // Weakest first. The order is the whole point: the top row is the thing
    // to work on, so nothing has to be labelled as advice.
    const sorted = rows.slice().sort((a, b) => a.accuracy - b.accuracy);
    const box = el('div', { class: 'peer-box' });
    box.appendChild(el('div', { class: 'row-end', style: 'margin:0 0 8px' }, [
      el('b', { style: 'font-size:13px', text: 'How each topic went' }),
      el('span', { class: 'dim small', text: sorted.length + ' topic(s) in this set' }),
    ]));
    sorted.forEach(r => {
      const tone = r.accuracy >= 60 ? 'var(--g4)' : r.accuracy >= 35 ? 'var(--warn)' : 'var(--bad)';
      const row = el('div', { style: 'margin:6px 0' });
      row.appendChild(el('div', { class: 'row-end', style: 'margin:0 0 3px' }, [
        el('span', { style: 'font-size:13px', text: r.topic }),
        el('span', { class: 'dim small',
                     text: r.correct + '/' + r.n + '  (' + r.accuracy + '%)' }),
      ]));
      const track = el('div', {
        style: 'height:4px;border-radius:2px;background:var(--line,#333);overflow:hidden',
      });
      track.appendChild(el('div', {
        style: 'height:4px;width:' + Math.max(2, r.accuracy) + '%;background:' + tone,
      }));
      row.appendChild(track);
      box.appendChild(row);
    });
    return box;
  }

  function nextActions(out) {
    const wrap = el('div', { class: 'row-end', style: 'gap:8px;margin:10px 0 0;flex-wrap:wrap' });
    const weakest = (out.breakdown || [])
      .slice()
      .sort((a, b) => a.accuracy - b.accuracy)[0];

    if (out.retry_available && (out.wrong_ids || []).length) {
      const n = out.wrong_ids.length;
      wrap.appendChild(el('button', {
        class: 'btn', text: 'Retry the ' + n + ' you missed',
        onclick: async ev => {
          ev.target.disabled = true;
          try {
            const built = await GG.api('/quiz/retry', { body: { question_ids: out.wrong_ids } });
            open(built, 'Retry');
          } catch (e) {
            ev.target.disabled = false;
            GG.toast('Could not build the retry set', e.message, 'bad');
          }
        },
      }));
    }

    if (weakest && weakest.topic) {
      wrap.appendChild(el('button', {
        class: 'btn', text: 'Practise 5 more on ' + weakest.topic,
        onclick: async ev => {
          ev.target.disabled = true;
          try {
            // The API resolves subject and topic slugs to ids itself, so this
            // needs no new endpoint and no id lookup on this side.
            const built = await GG.api('/quiz', {
              body: {
                subject: weakest.subject || null,
                topic: weakest.topic,
                count: 5,
                reason: 'weakest topic in the set you just finished',
              },
            });
            open(built, 'More on ' + weakest.topic);
          } catch (e) {
            ev.target.disabled = false;
            GG.toast('Could not build the set', e.message, 'bad');
          }
        },
      }));
    }
    return wrap.children.length ? wrap : null;
  }

  function peerBox(p) {'''),

    # ---- 3a. render the breakdown --------------------------------------
    ('static/js/practice.js',
     '    if (out.peer) body.appendChild(peerBox(out.peer));',

     '    if (out.peer) body.appendChild(peerBox(out.peer));\n'
     '    if ((out.breakdown || []).length > 1) body.appendChild(breakdownBox(out.breakdown));'),

    # ---- 3b. the footer -------------------------------------------------
    ('static/js/practice.js',
     "    const foot = $('#quizFoot');\n"
     "    foot.innerHTML = '';\n"
     "    foot.appendChild(el('button', { class: 'btn btn-primary', text: 'Done',\n"
     "      onclick: () => GG.modal('#modalQuiz', false) }));\n"
     "  }",

     "    const foot = $('#quizFoot');\n"
     "    foot.innerHTML = '';\n"
     "    const next = nextActions(out);\n"
     "    if (next) foot.appendChild(next);\n"
     "    // Done stays last: the offers sit before it rather than in place of\n"
     "    // it, so finishing is still the default and nothing is now two clicks\n"
     "    // away that used to be one.\n"
     "    foot.appendChild(el('button', { class: 'btn btn-primary', text: 'Done',\n"
     "      onclick: () => GG.modal('#modalQuiz', false) }));\n"
     "  }"),
]


def main():
    changed = skipped = 0
    for path, old, new in EDITS:
        if not os.path.isfile(path):
            sys.exit("missing %s - run this from the repo root" % path)
        s = io.open(path, encoding="utf-8", newline="").read()
        crlf = "\r\n" in s
        o = old.replace("\n", "\r\n") if crlf else old
        n = new.replace("\n", "\r\n") if crlf else new
        if n in s:
            print("  skip    %-26s already applied" % path)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d times, expected 1"
                     % (path, s.count(o)))
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-26s ok" % path)
        changed += 1
    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    if changed:
        print("  Hard-refresh the browser - practice.js is cached.")
    return 0


if __name__ == "__main__":
    sys.exit(main())