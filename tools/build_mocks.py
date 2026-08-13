#!/usr/bin/env python3
"""Build mock papers shaped like a real GATE paper, from clean questions only.

A mock copies a real paper's blueprint: the same section split and the same
per-subject question counts. Difficulty mix is held constant across all mocks, so
a score on mock 3 means the same thing as a score on mock 17.

Mocks are written to content/mocks.json. content.papers() reads that file
alongside the banks, so every existing surface - the papers table, "Sit it",
attempts.paper_id, bank_defects - works on them with no further change.

  python tools/build_mocks.py --dry-run
  python tools/build_mocks.py --count 20 --apply
"""

import argparse
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core import content, db  # noqa: E402

MOCKS_FILE = os.path.join(ROOT, "content", "mocks.json")

FILLER = re.compile(
    r"^(?:[\s,.:;()/\-]|and|or|only|both|neither|nor|is|are|the|of|in|to|then"
    r"|ns|s|ms|us|kb|mb|gb|bit|bits|byte|bytes|%)*$",
    re.I,
)


def is_clean(q):
    """Servable and answerable by a human, not merely valid to the validator."""
    if q.get("answer_pending") or q.get("needs_fix"):
        return False
    if q.get("type") not in ("mcq", "msq"):
        return q.get("type") == "nat" and q.get("answer_value") is not None
    opts = [str(o) for o in (q.get("options") or [])]
    if len(opts) < 4 or any(not o.strip() for o in opts):
        return False
    if len(set(opts)) < len(opts):
        return False
    return len([o for o in opts if not FILLER.match(o.strip())]) >= 2


GA_STRUCTURE = (5, 5)  # GATE prints 5 one-mark and 5 two-mark GA questions.
CORE_ONE_MARK = 25       # core is 25 one-mark + 30 two-mark = 85 marks.
CORE_TWO_MARK = 30


def allocate(total, weights):
    """Split `total` picks across subjects by weight, largest-remainder method.

    Plain rounding loses or gains a question, and a mock that is 64 or 66 long is
    not a mock. Largest remainder keeps the total exact.
    """
    if total <= 0:
        return {}
    pool_w = sum(weights.values()) or 1
    exact = {s: total * w / pool_w for s, w in weights.items()}
    base = {s: int(v) for s, v in exact.items()}
    short = total - sum(base.values())
    for s in sorted(exact, key=lambda x: (-(exact[x] - base[x]), x))[:short]:
        base[s] += 1
    return {s: c for s, c in base.items() if c}


def subject_pool(bank):
    """(section, subject) -> [question_id], clean only, MSQ/NAT first.

    Ordering matters: marks are assigned after the picking, and GATE puts MSQ and
    NAT overwhelmingly in the two-mark half. Sorting them to the front of each
    subject bucket means the two-mark slots land on them by preference, without
    making type a hard constraint - which the pool cannot support, since
    computer-organization has only eight clean MSQs in total.
    """
    out = defaultdict(list)
    for q in bank.values():
        if not is_clean(q):
            continue
        section = "ga" if q["subject"] == "general-aptitude" else "core"
        subject = "general-aptitude" if section == "ga" else q["subject"]
        out[(section, subject)].append(q)
    ranked = {}
    for key, items in out.items():
        items.sort(key=lambda q: (0 if q.get("type") in ("msq", "nat") else 1, q["id"]))
        ranked[key] = items
    return ranked


def subject_shape(conn, slug):
    """(section, subject) -> count, taken from a real paper."""
    papers = content.papers()
    if slug not in papers:
        raise SystemExit("No such paper: %s" % slug)
    bank = content.question_bank()
    shape = Counter()
    for r in papers[slug]["questions"]:
        q = bank.get(r["id"])
        if q:
            subject = "general-aptitude" if r["section"] == "ga" else q["subject"]
            shape[(r["section"], subject)] += 1
    return shape


def main():
    ap = argparse.ArgumentParser(description="Generate blueprint mock papers.")
    ap.add_argument("--template", default="gate-cse-2024-set-1")
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20260812, help="fixed for reproducibility")
    ap.add_argument("--duration", type=int, default=180)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    conn = db.init()
    content.seed(conn)
    bank = content.question_bank(reload=True)

    pool = subject_pool(bank)
    weights = subject_shape(conn, args.template)
    core_weight = {s: c for (sec, s), c in weights.items() if sec == "core"}
    core_need = allocate(CORE_ONE_MARK + CORE_TWO_MARK, core_weight)
    ga_need = sum(GA_STRUCTURE)

    print("\nper-mock shape from %s: 65 questions, 100 marks" % args.template)
    print("  GA   5 x 1 + 5 x 2 = 15")
    print("  core %d x 1 + %d x 2 = 85\n" % (CORE_ONE_MARK, CORE_TWO_MARK))
    print("  %-26s %5s %7s %7s %6s" % ("subject", "need", "clean", "msq+nat", "mocks"))
    print("  " + "-" * 56)
    cap = args.count
    for section, subject, need in [("ga", "general-aptitude", ga_need)] + [
        ("core", s, n) for s, n in sorted(core_need.items(), key=lambda kv: -kv[1])
    ]:
        items = pool.get((section, subject), [])
        rich = sum(1 for q in items if q.get("type") in ("msq", "nat"))
        k = len(items) // need if need else 0
        cap = min(cap, k)
        print("  %-26s %5d %7d %7d %6d" % (subject, need, len(items), rich, k))
    print("\n  mocks requested %d, achievable %d" % (args.count, cap))
    n = min(args.count, cap)
    if n < 1:
        raise SystemExit("\n  not enough clean questions for even one mock.\n")

    rng = random.Random(args.seed)
    order = {}
    for key, items in pool.items():
        # Shuffle inside each type tier so the tiers survive but the picks vary.
        rich = [q["id"] for q in items if q.get("type") in ("msq", "nat")]
        plain = [q["id"] for q in items if q.get("type") not in ("msq", "nat")]
        rng.shuffle(rich)
        rng.shuffle(plain)
        order[key] = rich + plain
    cursor = Counter()
    type_of = {q["id"]: q.get("type") for q in bank.values()}
    subject_of = {q["id"]: q["subject"] for q in bank.values()}

    def take(section, subject, k):
        key = (section, subject)
        ids = order.get(key, [])
        chunk = ids[cursor[key] : cursor[key] + k]
        cursor[key] += k
        return chunk

    mocks = []
    for i in range(1, n + 1):
        ga_ids = take("ga", "general-aptitude", ga_need)
        core_ids = []
        for subject, need in sorted(core_need.items()):
            core_ids += take("core", subject, need)

        # Two-mark slots go to MSQ and NAT first, then to MCQs. This is the one
        # place a mark value is invented, and it is invented on questions whose
        # stored marks were an importer default anyway.
        def rank(qid):
            return (0 if type_of.get(qid) in ("msq", "nat") else 1, qid)

        core_sorted = sorted(core_ids, key=rank)
        two = set(core_sorted[:CORE_TWO_MARK])
        picked = [
            dict(id=qid, section="ga", marks=1.0 if j < GA_STRUCTURE[0] else 2.0)
            for j, qid in enumerate(ga_ids)
        ]
        picked += [
            dict(id=qid, section="core", marks=2.0 if qid in two else 1.0)
            for qid in core_ids
        ]
        picked.sort(
            key=lambda r: (
                0 if r["section"] == "ga" else 1,
                r["marks"],
                subject_of.get(r["id"], ""),
                r["id"],
            )
        )
        total = sum(r["marks"] for r in picked)
        mocks.append(
            dict(
                slug="gitgrind-mock-%02d" % i,
                exam="GitGrind Mock",
                year=2026,
                session="mock-%02d" % i,
                code="blueprint:%s" % args.template,
                name="GitGrind Mock %02d" % i,
                total_marks=int(round(total)),
                duration_mins=args.duration,
                printed_questions=len(picked),
                section_marks={
                    "ga": int(round(sum(r["marks"] for r in picked if r["section"] == "ga"))),
                    "core": int(round(sum(r["marks"] for r in picked if r["section"] == "core"))),
                },
                key_note=(
                    "Assembled from clean bank questions on the GATE structure: "
                    "65 questions, GA 5x1 + 5x2, core %d x1 + %d x2. Subject "
                    "weighting follows %s. Two-mark slots go to MSQ and NAT "
                    "first, because the source did not record 1-mark vs 2-mark "
                    "for most questions."
                    % (CORE_ONE_MARK, CORE_TWO_MARK, args.template)
                ),
                questions=picked,
            )
        )

    first = mocks[0]
    print("\n  %d mock(s), %d question(s) each" % (len(mocks), len(first["questions"])))
    print("  marks per mock: %d (ga %d / core %d)" % (
        first["total_marks"], first["section_marks"]["ga"], first["section_marks"]["core"]))
    used = {r["id"] for m in mocks for r in m["questions"]}
    print("  questions reserved for mocks: %d" % len(used))
    assert len(used) == sum(len(m["questions"]) for m in mocks), "a question repeats"
    assert all(m["total_marks"] == 100 for m in mocks), "a mock does not total 100"
    assert all(len(m["questions"]) == 65 for m in mocks), "a mock is not 65 long"

    types = Counter(type_of.get(r["id"]) for r in first["questions"] if r["marks"] == 2)
    print("  mock 01 two-mark slots by type: %s" % dict(types))
    spread = Counter(subject_of.get(r["id"], "?") for r in first["questions"])
    print("\n  mock 01 subject spread")
    for s, c in spread.most_common():
        print("    %-26s %d" % (s, c))

    if not args.apply:
        print("\n  dry run: nothing written. Add --apply.\n")
        return 0

    with open(MOCKS_FILE, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "note": "Generated by tools/build_mocks.py. Delete a mock here and "
                "its questions return to the practice pool automatically.",
                "template": args.template,
                "seed": args.seed,
                "structure": {"ga": "5x1+5x2", "core_one_mark": CORE_ONE_MARK,
                              "core_two_mark": CORE_TWO_MARK},
                "mocks": mocks,
            },
            fh,
            ensure_ascii=False,
            indent=1,
        )
    print("\n  wrote content/mocks.json")
    content.invalidate()
    content.sync_papers(conn)
    print("  papers table now: %d" % conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0])
    print('\n  next: "Reload from disk" in the Bank tab\n')
    return 0


if __name__ == "__main__":
    sys.exit(main())