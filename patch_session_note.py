#!/usr/bin/env python3
"""Build the after-session quiz from what you typed, not only what you ticked.

The flow already exists end to end. timer.js stop() posts the note, the ticked
topic chips, with_quiz and quiz_count; /api/sessions builds a set; and the
timer reopens it as "Quiz on what you just studied". The one thing missing is
the note itself:

    if body.get("with_quiz") and topic_ids:
        built, err = quiz.build_quiz(conn, topic_ids=topic_ids, ...)

The note is stored on the session and never used to choose anything, so a
session tagged "banker algo" produces a set drawn from the whole deadlock
topic - 32 questions - rather than the two about Banker's algorithm. And with
no chip ticked, nothing is built at all even when the note says exactly what
was studied.

This runs the note through topicmatch and lets the result narrow the set:

  resolves to a subtopic   filter on it, and drop topic_ids. A subtopic can sit
                           under more than one topic and pinning it to the
                           ticked one would drop the rest. This is the case the
                           whole exercise was for.
  resolves to a topic      the chips win if there are any: ticking a topic is
                           deliberate, while a note is a description. The note
                           only takes over when nothing was ticked.
  resolves to nothing but
  the words appear in
  question text            pass those question ids. "tlb" matches 14 questions
                           by text and only 2 by label, so the text is the
                           better answer there.
  resolves to nothing      behave exactly as before.

Also relaxes the `and topic_ids` guard, so a note alone is enough to get a set.
Without that, the feature only works for people who were already ticking chips,
which is the group that needed it least.

The response gains quiz_from, naming what the set was narrowed by, so the UI
can say so instead of claiming it is "what you just studied" when it guessed.

Two edits in core/api.py. Requires core/topicmatch.py and
patch_subtopic_api.py.

CRLF-safe and idempotent. Run from the repo root:  python patch_session_note.py
"""
import io
import os
import sys

EDITS = [
    ('core/api.py',
     '    stats,\n'
     ')',

     '    stats,\n'
     '    topicmatch,\n'
     ')'),

    ('core/api.py',
     '        if body.get("with_quiz") and topic_ids:\n'
     '            bundle = stats.gather(conn)\n'
     '            built, err = quiz.build_quiz(\n'
     '                conn,\n'
     '                subject_id=int(subject_id),\n'
     '                topic_ids=topic_ids,\n'
     '                count=body.get("quiz_count", 5),\n'
     '                session_id=session_id,\n'
     '                metrics=bundle["metrics"],\n'
     '                topic_health=bundle["topic_health"],\n'
     '            )\n'
     '            out["quiz"] = built\n'
     '            out["quiz_error"] = err',

     '        # The note says what was actually studied, in the words of the\n'
     '        # person who studied it, at the moment they still remember. That\n'
     '        # is a better description of the session than a topic chip, and\n'
     '        # until now it was only ever stored.\n'
     '        narrowed = topicmatch.plan(note) if note else None\n'
     '        note_args, quiz_from = {}, ""\n'
     '        if narrowed:\n'
     '            label = narrowed.get("label")\n'
     '            if label and label["kind"] == "subtopic":\n'
     '                # Deliberately without topic_ids: a subtopic can sit under\n'
     '                # more than one topic, and pinning it to the ticked one\n'
     '                # would drop the rest of its questions.\n'
     '                note_args = dict(subtopic_slugs=[label["slug"]])\n'
     '                quiz_from = label["slug"]\n'
     '            elif narrowed["advice"] == "mentions" and narrowed["mention_ids"]:\n'
     '                note_args = dict(question_ids=narrowed["mention_ids"])\n'
     '                quiz_from = "questions mentioning %r" % note[:40]\n'
     '            elif label and not topic_ids:\n'
     '                # A ticked chip beats a note: ticking is a choice, writing\n'
     '                # is a description. With nothing ticked the note is all\n'
     '                # there is. build_quiz takes topic ids rather than slugs,\n'
     '                # so this goes through the same lookup /api/quiz uses.\n'
     '                row = conn.execute(\n'
     '                    "SELECT id FROM topics WHERE slug = ?", (label["slug"],)\n'
     '                ).fetchone()\n'
     '                if row:\n'
     '                    topic_ids = [row["id"]]\n'
     '                    quiz_from = label["slug"]\n'
     '\n'
     '        if body.get("with_quiz") and (topic_ids or note_args):\n'
     '            bundle = stats.gather(conn)\n'
     '            built, err = quiz.build_quiz(\n'
     '                conn,\n'
     '                subject_id=int(subject_id),\n'
     '                topic_ids=[] if note_args else topic_ids,\n'
     '                count=body.get("quiz_count", 5),\n'
     '                session_id=session_id,\n'
     '                metrics=bundle["metrics"],\n'
     '                topic_health=bundle["topic_health"],\n'
     '                **note_args,\n'
     '            )\n'
     '            # Reported so the UI can name what it narrowed to rather than\n'
     '            # claiming to know what was studied.\n'
     '            out["quiz_from"] = quiz_from\n'
     '            out["quiz"] = built\n'
     '            out["quiz_error"] = err'),
]


def main():
    path = "core/api.py"
    if not os.path.isfile(path):
        sys.exit("missing %s - run this from the repo root" % path)
    if not os.path.isfile("core/topicmatch.py"):
        sys.exit("core/topicmatch.py is missing - install it first")

    changed = skipped = 0
    for target, old, new in EDITS:
        s = io.open(target, encoding="utf-8", newline="").read()
        crlf = "\r\n" in s
        o = old.replace("\n", "\r\n") if crlf else old
        n = new.replace("\n", "\r\n") if crlf else new
        if n in s:
            print("  skip    %-14s already applied" % target)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d times, expected 1.\n"
                     "          Run patch_subtopic_api.py first." % (target, s.count(o)))
        io.open(target, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-14s ok" % target)
        changed += 1

    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    if changed:
        print("  Restart the app. Then run the timer for a minute, put")
        print("  \"banker algo\" in the note, tick \"quiz me after\", and stop it.")
        print("  Verify with: python tools/session_note_check.py \"banker algo\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())