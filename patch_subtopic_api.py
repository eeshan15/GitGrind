#!/usr/bin/env python3
"""Carry subtopic through build_quiz, /api/quiz, and the session-end payload.

quiz.select has understood subtopic_slugs since patch_subtopic.py, but nothing
above it does, so the only way to use it is to call select directly. Three
places need to know:

  build_quiz    accepts subtopic_slugs and hands it to select. Added at the end
                of the signature and passed by keyword at all four call sites,
                for the reason patch_argorder.py exists: putting it mid-list and
                relying on position is what made kinds bind to subtopic_slugs
                and silently emptied every set built with a kind filter.

  /api/quiz     accepts subtopic and subtopics as slugs, mirroring how topic and
                topics already work. No id lookup: subtopics are not rows in a
                table, they are labels on questions, so the slug is the whole
                identity.

  submit_quiz   returns subtopic_breakdown alongside breakdown. The results
                panel currently offers "Practise 5 more on analytical" because
                topic is the finest thing it is told about; with this it can
                offer venn-diagram instead, which is the difference between a
                set of 70 and a set of 7.

subtopic_breakdown only counts questions that carry a subtopic, and is empty
when none of them do - about 164 of 3,862 have no heading to derive one from,
and a breakdown row labelled "" would be worse than no row.

Seven edits across core/quiz.py and core/api.py. Run patch_subtopic.py and
patch_argorder.py first.

CRLF-safe and idempotent. Run from the repo root:  python patch_subtopic_api.py
"""
import io
import os
import sys

EDITS = [
    # ---- 1. build_quiz signature ---------------------------------------
    ('core/quiz.py',
     '    question_ids=None,\n'
     '    paper_id=None,\n'
     '):',

     '    question_ids=None,\n'
     '    paper_id=None,\n'
     '    # At the end, and passed on by keyword only. See patch_argorder.py:\n'
     '    # select is called positionally below, so a parameter added in the\n'
     '    # middle of either signature captures the next one\'s argument.\n'
     '    subtopic_slugs=None,\n'
     '):'),

    # ---- 2..5. the four select call sites, by keyword -------------------
    ('core/quiz.py',
     '                purpose,\n'
     '                count,\n'
     '                subject_slug,\n'
     '                topic_slugs,\n'
     '                kinds,\n'
     '                metrics=metrics,',

     '                purpose,\n'
     '                count,\n'
     '                subject_slug,\n'
     '                topic_slugs,\n'
     '                kinds,\n'
     '                subtopic_slugs=subtopic_slugs,\n'
     '                metrics=metrics,'),

    ('core/quiz.py',
     '                "weak",\n'
     '                count,\n'
     '                subject_slug,\n'
     '                topic_slugs,\n'
     '                kinds,\n'
     '                metrics=metrics,',

     '                "weak",\n'
     '                count,\n'
     '                subject_slug,\n'
     '                topic_slugs,\n'
     '                kinds,\n'
     '                subtopic_slugs=subtopic_slugs,\n'
     '                metrics=metrics,'),

    ('core/quiz.py',
     '                    "mixed",\n'
     '                    count - len(picked),\n'
     '                    subject_slug,\n'
     '                    topic_slugs,\n'
     '                    kinds,\n'
     '                    exclude=have,',

     '                    "mixed",\n'
     '                    count - len(picked),\n'
     '                    subject_slug,\n'
     '                    topic_slugs,\n'
     '                    kinds,\n'
     '                    subtopic_slugs=subtopic_slugs,\n'
     '                    exclude=have,'),

    ('core/quiz.py',
     '                    "fresh",\n'
     '                    count - len(picked),\n'
     '                    subject_slug,\n'
     '                    topic_slugs,\n'
     '                    kinds,\n'
     '                    exclude=have,',

     '                    "fresh",\n'
     '                    count - len(picked),\n'
     '                    subject_slug,\n'
     '                    topic_slugs,\n'
     '                    kinds,\n'
     '                    subtopic_slugs=subtopic_slugs,\n'
     '                    exclude=have,'),

    # ---- 6. session-end subtopic breakdown -----------------------------
    ('core/quiz.py',
     '            t = per_topic.setdefault(\n'
     '                q.get("topic", ""), dict(n=0, ok=0, subject=q["subject"])\n'
     '            )\n'
     '            t["n"] += 1',

     '            t = per_topic.setdefault(\n'
     '                q.get("topic", ""), dict(n=0, ok=0, subject=q["subject"])\n'
     '            )\n'
     '            t["n"] += 1\n'
     '            # Only questions that carry a subtopic. A row labelled "" is\n'
     '            # worse than no row, and roughly 164 of the bank has no source\n'
     '            # heading to derive one from.\n'
     '            if q.get("subtopic"):\n'
     '                st = per_subtopic.setdefault(\n'
     '                    q["subtopic"],\n'
     '                    dict(n=0, ok=0, subject=q["subject"], topic=q.get("topic", "")),\n'
     '                )\n'
     '                st["n"] += 1\n'
     '                st["ok"] += 1 if ok else 0',

     ),

    ('core/quiz.py',
     '    per_topic = {}\n',
     '    per_topic = {}\n    per_subtopic = {}\n'),

    ('core/quiz.py',
     '    breakdown = [\n'
     '        dict(\n'
     '            topic=k,',

     '    subtopic_breakdown = [\n'
     '        dict(\n'
     '            subtopic=k,\n'
     '            topic=v["topic"],\n'
     '            subject=v["subject"],\n'
     '            n=v["n"],\n'
     '            correct=v["ok"],\n'
     '            accuracy=round(v["ok"] / v["n"] * 100),\n'
     '        )\n'
     '        for k, v in sorted(per_subtopic.items(), key=lambda kv: -kv[1]["n"])\n'
     '    ]\n'
     '    breakdown = [\n'
     '        dict(\n'
     '            topic=k,'),

    ('core/quiz.py',
     '        breakdown=breakdown,\n'
     '        wrong_ids=',

     '        breakdown=breakdown,\n'
     '        subtopic_breakdown=subtopic_breakdown,\n'
     '        wrong_ids='),

    # ---- 7. API passthrough --------------------------------------------
    ('core/api.py',
     '            topic_ids = list(body.get("topic_ids") or [])',

     '            # Subtopics are labels on questions rather than rows in a\n'
     '            # table, so unlike topic there is no id to look up - the slug\n'
     '            # is the whole identity.\n'
     '            subtopic_slugs = [\n'
     '                s for s in (\n'
     '                    ([body["subtopic"]] if body.get("subtopic") else [])\n'
     '                    + list(body.get("subtopics") or [])\n'
     '                ) if s\n'
     '            ]\n'
     '            topic_ids = list(body.get("topic_ids") or [])'),

    ('core/api.py',
     '                question_ids=question_ids,\n'
     '                paper_id=paper_id,',

     '                question_ids=question_ids,\n'
     '                paper_id=paper_id,\n'
     '                subtopic_slugs=subtopic_slugs,'),
]


def main():
    changed = skipped = 0
    for path, old, new in EDITS:
        if not os.path.isfile(path):
            sys.exit("missing %s - run this from the repo root" % path)
        s = io.open(path, encoding="utf-8", newline="").read()
        crlf = "\r\n" in s
        o = old.replace("\n", "\r\n") if crlf else old
        n = new.replace("\n", "\r\n") if crlf else new
        if n in s:
            print("  skip    %-16s already applied" % path)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d times, expected 1.\n"
                     "          Run patch_subtopic.py and patch_argorder.py first."
                     % (path, s.count(o)))
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-16s ok" % path)
        changed += 1
    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    if changed:
        print("  Restart the app, then check:")
        print("    /api/quiz with {\"subtopic\": \"adder\", \"count\": 5}")
    return 0


if __name__ == "__main__":
    sys.exit(main())