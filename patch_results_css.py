#!/usr/bin/env python3
"""Rebuild the results panel additions on the stylesheet's own components.

patch_results.py was written without static/css/style.css to hand, so it laid
the breakdown out with inline styles and a hand-rolled bar. With the stylesheet
available, three things are worth correcting:

  .row-end is defined twice - line 154 with justify-content:space-between and
  line 732 with flex-end. The second wins, so every .row-end header in the app
  right-aligns both children instead of pushing them apart. That is why the
  breakdown label and its count ended up stuck together on the right, and it is
  also why the peer box header above it looks the same way. Not a bug this patch
  introduced and not one it fixes - see the note at the bottom - but the panel
  should not depend on that class to lay out a header.

  .ready-bars / .rb / .rb-name / .bar tall / .rb-val already exist and are
  exactly this component: the readiness page renders per-topic bars with them.
  A 110px name column, a flexible bar, a 92px right-aligned value. Reusing it
  gets correct alignment, the existing width transition, and one less place
  that has to be restyled if the theme changes.

  Bar widths are set through dataset.w and grown after paint by GG.growBars, so
  the CSS transition is visible. Bars written with a literal width skip that
  animation and look different from every other bar in the app. growBars is
  already destructured at the top of practice.js.

Also drops the wrapper div around the footer buttons. .modal-foot is already
display:flex with justify-content:flex-end and gap:8px, so the buttons belong
directly in it - the wrapper was adding a margin-top meant for page sections.

Four edits, all in static/js/practice.js. Run patch_results.py first.

  1. breakdownBox   rebuilt on .ready-bars / .rb, header on .track-head
  2. nextActions    returns an array of buttons rather than a wrapper
  3. results        append the buttons directly, before Done
  4. results        call growBars so the new bars animate like the rest

CRLF-safe and idempotent. Run from the repo root:  python patch_results_css.py
"""
import io
import os
import sys

OLD_BREAKDOWN = '''  function breakdownBox(rows) {
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
  }'''

NEW_BREAKDOWN = '''  function breakdownBox(rows) {
    // Weakest first. The order is the whole point: the top row is the thing
    // to work on, so nothing has to be labelled as advice.
    const sorted = rows.slice().sort((a, b) => a.accuracy - b.accuracy);
    const box = el('div', { class: 'peer-box' });
    // .track-head puts the label left and .track-count pushes the count right
    // with margin-left:auto. .row-end would not: it is declared twice in
    // style.css and the winning rule right-aligns both children.
    box.appendChild(el('div', { class: 'track-head' }, [
      el('b', { style: 'font-size:13px', text: 'How each topic went' }),
      el('span', { class: 'track-count', text: sorted.length + ' topic(s)' }),
    ]));
    const host = el('div', { class: 'ready-bars', style: 'margin-top:12px' });
    sorted.forEach(r => {
      host.appendChild(el('div', { class: 'rb' }, [
        el('span', { class: 'rb-name', text: r.topic,
                     title: r.subject ? r.subject + '/' + r.topic : r.topic }),
        // dataset.w rather than a literal width: GG.growBars sets it after
        // paint so the bar animates like every other bar in the app.
        el('div', { class: 'bar tall' }, el('i', {
          dataset: { w: Math.max(2, r.accuracy) },
          style: 'background:' + (r.accuracy >= 60 ? 'var(--g4)'
                  : r.accuracy >= 35 ? 'var(--warn)' : 'var(--bad)'),
        })),
        el('span', { class: 'rb-val' }, [
          el('b', { text: r.correct + '/' + r.n }),
          document.createTextNode(' \\u00b7 ' + r.accuracy + '%'),
        ]),
      ]));
    });
    box.appendChild(host);
    return box;
  }'''

EDITS = [
    ('static/js/practice.js', OLD_BREAKDOWN, NEW_BREAKDOWN),

    # ---- 2. nextActions returns buttons, not a wrapper ------------------
    ('static/js/practice.js',
     "  function nextActions(out) {\n"
     "    const wrap = el('div', { class: 'row-end', style: 'gap:8px;margin:10px 0 0;flex-wrap:wrap' });\n"
     "    const weakest = (out.breakdown || [])",

     "  function nextActions(out) {\n"
     "    // Returns buttons, not a container. .modal-foot is already a flex row\n"
     "    // with justify-content:flex-end and gap:8px, so a wrapper only added a\n"
     "    // margin-top intended for page sections.\n"
     "    const out_btns = [];\n"
     "    const wrap = { appendChild: b => out_btns.push(b) };\n"
     "    const weakest = (out.breakdown || [])"),

    ('static/js/practice.js',
     '    return wrap.children.length ? wrap : null;\n'
     '  }',

     '    return out_btns;\n'
     '  }'),

    # ---- 3 + 4. results(): append buttons directly, grow the bars -------
    ('static/js/practice.js',
     "    const next = nextActions(out);\n"
     "    if (next) foot.appendChild(next);",

     "    nextActions(out).forEach(b => foot.appendChild(b));"),

    ('static/js/practice.js',
     "    foot.appendChild(el('button', { class: 'btn btn-primary', text: 'Done',\n"
     "      onclick: () => GG.modal('#modalQuiz', false) }));\n"
     "  }\n"
     "\n"
     "  function breakdownBox(rows) {",

     "    foot.appendChild(el('button', { class: 'btn btn-primary', text: 'Done',\n"
     "      onclick: () => GG.modal('#modalQuiz', false) }));\n"
     "    growBars(body);\n"
     "  }\n"
     "\n"
     "  function breakdownBox(rows) {"),
]

NOTE = """
  Not changed, on purpose: the duplicate .row-end in static/css/style.css.
  Deleting either rule would silently re-lay-out every .row-end in the app,
  which is a separate change with its own testing. Worth its own issue.
"""


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
            sys.exit("  ERROR   %s: anchor found %d times, expected 1."
                     " Run patch_results.py first." % (path, s.count(o)))
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-26s ok" % path)
        changed += 1
    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    if changed:
        print("  Hard-refresh the browser - practice.js is cached.")
        print(NOTE.rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())