#!/usr/bin/env python3
"""Extract every question from the GATE Overflow volumes into bank files.

The normal importer is deliberately strict: anything it cannot fully resolve is
held back so a bad parse never reaches your practice sets. That is the right
default, but it means questions whose answer is not printed in the source get
dropped, and the GO volumes have a lot of those.

This tool takes the opposite stance on purpose: **keep everything**, and be loud
about what is missing.

* A question with an answer is written normally and is immediately usable.
* A question without an answer is still written, marked ``answer_pending``, with
  an explanation telling you to look the answer up and fill it in. It is kept out
  of quizzes until you do, so it can never be graded wrongly.
* A question whose topic could not be resolved goes to ``_unsorted.json`` with
  its original GO tags kept, so you can file it by hand.

Usage:

    python tools/extract_go_bank.py                     all three volumes
    python tools/extract_go_bank.py papers/vol1.txt     just one file
    python tools/extract_go_bank.py --out content/banks/go-extracted
    python tools/extract_go_bank.py --stats             report only, write nothing

Once written, fill the missing answers in with:

    python tools/answer_fill.py --next
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import import_questions as imp
import ingest
from core import content as registry
from core import db as database

DEFAULT_OUT = os.path.join(ROOT, "content", "banks", "go-extracted")
DEFAULT_INPUTS = ["filter1_volume1.txt", "filter1_volume2.txt", "filter1_volume3.txt"]

PENDING_NOTE = (
    "Answer not printed in the source PDF. Look this one up (GATE Overflow, the "
    "official key, or a textbook), then run 'python tools/answer_fill.py --next' "
    "to record it. Until then this question is kept out of quizzes so it cannot "
    "be graded against a missing answer."
)

OPTIONS_NOTE = (
    "The answer is known but the option list did not survive text extraction "
    "from the PDF. Open the page listed under 'origin' , copy the options in, and "
    "this question becomes usable. Kept out of quizzes until then."
)


# ---------------------------------------------------------------------------
# Table-of-contents reconstruction
#
# The GO volumes lose their chapter and section headings during text extraction:
# the only place the structure survives is the table of contents, which lists
# every section with the number of questions it holds. Meanwhile each question in
# the body announces its own section in its title line
# ("Balls In Bins: GATE CSE 2018 | Question: 12").
#
# So the TOC is used as a manifest: match each question's title hint back to a
# TOC section, then number it within that section in body order. That rebuilds
# the "1.2.7"-style references the answer-key tables use, which is the only way
# to attach the printed answers, and it also recovers the correct subject.
# ---------------------------------------------------------------------------
def _norm(text):
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def parse_toc(lines):
    """Return (by_name, toc_end). by_name maps a normalised section name to its
    reference, display name, declared question count and owning chapter."""
    section_lines = [i for i, l in enumerate(lines) if imp.GO_SECTION.match(l)]
    if not section_lines:
        return {}, -1
    toc_end = max(section_lines)

    by_name = {}
    chapter = None
    for line in lines[: toc_end + 1]:
        mc = imp.GO_CHAPTER_TITLE.match(line)
        if mc:
            chapter = dict(
                num=mc.group(1), subject=mc.group(2).strip(), group=mc.group(3).strip()
            )
            continue
        ms = imp.GO_SECTION.match(line)
        if ms:
            name = ms.group(2).strip()
            by_name[_norm(name)] = dict(
                ref=ms.group(1), name=name, count=int(ms.group(3)), chapter=chapter
            )
    return by_name, toc_end


def reattach_structure(blocks, toc):
    """Give every block its true section and a reference the answer key can match.

    A block that names its own section is authoritative. One that does not - the
    aptitude questions whose title is the question itself - inherits the section
    of the block before it, because questions from one section are contiguous.
    """
    if not toc:
        return 0, 0
    counters = {}
    current = None
    matched = inherited = 0

    for block in blocks:
        found = toc.get(_norm(block.get("topic_hint")))
        if found:
            current = found
            matched += 1
        elif current:
            inherited += 1
        if not current:
            # Nothing to inherit yet: keep whatever ref the parser produced so the
            # question is still kept, just without a matchable answer reference.
            continue

        ref = current["ref"]
        counters[ref] = counters.get(ref, 0) + 1
        block["ref"] = "%s.%d" % (ref, counters[ref])
        block["section"] = current["name"]
        block["section_ref"] = ref
        # Deliberately drop the chapter. Two of the three volumes list few or no
        # chapter headings, so whatever the parser was holding is stale, and
        # resolve_topic uses the chapter's subject to *veto* a section match. A
        # wrong veto is how every Algorithms question ended up filed under Data
        # Structures. The section name is the most specific signal available, so
        # let it stand on its own.
        block["chapter"] = None
    return matched, inherited


class Args(object):
    """Stand-in for the importer's argparse namespace."""

    def __init__(self, marks=2, kind="pyq", year=None, subject=None, min_score=3.0):
        self.marks = marks
        self.kind = kind
        self.year = year
        self.subject = subject
        self.min_score = min_score
        self.format = "go"


def has_answer(q):
    """True when the question carries something we could actually grade against."""
    if q.get("answer"):
        return True
    if q.get("answer_value") is not None:
        return True
    if q.get("answer_low") is not None and q.get("answer_high") is not None:
        return True
    return False


LETTERS = "ABCDEFGH"


def answer_indices(raw, options):
    """Bank files store answers as zero-based indices, e.g. [1] for option B.

    The parser hands back letters, so convert here. Returns None when the letters
    do not line up with the options that were extracted, which is itself a useful
    signal.
    """
    if raw is None or raw == "":
        return None
    if isinstance(raw, list) and all(isinstance(x, int) for x in raw):
        return raw
    text = str(raw).replace(",", "").replace(" ", "").upper()
    if not text or not all(c in LETTERS for c in text):
        return None
    idx = [LETTERS.index(c) for c in text]
    if options and any(i >= len(options) for i in idx):
        return None
    return idx


def problem_with(q):
    """Name the one thing stopping this question from being servable."""
    opts = q.get("options") or []
    if not opts:
        return None if q.get("answer_value") is not None else "options_missing"
    if len(opts) < 2:
        return "options_missing"
    if q.get("answer") and answer_indices(q.get("answer"), opts) is None:
        return "answer_out_of_range"
    return None


def clean_question(q, pending):
    """Strip the importer's private fields and settle the public shape."""
    out = {}
    for field in (
        "id",
        "topic",
        "kind",
        "type",
        "marks",
        "difficulty",
        "year",
        "text",
        "options",
        "answer",
        "answer_value",
        "answer_low",
        "answer_high",
        "explain",
    ):
        if field in q and q[field] not in (None, ""):
            out[field] = q[field]

    # Convert the parser's letter answer into the index list the bank uses.
    if "answer" in out:
        idx = answer_indices(out["answer"], out.get("options"))
        if idx is None:
            out["answer_from_source"] = out.pop("answer")
        else:
            out["answer"] = idx

    # Infer the type when the parser did not set one.
    if "type" not in out:
        if out.get("options"):
            out["type"] = "msq" if len(out.get("answer") or []) > 1 else "mcq"
        else:
            out["type"] = "nat"

    out.setdefault("marks", 2)
    out.setdefault("difficulty", "medium")
    out.setdefault("kind", "pyq")

    # Provenance, so you can always find the original page.
    src = {}
    if q.get("_source"):
        src["file"] = q["_source"]
    if q.get("_go_ref"):
        src["ref"] = q["_go_ref"]
    if q.get("_go_exam"):
        src["exam"] = q["_go_exam"]
    if q.get("_go_section"):
        src["section"] = q["_go_section"]
    if q.get("_go_tags"):
        src["tags"] = q["_go_tags"]
    if src:
        out["origin"] = src

    problem = problem_with(q)

    if pending:
        out["answer_pending"] = True
        out["answer"] = ""
        out["explain"] = PENDING_NOTE
    elif problem == "options_missing":
        # The answer exists but there is nothing to attach it to. Marking it as an
        # options problem rather than an answer problem tells you which fix it
        # needs, and keeps it out of quizzes either way.
        out["needs_fix"] = "options_missing"
        out["explain"] = OPTIONS_NOTE
        out["answer_from_source"] = out.pop("answer", "")
        out["options"] = out.get("options") or []
    elif problem == "answer_out_of_range":
        out["needs_fix"] = "answer_out_of_range"
        out["explain"] = (
            "The printed answer does not line up with the options that "
            "were extracted, so one of the two is wrong. Check the "
            "source page under 'origin' before using this question."
        )
        out["answer_from_source"] = out.pop("answer", "")
    elif not out.get("explain"):
        out["explain"] = ""

    return out


def build_all(path, args, matchers, topics):
    """Parse one volume, rebuild its structure, then classify every block.

    This mirrors import_questions.build_go but keeps questions the importer would
    discard, and runs the table-of-contents reconstruction first so topics and
    answers land correctly.
    """
    topic_map, subject_map, chapter_map, ignore = imp.load_tag_map()
    stem = re.sub(
        r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(path))[0].lower()
    ).strip("-")

    lines = imp.clean_lines(imp.repair_mojibake(imp.read_input(path)))
    toc, toc_end = parse_toc(lines)
    blocks, key_answers = imp.parse_go_document(lines)
    matched, inherited = reattach_structure(blocks, toc)

    print(
        "  %d lines, %d blocks, %d answer-key entries, %d TOC sections"
        % (len(lines), len(blocks), len(key_answers), len(toc))
    )
    print(
        "  structure: %d block(s) named their section, %d inherited it"
        % (matched, inherited)
    )

    out = []
    attached = 0
    for block in blocks:
        parsed = imp.parse_go_body(block)
        if len(parsed["text"]) < 25:
            continue

        key, subject, source, _unknown = imp.resolve_topic(
            block, parsed, topic_map, subject_map, chapter_map, ignore, topics
        )
        score = None
        if key is None:
            key, _runner, score, _, problem = imp.classify(
                parsed["text"],
                parsed["options"],
                matchers,
                topics,
                subject or args.subject,
                args.min_score,
            )
            source = "keyword" if key and not problem else None
            if problem:
                key = None

        marks = args.marks
        for tag in parsed["tags"]:
            if tag in imp.GO_MARK_TAG:
                marks = imp.GO_MARK_TAG[tag]
                break

        year = None
        ym = imp.GO_YEAR.search(" ".join(parsed["tags"]) + " " + block.get("exam", ""))
        if ym:
            year = int(ym.group(1))

        q = dict(
            id="%s-%s" % (stem, str(block.get("ref", "")).replace(".", "-")),
            kind=args.kind,
            difficulty=(
                "hard"
                if "difficult" in parsed["tags"]
                else ("easy" if "easy" in parsed["tags"] else "medium")
            ),
            marks=marks or 2,
            text=parsed["text"],
            options=parsed["options"],
            explain="",
            _source=os.path.basename(path),
            _go_ref=block.get("ref", ""),
            _go_exam=block.get("exam", ""),
            _tag_source=source or "none",
        )
        if block.get("section"):
            q["_go_section"] = block["section"]
        if year or args.year:
            q["year"] = year or args.year
        if parsed["tags"]:
            q["_go_tags"] = parsed["tags"][:8]
        if score is not None:
            q["_score"] = round(score, 1)

        raw = key_answers.get(block.get("ref"))
        imp.apply_answer(q, raw)
        if raw:
            attached += 1

        if key:
            q["subject"] = topics[key]["subject"]
            q["topic"] = topics[key]["topic"]
        out.append(q)

    print("  answers attached: %d of %d" % (attached, len(out)))
    return out


def extract(paths, args, stats_only=False):
    topics = imp.load_syllabus()
    # compile_lexicon returns (matchers, topics_without_keywords)
    matchers, _missing_lexicon = imp.compile_lexicon(topics)

    by_subject = defaultdict(list)
    unsorted = []
    seen = {}
    counts = Counter()
    per_file = {}

    for path in paths:
        if not os.path.isfile(path):
            print("  skipped (not found): %s" % path)
            continue
        print("\n%s" % os.path.relpath(path, ROOT))

        found = build_all(path, args, matchers, topics)
        per_file[os.path.basename(path)] = len(found)

        for q in found:
            fingerprint = ingest.text_hash(q)
            if fingerprint in seen:
                counts["duplicate"] += 1
                continue
            seen[fingerprint] = q.get("id")

            pending = not has_answer(q)
            record = clean_question(q, pending)
            if pending:
                counts["pending"] += 1
            elif record.get("needs_fix"):
                counts[record["needs_fix"]] += 1
            else:
                counts["usable"] += 1
            subject = q.get("subject")
            if subject and q.get("topic"):
                by_subject[subject].append(record)
                counts["filed"] += 1
            else:
                # Keep the GO tags visible; they are the best clue for filing.
                record["_note"] = (
                    "Topic could not be resolved automatically. "
                    "Set 'topic' to a slug from content/syllabus.json "
                    "and move this entry into that subject's file."
                )
                unsorted.append(record)
                counts["unsorted"] += 1

    return by_subject, unsorted, counts, per_file


def write_bank(by_subject, unsorted, out_dir, source_slug="go-pdfs"):
    os.makedirs(out_dir, exist_ok=True)
    written = {}

    for subject, questions in sorted(by_subject.items()):
        payload = {
            "subject": subject,
            "source": {
                "slug": source_slug,
                "name": "GATE Overflow PDFs (volumes 1-3)",
                "kind": "release",
                "url": "https://github.com/GATEOverflow/GO-PDFs/releases",
                "licence_note": "Public GitHub release assets, extracted locally.",
            },
            "note": (
                "Extracted automatically from the GO volumes. Entries with "
                '"answer_pending": true have no answer in the source; they '
                "are excluded from quizzes until an answer is filled in."
            ),
            "questions": questions,
        }
        path = os.path.join(out_dir, "%s.json" % subject)
        ingest.write_json_atomic(path, payload)
        pending = sum(1 for q in questions if q.get("answer_pending"))
        broken = sum(1 for q in questions if q.get("needs_fix"))
        written[subject] = (len(questions), pending, broken)

    if unsorted:
        path = os.path.join(out_dir, "_unsorted.json")
        ingest.write_json_atomic(
            path,
            {
                "subject": "",
                "note": (
                    "These questions were extracted successfully but their topic "
                    "could not be matched to content/syllabus.json. Give each one a "
                    "'topic' slug and move it into the matching subject file. They "
                    "are ignored by the app until then."
                ),
                "questions": unsorted,
            },
        )
        written["_unsorted"] = (
            len(unsorted),
            sum(1 for q in unsorted if q.get("answer_pending")),
            sum(1 for q in unsorted if q.get("needs_fix")),
        )
    return written


def annotate_from_validator(out_dir):
    """Second pass: let the app's own validator decide what is servable.

    The extractor cannot reliably predict this on its own, because the bank loader
    normalises answers, infers types and resolves topics as it reads a file. So
    write the files first, load them through the real registry, and then record
    the verdict back into each entry. That way the flags in the file can never
    disagree with what the app actually does.
    """
    registry.invalidate()
    bank = (
        registry.question_bank(reload=True)
        if "reload" in registry.question_bank.__code__.co_varnames
        else registry.question_bank()
    )

    verdicts = {}
    for qid, q in bank.items():
        if "go-extracted" not in str(q.get("file", "")):
            continue
        verdicts[qid] = registry.validate_question(q)

    counts = Counter()
    for name in sorted(os.listdir(out_dir)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(out_dir, name)
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)

        changed = False
        for q in payload.get("questions", []):
            issues = verdicts.get(q.get("id"))
            if issues is None:
                # Not loaded at all, which for _unsorted.json is expected.
                counts["not_loaded"] += 1
                continue
            if q.get("answer_pending"):
                counts["pending"] += 1
                continue
            if issues:
                reason = "; ".join(issues)
                if q.get("needs_fix") != reason:
                    q["needs_fix"] = reason
                    changed = True
                if not q.get("explain") or q["explain"] == OPTIONS_NOTE:
                    q["explain"] = (
                        "Not servable yet - %s. The answer from the source is kept in "
                        "'answer_from_source' where one was printed; fix the fields "
                        "listed and this question becomes usable." % reason
                    )
                    changed = True
                counts["needs_fix"] += 1
            else:
                if q.pop("needs_fix", None) is not None:
                    changed = True
                counts["usable"] += 1

        if changed:
            ingest.write_json_atomic(path, payload)
    return counts


def main():
    ap = argparse.ArgumentParser(
        description="Extract every question from the GO volumes, answered or not."
    )
    ap.add_argument(
        "inputs",
        nargs="*",
        help="text or PDF files (default: the three GO volumes in papers/)",
    )
    ap.add_argument("--out", default=DEFAULT_OUT, help="output directory")
    ap.add_argument(
        "--marks",
        type=int,
        default=2,
        choices=(1, 2),
        help="marks to assume when the source does not say (default 2)",
    )
    ap.add_argument(
        "--min-score",
        type=float,
        default=3.0,
        help="keyword classification threshold (default 3.0)",
    )
    ap.add_argument("--kind", default="pyq", choices=("pyq", "dpp"))
    ap.add_argument("--stats", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    paths = args.inputs or [os.path.join(ROOT, "papers", n) for n in DEFAULT_INPUTS]
    paths = [p if os.path.isabs(p) else os.path.join(ROOT, p) for p in paths]

    print("\nGO bank extraction")
    print("keeping every question, including ones with no printed answer.")

    build_args = Args(marks=args.marks, kind=args.kind, min_score=args.min_score)
    by_subject, unsorted, counts, per_file = extract(paths, build_args)

    total = (
        counts["usable"]
        + counts["pending"]
        + counts["options_missing"]
        + counts["answer_out_of_range"]
    )
    print("\n" + "-" * 66)
    print("  per file")
    for name, n in per_file.items():
        print("    %-34s %5d block(s)" % (name, n))
    print("\n  %-34s %5d" % ("unique questions kept", total))
    print("  %-34s %5d" % ("usable right now", counts["usable"]))
    print("  %-34s %5d" % ("answer pending (look it up)", counts["pending"]))
    print("  %-34s %5d" % ("options lost in extraction", counts["options_missing"]))
    print("  %-34s %5d" % ("answer/option mismatch", counts["answer_out_of_range"]))
    print("  %-34s %5d" % ("duplicates across volumes dropped", counts["duplicate"]))
    print("  %-34s %5d" % ("filed under a syllabus topic", counts["filed"]))
    print("  %-34s %5d" % ("topic unresolved (_unsorted.json)", counts["unsorted"]))
    print("-" * 66)

    if args.stats:
        print("\n  --stats given: nothing written.\n")
        return 0

    written = write_bank(by_subject, unsorted, args.out)
    print("\n  wrote %s/" % os.path.relpath(args.out, ROOT))
    print("    %-30s %7s %8s %8s" % ("file", "total", "pending", "needsfix"))
    for subject, (n, pending, broken) in sorted(written.items()):
        print("    %-30s %7d %8d %8d" % (subject + ".json", n, pending, broken))

    # Register the source so imports and the Bank tab can attribute these.
    conn = database.init()
    try:
        registry.seed(conn)
        ingest.register_source(
            conn,
            "go-pdfs",
            "GATE Overflow PDFs (volumes 1-3)",
            kind="release",
            url="https://github.com/GATEOverflow/GO-PDFs/releases",
            licence_note="Public GitHub release assets, extracted locally.",
            trust=0.8,
        )
    finally:
        conn.close()

    verdict = annotate_from_validator(args.out)
    print("\n  verified against the app's own validator:")
    print("    %-32s %5d" % ("servable right now", verdict["usable"]))
    print("    %-32s %5d" % ("answer pending (look it up)", verdict["pending"]))
    print("    %-32s %5d" % ("needs a field fixed", verdict["needs_fix"]))
    if verdict["not_loaded"]:
        print("    %-32s %5d" % ("unsorted, not loaded yet", verdict["not_loaded"]))

    registry.invalidate()
    stats = registry.bank_stats(reload=True)
    print(
        "\n  bank now: %d questions, %d%% usable, %d%% topic coverage"
        % (stats["total"], stats["health_pct"], stats["coverage_pct"])
    )

    print("\n  next: python tools/answer_fill.py --next\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
