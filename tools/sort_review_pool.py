#!/usr/bin/env python3
"""Sort content/review/*-unsorted.json into the live bank.

WHY THIS EXISTS

  A question lands in content/review/<bank>-unsorted.json when the importer could
  not decide its topic. Nothing else is wrong with it: the text, options, answer
  and origin block are all intact. But bank_files() never scans content/review/,
  so those questions do not exist as far as the app is concerned - they are absent
  from the bank, from coverage, and from every paper they belong to.

  The fix is a retag, not a re-extraction. Re-running the PDF extractor would
  build a second parallel bank from the same source with a different id scheme,
  which duplicates every question instead of recovering the missing ones.

  So this reuses the importer's own classifier - GO tags first, then the keyword
  lexicon restricted to the subject the tags imply - and merges whatever resolves
  into the matching content/banks/<bank>/<subject>.json. Anything that still will
  not resolve stays in the unsorted file, so the run is repeatable.

USAGE

  python tools/sort_review_pool.py --dry-run        report only, writes nothing
  python tools/sort_review_pool.py --audit-tags     tags blocking resolution
  python tools/sort_review_pool.py --bank mineru    merge into content/banks/mineru
  python tools/sort_review_pool.py --bank mineru --apply
"""

import argparse
import json
import os
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import import_questions as imp  # noqa: E402

CONTENT = os.path.join(ROOT, "content")
REVIEW = os.path.join(CONTENT, "review")
BANKS = os.path.join(CONTENT, "banks")


def resolve(q, maps, topics, matchers, min_score):
    """Return (topic_key, how, unknown_tags) for one unsorted question."""
    topic_map, subject_map, chapter_map, ignore = maps
    origin = q.get("origin") or {}
    tags = [str(t).lower() for t in (origin.get("tags") or [])]

    # resolve_topic() wants the importer's block/parsed shapes. The unsorted
    # record already holds everything they carry, so build them rather than
    # duplicating the lookup order here and letting the two drift apart.
    block = dict(section=origin.get("section") or "", topic_hint="", chapter={})
    parsed = dict(text=q.get("text", ""), options=[str(o) for o in (q.get("options") or [])], tags=tags)

    key, subject, how, unknown = imp.resolve_topic(
        block, parsed, topic_map, subject_map, chapter_map, ignore, topics
    )
    if key:
        return key, how, unknown

    # No exact tag hit. Narrow the keyword classifier to the subject the tags
    # imply - the tag map's own note says this is far more accurate than
    # searching all 101 topics, and it is the difference between a usable
    # guess and a wrong one.
    if subject is None:
        for tag in tags:
            if tag in subject_map:
                subject = subject_map[tag]
                break

    key, _runner, score, _hits, problem = imp.classify(
        parsed["text"], parsed["options"], matchers, topics, subject, min_score
    )
    if problem or not key:
        return None, None, unknown
    return key, "keyword/%s" % (subject or "any"), unknown


def main():
    ap = argparse.ArgumentParser(description="Sort the review pool into the bank.")
    ap.add_argument("--bank", default="mineru", help="target bank under content/banks")
    ap.add_argument("--file", action="append", help="specific unsorted file(s)")
    ap.add_argument("--min-score", type=float, default=3.0)
    ap.add_argument("--apply", action="store_true", help="write the changes")
    ap.add_argument("--dry-run", action="store_true", help="report only (default)")
    ap.add_argument("--audit-tags", action="store_true", help="list blocking tags")
    args = ap.parse_args()

    topics = imp.load_syllabus()
    if not topics:
        raise SystemExit("content/syllabus.json is missing or empty.")
    maps = imp.load_tag_map()
    if not maps[0]:
        raise SystemExit("content/go_tag_map.json is missing or empty.")
    matchers, _missing = imp.compile_lexicon(topics)

    files = args.file or sorted(
        os.path.join(REVIEW, f)
        for f in os.listdir(REVIEW)
        if f.endswith("-unsorted.json")
    )
    if not files:
        raise SystemExit("No *-unsorted.json under content/review/.")

    # ids already live in a bank: never re-add one, or the same question ends up
    # in two files and question_bank() silently drops whichever it reads second.
    live_ids = set()
    for root, _d, names in os.walk(BANKS):
        for n in names:
            if not n.endswith(".json"):
                continue
            data = imp.load_json(os.path.join(root, n), {})
            for q in (data.get("questions") if isinstance(data, dict) else data) or []:
                if q.get("id"):
                    live_ids.add(q["id"])

    placed = defaultdict(list)
    how_counts = Counter()
    unknown_tags = Counter()
    stuck = defaultdict(list)
    already = 0

    for path in files:
        data = imp.load_json(path, {})
        pool = (data.get("questions") if isinstance(data, dict) else data) or []
        for q in pool:
            if q.get("id") in live_ids:
                already += 1
                continue
            key, how, unknown = resolve(q, maps, topics, matchers, args.min_score)
            for t in unknown:
                unknown_tags[t] += 1
            if not key:
                stuck[path].append(q)
                continue
            subject, topic = key.split("/", 1)
            item = dict(q)
            item["topic"] = topic
            item.pop("subject", None)
            placed[(path, subject)].append(item)
            how_counts[how or "?"] += 1

    total_placed = sum(len(v) for v in placed.values())
    total_stuck = sum(len(v) for v in stuck.values())

    print("\nreview pool")
    for path in files:
        data = imp.load_json(path, {})
        pool = (data.get("questions") if isinstance(data, dict) else data) or []
        print("  %-44s %4d question(s)" % (os.path.relpath(path, ROOT), len(pool)))
    print("\n  already in a bank (skipped)     %5d" % already)
    print("  resolved to a syllabus topic    %5d" % total_placed)
    print("  still unresolved                %5d" % total_stuck)
    if how_counts:
        print("\n  how each one resolved")
        for how, n in how_counts.most_common():
            print("    %-28s %5d" % (how, n))

    by_subject = Counter()
    for (_p, subject), items in placed.items():
        by_subject[subject] += len(items)
    if by_subject:
        print("\n  destination files under content/banks/%s/" % args.bank)
        for subject, n in sorted(by_subject.items(), key=lambda kv: -kv[1]):
            print("    %-34s +%d" % (subject + ".json", n))

    if args.audit_tags:
        print("\n  tags not in go_tag_map.json, most frequent first")
        print("  add the frequent ones to the 'topics' block and rerun\n")
        for t, n in unknown_tags.most_common(30):
            print("    %-38s %d" % (t, n))

    if not args.apply:
        print("\n  dry run: nothing written. Add --apply to merge.\n")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    written = 0
    for (path, subject), items in sorted(placed.items()):
        dest = os.path.join(BANKS, args.bank, "%s.json" % subject)
        if not os.path.isfile(dest):
            print("  skip %s: no such bank file" % os.path.relpath(dest, ROOT))
            continue
        shutil.copy2(dest, dest + ".%s.bak" % stamp)
        data = imp.load_json(dest, {})
        data.setdefault("questions", [])
        have = {q.get("id") for q in data["questions"]}
        for item in items:
            if item.get("id") not in have:
                data["questions"].append(item)
                written += 1
        tmp = dest + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, dest)

    # Rewrite each unsorted file with only what is still stuck, so a second run
    # is a no-op rather than a duplicate merge.
    for path in files:
        data = imp.load_json(path, {})
        remaining = stuck.get(path, [])
        shutil.copy2(path, path + ".%s.bak" % stamp)
        if isinstance(data, dict):
            data["questions"] = remaining
        else:
            data = remaining
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, path)

    print("\n  merged %d question(s) into content/banks/%s/" % (written, args.bank))
    print("  .bak written next to every file touched")
    print("\n  next: press \"Reload from disk\" in the Bank tab, then")
    print("        python tools/bank_defects.py\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())