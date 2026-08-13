#!/usr/bin/env python3
"""Remove foreign-extraction questions from a bank.

WHY THIS EXISTS

  content/review/ held two unsorted pools, one per extraction run:

    mineru-unsorted.json   ids like mineru-filter1-volume2-5-4-2
    go-unsorted.json       ids like filter1-volume2-5-4-2

  Both were produced from the same three GO volumes, so the same printed question
  appears in both with a different id prefix. Merging both into one bank puts two
  copies of that question in the same paper - question_bank() cannot dedupe them
  because the ids genuinely differ.

  A bank should hold exactly one extraction's ids. This drops every question whose
  id does not carry the bank's own prefix, and reports which papers it repaired.

USAGE

  python tools/prune_foreign_ids.py --bank mineru --dry-run
  python tools/prune_foreign_ids.py --bank mineru --apply
"""

import argparse
import json
import os
import shutil
import sys
from collections import Counter
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

BANKS = os.path.join(ROOT, "content", "banks")


def main():
    ap = argparse.ArgumentParser(description="Drop foreign-extraction ids from a bank.")
    ap.add_argument("--bank", default="mineru")
    ap.add_argument(
        "--prefix",
        help="required id prefix; defaults to '<bank>-'",
    )
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--restore-to",
        help="write the removed questions here so nothing is destroyed",
    )
    args = ap.parse_args()

    prefix = args.prefix or ("%s-" % args.bank)
    bank_dir = os.path.join(BANKS, args.bank)
    if not os.path.isdir(bank_dir):
        raise SystemExit("No such bank: %s" % bank_dir)

    files = sorted(f for f in os.listdir(bank_dir) if f.endswith(".json"))
    removed_all = []
    per_file = Counter()
    kept = 0

    for name in files:
        path = os.path.join(bank_dir, name)
        data = json.load(open(path, encoding="utf-8"))
        pool = data.get("questions") if isinstance(data, dict) else data
        keep, drop = [], []
        for q in pool or []:
            (keep if str(q.get("id", "")).startswith(prefix) else drop).append(q)
        kept += len(keep)
        if drop:
            per_file[name] = len(drop)
            removed_all.extend(drop)
            if args.apply:
                shutil.copy2(
                    path, path + ".%s.bak" % datetime.now().strftime("%Y%m%d-%H%M%S")
                )
                if isinstance(data, dict):
                    data["questions"] = keep
                else:
                    data = keep
                tmp = path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=1)
                os.replace(tmp, path)

    print("\nbank content/banks/%s  (required id prefix: %r)\n" % (args.bank, prefix))
    if not per_file:
        print("  nothing to prune: every id already carries the prefix.\n")
        return 0
    for name, n in per_file.most_common():
        print("  %-38s -%d" % (name, n))
    print("\n  keeping  %d" % kept)
    print("  dropping %d" % len(removed_all))

    if args.restore_to and args.apply:
        with open(args.restore_to, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "note": "Questions pruned from the %s bank because their ids "
                    "belong to a different extraction run." % args.bank,
                    "questions": removed_all,
                },
                fh,
                ensure_ascii=False,
                indent=1,
            )
        print("  removed questions saved to %s" % args.restore_to)

    if not args.apply:
        print("\n  dry run: nothing written. Add --apply to prune.\n")
    else:
        print("\n  .bak written next to every file touched")
        print('  next: "Reload from disk" in the Bank tab, then bank_defects.py\n')
    return 0


if __name__ == "__main__":
    sys.exit(main())