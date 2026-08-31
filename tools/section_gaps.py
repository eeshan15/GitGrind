#!/usr/bin/env python3
"""Find questions whose origin.section leaked from a neighbouring block.

The source volumes number every question chapter.section.question and lay the
sections out in alphabetical order. That ordering is a checkable invariant, and
where it breaks the heading is wrong.

Two shapes show up:

  duplicate     two consecutive blocks carrying the identical heading. The
                second block failed to capture its own heading and inherited
                the one above it. Volume 3 chapter 5 has exactly two of these
                (5.1/5.2 both "Bankers Algorithm", 5.25/5.26 both "Resource
                Allocation"), and in both cases the questions in the second
                block are plainly about something else.

  out of order  a block whose heading does not fit the alphabetical run around
                it. This is the same failure at a chapter boundary, where there
                is no preceding block in the chapter to duplicate, so the
                heading comes from the end of the previous chapter instead.
                Volume 3 block 4.1 carries "Two Phase Locking Protocol" over
                nine carry-lookahead and full-adder questions.

Detection is one rule for both: sections that cannot belong to any longest
non-decreasing run through the chapter are suspects, plus any exact duplicate
of the block above.

The topic tag is usually fine - it was derived before the heading was stored,
and every case checked so far had the right topic and the wrong section. So
this is about the subtopic slug, which is what a concept search will match on.

Read-only. Writes one report to content/review/section_gaps.json, which is
meant to be edited by hand: fill in "correct_section" where you know it, leave
it empty to skip. Nothing is applied here.

Run from the repo root:  python tools/section_gaps.py
"""
import bisect
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())

try:
    from core import content
except ImportError as exc:
    sys.exit("cannot import core.content - run this from the repo root (%s)" % exc)

OUT = os.path.join("content", "review", "section_gaps.json")
SNIPPET = 110


def norm(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").strip().lower()).strip("-")


def off_run(seq):
    """Indices of seq that cannot lie on a longest non-decreasing run.

    Sorted input returns nothing, which is the whole point: a clean chapter
    produces no findings and the report stays small enough to read.
    """
    if not seq:
        return []
    tails, tail_at, prev = [], [], [-1] * len(seq)
    for i, v in enumerate(seq):
        j = bisect.bisect_right(tails, v)
        if j == len(tails):
            tails.append(v)
            tail_at.append(i)
        else:
            tails[j] = v
            tail_at[j] = i
        prev[i] = tail_at[j - 1] if j else -1
    keep, k = set(), tail_at[-1] if tail_at else -1
    while k != -1:
        keep.add(k)
        k = prev[k]
    return [i for i in range(len(seq)) if i not in keep]


def main():
    bank = content.question_bank(reload=True)
    if not bank:
        sys.exit("question bank is empty")

    # (volume, chapter) -> section_index -> [questions]
    chapters = collections.defaultdict(lambda: collections.defaultdict(list))
    no_ref = 0
    for q in bank.values():
        origin = q.get("origin") or {}
        if not isinstance(origin, dict):
            no_ref += 1
            continue
        parts = (origin.get("ref") or "").split(".")
        if len(parts) < 3 or not parts[1].isdigit():
            no_ref += 1
            continue
        chapters[(origin.get("volume") or "", parts[0])][int(parts[1])].append(q)

    print("\n  bank: %d questions, %d without a usable ref" % (len(bank), no_ref))
    print("  chapters: %d\n" % len(chapters))

    findings = []
    unordered_chapters = []

    for (volume, chapter) in sorted(chapters):
        blocks = chapters[(volume, chapter)]
        order = sorted(blocks)
        if len(order) < 3:
            continue  # too short for the ordering argument to mean anything

        secs = [blocks[i][0].get("origin", {}).get("section", "") for i in order]
        slugs = [norm(s) for s in secs]
        # Order on the raw heading, not the slug. The volumes sort headings as
        # plain strings, so an uppercase acronym lands before a mixed-case word:
        # "SQL" < "Safe Query" because Q is 81 and a is 97. Lowercasing first
        # inverts exactly those pairs, and acronym-heavy chapters - DMA, IO
        # Handling, CSMA CD, SQL - then read as out of order when they are not.
        keys = list(secs)

        # If a chapter is not broadly alphabetical the invariant does not hold
        # there and every finding would be noise. Measure that by how much of
        # the chapter falls off the run, not by counting out-of-order pairs:
        # in a five-block chapter a single leaked heading breaks a quarter of
        # the pairs, which would throw away exactly the case worth catching.
        off = off_run(keys)
        if len(off) > max(1, int(0.25 * len(order))):
            unordered_chapters.append(
                (volume, chapter, len(off), len(order))
            )
            continue

        flagged = set(off)
        for pos in range(1, len(order)):
            if slugs[pos] and slugs[pos] == slugs[pos - 1]:
                flagged.add(pos)

        for pos in sorted(flagged):
            idx = order[pos]
            qs = blocks[idx]
            before = secs[pos - 1] if pos else ""
            after = secs[pos + 1] if pos + 1 < len(secs) else ""
            reason = (
                "duplicate of the block above"
                if pos and slugs[pos] == slugs[pos - 1]
                else "breaks the chapter's alphabetical order"
            )
            findings.append(
                dict(
                    volume=volume,
                    block="%s.%d" % (chapter, idx),
                    reason=reason,
                    current_section=secs[pos],
                    current_subtopic=slugs[pos],
                    alphabetical_window=dict(after=before, before=after),
                    question_count=len(qs),
                    topics=sorted({q.get("topic", "") for q in qs}),
                    subjects=sorted({q.get("subject", "") for q in qs}),
                    correct_section="",
                    questions=[
                        dict(
                            id=q["id"],
                            ref=q.get("origin", {}).get("ref", ""),
                            exam=q.get("origin", {}).get("exam", ""),
                            text=(q.get("text") or "")[:SNIPPET].replace("\n", " "),
                        )
                        for q in sorted(
                            qs, key=lambda x: x.get("origin", {}).get("ref", "")
                        )
                    ],
                )
            )

    # ---- report ---------------------------------------------------------
    if unordered_chapters:
        print("  chapters skipped, not alphabetical enough to judge:")
        for volume, chapter, off, n in unordered_chapters:
            print("    %s ch%s  %d of %d blocks off the run"
                  % (volume, chapter, off, n))
        print("")

    if not findings:
        print("  No suspect headings. Every chapter's sections sit in order.")
        return 0

    findings.sort(key=lambda f: -f["question_count"])
    affected = sum(f["question_count"] for f in findings)
    print("  %d suspect block(s), %d question(s) affected  (%.2f%% of the bank)\n"
          % (len(findings), affected, affected * 100.0 / len(bank)))

    for f in findings:
        win = f["alphabetical_window"]
        print("  %-22s %s  (%d q, %s)"
              % (f["volume"], f["block"], f["question_count"], f["reason"]))
        print("      heading now : %s" % (f["current_section"] or "(empty)"))
        print("      should sort : after %r, before %r"
              % (win["after"] or "(start)", win["before"] or "(end)"))
        print("      topic tag   : %s" % ", ".join(f["topics"]))
        for q in f["questions"][:3]:
            print("      %-13s %s" % (q["ref"], q["text"]))
        if len(f["questions"]) > 3:
            print("      ... and %d more" % (len(f["questions"]) - 3))
        print("")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(
            dict(
                note="Edit correct_section on each finding, then run "
                     "tools/section_fix.py. Leave it empty to skip that block. "
                     "The topic tag is not touched by either script.",
                bank_total=len(bank),
                findings=findings,
            ),
            fh,
            indent=2,
            ensure_ascii=False,
        )
    print("  report written to %s" % OUT)
    print("  Fill in correct_section where you know it, leave the rest empty.")
    return 0


if __name__ == "__main__":
    sys.exit(main())