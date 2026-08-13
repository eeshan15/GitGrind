#!/usr/bin/env python3
"""Audit the bank for repairable defects, ordered by what it costs you.

WHY THIS EXISTS

  There are more broken questions than you will ever fix by hand, so the only
  question that matters is which ones to fix first. Two signals decide that:

    * whether the question sits in a paper you intend to sit, and
    * whether the defect is machine-repairable or needs your eyes.

  bank_stats() already reports how many questions are broken. It cannot tell you
  which paper they ruin, because until v9 the bank had no idea papers existed.
  This does, and it sorts the work accordingly.

DEFECT FAMILIES

  degenerate   options survived extraction as connective words: ['and', 'and',
               'and', 'and'], ['/s', '/s', '/s', '/s']. The formula bodies were
               images in the source PDF and the text layer never had them. These
               are NOT empty, so tools/recover_options.py skips them - it looks
               for blanks. They are the largest repairable group.
  blank        options are empty strings. recover_options.py already targets these.
  thin         fewer than four options where four were printed, usually because
               two options merged into one during extraction.
  suspect_ocr  an option that a previous recovery pass wrote as LaTeX which
               renders to one or two glyphs, e.g. $1{\\boldsymbol{2}}$. A formula
               OCR model produced it and was probably wrong.
  pending      answer_pending: the source never printed an answer. Not an
               extraction defect; it needs a lookup, not a repair.

USAGE

  python tools/bank_defects.py                    summary, worst papers first
  python tools/bank_defects.py --paper gate-cse-2010
  python tools/bank_defects.py --family degenerate --limit 30
  python tools/bank_defects.py --csv defects.csv  a worklist you can tick off
"""

import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core import content, db  # noqa: E402

# Words and units that are all that survives when a formula is dropped from the
# text layer. An option made only of these carries no information.
FILLER = re.compile(
    r"^(?:[\s,.:;()/\-]|and|or|only|both|neither|nor|is|are|the|of|in|to|then"
    r"|ns|s|ms|us|kb|mb|gb|bit|bits|byte|bytes|%)*$",
    re.I,
)
# LaTeX that renders to almost nothing once the styling macros are stripped.
STYLE = re.compile(r"\\(?:boldsymbol|mathbf|mathrm|textbf|textit|text|bf|it|rm)|[\\{}$]")


def _bare(text):
    return STYLE.sub("", str(text)).strip()


def classify(q):
    """Return the set of defect families this question belongs to."""
    out = set()
    if q.get("answer_pending"):
        out.add("pending")
    if q.get("type") not in ("mcq", "msq"):
        return out

    opts = [str(o) for o in (q.get("options") or [])]
    if not opts:
        out.add("blank")
        return out
    if any(not o.strip() for o in opts):
        out.add("blank")
    if len(opts) < 4:
        out.add("thin")

    informative = [o for o in opts if not FILLER.match(o.strip())]
    # Duplicates and filler-only bodies are the same disease: the distinguishing
    # part of the option never made it out of the PDF.
    if len(informative) < 2 or len(set(opts)) < max(2, len(opts) - 1):
        out.add("degenerate")

    for o in opts:
        bare = _bare(o)
        if o.strip() and len(bare) <= 2 and not bare.isdigit() and "\\" in o:
            out.add("suspect_ocr")
            break
    return out


FAMILIES = ("degenerate", "blank", "thin", "suspect_ocr", "pending")
# Machine-repairable families, in the order the tooling can attack them.
REPAIRABLE = ("blank", "degenerate", "thin")


def main():
    ap = argparse.ArgumentParser(description="Audit repairable bank defects.")
    ap.add_argument("--paper", help="only this paper slug")
    ap.add_argument("--family", choices=FAMILIES, help="only this defect family")
    ap.add_argument("--limit", type=int, default=20, help="rows to list")
    ap.add_argument("--csv", help="write the full worklist to this file")
    args = ap.parse_args()

    conn = db.init()
    content.seed(conn)
    bank = content.question_bank(reload=True)
    papers = content.papers()

    rows = []
    counts = Counter()
    per_paper = defaultdict(Counter)
    for q in bank.values():
        fams = classify(q)
        if not fams:
            continue
        counts.update(fams)
        paper = q.get("paper") or ""
        if paper:
            per_paper[paper].update(fams)
        rows.append(
            dict(
                id=q["id"],
                paper=paper,
                position=q.get("position_in_paper") or 0,
                section=q.get("paper_section", ""),
                subject=q["subject"],
                families=",".join(sorted(fams)),
                file=q.get("file", ""),
                ref=(q.get("origin") or {}).get("ref", ""),
                page=(q.get("origin") or {}).get("page_idx", ""),
                options=" | ".join(str(o) for o in (q.get("options") or []))[:160],
            )
        )

    print("\nbank: %d questions, %d with a defect\n" % (len(bank), len(rows)))
    print("  family        count   what fixes it")
    print("  " + "-" * 62)
    fixes = {
        "degenerate": "recover_options.py, after widening its selector",
        "blank": "recover_options.py --crops / --ocr / --apply",
        "thin": "repair_bank.py, then a manual look",
        "suspect_ocr": "re-OCR from the crop, or fix by hand",
        "pending": "answer_fill.py, or the Bank tab",
    }
    for f in FAMILIES:
        if counts[f]:
            print("  %-13s %5d   %s" % (f, counts[f], fixes[f]))

    # Which papers are worst off: a defect inside a paper you will sit costs more
    # than one in a question you would never have been served.
    print("\n  papers ranked by repairable defects\n")
    print("  %-24s %5s %5s %5s %6s  %s" % ("paper", "have", "need", "bad", "usable", "%"))
    print("  " + "-" * 68)
    ranked = []
    for slug, p in papers.items():
        bad = sum(per_paper[slug][f] for f in REPAIRABLE)
        have = p["question_count"]
        printed = p.get("printed_questions") or 0
        usable = have - bad
        ranked.append((slug, have, printed, bad, usable))
    ranked.sort(key=lambda r: (-r[3], r[0]))
    for slug, have, printed, bad, usable in ranked[: args.limit]:
        pct = round(usable / have * 100) if have else 0
        print(
            "  %-24s %5d %5s %5d %6d  %d%%"
            % (slug, have, printed or "?", bad, usable, pct)
        )

    if args.paper or args.family:
        sel = [
            r
            for r in rows
            if (not args.paper or r["paper"] == args.paper)
            and (not args.family or args.family in r["families"].split(","))
        ]
        sel.sort(key=lambda r: (r["paper"], r["position"]))
        print("\n  %d matching question(s)\n" % len(sel))
        for r in sel[: args.limit]:
            print(
                "  %-34s Q%-3s %-22s %s"
                % (r["id"], r["position"] or "-", r["families"], r["ref"])
            )
            print("      %s" % r["options"])

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(sorted(rows, key=lambda r: (r["paper"], r["position"])))
        print("\n  wrote %s (%d rows)" % (args.csv, len(rows)))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())