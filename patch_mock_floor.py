#!/usr/bin/env python3
"""Repair patch_mock_floor.py, which inserted unreachable code.

reserved_for_mocks returns its set comprehension directly:

    try:
        return {
            r["question_id"]
            for r in conn.execute(...)
        }

patch_mock_floor.py appended its call after that closing brace, which put it
after a return. The line never executes, `held` is never bound, and the
function behaves exactly as it did before - which is why
tools/mock_reserve_check.py reported the same three empty topics after the
patch as before it.

The sandbox test missed it because it called _keep_topics_practisable directly
instead of going through reserved_for_mocks. That is the second time a test
here has exercised a helper rather than the path that uses it; the first let a
parameter-order bug through because it only ever called select with keyword
arguments. Both were checks written against the change rather than against the
caller.

This binds the comprehension to a name and returns the filtered value, so there
is one return and it goes through the filter. It also verifies the effect by
calling reserved_for_mocks itself rather than the helper.

CRLF-safe and idempotent. Run from the repo root:  python patch_mock_floor_fix.py
"""
import io
import os
import sys

OLD = '''    try:
        return {
            r["question_id"]
            for r in conn.execute(
                "SELECT pq.question_id FROM paper_questions pq"
                " JOIN papers p ON p.id = pq.paper_id"
                " WHERE p.exam = 'GitGrind Mock'"
            )
        }
        return _keep_topics_practisable(held)'''

NEW = '''    try:
        held = {
            r["question_id"]
            for r in conn.execute(
                "SELECT pq.question_id FROM paper_questions pq"
                " JOIN papers p ON p.id = pq.paper_id"
                " WHERE p.exam = 'GitGrind Mock'"
            )
        }
        # Bound rather than returned directly, so the floor actually runs. The
        # first version of this appended the call after the return and was
        # unreachable.
        return _keep_topics_practisable(held)'''


def main():
    path = "core/quiz.py"
    if not os.path.isfile(path):
        sys.exit("missing %s - run this from the repo root" % path)
    s = io.open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in s
    o = OLD.replace("\n", "\r\n") if crlf else OLD
    n = NEW.replace("\n", "\r\n") if crlf else NEW

    if n in s:
        print("  skip    already applied")
    elif s.count(o) != 1:
        sys.exit("  ERROR   anchor found %d times, expected 1.\n"
                 "          Run patch_mock_reserve.py and patch_mock_floor.py first."
                 % s.count(o))
    else:
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched core/quiz.py ok")

    # Verify through the function the app calls, not through the helper.
    sys.path.insert(0, os.getcwd())
    try:
        from core import content, db, quiz
    except ImportError as exc:
        print("\n  could not import to verify (%s)" % exc)
        return 0
    conn = db.connect()
    try:
        bank = content.question_bank()
        held = quiz.reserved_for_mocks(conn)
        free = {}
        total = {}
        for qid, q in bank.items():
            key = (q.get("subject", ""), q.get("topic", ""))
            total[key] = total.get(key, 0) + 1
            if qid not in held:
                free[key] = free.get(key, 0) + 1
        empty = [k for k in total if free.get(k, 0) == 0]
        print("\n  reserved_for_mocks returns %d id(s)" % len(held))
        print("  topics with nothing left outside mocks: %d" % len(empty))
        for key in empty:
            print("    %s/%s" % key)
        if empty:
            print("\n  Still emptying topics. MOCK_TOPIC_FLOOR may be 0, or the")
            print("  helper is not being reached.")
            return 1
        print("  Every topic keeps at least one question outside the mocks.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())