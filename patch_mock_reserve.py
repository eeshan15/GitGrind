#!/usr/bin/env python3
"""Stop discarding the mock reservation that select() just computed.

quiz.select opens like this:

    # Questions held by a mock paper stay out of practice, so sitting a mock is
    # not a re-run of what you already saw. This is a query, not a partition:
    # delete a mock and its questions come straight back into the pool.
    exclude = set(exclude or []) | reserved_for_mocks(conn)
    bank = content.question_bank()
    if not bank:
        return []

    exclude = set(exclude or [])

The last line throws away the first. The comment states the intention plainly
and five lines later the code drops it, so no mock question is reserved and
every one of them is available to ordinary practice. With twenty mock papers of
sixty-five questions each that is around 1,300 questions - roughly a third of
the bank - and the consequence is the exact thing the comment says it prevents:
sitting a mock re-runs questions already seen in practice.

This is not the cause of the repeat complaint. That was measured separately -
select() returned 4 repeats in 150 picks, none inside the cooldown window - and
this bug points the other way anyway: it leaks mock questions into practice
rather than practice questions into practice. It is worth fixing because a
statement of intent that the next line deletes will otherwise be read as
working behaviour by whoever looks next.

One edit: delete the second assignment. The first already does the work, and
the call to reserved_for_mocks is a query, so nothing is cached or partitioned
and deleting a mock still returns its questions to the pool.

CRLF-safe and idempotent. Run from the repo root:  python patch_mock_reserve.py
"""
import io
import os
import sys

EDITS = [
    ('core/quiz.py',
     '    bank = content.question_bank()\n'
     '    if not bank:\n'
     '        return []\n'
     '\n'
     '    exclude = set(exclude or [])\n'
     '    settings = db.get_settings(conn)',

     '    bank = content.question_bank()\n'
     '    if not bank:\n'
     '        return []\n'
     '\n'
     '    settings = db.get_settings(conn)'),
]


def report(conn_path="core/quiz.py"):
    s = io.open(conn_path, encoding="utf-8", newline="").read()
    return s.count("exclude = set(exclude or [])")


def main():
    path = "core/quiz.py"
    if not os.path.isfile(path):
        sys.exit("missing %s - run this from the repo root" % path)

    print("  assignments to exclude before: %d" % report(path))

    changed = skipped = 0
    for target, old, new in EDITS:
        s = io.open(target, encoding="utf-8", newline="").read()
        crlf = "\r\n" in s
        o = old.replace("\n", "\r\n") if crlf else old
        n = new.replace("\n", "\r\n") if crlf else new
        if n in s and o not in s:
            print("  skip    %-14s already applied" % target)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d times, expected 1"
                     % (target, s.count(o)))
        io.open(target, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-14s ok" % target)
        changed += 1

    after = report(path)
    print("  assignments to exclude after:  %d" % after)
    if after != 1:
        sys.exit("  ERROR   expected exactly one assignment to remain")

    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    if changed:
        print("  Restart the app. Mock-reserved questions will now stay out of")
        print("  practice sets; check with tools/mock_reserve_check.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())