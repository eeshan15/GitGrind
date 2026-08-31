#!/usr/bin/env python3
"""Fill the subtopic field from origin.section, then make it filterable.

content._hydrate has always reserved item["subtopic"] and public_question has
always exported it, but nothing ever wrote to it - the only two references to
"subtopic" in the whole codebase are those two lines. Meanwhile MinerU kept the
source volume's section heading on every imported question and
import_mineru_bank.py used it to pick the syllabus topic, then left it buried in
origin. So "Bankers Algorithm" exists as a label on real questions and there is
no way to ask for it: operating-systems/deadlock is the finest grain the app
offers, and it holds 30 questions covering resource allocation, RAG, detection
and Banker's together.

Four edits, all wiring, no new logic:

  1. content._hydrate   fill subtopic from origin.section when it is empty
  2. content.search     accept a subtopic argument, and put subtopic in the
                        free-text haystack so typing "banker" finds it
  3. quiz.select        accept subtopic_slugs and filter on it
  4. api /api/questions pass ?subtopic= through to content.search

Keyword matching on question text was the obvious alternative and it does not
work here: of the 30 questions under operating-systems/deadlock only 2 contain
the string "banker". The rest present an allocation/max/available snapshot and
never name the algorithm, because that is how the exam asks. The section
heading is the reliable signal, and it is already in the data.

Nothing is removed and no existing caller changes behaviour: both new
parameters default to empty, and a question with no origin.section keeps the
empty subtopic it has today.

CRLF-safe and idempotent. Run from the repo root:  python patch_subtopic.py
"""
import io
import os
import sys

EDITS = [
    # ---- 1. backfill on hydrate ---------------------------------------
    ('core/content.py',
     '    item.setdefault("topic", "")\n'
     '    item.setdefault("subtopic", "")',

     '    item.setdefault("topic", "")\n'
     '    # The importer derived the syllabus topic from the source volume\'s\n'
     '    # section heading and then left the heading in origin, so the finest\n'
     '    # grain the app could offer was the topic - one bucket for everything\n'
     '    # under it. The heading is a real label on real questions, so promote\n'
     '    # it. A question that arrived without one keeps the empty string it\n'
     '    # has today; an explicit subtopic in the bank file always wins.\n'
     '    if not q.get("subtopic"):\n'
     '        origin = q.get("origin") or {}\n'
     '        if isinstance(origin, dict) and origin.get("section"):\n'
     '            item["subtopic"] = _norm_key(origin["section"])\n'
     '    item.setdefault("subtopic", "")'),

    # ---- 2a. search signature -----------------------------------------
    ('core/content.py',
     'def search(\n'
     '    query="", subject="", topic="", qtype="", difficulty="", kind="", source="",\n'
     '    paper="", limit=40\n'
     '):',

     'def search(\n'
     '    query="", subject="", topic="", qtype="", difficulty="", kind="", source="",\n'
     '    paper="", subtopic="", limit=40\n'
     '):'),

    # ---- 2b. search filter --------------------------------------------
    ('core/content.py',
     '        if topic and item.get("topic") != topic:\n'
     '            continue',

     '        if topic and item.get("topic") != topic:\n'
     '            continue\n'
     '        if subtopic and item.get("subtopic") != subtopic:\n'
     '            continue'),

    # ---- 2c. search haystack ------------------------------------------
    ('core/content.py',
     '                    item.get("text", ""),\n'
     '                    item.get("topic", ""),\n'
     '                    item.get("subject", ""),',

     '                    item.get("text", ""),\n'
     '                    item.get("topic", ""),\n'
     '                    # Free-text search reaches the section heading too, so\n'
     '                    # "banker" finds the Banker\'s questions whose stems only\n'
     '                    # ever show an allocation table.\n'
     '                    item.get("subtopic", ""),\n'
     '                    item.get("subject", ""),'),

    # ---- 3a. select signature -----------------------------------------
    ('core/quiz.py',
     '    subject_slug=None,\n'
     '    topic_slugs=None,\n'
     '    kinds=None,',

     '    subject_slug=None,\n'
     '    topic_slugs=None,\n'
     '    subtopic_slugs=None,\n'
     '    kinds=None,'),

    # ---- 3b. select filter set ----------------------------------------
    ('core/quiz.py',
     '    topic_filter = set(topic_slugs or [])',

     '    topic_filter = set(topic_slugs or [])\n'
     '    # Narrower than topic_filter and independent of it: passing only\n'
     '    # subtopics selects across whatever topics carry them, which is what a\n'
     '    # user typing one concept name is asking for.\n'
     '    subtopic_filter = set(subtopic_slugs or [])'),

    # ---- 3c. select filter test ---------------------------------------
    ('core/quiz.py',
     '        if topic_filter and q.get("topic") not in topic_filter:\n'
     '            continue',

     '        if topic_filter and q.get("topic") not in topic_filter:\n'
     '            continue\n'
     '        if subtopic_filter and q.get("subtopic") not in subtopic_filter:\n'
     '            continue'),

    # ---- 4. api passthrough -------------------------------------------
    ('core/api.py',
     '                        topic=one("topic"),',

     '                        topic=one("topic"),\n'
     '                        subtopic=one("subtopic"),'),
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
            print("  skip    %-26s already applied" % path)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit(
                "  ERROR   %s: anchor found %d times, expected 1" % (path, s.count(o))
            )
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-26s ok" % path)
        changed += 1
    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    if changed:
        print("  content._cache is per-process, so this takes effect on restart.")
        print("  Verify with:  python tools/subtopic_verify.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())