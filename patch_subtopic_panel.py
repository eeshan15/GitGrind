#!/usr/bin/env python3
"""Offer the weakest subtopic after a session, not just the weakest topic.

The results panel says "Practise 5 more on analytical" because topic was the
finest label it was told about. With subtopic_breakdown available it can say
venn-diagram instead, which for that set is the difference between 70 questions
and 7.

It cannot simply always prefer the subtopic though. Subtopics are narrow by
construction and some are very thin - bankers-algorithm carries two questions
in the whole bank - so offering "5 more" there delivers one, which is a worse
answer than the wider topic would have been. The panel has no way to know that
from the breakdown alone.

So each breakdown row gains "available": how many questions in the bank carry
that label, not just how many were in the set. Counted only for the handful of
labels this quiz actually touched, in one pass, which costs a few milliseconds
on submit and saves adding a cache to quiz.py.

The frontend then prefers the weakest subtopic when at least five questions
exist behind it and falls back to the weakest topic otherwise. Both buttons are
never shown at once: two offers is a decision, and the point of this panel is
to make the next step obvious.

Three edits:

  1. quiz.submit_quiz   add "available" to both breakdown lists
  2. practice.js        pick the subtopic when it can be filled
  3. practice.js        show the subtopic under its topic in the bar list, so
                        an unfamiliar slug has context

Run patch_subtopic_api.py first.

CRLF-safe and idempotent. Run from the repo root:  python patch_subtopic_panel.py
"""
import io
import os
import sys

EDITS = [
    # ---- 1. available counts -------------------------------------------
    ('core/quiz.py',
     '    subtopic_breakdown = [\n'
     '        dict(\n'
     '            subtopic=k,',

     '    # How much the bank holds for each label this quiz touched, so the\n'
     '    # panel can avoid offering a set it cannot fill. Only these few slugs\n'
     '    # are counted, so this is one pass and no cache.\n'
     '    _want_t = set(per_topic)\n'
     '    _want_s = set(per_subtopic)\n'
     '    _have_t = dict.fromkeys(_want_t, 0)\n'
     '    _have_s = dict.fromkeys(_want_s, 0)\n'
     '    for _q in bank.values():\n'
     '        _t = _q.get("topic", "")\n'
     '        if _t in _want_t:\n'
     '            _have_t[_t] += 1\n'
     '        _s = _q.get("subtopic", "")\n'
     '        if _s in _want_s:\n'
     '            _have_s[_s] += 1\n'
     '\n'
     '    subtopic_breakdown = [\n'
     '        dict(\n'
     '            available=_have_s.get(k, 0),\n'
     '            subtopic=k,'),

    ('core/quiz.py',
     '    breakdown = [\n'
     '        dict(\n'
     '            topic=k,',

     '    breakdown = [\n'
     '        dict(\n'
     '            available=_have_t.get(k, 0),\n'
     '            topic=k,'),

    # ---- 2. prefer the subtopic when it can be filled -------------------
    ('static/js/practice.js',
     "    const out_btns = [];\n"
     "    const wrap = { appendChild: b => out_btns.push(b) };\n"
     "    const weakest = (out.breakdown || [])\n"
     "      .slice()\n"
     "      .sort((a, b) => a.accuracy - b.accuracy)[0];\n",

     "    const out_btns = [];\n"
     "    const wrap = { appendChild: b => out_btns.push(b) };\n"
     "    const byAccuracy = rows => rows.slice().sort((a, b) => a.accuracy - b.accuracy)[0];\n"
     "    // A subtopic is the sharper offer, but only when the bank can fill\n"
     "    // it: bankers-algorithm has two questions in total, so \"5 more\"\n"
     "    // there would hand back one. Below that, the topic is the better\n"
     "    // answer even though it is broader.\n"
     "    const weakSub = byAccuracy((out.subtopic_breakdown || [])\n"
     "      .filter(r => (r.available || 0) >= 5));\n"
     "    const weakTopic = byAccuracy(out.breakdown || []);\n"
     "    const weakest = weakSub || weakTopic;\n",

     ),

    ('static/js/practice.js',
     "    if (weakest && weakest.topic) {\n"
     "      wrap.appendChild(el('button', {\n"
     "        class: 'btn', text: 'Practise 5 more on ' + weakest.topic,",

     "    if (weakest && (weakest.subtopic || weakest.topic)) {\n"
     "      const label = weakest.subtopic || weakest.topic;\n"
     "      wrap.appendChild(el('button', {\n"
     "        class: 'btn', text: 'Practise 5 more on ' + label.replace(/-/g, ' '),"),

    ('static/js/practice.js',
     "            const built = await GG.api('/quiz', {\n"
     "              body: {\n"
     "                subject: weakest.subject || null,\n"
     "                topic: weakest.topic,\n"
     "                count: 5,\n"
     "                reason: 'weakest topic in the set you just finished',\n"
     "              },\n"
     "            });\n"
     "            open(built, 'More on ' + weakest.topic);",

     "            const built = await GG.api('/quiz', {\n"
     "              body: {\n"
     "                subject: weakest.subject || null,\n"
     "                // Send one or the other, never both: a subtopic can sit\n"
     "                // under more than one topic, and pinning it to this set's\n"
     "                // topic would drop the rest.\n"
     "                topic: weakest.subtopic ? null : weakest.topic,\n"
     "                subtopic: weakest.subtopic || null,\n"
     "                count: 5,\n"
     "                reason: 'weakest ' + (weakest.subtopic ? 'subtopic' : 'topic')\n"
     "                        + ' in the set you just finished',\n"
     "              },\n"
     "            });\n"
     "            open(built, 'More on ' + label.replace(/-/g, ' '));"),

    # ---- 3. show subtopic rows with their topic for context -------------
    ('static/js/practice.js',
     "    if ((out.breakdown || []).length > 1) body.appendChild(breakdownBox(out.breakdown));",

     "    // Prefer the subtopic view when it says more than the topic view -\n"
     "    // one row per topic is no breakdown at all.\n"
     "    const sub = out.subtopic_breakdown || [];\n"
     "    const top = out.breakdown || [];\n"
     "    const rows = sub.length > top.length ? sub : top;\n"
     "    if (rows.length > 1) body.appendChild(breakdownBox(rows));"),

    ('static/js/practice.js',
     "        el('span', { class: 'rb-name', text: r.topic,\n"
     "                     title: r.subject ? r.subject + '/' + r.topic : r.topic }),",

     "        el('span', { class: 'rb-name',\n"
     "                     text: (r.subtopic || r.topic || '').replace(/-/g, ' '),\n"
     "                     title: [r.subject, r.topic, r.subtopic]\n"
     "                       .filter(Boolean).join('/') }),"),
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
            print("  skip    %-24s already applied" % path)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d times, expected 1.\n"
                     "          Run patch_subtopic_api.py first." % (path, s.count(o)))
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-24s ok" % path)
        changed += 1
    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    if changed:
        print("  Restart the app and hard-refresh the browser.")
    return 0


if __name__ == "__main__":
    sys.exit(main())