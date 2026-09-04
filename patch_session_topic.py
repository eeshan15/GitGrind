#!/usr/bin/env python3
"""Finish the job patch_session_subject.py started: the topic branch too.

That patch dropped the session's subject when the note narrowed the set, and
keyed the decision on note_args:

    subject_id=None if note_args else int(subject_id),
    topic_ids=[] if note_args else topic_ids,

Two of the three note branches populate note_args. The third does not - when
the note resolves to a topic rather than a subtopic it assigns topic_ids and
leaves note_args empty - so that branch kept the subject pin and kept failing
in the same way:

    note 'deadlock'
      topicmatch  label deadlock (topic, 32 q)
      endpoint    quiz_from 'deadlock', 0 question(s)

Same cause, same misleading message about the bank being empty or everything
being in cooldown, and it survived the first fix because the condition asked
the wrong question. What matters is whether the note decided the scope, not
which variable happened to carry the answer.

So this adds an explicit flag for that, and while it is in there, scopes the
topic lookup to the label's own subject. "SELECT id FROM topics WHERE slug = ?"
takes whichever row comes first, and topic slugs are unique per subject rather
than globally - the label already knows which subject it came from, in
targets[0], so there is no reason to guess.

Two edits in core/api.py. Requires patch_session_note.py and
patch_session_subject.py.

CRLF-safe and idempotent. Run from the repo root:  python patch_session_topic.py
"""
import io
import os
import sys

EDITS = [
    ('core/api.py',
     '        narrowed = topicmatch.plan(note) if note else None\n'
     '        note_args, quiz_from = {}, ""',

     '        narrowed = topicmatch.plan(note) if note else None\n'
     '        note_args, quiz_from = {}, ""\n'
     '        # Whether the note decided the scope, which is the question the\n'
     '        # subject and topic decisions below actually turn on. Keying them\n'
     '        # on note_args missed the topic branch, because that one narrows\n'
     '        # through topic_ids instead.\n'
     '        by_note = False'),

    ('core/api.py',
     '                note_args = dict(subtopic_slugs=[label["slug"]])\n'
     '                quiz_from = label["slug"]',

     '                note_args = dict(subtopic_slugs=[label["slug"]])\n'
     '                quiz_from = label["slug"]\n'
     '                by_note = True'),

    ('core/api.py',
     '                note_args = dict(question_ids=narrowed["mention_ids"])\n'
     '                quiz_from = "questions mentioning %r" % note[:40]',

     '                note_args = dict(question_ids=narrowed["mention_ids"])\n'
     '                quiz_from = "questions mentioning %r" % note[:40]\n'
     '                by_note = True'),

    ('core/api.py',
     '                row = conn.execute(\n'
     '                    "SELECT id FROM topics WHERE slug = ?", (label["slug"],)\n'
     '                ).fetchone()\n'
     '                if row:\n'
     '                    topic_ids = [row["id"]]\n'
     '                    quiz_from = label["slug"]',

     '                # Scoped to the subject the label came from. Topic slugs\n'
     '                # are unique within a subject, not across the bank, and\n'
     '                # targets[0] already says which subject this is.\n'
     '                where = (label.get("targets") or [{}])[0].get("subject") or ""\n'
     '                row = conn.execute(\n'
     '                    "SELECT t.id FROM topics t JOIN subjects s"\n'
     '                    " ON s.id = t.subject_id"\n'
     '                    " WHERE t.slug = ? AND (s.slug = ? OR ? = \'\')",\n'
     '                    (label["slug"], where, where),\n'
     '                ).fetchone()\n'
     '                if row:\n'
     '                    topic_ids = [row["id"]]\n'
     '                    quiz_from = label["slug"]\n'
     '                    by_note = True'),

    ('core/api.py',
     '        if body.get("with_quiz") and (topic_ids or note_args):',
     '        if body.get("with_quiz") and (topic_ids or note_args):'),

    ('core/api.py',
     '                subject_id=None if note_args else int(subject_id),\n'
     '                topic_ids=[] if note_args else topic_ids,',

     '                subject_id=None if by_note else int(subject_id),\n'
     '                topic_ids=[] if note_args else topic_ids,'),
]


def main():
    path = "core/api.py"
    if not os.path.isfile(path):
        sys.exit("missing %s - run this from the repo root" % path)

    changed = skipped = 0
    for target, old, new in EDITS:
        if old == new:
            continue
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
                     "          Run patch_session_note.py and"
                     " patch_session_subject.py first." % (target, s.count(o)))
        io.open(target, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-14s ok" % target)
        changed += 1

    s = io.open(path, encoding="utf-8", newline="").read()
    flags = s.count("by_note = True")
    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    print("  branches that set by_note: %d of 3 expected" % flags)
    if flags != 3:
        sys.exit("  ERROR   not every note branch flags itself")
    if changed:
        print("  Restart the app, then: python tools\\session_note_check.py")
        print("  A note of 'deadlock' should build questions now.")
    return 0


if __name__ == "__main__":
    sys.exit(main())