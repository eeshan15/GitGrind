#!/usr/bin/env python3
"""Report whether the attempt log can actually carry the planned models.

WHY THIS EXISTS

  Before fitting anything, the honest question is what the data supports. A model
  fitted on a column that is 6% populated will produce a number, and the number
  will look as confident as a real one. This checks each ingredient separately and
  says which models are viable today, which need more logging, and which need only
  more time.

WHAT IT CHECKS

  completeness   how much of each attempt feature is actually recorded, not just
                 present as a column
  labels         how many usable (item, correct) pairs exist, and over how many
                 distinct items - Rasch needs items seen more than once to
                 separate difficulty from luck
  repeats        how many items were attempted twice or more, which is what makes
                 forgetting estimable at all
  calibration    how many timed paper sittings exist, which is the only ground
                 truth the score projection can ever have
  leakage        whether attempts reference questions that no longer exist, which
                 silently drops them out of every per-topic figure

THRESHOLDS

  These are minimums for a fit that is not mostly prior, not targets. They are
  deliberately low, and passing one does not mean the estimate will be good - it
  means it will not be meaningless.

USAGE

  python tools/feature_audit.py
  python tools/feature_audit.py --verbose
"""

import argparse
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core import content, db  # noqa: E402

# Features the planned models would read, and which model needs each.
FEATURES = [
    ("correct", "label for every model", True),
    ("question_id", "item identity - Rasch, logistic", True),
    ("topic_slug", "per-topic ability", True),
    ("created_at", "spacing between attempts - HLR", True),
    ("seconds", "time pressure feature - logistic", False),
    ("confidence", "self-report feature - logistic, mistake analysis", False),
    ("mistake_kind", "error taxonomy - recommendations", False),
    ("reattempt", "distinguishes review from first sight - HLR", False),
    ("marks_total", "item weight", False),
    ("paper_id", "which paper a sitting belonged to - calibration", False),
]

NEEDS = [
    ("Rasch / 1PL item difficulty", "attempts", 300, "items seen 2+ times", 60),
    ("Logistic next-attempt model", "attempts", 500, "distinct items", 200),
    ("Half-life regression (forgetting)", "repeat attempts", 200, "items seen 2+ times", 80),
    ("Score projection calibration", "timed paper sittings", 8, None, 0),
]


def pct(n, d):
    return 0.0 if not d else round(100.0 * n / d, 1)


def bar(p, width=22):
    filled = int(round(width * p / 100.0))
    return "#" * filled + "." * (width - filled)


def main():
    ap = argparse.ArgumentParser(description="Audit attempt-log readiness for modelling.")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    conn = db.init()
    content.seed(conn)
    bank = content.question_bank(reload=True)

    total = conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
    print("\nattempts logged: %d\n" % total)
    if not total:
        print("  Nothing to audit yet. Practise, then run this again.\n")
        return 0

    cols = {r[1] for r in conn.execute("PRAGMA table_info(attempts)")}

    print("  feature completeness")
    print("  " + "-" * 74)
    gaps = []
    for name, why, required in FEATURES:
        if name not in cols:
            print("  %-14s MISSING COLUMN   %s" % (name, why))
            gaps.append((name, why, required))
            continue
        # An empty string is as absent as a NULL for modelling purposes, and the
        # schema uses both, so count them together.
        filled = conn.execute(
            "SELECT COUNT(*) FROM attempts WHERE %s IS NOT NULL AND TRIM(CAST(%s AS TEXT)) != ''"
            % (name, name)
        ).fetchone()[0]
        p = pct(filled, total)
        flag = "  " if p >= 90 else ("!!" if required else " ?")
        print("  %-14s %s %5.1f%% %s  %s" % (name, bar(p), p, flag, why))
        if p < 90:
            gaps.append((name, why, required))

    # Label structure. Rasch cannot separate a hard item from an unlucky one
    # unless the item has been seen more than once, so that count matters more
    # than the raw attempt total.
    rows = list(
        conn.execute(
            "SELECT question_id, COUNT(*) c FROM attempts WHERE question_id IS NOT NULL"
            " GROUP BY question_id"
        )
    )
    items = len(rows)
    repeats = sum(1 for r in rows if r[1] >= 2)
    repeat_rows = sum(r[1] for r in rows if r[1] >= 2)
    orphan_rows = 0
    for qid, c in rows:
        if qid not in bank:
            orphan_rows += c

    graded = conn.execute(
        "SELECT COUNT(*) FROM attempts WHERE correct IS NOT NULL"
    ).fetchone()[0]
    topics = conn.execute(
        "SELECT COUNT(DISTINCT topic_slug) FROM attempts WHERE topic_slug != ''"
    ).fetchone()[0]

    print("\n  label structure")
    print("  " + "-" * 74)
    print("  graded attempts          %d" % graded)
    print("  distinct items           %d" % items)
    print("  items seen 2+ times      %d  (%d rows)" % (repeats, repeat_rows))
    print("  topics touched           %d of 101" % topics)
    if orphan_rows:
        print(
            "  ORPHANED rows            %d  <- item no longer in the bank;"
            " excluded from every per-topic figure" % orphan_rows
        )
        print("                           fix: python tools/remap_question_ids.py")

    # A column can be 100% populated and still carry no information. seconds is
    # the case here: the UI submits one duration for the whole set, so the value
    # is divided evenly rather than measured per question. A constant feature
    # cannot help a model, so it is reported as absent rather than complete.
    degenerate = []
    for name in ("seconds", "confidence"):
        if name not in cols:
            continue
        rows = list(
            conn.execute(
                "SELECT COUNT(DISTINCT %s) d, COUNT(*) n FROM attempts"
                " WHERE quiz_id IS NOT NULL GROUP BY quiz_id" % name
            )
        )
        flat = sum(1 for d, n in rows if n > 1 and d <= 1)
        if rows and flat == len([r for r in rows if r[1] > 1]) and flat:
            degenerate.append(name)
    if degenerate:
        print("\n  constant within every set (no information):  %s" % ", ".join(degenerate))
        print("     the UI submits one duration per set, not per question, so this")
        print("     column is filled but flat - fix the payload before trusting it")

    sittings = 0
    if "paper_id" in cols:
        sittings = conn.execute(
            "SELECT COUNT(DISTINCT quiz_id) FROM attempts WHERE paper_id IS NOT NULL"
        ).fetchone()[0]
    logged = conn.execute("SELECT COUNT(*) FROM readiness_log").fetchone()[0]
    print("\n  calibration")
    print("  " + "-" * 74)
    print("  paper sittings recorded  %d" % sittings)
    print("  readiness snapshots      %d" % logged)
    if not sittings:
        print(
            "  No paper has been sat yet. Until one is, est_score rests entirely on\n"
            "  the hand-set anchors in the score model - it is an assumption, not a\n"
            "  measurement, however precise the number looks."
        )

    have = dict(
        attempts=total,
        **{"repeat attempts": repeat_rows, "timed paper sittings": sittings}
    )
    second = {"items seen 2+ times": repeats, "distinct items": items}

    print("\n  model viability")
    print("  " + "-" * 74)
    for label, key, need, key2, need2 in NEEDS:
        got = have.get(key, 0)
        ok = got >= need
        extra = ""
        if key2:
            got2 = second.get(key2, 0)
            ok = ok and got2 >= need2
            extra = ", %s %d/%d" % (key2, got2, need2)
        print(
            "  %-36s %-6s %s %d/%d%s"
            % (label, "ready" if ok else "wait", "" if ok else "-", got, need, extra)
        )

    print("\n  what to do next")
    print("  " + "-" * 74)
    required_gaps = [g for g in gaps if g[2]]
    optional_gaps = [g for g in gaps if not g[2]]
    if degenerate:
        print(
            "  0. %s is logged but constant within a set. The submit payload in\n"
            "     static/js/practice.js sends only question_id and response, so\n"
            "     per-question timing and confidence never reach the server. That\n"
            "     is a UI fix, and until it lands the logistic model has two fewer\n"
            "     real features than the column list suggests." % ", ".join(degenerate)
        )
    if required_gaps:
        print("  1. Fix logging for: %s" % ", ".join(g[0] for g in required_gaps))
        print("     These are load-bearing; a model without them is not worth fitting.")
    elif optional_gaps:
        print(
            "  1. Optional features thin: %s"
            % ", ".join(g[0] for g in optional_gaps)
        )
        print("     Rasch works without them. The logistic model will be weaker.")
    else:
        print("  1. Logging is complete. Nothing to fix.")

    if total < 300:
        print(
            "  2. Keep practising: %d more graded attempts before Rasch is worth\n"
            "     running, and repeats matter more than volume - the selector's\n"
            "     cooldown already brings items back, so this happens on its own."
            % max(0, 300 - total)
        )
    else:
        print("  2. Enough volume for a first Rasch fit.")

    print(
        "  3. Sit real papers, timed. Eight sittings turn est_score from a\n"
        "     hand-drawn line into a fitted one, and nothing else can."
    )

    if args.verbose:
        print("\n  attempts by day")
        for day, c in conn.execute(
            "SELECT day, COUNT(*) FROM attempts GROUP BY day ORDER BY day"
        ):
            print("    %-12s %d" % (day, c))
        print("\n  mistake_kind spread")
        for k, c in Counter(
            r[0] or "(blank)"
            for r in conn.execute("SELECT mistake_kind FROM attempts")
        ).most_common():
            print("    %-16s %d" % (k, c))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())