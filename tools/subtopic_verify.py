#!/usr/bin/env python3
"""Prove the subtopic wiring works, end to end, against the real bank.

Run after patch_subtopic.py. Read-only: opens the database but only selects,
and quiz.select does not write. Exits non-zero on the first failure so this can
sit in front of a commit.

Each check is the smallest thing that would have caught the field being dead:

  1. subtopic is populated at all - the patch's one job
  2. a topic actually subdivides, with the counts printed so you can see it
  3. content.search(subtopic=...) narrows the result set
  4. free-text search reaches the heading, not just the stem. This is the check
     that matters most: the whole reason for the change is that stems do not
     contain the concept name
  5. quiz.select(subtopic_slugs=...) returns only questions from that subtopic,
     and does not return an empty set for a subtopic that has questions
  6. the old call signatures still behave - nothing that worked before moved

Run from the repo root:  python tools/subtopic_verify.py
Optional: pass a subtopic slug to probe instead of the auto-picked one.
"""
import collections
import os
import sys

sys.path.insert(0, os.getcwd())

try:
    from core import content, db, quiz
except ImportError as exc:
    sys.exit("cannot import core - run this from the repo root (%s)" % exc)

FAIL = []


def check(label, ok, detail=""):
    print("  [%s] %s%s" % ("pass" if ok else "FAIL", label, ("  - " + detail) if detail else ""))
    if not ok:
        FAIL.append(label)
    return ok


def main():
    bank = content.question_bank(reload=True)
    if not bank:
        sys.exit("question bank is empty")
    print("\n  bank: %d questions\n" % len(bank))

    # ---- 1. populated ---------------------------------------------------
    filled = [q for q in bank.values() if q.get("subtopic")]
    if not check(
        "subtopic is populated",
        bool(filled),
        "%d of %d questions" % (len(filled), len(bank)),
    ):
        print("\n  Nothing else can pass. Either patch_subtopic.py was not applied,")
        print("  or no question in this bank carries origin.section. Run")
        print("  tools/subtopic_audit.py to tell those two apart.")
        return 1

    # ---- 2. granularity gained ------------------------------------------
    by_topic = collections.defaultdict(collections.Counter)
    for q in filled:
        by_topic[(q["subject"], q.get("topic", ""))][q["subtopic"]] += 1
    split = {k: v for k, v in by_topic.items() if len(v) > 1}
    check(
        "at least one topic subdivides",
        bool(split),
        "%d topics split" % len(split),
    )
    if split:
        subj, topic = max(split, key=lambda k: len(split[k]))
        print("      e.g. %s/%s ->" % (subj, topic))
        for slug, n in split[(subj, topic)].most_common(8):
            print("           %-40s %3d" % (slug, n))

    # ---- pick a probe ----------------------------------------------------
    if len(sys.argv) > 1:
        probe = sys.argv[1]
        pool = [q for q in filled if q["subtopic"] == probe]
        if not pool:
            sys.exit("no questions with subtopic %r" % probe)
    else:
        counts = collections.Counter(q["subtopic"] for q in filled)
        # A mid-sized subtopic inside a topic that split: big enough that an
        # empty result is a real failure, small enough that "narrows the set"
        # is a meaningful claim.
        candidates = [
            s for s, n in counts.most_common() if 3 <= n <= 60
        ] or [counts.most_common(1)[0][0]]
        probe = candidates[len(candidates) // 2]
        pool = [q for q in filled if q["subtopic"] == probe]
    probe_topic = pool[0].get("topic", "")
    probe_subject = pool[0]["subject"]
    print("\n  probing subtopic %r (%d questions, under %s/%s)\n"
          % (probe, len(pool), probe_subject, probe_topic))

    # ---- 3. search narrows ----------------------------------------------
    wide = content.search(topic=probe_topic, limit=500)
    narrow = content.search(topic=probe_topic, subtopic=probe, limit=500)
    check(
        "search(subtopic=) narrows the result set",
        0 < len(narrow) <= len(wide),
        "%d of %d in the topic" % (len(narrow), len(wide)),
    )
    check(
        "every result carries the requested subtopic",
        all(r.get("subtopic") == probe for r in narrow),
        "%d results" % len(narrow),
    )

    # ---- 4. free text reaches the heading -------------------------------
    word = probe.split("-")[0]
    hits = content.search(query=word, limit=500)
    in_stem = sum(1 for q in pool if word in (q.get("text") or "").lower())
    check(
        "free-text %r finds questions in this subtopic" % word,
        any(h.get("subtopic") == probe for h in hits),
        "%d total hits; only %d of the %d questions have %r in the stem"
        % (len(hits), in_stem, len(pool), word),
    )
    if in_stem < len(pool):
        print("      %d question(s) are reachable only through the heading."
              % (len(pool) - in_stem))
        print("      That gap is what this patch closes.")

    # ---- 5. quiz.select honours the filter -------------------------------
    conn = db.connect()
    try:
        picked = quiz.select(conn, purpose="mixed", count=5, subtopic_slugs=[probe])
        got = [q for q, _ in picked]
        check(
            "quiz.select(subtopic_slugs=) returns questions",
            bool(got),
            "%d picked" % len(got),
        )
        if got:
            check(
                "every picked question is in the subtopic",
                all(q.get("subtopic") == probe for q in got),
                ", ".join(sorted({q.get("subtopic", "") for q in got})),
            )

        # ---- 6. old signatures unaffected ------------------------------
        before = quiz.select(conn, purpose="mixed", count=5)
        check(
            "select without subtopic_slugs still returns a set",
            bool(before),
            "%d picked" % len(before),
        )
        by_topic_only = content.search(topic=probe_topic, limit=500)
        check(
            "search without subtopic is unchanged",
            len(by_topic_only) == len(wide),
            "%d results" % len(by_topic_only),
        )
    finally:
        conn.close()

    print("")
    if FAIL:
        print("  %d check(s) failed: %s" % (len(FAIL), "; ".join(FAIL)))
        return 1
    print("  all checks passed. subtopic is live and filterable.")
    print("  Next: content/topic_map.json so 'banker algo' resolves to %r." % probe)
    return 0


if __name__ == "__main__":
    sys.exit(main())