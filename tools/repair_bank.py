#!/usr/bin/env python3
"""Repair questions that bled into each other during extraction.

The GO volumes number every question `<chapter>.<section>.<n>`. The extractor did
not treat that marker as a hard boundary, so a question's text and its last option
often swallowed the beginning of the next question. That is the overlap visible in
practice: option D containing an entire second question.

    python tools/repair_bank.py --dry-run
    python tools/repair_bank.py
"""

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

MARKER = re.compile(r"\s*\b\d{1,2}\.\d{1,2}\.\d{1,3}\b.*$", re.S)
MERGED = re.compile(r"\b[A-D]\b[^A-D]{15,}\b[A-D]\b[^A-D]{15,}\b[A-D]\b")

NOTE_OPTS = (
    "The source's option list did not survive text extraction. Open the "
    "original PDF at the reference below, paste the options in and log the "
    "answer from the Bank tab."
)


def cut(text):
    if not text:
        return text, False
    trimmed = MARKER.sub("", str(text)).strip()
    return trimmed, trimmed != str(text).strip()


def repair(q):
    what = []
    new_text, hit = cut(q.get("text", ""))
    if hit:
        q["text"] = new_text
        what.append("text")

    opts = q.get("options") or []
    if opts:
        clean, dropped = [], 0
        for o in opts:
            o = str(o)
            if MERGED.search(o) or len(o) > 260:
                dropped += 1
                continue
            trimmed, hit = cut(o)
            if hit:
                what.append("option")
            if trimmed:
                clean.append(trimmed)
            else:
                dropped += 1
        if dropped:
            what.append("dropped %d merged option(s)" % dropped)
        q["options"] = clean

        if len(clean) < 2:
            q["answer_pending"] = True
            q["answer"] = None
            q["needs_options"] = True
            q["answer_note"] = NOTE_OPTS
            what.append("demoted to answer_pending")
        elif q.get("answer") and isinstance(q["answer"], list):
            if any(i >= len(clean) for i in q["answer"]):
                q["answer_pending"] = True
                q["answer"] = None
                q["answer_note"] = NOTE_OPTS
                what.append("answer index no longer valid")

    if len(str(q.get("text", "")).strip()) < 25:
        q["answer_pending"] = True
        q["answer"] = None
        q["needs_options"] = True
        q["answer_note"] = NOTE_OPTS
        what.append("stem too short after trimming")

    return bool(what), what


def main():
    ap = argparse.ArgumentParser(description="Repair bled-together bank questions.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--glob", default="content/banks/go-extracted/*.json")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(ROOT, args.glob)))
    if not files:
        print("No bank files matched %s" % args.glob)
        return 1

    from core import content as registry
    import ingest

    totals = dict(seen=0, fixed=0, demoted=0, dropped_opts=0)
    for path in files:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        rows = data.get("questions", [])
        touched = 0
        for q in rows:
            totals["seen"] += 1
            changed, what = repair(q)
            if changed:
                touched += 1
                totals["fixed"] += 1
                if any(
                    "demoted" in w or "no longer valid" in w or "too short" in w
                    for w in what
                ):
                    totals["demoted"] += 1
                for w in what:
                    if w.startswith("dropped"):
                        totals["dropped_opts"] += int(w.split()[1])
        print(
            "  %-46s %4d of %4d repaired"
            % (os.path.relpath(path, ROOT), touched, len(rows))
        )
        if touched and not args.dry_run:
            ingest.backup_file(path)
            ingest.write_json_atomic(path, data)

    print("\n  %-32s %d" % ("questions examined", totals["seen"]))
    print("  %-32s %d" % ("questions repaired", totals["fixed"]))
    print("  %-32s %d" % ("merged options discarded", totals["dropped_opts"]))
    print("  %-32s %d" % ("demoted to answer_pending", totals["demoted"]))

    if args.dry_run:
        print("\n  dry run: nothing written.")
        return 0

    stats = registry.bank_stats(reload=True)
    print(
        "\n  bank now: %d questions, %d gradable, %d pending, %d broken, %d%% coverage"
        % (
            stats["total"],
            stats["usable"],
            stats["pending"],
            stats["broken"],
            stats["coverage_pct"],
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
