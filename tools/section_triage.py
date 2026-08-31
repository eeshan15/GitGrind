#!/usr/bin/env python3
"""Sort the section_gaps findings into buckets you can act on.

tools/section_gaps.py finds blocks whose origin.section is wrong. It cannot say
whether that also corrupted the topic tag, and the topic is what the readiness
model and every practice filter run on. This decides that, per block, and says
what to do with each one.

Two signals, in order of trust:

  1. Is the bad heading in go_tag_map.json?

     import_questions.resolve_topic tries the section heading first, then the
     question title, then tags, then the chapter. A heading that is not in the
     map fails that first step, so the topic came from a later fallback and is
     probably right - only the subtopic is wrong. A heading that IS in the map
     produced the topic directly, so a wrong heading means a wrong topic.

     This is deterministic and needs no guessing. "Bankers Algorithm" and "Two
     Phase Locking Protocol" are unmapped, which is why those blocks kept
     correct topics. "Determinant", "Graph Algorithms" and "Stop and Wait" are
     mapped, which is how eigenvalue questions ended up under matrices.

  2. What does the existing keyword classifier say about the block?

     Per question that classifier is not reliable enough to act on - measured
     against the operating-systems bank it agreed with the existing tag on 57%
     of questions, disagreed on 11% and returned nothing usable on 30%. Per
     block it is much better: modal vote matched the existing topic on 17 of 18
     blocks, and the single miss had one vote behind it. So the vote is only
     reported where enough questions actually scored, and it is a suggestion to
     review, never an answer.

Recommended actions, and why:

  keep             The heading is in the tag map and the block votes for the
                   topic that heading produced, so the heading is right and the
                   flag was the detector's limitation, not a defect. GATE
                   Overflow splits a long section across consecutive numbered
                   blocks; "Digital Circuits" over eighteen flip-flop and
                   counter questions is a continuation, not a leak. Clearing
                   these would throw away a correct label.
  clear-subtopic   The heading is not in the tag map, so it is not a concept
                   this bank recognises in that position - "Two Phase Locking
                   Protocol" over nine adder questions. Blanking the subtopic
                   is the honest fix: an empty field costs granularity, a wrong
                   one actively misroutes searches.
  check-topic      The topic was derived from the wrong heading. These need a
                   decision, and the block vote is there to speed it up.
  review           Not enough evidence either way. Left for a human.
  skip             The heading is a placeholder from the source, not an
                   extraction fault - "No Classified Topic" is GATE Overflow's
                   own label. Nothing to repair.

Read-only apart from rewriting the report. Run from the repo root:

    python tools/section_triage.py
"""
import collections
import json
import os
import re
import sys

ROOT = os.getcwd()
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

try:
    from core import content
    from import_questions import (
        classify,
        compile_lexicon,
        load_json,
        load_syllabus,
        load_tag_map,
        map_lookup,
        slugify,
    )
except ImportError as exc:
    sys.exit("cannot import - run this from the repo root (%s)" % exc)

REPORT = os.path.join("content", "review", "section_gaps.json")
MIN_VOTES = 4
MIN_SHARE = 0.5
PLACEHOLDER = {"no-classified-topic", "medium", "easy", "hard", "computer-science"}


def main():
    if not os.path.isfile(REPORT):
        sys.exit("%s not found - run tools/section_gaps.py first" % REPORT)
    report = load_json(REPORT, {})
    findings = report.get("findings") or []
    if not findings:
        sys.exit("no findings in the report")

    topic_map, subject_map, _chapter_map, _ignore = load_tag_map()
    if not topic_map:
        sys.exit("content/go_tag_map.json is missing or empty")
    topics = load_syllabus()
    matchers, _missing = compile_lexicon(topics)

    bank = content.question_bank(reload=True)
    # Group the bank the same way section_gaps did, so a finding's block can be
    # scored over all of its questions rather than the three in the snippet.
    blocks = collections.defaultdict(list)
    for q in bank.values():
        origin = q.get("origin") or {}
        if not isinstance(origin, dict):
            continue
        parts = (origin.get("ref") or "").split(".")
        if len(parts) < 3 or not parts[1].isdigit():
            continue
        blocks[(origin.get("volume") or "", parts[0], int(parts[1]))].append(q)

    buckets = collections.Counter()
    q_by_bucket = collections.Counter()

    for f in findings:
        chapter, idx = f["block"].split(".")
        qs = blocks.get((f["volume"], chapter, int(idx)), [])
        slug = f.get("current_subtopic", "")
        first_in_chapter = idx == "1"

        # ---- signal 1: did the bad heading feed the topic? --------------
        subject = qs[0]["subject"] if qs else ""
        mapped = map_lookup(topic_map, slugify(f.get("current_section", "")), subject)
        f["heading_in_tag_map"] = mapped
        f["topic_from_bad_heading"] = bool(mapped)
        f["first_block_in_chapter"] = first_in_chapter

        # ---- signal 2: block-level modal vote ---------------------------
        votes = collections.Counter()
        for q in qs:
            key, _runner, _score, _hits, problem = classify(
                q.get("text") or "",
                [str(o) for o in (q.get("options") or [])],
                matchers,
                topics,
            )
            if key and not problem:
                votes[key] += 1
        total = sum(votes.values())
        current = "%s/%s" % (subject, qs[0].get("topic", "")) if qs else ""
        if total >= MIN_VOTES:
            modal, n = votes.most_common(1)[0]
            share = n / float(total)
            f["block_vote"] = dict(
                modal=modal,
                votes=n,
                scored=total,
                of_questions=len(qs),
                share=round(share, 2),
                agrees_with_current=modal == current,
            )
        else:
            f["block_vote"] = dict(
                modal="", votes=0, scored=total, of_questions=len(qs), share=0.0,
                agrees_with_current=None,
            )
        f["current_topic"] = current

        # ---- recommendation --------------------------------------------
        vote = f["block_vote"]
        if slug in PLACEHOLDER:
            action = "skip"
            note = "source placeholder, not an extraction fault"
        elif not mapped:
            action = "clear-subtopic"
            note = "heading unmapped, so the topic came from a fallback"
        elif vote["agrees_with_current"] is True and vote["share"] >= MIN_SHARE:
            action = "keep"
            note = "heading mapped and the block votes for its own topic"
        elif vote["agrees_with_current"] is False and vote["share"] >= MIN_SHARE:
            action = "check-topic"
            note = "topic came from the bad heading; block votes %s" % vote["modal"]
        else:
            action = "review"
            note = "only %d of %d questions scored" % (vote["scored"], len(qs))
        f["recommended_action"] = action
        f["recommendation_note"] = note
        f.setdefault("correct_section", "")

        buckets[action] += 1
        q_by_bucket[action] += f["question_count"]

    # ---- print ---------------------------------------------------------
    order = ["check-topic", "clear-subtopic", "keep", "review", "skip"]
    print("")
    for action in order:
        if not buckets[action]:
            continue
        print("  %-16s %2d block(s), %3d question(s)"
              % (action, buckets[action], q_by_bucket[action]))
    print("")

    for action in order:
        rows = [f for f in findings if f["recommended_action"] == action]
        if not rows:
            continue
        rows.sort(key=lambda f: -f["question_count"])
        print("  === %s ===" % action)
        for f in rows:
            vote = f["block_vote"]
            flag = " [chapter-first]" if f["first_block_in_chapter"] else ""
            print("  %-16s %-7s %3dq  %s%s"
                  % (f["volume"], f["block"], f["question_count"],
                     f["current_section"] or "(empty)", flag))
            print("        topic now  %s%s"
                  % (f["current_topic"],
                     "  <- from this heading" if f["topic_from_bad_heading"] else ""))
            if vote["modal"]:
                print("        block vote %s  %d/%d scored of %dq"
                      % (vote["modal"], vote["votes"], vote["scored"],
                         vote["of_questions"]))
            print("        %s" % f["recommendation_note"])
        print("")

    report["findings"] = findings
    report["triage"] = dict(
        min_votes=MIN_VOTES,
        min_share=MIN_SHARE,
        buckets={k: buckets[k] for k in order if buckets[k]},
        questions={k: q_by_bucket[k] for k in order if q_by_bucket[k]},
    )
    with open(REPORT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print("  report updated in place: %s" % REPORT)
    print("  Read check-topic first - those are the ones that moved questions")
    print("  into the wrong topic, which is what the readiness model reads.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
    