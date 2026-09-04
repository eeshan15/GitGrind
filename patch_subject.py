#!/usr/bin/env python3
"""Don't pin a note-resolved set to the session's subject.

patch_session_note.py narrows the after-session quiz by the note, but left
subject_id in place, so build_quiz filtered by both. That is fine when the two
agree and empty when they do not:

    note 'banker algo'
      topicmatch  label bankers-algorithm (subtopic, 2 q)
      endpoint    quiz_from 'bankers-algorithm', 0 question(s)
                  nothing built - the bank has none, or everything is inside
                  its repeat cooldown

The message is wrong twice over. The bank has two, and neither is in cooldown;
they are just not in the subject the session was logged under. Log an hour
against Digital Logic, write "banker algo" in the note, and you get nothing,
with an explanation that sends you looking in the wrong place.

Pinning is redundant anyway. A subtopic filter is strictly narrower than a
subject filter - bankers-algorithm only exists inside operating systems - so
adding the subject can subtract questions and can never add one. The same
already applies to topic_ids, which this patch's predecessor cleared for the
same reason.

So when the note resolves to anything, the label decides the scope and
subject_id is left out. The session still records its own subject; that is what
the subject is for. Only the quiz stops being constrained by it.

The question_ids route was already unaffected, which is why "tlb" returned 15
questions across three subjects while the label routes returned none.

One edit in core/api.py. Requires patch_session_note.py.

CRLF-safe and idempotent. Run from the repo root:  python patch_session_subject.py
"""
import io
import os
import sys

OLD = '''            built, err = quiz.build_quiz(
                conn,
                subject_id=int(subject_id),
                topic_ids=[] if note_args else topic_ids,'''

NEW = '''            built, err = quiz.build_quiz(
                conn,
                # Left out when the note decided the scope. A subtopic exists
                # inside exactly one subject, so filtering by both can only
                # ever subtract - and it did: a note of "banker algo" on a
                # session logged against another subject built nothing and
                # blamed the cooldown.
                subject_id=None if note_args else int(subject_id),
                topic_ids=[] if note_args else topic_ids,'''


def main():
    path = "core/api.py"
    if not os.path.isfile(path):
        sys.exit("missing %s - run this from the repo root" % path)
    s = io.open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in s
    o = OLD.replace("\n", "\r\n") if crlf else OLD
    n = NEW.replace("\n", "\r\n") if crlf else NEW

    if n in s:
        print("  skip    already applied")
        return 0
    if s.count(o) != 1:
        sys.exit("  ERROR   anchor found %d times, expected 1.\n"
                 "          Run patch_session_note.py first." % s.count(o))
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
    print("  patched core/api.py ok")
    print("\n  Restart the app, then: python tools\\session_note_check.py")
    print("  The subtopic notes should build questions instead of nothing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())