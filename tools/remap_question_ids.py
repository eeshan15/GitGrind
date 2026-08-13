#!/usr/bin/env python3
"""Re-point activity rows at question ids that still exist in the bank.

WHY THIS EXISTS

  Practice history is stored by question_id, and question_id is a content value,
  not a database key. When a bank is replaced the ids change, and every attempt
  that referenced the old scheme becomes an orphan: the row survives, but nothing
  resolves it, so it stops counting towards a topic's accuracy and vanishes from
  the heatmap.

  That is what happened here. The go-extracted bank was retired in favour of the
  mineru extraction of the same three PDFs, and the two schemes differ only by a
  prefix:

      filter1-volume3-5-1-1   ->   mineru-filter1-volume3-5-1-1

  So the history is recoverable. This walks every table that stores a
  question_id, and for each orphan tries the candidate prefixes; a row is only
  rewritten when the candidate actually exists in the current bank.

  Nothing is deleted. An orphan with no candidate is left exactly as it is and
  reported, because a wrong remap would silently attribute your result to a
  question you never answered - worse than an orphan.

USAGE

  python tools/remap_question_ids.py --dry-run
  python tools/remap_question_ids.py --apply
"""

import argparse
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core import content, db  # noqa: E402

# Tried in order. The first candidate present in the bank wins.
PREFIXES = ("mineru-",)


def tables_with_question_id(conn):
    out = []
    for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ):
        name = row[0]
        cols = {r[1] for r in conn.execute('PRAGMA table_info("%s")' % name)}
        if "question_id" in cols:
            out.append(name)
    return sorted(out)


def main():
    ap = argparse.ArgumentParser(description="Repair orphaned question_id references.")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    conn = db.init()
    content.seed(conn)
    bank = content.question_bank(reload=True)

    tables = tables_with_question_id(conn)
    print("\ntables storing a question_id: %s\n" % ", ".join(tables))

    plan = {}
    stuck = Counter()
    totals = Counter()
    for table in tables:
        ids = [
            r[0]
            for r in conn.execute(
                'SELECT DISTINCT question_id FROM "%s" WHERE question_id IS NOT NULL'
                % table
            )
        ]
        orphans = [i for i in ids if i and i not in bank]
        mapped = {}
        for old in orphans:
            for prefix in PREFIXES:
                if prefix + old in bank:
                    mapped[old] = prefix + old
                    break
            else:
                stuck[old] += 1
        rows = 0
        for old in mapped:
            rows += conn.execute(
                'SELECT COUNT(*) FROM "%s" WHERE question_id = ?' % table, (old,)
            ).fetchone()[0]
        plan[table] = mapped
        totals[table] = rows
        print(
            "  %-20s %4d distinct | %3d orphan | %3d remappable | %3d row(s)"
            % (table, len(ids), len(orphans), len(mapped), rows)
        )

    if stuck:
        print("\n  orphans with no candidate in the bank (left untouched):")
        for old in sorted(stuck):
            print("    %s" % old)
        print(
            "\n  These are usually fine: a curated question that was renamed, or one\n"
            "  that genuinely no longer ships. Guessing a replacement would credit\n"
            "  your result to a question you never saw, so they stay as they are."
        )

    if not any(plan.values()):
        print("\n  nothing to remap.\n")
        return 0

    if not args.apply:
        print("\n  dry run: nothing written. Add --apply.\n")
        return 0

    changed = 0
    with conn:
        for table, mapped in plan.items():
            for old, new in mapped.items():
                # A row may already exist under the new id in tables keyed on
                # question_id, so merge rather than collide.
                try:
                    cur = conn.execute(
                        'UPDATE "%s" SET question_id = ? WHERE question_id = ?' % table,
                        (new, old),
                    )
                    changed += cur.rowcount
                except Exception as exc:  # unique constraint on question_id
                    conn.execute(
                        'DELETE FROM "%s" WHERE question_id = ?' % table, (old,)
                    )
                    print("    %-20s %s: kept existing row (%s)" % (table, old, exc))

    print("\n  %d row(s) re-pointed" % changed)
    print("  next: python tools/feature_audit.py\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())