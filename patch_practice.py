#!/usr/bin/env python3
"""Send per-question timing and confidence from the quiz UI.

core/quiz.py already reads seconds, confidence and mistake_kind off each
response. static/js/practice.js never sent them, so attempts.seconds held the
set duration divided evenly - flat within every set, and useless as a feature.
This is the UI half.

CRLF-safe and idempotent. Run from the repo root:  python patch_practice.py
"""
import io, os, sys

EDITS = [
    ('static/js/practice.js',
     '      responses: built.questions.map(() => null),\n      idx: 0,',
     '      responses: built.questions.map(() => null),\n      // Per-question timing and confidence. The backend has always read these\n      // off each response (quiz._record_attempt), but the UI never sent them, so\n      // attempts.seconds was the set duration divided evenly - a column that\n      // looked complete and carried no information.\n      times: built.questions.map(() => 0),\n      conf: built.questions.map(() => null),\n      shownAt: Date.now(),\n      idx: 0,'),
    ('static/js/practice.js',
     '  function draw() {\n    const q = quiz.questions[quiz.idx];',
     '  /* Bank the time spent on the question now on screen. Called before every\n     move, so revisiting a question accumulates rather than overwrites. */\n  function stamp() {\n    if (!quiz) return;\n    const now = Date.now();\n    quiz.times[quiz.idx] += Math.max(0, Math.round((now - quiz.shownAt) / 1000));\n    quiz.shownAt = now;\n  }\n\n  function go(i) {\n    stamp();\n    quiz.idx = i;\n    draw();\n  }\n\n  function draw() {\n    const q = quiz.questions[quiz.idx];\n    quiz.shownAt = Date.now();'),
    ('static/js/practice.js',
     '        text: String(i + 1),\n        onclick: () => { quiz.idx = i; draw(); },',
     '        text: String(i + 1),\n        onclick: () => go(i),'),
    ('static/js/practice.js',
     "    if (quiz.idx > 0) foot.appendChild(el('button', {\n      class: 'btn', text: '< Back', onclick: () => { quiz.idx--; draw(); } }));\n    if (quiz.idx < quiz.questions.length - 1) {\n      foot.appendChild(el('button', {\n        class: 'btn', text: 'Next >', onclick: () => { quiz.idx++; draw(); } }));\n    }",
     "    if (quiz.idx > 0) foot.appendChild(el('button', {\n      class: 'btn', text: '< Back', onclick: () => go(quiz.idx - 1) }));\n    if (quiz.idx < quiz.questions.length - 1) {\n      foot.appendChild(el('button', {\n        class: 'btn', text: 'Next >', onclick: () => go(quiz.idx + 1) }));\n    }"),
    ('static/js/practice.js',
     '      onPick: v => { quiz.responses[quiz.idx] = v; draw(); },\n    }));\n    body.appendChild(holder);',
     '      onPick: v => { stamp(); quiz.responses[quiz.idx] = v; draw(); },\n    }));\n\n    /* Confidence is asked for, not inferred. A wrong answer given confidently is\n       a different problem from a wrong guess, and only the person answering\n       knows which it was. Optional: skipping it logs null, not a fake value. */\n    const conf = el(\'div\', { class: \'row-end\', style: \'gap:6px;margin-top:10px\' }, [\n      el(\'span\', { class: \'dim small\', style: \'margin-right:auto\',\n        text: \'How sure are you?\' }),\n    ]);\n    /* 1-5, matching the clamp in quiz._record_attempt. A 0-1 float would be\n       squashed to 1 by int() and every rating would read as "no idea". */\n    [[\'No idea\', 1], [\'Guess\', 2], [\'Unsure\', 3], [\'Fairly sure\', 4], [\'Certain\', 5]]\n      .forEach(([label, v]) => {\n        const on = quiz.conf[quiz.idx] === v;\n        conf.appendChild(el(\'button\', {\n          class: \'btn btn-sm\' + (on ? \' btn-primary\' : \'\'),\n          text: label,\n          onclick: () => {\n            stamp();\n            quiz.conf[quiz.idx] = on ? null : v;\n            draw();\n          },\n        }));\n      });\n    holder.appendChild(conf);\n    body.appendChild(holder);'),
    ('static/js/practice.js',
     '    const payload = quiz.questions.map((q, i) => ({\n      question_id: q.id, response: quiz.responses[i],\n    }));',
     '    stamp();\n    const payload = quiz.questions.map((q, i) => ({\n      question_id: q.id,\n      response: quiz.responses[i],\n      seconds: quiz.times[i],\n      confidence: quiz.conf[i],\n    }));'),
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
            sys.exit("  ERROR   %s: anchor found %d times, expected 1" % (path, s.count(o)))
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-26s ok" % path)
        changed += 1
    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())