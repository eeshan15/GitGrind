#!/usr/bin/env python3
"""Prove a session note narrows the quiz, by going through the real endpoint.

Twice in this work a check exercised a helper instead of the path that calls it,
and twice a bug went through: subtopic_verify called select with keyword
arguments only and missed a parameter-order fault, and the mock floor test
called _keep_topics_practisable directly and missed that the patch had put the
call after a return. So this one posts to the /api/sessions handler and reads
what comes back, rather than calling topicmatch and assuming the rest.

It runs against a throwaway copy of the database, made before core is even
imported so that db.DB_PATH picks the copy up. The first version of this tried
to wrap the write in BEGIN/ROLLBACK, which does not work: _create_session
commits through its own "with conn:" block, so the transaction was already
closed and the session would have been written for real. Copying the file is
the only honest way to say nothing is touched.

    python tools/session_note_check.py                 a few built-in notes
    python tools/session_note_check.py "banker algo"   your own

For each note it reports what topicmatch made of it, what the endpoint narrowed
the set to, and whether every question that came back actually carries that
label - which is the part that a resolver test on its own cannot tell you.
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())

# Before importing core: db.DB_PATH is read at import time, so the environment
# has to point at the copy first or the real database gets written.
_REAL = os.environ.get("GITGRIND_DB") or os.path.join("data", "gitgrind.db")
if not os.path.isfile(_REAL):
    sys.exit("database not found at %s - run this from the repo root" % _REAL)
_TMP = os.path.join(tempfile.mkdtemp(prefix="gg-notecheck-"), "copy.db")
shutil.copy(_REAL, _TMP)
for _side in ("-wal", "-shm"):
    if os.path.isfile(_REAL + _side):
        shutil.copy(_REAL + _side, _TMP + _side)
os.environ["GITGRIND_DB"] = _TMP

try:
    from core import api, content, db, topicmatch as tm
except ImportError as exc:
    sys.exit("cannot import core - run this from the repo root (%s)" % exc)

NOTES = [
    "banker algo",
    "page replacement",
    "tlb",
    "deadlock",
    "read the chapter and took notes",
]


class Probe(api.Handler):
    """The handler's session writer, without the HTTP server around it."""

    def __init__(self):
        pass


def subject_id(conn):
    row = conn.execute("SELECT id FROM subjects ORDER BY id LIMIT 1").fetchone()
    if not row:
        sys.exit("no subjects in the database")
    return row["id"]


def main():
    notes = sys.argv[1:] or NOTES
    bank = content.question_bank()
    conn = db.connect()
    try:
        sid = subject_id(conn)
        today = db.today() if hasattr(db, "today") else None
        if not today:
            from datetime import date
            today = date.today().isoformat()

        probe = Probe()
        writer = getattr(probe, "_create_session", None)
        if writer is None:
            names = [n for n in dir(probe) if "session" in n.lower()]
            sys.exit("cannot find the session writer on Handler. Candidates: %s"
                     % ", ".join(names))

        print("\n  database copied to %s" % _TMP)
        print("  posting through %s; the real file is untouched\n"
              % writer.__name__)
        for note in notes:
            planned = tm.plan(note)
            label = planned["label"]
            lab = "%s (%s, %d q)" % (label["slug"], label["kind"], label["count"]) \
                if label else "-"
            print("  note %r" % note)
            print("    topicmatch     label %s, mentions %d, advice %s"
                  % (lab, planned["mention_count"], planned["advice"]))

            try:
                out = writer(conn, dict(
                    subject_id=sid, day=today, minutes=5, kind="concept",
                    note=note, topic_ids=[], with_quiz=True, quiz_count=5,
                ))
                built = out.get("quiz")
                qs = (built or {}).get("questions") or []
                print("    endpoint       quiz_from %r, %d question(s)"
                      % (out.get("quiz_from", ""), len(qs)))
                if not qs:
                    print("    ->             nothing built%s"
                          % ("  (%s)" % out["quiz_error"] if out.get("quiz_error")
                             else ""))
                else:
                    want = out.get("quiz_from") or ""
                    subs = sorted({q.get("subtopic") or "-" for q in qs})
                    tops = sorted({q.get("topic") or "-" for q in qs})
                    print("    ->             subtopics %s" % subs)
                    print("                   topics    %s" % tops)
                    # Assert on the field the route actually filtered by.
                    # 32 slugs are both a topic and a subtopic, so testing
                    # subtopic just because the name appears there reports a
                    # topic-scoped set as broken when it is not.
                    if label and want == label["slug"]:
                        field = ("subtopic" if label["kind"] == "subtopic"
                                 else "topic")
                        ok = all((q.get(field) or "") == want for q in qs)
                        print("    check          every question's %s is %r: %s"
                              % (field, want, "yes" if ok else "NO"))
                    elif want.startswith("questions mentioning"):
                        # Options too, because mentions() searches them: a
                        # question can name the thing only in an answer choice,
                        # and counting the stem alone under-reports.
                        needle = note.lower()
                        hits = 0
                        for q in qs:
                            blob = (q.get("text") or "") + " " + " ".join(
                                str(o) for o in (q.get("options") or []))
                            if needle in blob.lower():
                                hits += 1
                        print("    check          %d of %d mention the words"
                              % (hits, len(qs)))
            except Exception as exc:
                print("    endpoint       raised %s: %s" % (type(exc).__name__, exc))
            print()

        left = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        print("  sessions written to the copy: %d" % left)
        print("  bank: %d questions" % len(bank))
        print("  the copy can be deleted: %s" % os.path.dirname(_TMP))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())