#!/usr/bin/env python3
"""Read-only audit of origin.section before the subtopic backfill.

MinerU kept the source volume's section heading on every question it imported
(origin.section), and import_mineru_bank.py used it to derive the syllabus
topic - then dropped it. content._hydrate already reserves an empty
"subtopic" field. This script measures whether section is good enough to fill
that field before any code is changed.

What matters, and what this prints:

  coverage      how many questions carry a section at all. Anything the
                backfill cannot reach stays exactly as it is today, so low
                coverage means a smaller win, not a regression.
  fan-out       sections per syllabus topic. This is the whole point: if a
                topic has one section the backfill buys nothing there.
  straddling    one section appearing under two different topics. Usually a
                mis-tag upstream and worth eyeballing, because a subtopic
                filter would then pull questions from two topics at once.
  collisions    two different section strings slugging to the same key.
                Harmless (they merge) but you should know it happened.

Writes nothing. Run from the repo root:  python tools/subtopic_audit.py
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.getcwd())

try:
    from core import content
except ImportError:
    sys.exit("cannot import core.content - run this from the repo root")


def norm(text):
    """Same rule as content._norm_key, duplicated so this stays read-only."""
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").strip().lower()).strip("-")


def main():
    bank = content.question_bank()
    if not bank:
        sys.exit("question bank is empty")

    total = len(bank)
    with_section = 0
    per_subject = collections.Counter()
    per_subject_missing = collections.Counter()
    sections_by_topic = collections.defaultdict(collections.Counter)
    topics_by_slug = collections.defaultdict(set)
    raw_by_slug = collections.defaultdict(set)
    already = 0

    for q in bank.values():
        if q.get("subtopic"):
            already += 1
        origin = q.get("origin") or {}
        raw = origin.get("section") if isinstance(origin, dict) else ""
        key = (q.get("subject", ""), q.get("topic", ""))
        if not raw:
            per_subject_missing[q.get("subject", "")] += 1
            continue
        with_section += 1
        per_subject[q.get("subject", "")] += 1
        slug = norm(raw)
        sections_by_topic[key][slug] += 1
        topics_by_slug[slug].add(key)
        raw_by_slug[slug].add(raw)

    pct = with_section * 100.0 / total
    print("\n=== coverage ===")
    print("  %d of %d questions carry origin.section  (%.1f%%)" % (with_section, total, pct))
    if already:
        print("  %d already have a subtopic set - backfill will not touch these" % already)

    print("\n=== per subject ===")
    print("  %-26s %7s %8s" % ("subject", "with", "without"))
    for subj in sorted(set(per_subject) | set(per_subject_missing)):
        print("  %-26s %7d %8d" % (subj, per_subject[subj], per_subject_missing[subj]))

    print("\n=== fan-out: sections per topic ===")
    gain, flat = 0, 0
    rows = []
    for (subj, topic), counter in sections_by_topic.items():
        rows.append((len(counter), sum(counter.values()), subj, topic, counter))
    rows.sort(key=lambda r: (-r[0], -r[1]))
    for n_sec, n_q, subj, topic, counter in rows:
        if n_sec > 1:
            gain += 1
        else:
            flat += 1
        if n_sec > 1:
            spread = ", ".join(
                "%s(%d)" % (s, c) for s, c in counter.most_common(6)
            )
            print("  %-40s %2d sections over %3d q" % (subj + "/" + topic, n_sec, n_q))
            print("      %s%s" % (spread, " ..." if len(counter) > 6 else ""))
    print("\n  %d topics gain granularity, %d stay flat (single section)" % (gain, flat))

    straddle = {s: t for s, t in topics_by_slug.items() if len(t) > 1}
    print("\n=== straddling sections (one section, several topics) ===")
    if not straddle:
        print("  none")
    for slug, keys in sorted(straddle.items()):
        print("  %-34s %s" % (slug, ", ".join("/".join(k) for k in sorted(keys))))
    if straddle:
        print("\n  Not fatal, but a subtopic filter on these will cross topic")
        print("  boundaries. Check whether the upstream topic tag is wrong.")

    collide = {s: r for s, r in raw_by_slug.items() if len(r) > 1}
    print("\n=== slug collisions (different headings, same slug) ===")
    if not collide:
        print("  none")
    for slug, raws in sorted(collide.items()):
        print("  %-34s <- %s" % (slug, " | ".join(sorted(raws))))

    print("\n=== verdict ===")
    if pct < 50:
        print("  Under half the bank has a section. The backfill is still safe")
        print("  (missing sections are left empty) but will only help part of")
        print("  the bank. Worth checking why before wiring the UI to it.")
    elif gain == 0:
        print("  Sections exist but never subdivide a topic. The backfill would")
        print("  add a field with no new information - stop here.")
    else:
        print("  Sections cover %.0f%% of the bank and subdivide %d topics." % (pct, gain))
        print("  Backfill is worth applying. Next: python patch_subtopic.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())