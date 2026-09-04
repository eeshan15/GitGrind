#!/usr/bin/env python3
"""Measure what the restored mock reservation takes out of the practice pool.

patch_mock_reserve.py makes select() honour a reservation it had been
computing and discarding. That is a correctness fix, but it is also a large
behaviour change - with twenty mock papers the reservation is around a third of
the bank - and a fix that quietly shrinks the pool needs its effect stated as a
number rather than assumed to be fine.

The number that matters is not the total. It is the per-topic remainder: a
topic whose questions are nearly all inside mock papers has little left for
practice, and a topic with none left cannot be practised at all. Better to see
that here than to find out when a set comes back empty.

Reports:

  reservation   how many questions mock papers hold, as a share of the bank
  per topic     what each topic has left, worst first
  empty         topics with nothing left outside the mocks
  live check    whether select() actually avoids reserved questions now

Read-only. Run from the repo root:  python tools/mock_reserve_check.py
"""
import collections
import os
import sys

sys.path.insert(0, os.getcwd())

try:
    from core import content, db, quiz
except ImportError as exc:
    sys.exit("cannot import core - run this from the repo root (%s)" % exc)


def main():
    conn = db.connect()
    try:
        bank = content.question_bank()
        if not bank:
            sys.exit("question bank is empty")
        reserved = quiz.reserved_for_mocks(conn)

        print("\n=== reservation ===")
        print("  bank                    %d" % len(bank))
        print("  held by mock papers     %d  (%.1f%%)"
              % (len(reserved), len(reserved) * 100.0 / len(bank)))
        print("  left for practice       %d" % (len(bank) - len(reserved)))
        if not reserved:
            print("\n  Nothing is reserved, so this fix changes nothing yet.")
            print("  It will matter as soon as a mock paper is generated.")

        total = collections.Counter()
        free = collections.Counter()
        for qid, q in bank.items():
            key = "%s/%s" % (q["subject"], q.get("topic", ""))
            total[key] += 1
            if qid not in reserved:
                free[key] += 1

        rows = sorted(
            total, key=lambda k: (free[k] / float(total[k]), free[k])
        )
        print("\n=== topics with the least left ===")
        print("  %-44s %6s %6s %6s" % ("topic", "total", "free", "share"))
        for key in rows[:15]:
            print("  %-44s %6d %6d %5.0f%%"
                  % (key, total[key], free[key],
                     free[key] * 100.0 / total[key]))

        empty = [k for k in total if free[k] == 0]
        thin = [k for k in total if 0 < free[k] < 5]
        print("\n=== after the fix ===")
        print("  topics with nothing left outside mocks   %d" % len(empty))
        for key in empty:
            print("    %s  (all %d reserved)" % (key, total[key]))
        print("  topics with fewer than 5 left            %d" % len(thin))
        for key in sorted(thin, key=lambda k: free[k])[:10]:
            print("    %-44s %d left of %d" % (key, free[key], total[key]))
        if not empty and not thin:
            print("  Every topic keeps at least 5 questions outside the mocks.")

        print("\n=== live check ===")
        picked = []
        for purpose in ("weak", "mixed", "fresh"):
            for i in range(10):
                picked += [
                    q["id"] for q, _ in quiz.select(
                        conn, purpose, count=5, seed="mock-check-%s-%d" % (purpose, i)
                    )
                ]
        leaked = [qid for qid in picked if qid in reserved]
        print("  %d pick(s) sampled, %d reserved question(s) served"
              % (len(picked), len(leaked)))
        if leaked:
            print("  Still leaking - the fix is not applied, or something else")
            print("  builds sets without going through select().")
            for qid in leaked[:5]:
                print("    %s" % qid)
            return 1
        print("  None. The reservation is being honoured.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())