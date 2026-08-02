#!/usr/bin/env python3
"""Turn official GATE papers into question-bank JSON, with topics assigned.

WHAT THIS DOES

  1. Pulls text out of a paper (PDF or already-extracted .txt).
  2. Splits it into numbered question blocks and finds the (A)-(D) options.
  3. Merges the official answer key so every question has a real answer.
  4. Tags each question with a subject and topic slug from content/syllabus.json,
     by scoring its text against content/topic_keywords.json.
  5. Writes one file per subject into content/questions/, merged with anything
     already there. Restart the app and the questions are live.

Anything it is not confident about goes to content/review-queue.json, which the
app does NOT load, so a bad guess can never leak into a quiz. Clear that queue
with --review.

USAGE

  # see what it would do, write nothing (use this first)
  python tools/import_questions.py papers/gate2024-cs.pdf --year 2024 --dry-run

  # real import with the official key
  python tools/import_questions.py papers/gate2024-cs.pdf \
      --answers papers/gate2024-cs-key.pdf --year 2024

  # work through whatever needs a human
  python tools/import_questions.py --review

  # sanity-check a file you wrote or edited by hand
  python tools/import_questions.py --validate content/questions/operating-systems.json

PDF TEXT EXTRACTION

  Pure stdlib cannot read PDFs. In order of preference this uses:
    - the `pdftotext` command (poppler-utils; apt install poppler-utils)
    - the `pypdf` module          (pip install pypdf)
    - the `pdfplumber` module     (pip install pdfplumber)
  If none is available, run pdftotext -layout yourself and feed the .txt in.
  The .txt path needs no dependencies at all.

HONEST LIMITS

  Extraction from PDFs is messy. Anything that lives in a figure, a circuit
  diagram, a matrix, or a rendered equation will not survive as text - those
  questions get flagged rather than silently mangled. On a clean paper expect
  most questions to come through usable and a minority to need editing. Budget
  an evening per paper the first time, less once you have tuned the keywords.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

try:
    import ingest  # when run as tools/import_questions.py
except ImportError:  # pragma: no cover
    from tools import ingest  # when imported as a module
from core import content as registry
from core import db as database

CONTENT = os.path.join(ROOT, "content")
QUESTIONS_DIR = os.path.join(CONTENT, "questions")
REVIEW_PATH = os.path.join(CONTENT, "review-queue.json")

STRONG_POINTS = 3.0
WEAK_POINTS = 1.0
NAME_POINTS = 0.5
DEFAULT_MIN_SCORE = 3.0
AMBIGUOUS_MARGIN = 1.0

NAME_STOPWORDS = {
    "and",
    "the",
    "of",
    "in",
    "to",
    "for",
    "with",
    "from",
    "on",
    "by",
    "or",
    "its",
    "into",
    "basics",
    "general",
    "basic",
    "other",
    "using",
    "based",
}

FIGURE_HINTS = (
    "figure",
    "diagram",
    "circuit shown",
    "shown below",
    "shown in the",
    "following graph",
    "following circuit",
    "following tree",
    "given below",
    "as shown",
    "the table below",
    "following table",
)


# ===========================================================================
# content loading
# ===========================================================================
def load_json(path, fallback=None):
    if not os.path.isfile(path):
        return fallback
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_syllabus():
    data = load_json(os.path.join(CONTENT, "syllabus.json"), {"subjects": []})
    topics = {}
    for subj in data.get("subjects", []):
        for t in subj.get("topics", []):
            topics["%s/%s" % (subj["slug"], t["slug"])] = dict(
                subject=subj["slug"],
                subject_name=subj["name"],
                topic=t["slug"],
                topic_name=t["name"],
            )
    return topics


def compile_lexicon(topics):
    """Build (regex, points, key) triples once, so scoring is a single pass."""
    raw = load_json(os.path.join(CONTENT, "topic_keywords.json"), {})
    matchers = []
    seen_keys = set()

    def add(key, phrase, points):
        phrase = phrase.strip().lower()
        if not phrase:
            return
        # \b only behaves for alphanumeric edges. Phrases with punctuation
        # ("count(*)", "0/1 knapsack", "f'(x)") fall back to substring search.
        if re.match(r"^[a-z0-9]", phrase) and re.search(r"[a-z0-9]$", phrase):
            pattern = r"\b" + re.escape(phrase).replace(r"\ ", r"\s+") + r"\b"
        else:
            pattern = re.escape(phrase).replace(r"\ ", r"\s+")
        matchers.append((re.compile(pattern), points, key))

    for key, spec in raw.items():
        if key.startswith("_") or not isinstance(spec, dict):
            continue
        if key not in topics:
            print("  warning: topic_keywords.json has unknown key %r - ignored" % key)
            continue
        seen_keys.add(key)
        for phrase in spec.get("strong", []):
            add(key, phrase, STRONG_POINTS)
        for phrase in spec.get("weak", []):
            add(key, phrase, WEAK_POINTS)

    # every topic also matches on the words in its own name
    for key, meta in topics.items():
        for word in re.findall(r"[a-z0-9]+", meta["topic_name"].lower()):
            if len(word) > 3 and word not in NAME_STOPWORDS:
                add(key, word, NAME_POINTS)

    missing = sorted(set(topics) - seen_keys)
    return matchers, missing


# ===========================================================================
# text extraction
# ===========================================================================
def pdf_to_text(path):
    if shutil.which("pdftotext"):
        try:
            out = subprocess.run(
                ["pdftotext", "-layout", "-enc", "UTF-8", path, "-"],
                capture_output=True,
                timeout=180,
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.decode("utf-8", "replace")
        except (subprocess.SubprocessError, OSError):
            pass
    try:
        import pypdf

        reader = pypdf.PdfReader(path)
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except ImportError:
        pass
    except Exception as exc:
        print("  pypdf failed on this file: %s" % exc)
    try:
        import pdfplumber

        with pdfplumber.open(path) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages)
    except ImportError:
        pass
    except Exception as exc:
        print("  pdfplumber failed on this file: %s" % exc)

    raise SystemExit(
        "Cannot read PDFs: no pdftotext binary, no pypdf, no pdfplumber.\n"
        "  Either:  pip install pypdf\n"
        "  Or:      pdftotext -layout '%s' out.txt   and import out.txt instead" % path
    )


def read_input(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return pdf_to_text(path)
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


# ===========================================================================
# segmentation
# ===========================================================================
# Always junk, whatever the line looks like.
NOISE_ANY = [
    re.compile(r"^\s*page\s*\d+\s*$", re.I),
    # "3 / 12" is a page marker; "1/3" is an answer option. Requiring spaces
    # around the slash keeps fractions - which are most of the options in
    # probability and aptitude questions - from being deleted as noise.
    re.compile(r"^\s*\d{1,3}\s+/\s+\d{1,3}\s*$"),
    re.compile(r"^\s*\d{1,3}\s*$"),
    re.compile(r"copyright|all rights reserved", re.I),
    re.compile(r"do not (open|write)", re.I),
]

# Running headers and footers. These only count on a SHORT line: "GATE 2024" at
# the top of a page is noise, but "gate2015-set1 operating-system deadlock" is a
# GO tag row and carries the topic, so it must survive.
NOISE_HEADER = [
    re.compile(r"gate\s*20\d\d", re.I),
    re.compile(r"organi[sz]ing institute", re.I),
    re.compile(r"graduate aptitude test", re.I),
    re.compile(r"computer science and information technology", re.I),
    re.compile(r"^\s*(cs|cs1|cs2|csit)\s*$", re.I),
    re.compile(r"^\s*general aptitude\s*$", re.I),
    re.compile(r"^\s*technical section\s*$", re.I),
]
HEADER_MAX_LEN = 60

MARKS_ONE = re.compile(r"carry\s+one\s+mark", re.I)
MARKS_TWO = re.compile(r"carry\s+two\s+marks", re.I)
INSTRUCTION = re.compile(
    r"carry\s+(one|two)\s+marks?|^\s*Q\.?\s*\d+\s*[-\u2013to]+\s*Q\.?\s*\d+", re.I
)

# Papers number questions as "Q.1", "Q 1.", "Q1" or plain "1." - the dot can sit
# on either side of the digit, so both shapes are matched explicitly.
Q_START = re.compile(
    r"^\s*(?:"
    r"Q\s*\.?\s*(\d{1,3})\s*[\.\)]?"  # Q.1   Q1.   Q 1
    r"|(\d{1,3})\s*[\.\)]"  # 1.    1)
    r")\s+(?=\S)"
)
OPT_LINE = re.compile(r"^\s*\(?\s*([A-Da-d])\s*[\)\.\:]\s+(.*)$")


def clean_lines(text):
    out = []
    for line in text.replace("\r", "").split("\n"):
        line = line.replace("\u00a0", " ").rstrip()
        if not line.strip():
            out.append("")
            continue
        if any(p.search(line) for p in NOISE_ANY):
            continue
        # A GO tag row can contain "gate2015-set1", which would otherwise be
        # mistaken for a page header. Tag rows carry the topic, so keep them.
        if len(line) <= HEADER_MAX_LEN and not looks_like_tag_line(line):
            if any(p.search(line) for p in NOISE_HEADER):
                continue
        out.append(line)
    return out


def segment(lines):
    """Yield (number, marks, [lines]) for each numbered question found."""
    blocks = []
    current = None
    marks = 1
    for line in lines:
        if MARKS_ONE.search(line):
            marks = 1
        elif MARKS_TWO.search(line):
            marks = 2

        m = Q_START.match(line)
        if m and not INSTRUCTION.search(line):
            num = int(m.group(1) or m.group(2))
            # A "number." at the start of a continuation line is usually a list
            # item, not a new question. Only start a block if the number moves
            # forward from the last one.
            if current is None or num > current["num"]:
                if current:
                    blocks.append(current)
                current = dict(num=num, marks=marks, lines=[line[m.end() :].strip()])
                continue
        if current is not None:
            current["lines"].append(line.strip())
    if current:
        blocks.append(current)
    return blocks


def parse_block(block):
    """Split a block into stem text and options."""
    stem, options, current = [], [], None
    next_idx = 0
    for line in block["lines"]:
        m = OPT_LINE.match(line)
        if m:
            # Only treat it as a new option if it is the letter we are waiting
            # for. That keeps "(A) ..." inside a question stem from being read
            # as an option, and stops a stray letter from resetting the run.
            if m.group(1).upper() == chr(ord("A") + next_idx):
                if current is not None:
                    options.append(" ".join(current).strip())
                current = [m.group(2).strip()]
                next_idx += 1
                continue
        if current is not None:
            if line:
                current.append(line)
        else:
            stem.append(line)
    if current is not None:
        options.append(" ".join(current).strip())

    text = re.sub(r"\s+", " ", " ".join(x for x in stem if x)).strip()
    options = [re.sub(r"\s+", " ", o).strip() for o in options if o.strip()]
    return text, options


# ===========================================================================
# answer keys
# ===========================================================================
LETTERS = re.compile(r"^[A-D](?:\s*[,;/&]?\s*[A-D])*$", re.I)
RANGE = re.compile(r"^(-?\d+(?:\.\d+)?)\s*(?:to|-|\u2013)\s*(-?\d+(?:\.\d+)?)$", re.I)
NUMBER = re.compile(r"^-?\d+(?:\.\d+)?$")


def load_answers(path):
    """Lenient key reader. Handles the official tabular PDF, CSV and JSON."""
    if not path:
        return {}
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        raw = load_json(path, {})
        return {str(k): str(v) for k, v in raw.items()}

    text = read_input(path)
    answers = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line or re.search(r"q\.?\s*no|question type|marks", line, re.I):
            continue
        # first standalone integer is the question number
        head = re.match(r"^\D*?(\d{1,3})\b(.*)$", line)
        if not head:
            continue
        num, rest = head.group(1), head.group(2)
        tokens = [t for t in re.split(r"[\s|,;\t]+", rest.strip()) if t]
        found = None
        # scan right to left: keys sit near the end of the row
        for tok in reversed(tokens):
            tok = tok.strip(".:()")
            if not tok or tok.upper() in ("MCQ", "MSQ", "NAT", "CS", "GA", "1", "2"):
                continue
            if LETTERS.match(tok) or NUMBER.match(tok):
                found = tok.upper()
                break
        # a range is spread across tokens: "6.4 to 6.6"
        joined = " ".join(tokens)
        rng = RANGE.search(joined)
        if rng:
            found = "%s to %s" % (rng.group(1), rng.group(2))
        if found:
            answers[num] = found
    return answers


def apply_answer(q, raw):
    """Attach the answer and settle the question type."""
    if raw is None:
        q["_needs_review"] = True
        q["_review_reason"] = "no answer key entry"
        q["type"] = "mcq" if len(q.get("options", [])) >= 2 else "nat"
        q["answer"] = []
        return q

    raw = str(raw).strip()
    rng = RANGE.match(raw)
    if rng:
        lo, hi = float(rng.group(1)), float(rng.group(2))
        q["type"] = "nat"
        q["answer_value"] = round((lo + hi) / 2.0, 6)
        q["tolerance"] = round(abs(hi - lo) / 2.0, 6)
        q.pop("options", None)
        return q
    if NUMBER.match(raw):
        q["type"] = "nat"
        q["answer_value"] = float(raw)
        q["tolerance"] = 0.01 if "." in raw else 0
        q.pop("options", None)
        return q
    if LETTERS.match(raw):
        idx = sorted({ord(c.upper()) - 65 for c in re.findall(r"[A-Da-d]", raw)})
        q["type"] = "msq" if len(idx) > 1 else "mcq"
        q["answer"] = idx
        if q.get("options") and max(idx) >= len(q["options"]):
            q["_needs_review"] = True
            q["_review_reason"] = "answer %s but only %d options extracted" % (
                raw,
                len(q["options"]),
            )
        return q

    q["_needs_review"] = True
    q["_review_reason"] = "could not read answer %r" % raw
    q["answer"] = []
    return q


# ===========================================================================
# classification  --  this is what makes topic-filtered quizzes work
# ===========================================================================
def classify(
    text, options, matchers, topics, force_subject=None, min_score=DEFAULT_MIN_SCORE
):
    blob = (text + " " + " ".join(options)).lower()
    blob = re.sub(r"\s+", " ", blob)

    scores = defaultdict(float)
    hits = defaultdict(list)
    for pattern, points, key in matchers:
        if force_subject and topics[key]["subject"] != force_subject:
            continue
        if pattern.search(blob):
            scores[key] += points
            if points >= STRONG_POINTS:
                hits[key].append(pattern.pattern)

    if not scores:
        return None, None, 0.0, None, "no keyword matched"

    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    top_key, top_score = ranked[0]
    runner = ranked[1] if len(ranked) > 1 else None

    if top_score < min_score:
        return (
            top_key,
            runner,
            top_score,
            hits.get(top_key),
            "best score %.1f below threshold %.1f" % (top_score, min_score),
        )
    if runner and (top_score - runner[1]) < AMBIGUOUS_MARGIN:
        return (
            top_key,
            runner,
            top_score,
            hits.get(top_key),
            "ambiguous: %s %.1f vs %s %.1f" % (top_key, top_score, runner[0], runner[1]),
        )
    return top_key, runner, top_score, hits.get(top_key), None


# ===========================================================================
# GATE Overflow book format
# ===========================================================================
# GO books are generated from gateoverflow.in HTML, so they look nothing like an
# official paper: questions sit under hierarchical headings, options use "A."
# rather than "(A)", and each question carries GO's own tag list. Those tags are
# the reason this path exists - a real tag beats a keyword guess every time.
# A GO book is a three-level hierarchy, and that hierarchy is a BETTER source of
# topic than the tag row, because it is always present:
#
#   1 Discrete Mathematics: Combinatory (51)   <- chapter: subject + topic group
#     1.7 Recurrence Relation (7)              <- section: the topic itself
#       1.7.1 ...                              <- an actual question
#     Answer Keys                              <- answers for the whole chapter
#
# So topic is resolved section-first, then chapter, then tags, then keywords.
# Real GO extraction, learned from an actual volume:
#
#   3 Discrete Mathematics: Mathematical Logic (78)   <- chapter
#     3.1 First Order Logic (35)                      <- section = the topic
#       First Order Logic: GATE CSE 2018 | Question: 28   <- a question STARTS here
#       ...stem...
#       A / ". " / text        <- options are split over three lines each
#       gatecse-2018 / mathematical-logic / two-marks  <- one tag per line
#       Answer key                                    <- per-question marker only
#     Answer Keys                                     <- chapter-end, real values
#
# Two things to note. Questions are not numbered in the body, so a running index
# per section reproduces the 3.1.1 / 3.1.2 refs the answer key uses. And "Answer
# key" (singular) is a per-question link while "Answer Keys" (plural) is the
# section that actually holds the answers - they must not be confused.
GO_CHAPTER_TITLE = re.compile(
    r"^\s*(\d+)\s+([A-Z][^:]{3,60}):\s*(.{2,70}?)\s*\((\d+)\)\s*$"
)
GO_SECTION = re.compile(r"^\s*(\d+\.\d+)\s+(.{2,70}?)\s*\((\d+)\)\s*$")
GO_Q_TITLE = re.compile(
    r"^\s*(.{2,70}?):\s*"
    r"((?:GATE|ISRO|TIFR|UGC\s*NET|NIELIT|CMI|JEST|BARC|DRDO)[^|]{0,40}?)"
    r"\s*\|\s*Question:?\s*(\S+)\s*$",
    re.I,
)
GO_ANSWER_KEYS = re.compile(r"^\s*answer\s+keys\s*$", re.I)  # plural: real answers
GO_ANSWER_MARKER = re.compile(r"^\s*answer\s+key\s*$", re.I)  # singular: just a link
# A question heading, in any of the shapes GO uses: "Topic: GATE CSE 2018 |
# Question: 28", "Counting: Kenneth Rosen Edition 7 Exercise 6.1 Question 8",
# "Graph Theory: TIFR 2019 | Part A | Question: 5".
GO_TITLE_HINT = re.compile(
    r"^\s*[^:]{2,70}:\s*\S.*?"
    r"(?:\|\s*Question|Question\s*[:.]?\s*\d|Exercise|\b(?:19|20)\d\d\b)",
    re.I,
)
GO_OPT_ALONE = re.compile(r"^\s*\(?([A-D])\)?\s*\.?\s*$")
GO_DOT_ONLY = re.compile(r"^\s*[.\u2024\u00b7]\s*$")
GO_TAG_ALONE = re.compile(r"^\s*([a-z][a-z0-9]*(?:-[a-z0-9&]+)*)\s*$")
GO_KEY_PAIR = re.compile(
    r"(\d+\.\d+\.\d+)\s+("
    r"[A-D](?:\s*[,;&]\s*[A-D])*"
    r"|-?\d+(?:\.\d+)?(?:\s*(?:to|\u2013|-)\s*-?\d+(?:\.\d+)?)?"
    r"|[A-Za-z0-9]*[()+*/^][A-Za-z0-9()+\-*/^.]*"
    r")(?=\s|$)"
)
GO_REF_ALONE = re.compile(r"^\s*(\d+\.\d+\.\d+)\s*$")
GO_VAL_ALONE = re.compile(
    r"^\s*([A-D](?:\s*[,;&]\s*[A-D])*"
    r"|-?\d+(?:\.\d+)?(?:\s*(?:to|\u2013|-)\s*-?\d+(?:\.\d+)?)?)\s*$"
)
GO_STOP = re.compile(r"^\s*(contributors|index|about the (book|author))\s*$", re.I)
GO_SKIP_HEADING = re.compile(
    r"^\s*(topic-wise key concepts|quick formula reference|important tips for gate"
    r"|subject overview|table of contents|definition and core idea"
    r"|important formulas.*|key properties.*|common pitfalls.*"
    r"|standard problem-solving.*|problem-solving techniques.*)\s*:?\s*$",
    re.I,
)
GO_YEAR = re.compile(r"\b(?:gate|isro|tifr|ugcnet|nielit)[a-z]*[\s-]*(\d{4})\b", re.I)
GO_MARK_TAG = {"one-mark": 1, "1-mark": 1, "two-marks": 2, "2-marks": 2}
GO_NOISE = re.compile(r"^\s*[\u2600-\u27bf\ufe0f]+\s*$")


def looks_like_tag_line(line):
    """Protects tag rows from the page-header noise rules. Handles both shapes:
    several slugs on one line, or a single slug alone on its own line."""
    stripped = line.strip()
    if GO_TAG_ALONE.match(stripped) and "-" in stripped:
        return True
    tokens = re.findall(r"\b[a-z][a-z0-9]*(?:-[a-z0-9&]+)+\b", stripped.lower())
    return len(tokens) >= 2 and len(" ".join(tokens)) > len(stripped) * 0.5


def map_lookup(table, key, subject):
    """A map value is either a slug, or a dict keyed by subject for tags that
    mean different things in different chapters."""
    value = table.get(key)
    if value is None:
        return None
    if isinstance(value, dict):
        if subject and subject in value:
            return value[subject]
        return value.get("_default")
    return value


def slugify(text):
    text = text.replace("&", " ")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_tag_map():
    raw = load_json(os.path.join(CONTENT, "go_tag_map.json"), {})
    return (
        raw.get("topics") or {},
        raw.get("subjects") or {},
        raw.get("chapters") or {},
        set(raw.get("ignore") or []),
    )


def repair_mojibake(text):
    """pdftotext writes UTF-8; some toolchains hand it back as Latin-1."""
    if (
        text.count("\u00e2\u0080")
        + text.count("\u00c3\u00a9")
        + text.count("\u00ef\u00ac")
        > 3
    ):
        try:
            return text.encode("latin-1", "ignore").decode("utf-8", "ignore")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return text
    return text


def parse_go_document(lines):
    """Segment on the per-question "Answer key" marker.

    Titles are not a reliable anchor: only some are "Topic: GATE CSE 2018 |
    Question: 28", the rest are Rosen exercises, test-series questions and so on.
    But every question ends with an "Answer key" link, so a question is simply
    the text between a section heading (or the previous marker) and the next
    marker. That is numbering- and title-independent, and it keeps the running
    per-section index in step with the refs the answer key uses.
    """
    questions, answers = [], {}
    chapter = section = section_ref = None
    seq = 0
    current = None
    in_answers = False
    pending_ref = None

    def start():
        nonlocal current
        current = dict(
            lines=[],
            chapter=chapter,
            section=section,
            section_ref=section_ref,
            title="",
            topic_hint="",
            exam="",
            paper_q="",
        )

    def flush():
        nonlocal current, seq
        if not current:
            return
        body = [l for l in current["lines"] if l.strip()]
        if not body:
            current = None
            return
        # Only real questions may consume a sequence number. The "Topic-wise Key
        # Concepts" prose and the table of contents also form blocks, and if they
        # took a number every ref after them would drift out of step with the
        # answer key. A question always carries tags, options, or a heading line.
        has_tags = any(GO_TAG_ALONE.match(l) and "-" in l for l in body)
        has_opts = sum(1 for l in body if GO_OPT_ALONE.match(l)) >= 2
        titled = bool(GO_TITLE_HINT.match(body[0]))
        if not (has_tags or has_opts or titled):
            current = None
            return

        seq += 1
        if True:
            ref = current["section_ref"]
            current["ref"] = "%s.%d" % (ref, seq) if ref else "x%d" % seq
            title = body[0].strip()
            current["title"] = title
            # "First Order Logic: GATE CSE 2018 | Question: 28" -> hint + exam
            if ":" in title:
                head, tail = title.split(":", 1)
                if 2 < len(head) < 70:
                    current["topic_hint"] = head.strip()
                    current["exam"] = tail.strip()
            m = re.search(r"Question:?\s*(\S+)\s*$", title)
            if m:
                current["paper_q"] = m.group(1)
            current["lines"] = [l for l in current["lines"] if l.strip() != title]
            questions.append(current)
        current = None

    for line in lines:
        if GO_STOP.match(line):
            flush()
            in_answers = False
            continue
        if GO_NOISE.match(line) or GO_SKIP_HEADING.match(line):
            continue

        is_marker = bool(GO_ANSWER_MARKER.match(line))
        is_title = bool(GO_TITLE_HINT.match(line))
        is_chapter = bool(GO_CHAPTER_TITLE.match(line))
        is_section = bool(GO_SECTION.match(line))

        # Never stay stuck inside an answer-key block: any of these ends it.
        if in_answers and (is_marker or is_title or is_chapter or is_section):
            in_answers = False

        if in_answers:
            pairs = GO_KEY_PAIR.findall(line)
            if pairs:
                for ref, raw in pairs:
                    answers[ref] = raw.strip()
                continue
            m = GO_REF_ALONE.match(line)
            if m:
                pending_ref = m.group(1)
                continue
            if pending_ref:
                m = GO_VAL_ALONE.match(line)
                if m:
                    answers[pending_ref] = m.group(1).strip()
                    pending_ref = None
                    continue
            continue

        if is_marker:
            flush()
            start()
            continue

        if GO_ANSWER_KEYS.match(line):
            flush()
            in_answers = True
            pending_ref = None
            continue

        if is_chapter:
            m = GO_CHAPTER_TITLE.match(line)
            flush()
            chapter = dict(
                num=m.group(1),
                subject=m.group(2).strip(),
                group=m.group(3).strip(),
                count=int(m.group(4)),
            )
            section = section_ref = None
            seq = 0
            start()
            continue

        if is_section:
            m = GO_SECTION.match(line)
            flush()
            section_ref, section = m.group(1), m.group(2).strip()
            seq = 0
            start()
            continue

        # A heading-shaped line also opens a new question, which covers books
        # where the per-question "Answer key" link did not survive extraction.
        if is_title:
            flush()
            start()
            current["lines"].append(line.rstrip())
            continue

        if current is None:
            start()
        current["lines"].append(line.rstrip())

    flush()
    return questions, answers


def parse_go_body(block):
    """Reassemble the stem, the three-line options and the one-per-line tags."""
    stem, options, current = [], [], None
    next_idx = 0
    tags = []
    awaiting_dot = False

    for line in block["lines"]:
        if not line.strip():
            continue
        if GO_DOT_ONLY.match(line):
            awaiting_dot = False
            continue

        m = GO_OPT_ALONE.match(line)
        if m and m.group(1).upper() == chr(ord("A") + next_idx):
            if current is not None:
                options.append(" ".join(current).strip())
            current = []
            next_idx += 1
            awaiting_dot = True
            continue

        m = GO_TAG_ALONE.match(line)
        if m and (next_idx or not stem or len(line.strip()) < 40):
            tags.append(m.group(1))
            continue

        if current is not None:
            current.append(line.strip())
        else:
            stem.append(line.strip())

    if current is not None:
        options.append(" ".join(current).strip())

    text = re.sub(r"\s+", " ", " ".join(stem)).strip()
    return dict(
        text=text,
        options=[re.sub(r"\s+", " ", o).strip() for o in options if o.strip()],
        tags=tags,
    )


def resolve_topic(block, parsed, topic_map, subject_map, chapter_map, ignore, topics):
    """Section heading first, then the question's own title, then chapter, then tags."""
    unknown = []
    chapter = block.get("chapter") or {}
    chapter_subject = (
        subject_map.get(slugify(chapter.get("subject", ""))) if chapter else None
    )

    def ok(key):
        return key in topics and (
            chapter_subject is None or topics[key]["subject"] == chapter_subject
        )

    if block.get("section"):
        key = map_lookup(topic_map, slugify(block["section"]), chapter_subject)
        if ok(key):
            return key, None, "section", unknown

    # "First Order Logic: GATE CSE 2018 | Question: 28" names its own topic
    if block.get("topic_hint"):
        key = map_lookup(topic_map, slugify(block["topic_hint"]), chapter_subject)
        if ok(key):
            return key, None, "title", unknown

    for tag in parsed["tags"]:
        if tag in ignore or GO_YEAR.search(tag) or tag in GO_MARK_TAG:
            continue
        mapped = map_lookup(topic_map, tag, chapter_subject)
        if ok(mapped):
            return mapped, None, "tag", unknown
        if tag not in subject_map and tag not in topic_map:
            unknown.append(tag)

    chapter_key = None
    if chapter:
        chapter_key = chapter_map.get(
            slugify("%s %s" % (chapter.get("subject", ""), chapter.get("group", "")))
        )
        if chapter_key is None:
            chapter_key = chapter_map.get(slugify(chapter.get("group", "")))
        if chapter_key is None:
            chapter_key = map_lookup(
                topic_map, slugify(chapter.get("group", "")), chapter_subject
            )
    if ok(chapter_key):
        return chapter_key, None, "chapter", unknown

    return None, chapter_subject, None, unknown


def build_go(path, args, matchers, topics):
    topic_map, subject_map, chapter_map, ignore = load_tag_map()
    if not topic_map:
        raise SystemExit("content/go_tag_map.json is missing or empty.")

    stem = re.sub(
        r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(path))[0].lower()
    ).strip("-")
    lines = clean_lines(repair_mojibake(read_input(path)))
    blocks, key_answers = parse_go_document(lines)
    print(
        "  extracted %d lines, found %d question blocks, %d answer-key entries"
        % (len(lines), len(blocks), len(key_answers))
    )
    if blocks and not key_answers:
        print("  warning: no answers were found, so everything will go to review")

    accepted, review = [], []
    unknown_tags = Counter()
    sources = Counter()

    for block in blocks:
        parsed = parse_go_body(block)
        if len(parsed["text"]) < 25:
            continue

        key, subject, source, unknown = resolve_topic(
            block, parsed, topic_map, subject_map, chapter_map, ignore, topics
        )
        unknown_tags.update(unknown)

        score = None
        if key is None:
            key, runner, score, _, problem = classify(
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
        sources[source or "unresolved"] += 1

        marks = args.marks
        for tag in parsed["tags"]:
            if tag in GO_MARK_TAG:
                marks = GO_MARK_TAG[tag]
                break

        year = None
        ym = GO_YEAR.search(" ".join(parsed["tags"]) + " " + block.get("exam", ""))
        if ym:
            year = int(ym.group(1))

        q = dict(
            id="%s-%s" % (stem, block["ref"].replace(".", "-")),
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
            _go_ref=block["ref"],
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

        apply_answer(q, key_answers.get(block["ref"]))

        if key:
            q["subject"] = topics[key]["subject"]
            q["topic"] = topics[key]["topic"]
        else:
            q["_needs_review"] = True
            q["_review_reason"] = "could not resolve a topic"

        if any(h in parsed["text"].lower() for h in FIGURE_HINTS):
            q["_needs_review"] = True
            q["_review_reason"] = "refers to a figure that text extraction drops"

        (review if q.get("_needs_review") or not key else accepted).append(q)

    print(
        "  topic source: %s"
        % ", ".join("%s %d" % (k, v) for k, v in sources.most_common())
    )
    if unknown_tags:
        print("  %d tag(s) not in go_tag_map.json - see --audit-tags" % len(unknown_tags))
    return accepted, review, unknown_tags


def probe(path):
    """Show what the extracted text actually looks like before importing."""
    text = read_input(path)
    raw_lines = text.replace("\r", "").split("\n")
    text = repair_mojibake(text)
    lines = clean_lines(text)
    body = [l for l in lines if l.strip()]

    print("\n%s" % path)
    print("  %-34s %s" % ("raw lines", len(raw_lines)))
    print("  %-34s %s" % ("after noise removal", len(body)))
    print("  %-34s %s" % ("characters", len(text)))

    counts = dict(
        gate_style_numbering=sum(1 for l in body if Q_START.match(l)),
        go_chapters=sum(1 for l in body if GO_CHAPTER_TITLE.match(l)),
        go_sections=sum(1 for l in body if GO_SECTION.match(l)),
        go_question_titles=sum(1 for l in body if GO_Q_TITLE.match(l)),
        go_lone_option_letters=sum(1 for l in body if GO_OPT_ALONE.match(l)),
        go_lone_tags=sum(1 for l in body if GO_TAG_ALONE.match(l)),
        option_lines=sum(1 for l in body if OPT_LINE.match(l)),
        tag_lines=sum(1 for l in body if looks_like_tag_line(l)),
        per_question_answer_markers=sum(1 for l in body if GO_ANSWER_MARKER.match(l)),
        chapter_answer_key_sections=sum(1 for l in body if GO_ANSWER_KEYS.match(l)),
    )
    print("\n  pattern counts:")
    for k, v in counts.items():
        print("    %-32s %6d" % (k, v))

    go_signal = (
        counts["go_question_titles"] + counts["go_chapters"] + counts["go_sections"]
    )
    if go_signal > counts["gate_style_numbering"]:
        print("\n  Looks like a GO book. Import with:  --format go")
    elif counts["gate_style_numbering"]:
        print("\n  Looks like an official paper. Import with the default format.")
    else:
        print("\n  Neither pattern is common here. The text may be badly extracted -")
        print("  try pdftotext -layout, or check the PDF is not scanned images.")

    print("\n  first question titles seen (these anchor each question):")
    shown = 0
    for l in body:
        if GO_Q_TITLE.match(l):
            print("    %s" % l[:110])
            shown += 1
            if shown >= 5:
                break
    if not shown:
        print("    none found")

    print("\n  first tag-like lines seen:")
    shown = 0
    for l in body:
        if looks_like_tag_line(l):
            print("    %s" % l[:110])
            shown += 1
            if shown >= 6:
                break
    if not shown:
        print("    none found")

    print("\n  first 40 non-empty lines:")
    for l in body[:40]:
        print("    %s" % l[:110])
    return 0


# ===========================================================================
# building
# ===========================================================================
def guess_difficulty(marks, text):
    if marks >= 2 and len(text) > 320:
        return "hard"
    return "medium" if marks >= 2 else "easy"


def build(path, args, matchers, topics):
    stem = re.sub(
        r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(path))[0].lower()
    ).strip("-")
    text = read_input(path)
    lines = clean_lines(text)
    blocks = segment(lines)
    answers = load_answers(args.answers)

    print(
        "  extracted %d lines, found %d question blocks, %d answer-key entries"
        % (len(lines), len(blocks), len(answers))
    )
    if blocks and not answers and args.answers:
        print("  warning: answer key parsed to nothing - check the file")

    accepted, review = [], []
    for block in blocks:
        body, options = parse_block(block)
        if len(body) < 25:
            continue
        if INSTRUCTION.search(body):
            continue

        q = dict(
            id="%s-q%s" % (stem, block["num"]),
            kind=args.kind,
            difficulty=guess_difficulty(block["marks"], body),
            marks=block["marks"],
            text=body,
            options=options,
            explain="",
            _source=os.path.basename(path),
            _paper_number=block["num"],
        )
        if args.year:
            q["year"] = args.year

        apply_answer(q, answers.get(str(block["num"])))

        key, runner, score, strong_hits, problem = classify(
            body, options, matchers, topics, args.subject, args.min_score
        )

        if key:
            q["subject"] = topics[key]["subject"]
            q["topic"] = topics[key]["topic"]
            q["_score"] = round(score, 1)
            if strong_hits:
                q["_matched"] = strong_hits[:4]
            if runner:
                q["_runner_up"] = "%s (%.1f)" % (runner[0], runner[1])

        if any(h in q["text"].lower() for h in FIGURE_HINTS):
            q["_needs_review"] = True
            q["_review_reason"] = "refers to a figure or table that text extraction drops"
        if problem:
            q["_needs_review"] = True
            q["_review_reason"] = q.get("_review_reason") or problem
            q["_classify_note"] = problem
        if not options and q.get("type") != "nat":
            q["_needs_review"] = True
            q["_review_reason"] = q.get("_review_reason") or "no options extracted"

        (review if q.get("_needs_review") or not key else accepted).append(q)

    return accepted, review


# ===========================================================================
# writing
# ===========================================================================
def merge_into_subject_files(accepted, dry_run=False):
    """One file per subject, because the loader takes subject from the file."""
    by_subject = defaultdict(list)
    for q in accepted:
        by_subject[q["subject"]].append(q)

    written = {}
    for subject, items in sorted(by_subject.items()):
        path = os.path.join(QUESTIONS_DIR, "imported-%s.json" % subject)
        existing = load_json(path, {"subject": subject, "questions": []})
        index = {q["id"]: i for i, q in enumerate(existing.get("questions", []))}

        added = replaced = 0
        for q in items:
            clean = dict(q)
            clean.pop("subject", None)  # file-level field carries it
            if clean["id"] in index:
                existing["questions"][index[clean["id"]]] = clean
                replaced += 1
            else:
                existing["questions"].append(clean)
                added += 1

        existing["subject"] = subject
        existing["questions"].sort(
            key=lambda q: (q.get("year", 0), q.get("_paper_number", 0))
        )
        written[subject] = (path, added, replaced, len(existing["questions"]))

        if not dry_run:
            os.makedirs(QUESTIONS_DIR, exist_ok=True)
            # Back up first, then write atomically. A bad import can be undone by
            # restoring one file from content/backups/, and a crash mid-write
            # can never leave a truncated bank behind.
            backup = ingest.backup_file(path)
            ingest.write_json_atomic(path, existing)
            if backup:
                print("  backup: %s" % backup)
    return written


def append_review(review, dry_run=False):
    if not review:
        return 0
    queue = load_json(
        REVIEW_PATH,
        {
            "_note": "Not loaded by the app. Clear with: "
            "python tools/import_questions.py --review",
            "questions": [],
        },
    )
    index = {q["id"] for q in queue.get("questions", [])}
    fresh = [q for q in review if q["id"] not in index]
    queue["questions"] = queue.get("questions", []) + fresh
    if not dry_run:
        with open(REVIEW_PATH, "w", encoding="utf-8") as fh:
            json.dump(queue, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    return len(fresh)


# ===========================================================================
# reporting
# ===========================================================================
def report(accepted, review, topics, missing_lexicon):
    total = len(accepted) + len(review)
    print()
    print("  %-38s %d" % ("questions parsed", total))
    print("  %-38s %d" % ("classified and ready", len(accepted)))
    print("  %-38s %d" % ("sent to review queue", len(review)))
    if total:
        print("  %-38s %.0f%%" % ("auto-classified", len(accepted) / total * 100))

    if accepted:
        print("\n  by subject:")
        for subject, n in Counter(q["subject"] for q in accepted).most_common():
            print("    %-32s %3d" % (subject, n))
        print("\n  top topics:")
        pairs = Counter("%s/%s" % (q["subject"], q["topic"]) for q in accepted)
        for key, n in pairs.most_common(12):
            print("    %-44s %3d" % (key, n))
        by_tag = sum(
            1
            for q in accepted
            if q.get("_tag_source") in ("section", "title", "chapter", "tag")
        )
        if by_tag:
            print(
                "\n  %d of %d took their topic from the book's own structure, not a guess"
                % (by_tag, len(accepted))
            )
        # Only questions that actually went through keyword scoring have a score.
        weak = [
            q
            for q in accepted
            if isinstance(q.get("_score"), (int, float)) and q["_score"] < 5
        ]
        if weak:
            print(
                "\n  %d classified on a thin keyword score (<5) - worth a skim:"
                % len(weak)
            )
            for q in weak[:6]:
                print(
                    "    %-22s %-34s %.1f"
                    % (q["id"], q["subject"] + "/" + q["topic"], q["_score"])
                )

    if review:
        print("\n  review reasons:")
        for reason, n in Counter(
            q.get("_review_reason", "?") for q in review
        ).most_common():
            print("    %-52s %3d" % (reason[:52], n))

    if missing_lexicon:
        print(
            "\n  %d topics have no keywords yet, so nothing can be tagged to them:"
            % len(missing_lexicon)
        )
        for key in missing_lexicon[:10]:
            print("    %s" % key)


def report_extra(accepted, review, dupes, by_id, args):
    """The extra dry-run detail the spec asks for: matched, review, rejected, gaps."""
    print()
    print("  ingestion summary")
    print("  %-38s %d" % ("would be written to the bank", len(accepted)))
    print("  %-38s %d" % ("held for human review", len(review)))
    exact = [d for d in dupes if d["status"] == "exact"]
    near = [d for d in dupes if d["status"] == "near"]
    print("  %-38s %d" % ("rejected as exact duplicates", len(exact)))
    print("  %-38s %d" % ("flagged as near duplicates", len(near)))

    if accepted:
        confs = sorted(q["confidence"] for q in accepted)
        mid = confs[len(confs) // 2]
        print("  %-38s %.2f (median), %.2f (lowest)" % ("confidence", mid, confs[0]))

    if near:
        print("\n  near duplicates (kept, but worth a look):")
        for d in near[:8]:
            print(
                "    %-24s ~%.0f%% like %s"
                % (d["id"], d["similarity"] * 100, d["duplicate_of"])
            )
    if exact:
        print("\n  exact duplicates dropped:")
        for d in exact[:8]:
            print("    %-24s already in bank as %s" % (d["id"], d["duplicate_of"]))

    low = sorted((q for q in review), key=lambda q: q["confidence"])[:6]
    if low:
        print("\n  lowest-confidence items and why:")
        for q in low:
            print(
                "    %-22s %.2f  %s"
                % (q["id"], q["confidence"], "; ".join(q.get("_confidence_why", []))[:70])
            )

    gaps = ingest.gaps_report(limit=8)
    if gaps["empty"]:
        print("\n  still underrepresented after this import:")
        for t in gaps["empty"][:8]:
            print(
                "    %-46s %d marks" % ("%s/%s" % (t["subject"], t["topic"]), t["marks"])
            )


# ===========================================================================
# review mode
# ===========================================================================
def review_mode(matchers, topics):
    queue = load_json(REVIEW_PATH)
    if not queue or not queue.get("questions"):
        print("Review queue is empty.")
        return 0

    items = queue["questions"]
    print(
        "%d question(s) waiting. Enter a number to file it, s to skip, "
        "d to delete, q to stop.\n" % len(items)
    )
    keep, filed = [], []

    for i, q in enumerate(items, 1):
        print("=" * 72)
        print(
            "[%d/%d]  %s   marks %s   type %s"
            % (i, len(items), q["id"], q.get("marks"), q.get("type"))
        )
        print("reason: %s" % q.get("_review_reason", "-"))
        print("-" * 72)
        print(q["text"][:700])
        for j, opt in enumerate(q.get("options", [])):
            print("  (%s) %s" % (chr(65 + j), opt[:110]))
        if "answer" in q:
            print("answer: %s" % [chr(65 + x) for x in q["answer"]])
        elif "answer_value" in q:
            print("answer: %s (tol %s)" % (q["answer_value"], q.get("tolerance")))
        print("-" * 72)

        _, _, _, _, _ = classify(q["text"], q.get("options", []), matchers, topics)
        scores = defaultdict(float)
        blob = re.sub(
            r"\s+", " ", (q["text"] + " " + " ".join(q.get("options", []))).lower()
        )
        for pattern, points, key in matchers:
            if pattern.search(blob):
                scores[key] += points
        ranked = sorted(scores.items(), key=lambda kv: -kv[1])[:6]
        if ranked:
            for n, (key, sc) in enumerate(ranked, 1):
                print("  %d) %-46s %.1f" % (n, key, sc))
        else:
            print("  (no candidates - type a slug like operating-systems/deadlock)")

        choice = input("choice > ").strip().lower()
        if choice == "q":
            keep.extend(items[i - 1 :])
            break
        if choice == "d":
            continue
        if choice == "s" or not choice:
            keep.append(q)
            continue

        key = None
        if choice.isdigit() and ranked and 1 <= int(choice) <= len(ranked):
            key = ranked[int(choice) - 1][0]
        elif choice in topics:
            key = choice
        if not key:
            print("  not recognised, keeping it in the queue")
            keep.append(q)
            continue

        clean = dict(q)
        for junk in ("_needs_review", "_review_reason", "_classify_note", "_runner_up"):
            clean.pop(junk, None)
        clean["subject"] = topics[key]["subject"]
        clean["topic"] = topics[key]["topic"]
        clean["_score"] = "manual"
        filed.append(clean)
        print("  filed under %s" % key)

    if filed:
        written = merge_into_subject_files(filed)
        print()
        for subject, (path, added, replaced, total) in written.items():
            print(
                "  %-32s +%d new, %d replaced, %d total"
                % (os.path.relpath(path, ROOT), added, replaced, total)
            )

    queue["questions"] = keep
    with open(REVIEW_PATH, "w", encoding="utf-8") as fh:
        json.dump(queue, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("\n  filed %d, left %d in the queue" % (len(filed), len(keep)))
    print("  Restart the app to pick up the new questions.")
    return 0


# ===========================================================================
# validate mode
# ===========================================================================
def validate(paths, topics):
    problems = 0
    seen = {}
    for path in paths:
        data = load_json(path)
        if data is None:
            print("%s: cannot read" % path)
            problems += 1
            continue
        file_subject = data.get("subject")
        if file_subject and not any(
            m["subject"] == file_subject for m in topics.values()
        ):
            print("%s: file subject %r is not in syllabus.json" % (path, file_subject))
            problems += 1

        for q in data.get("questions", []):
            qid = q.get("id", "<no id>")
            where = "%s [%s]" % (os.path.basename(path), qid)
            if not q.get("id"):
                print("%s: missing id" % where)
                problems += 1
            elif qid in seen:
                print("%s: duplicate id, also in %s" % (where, seen[qid]))
                problems += 1
            else:
                seen[qid] = os.path.basename(path)

            subject = file_subject or q.get("subject")
            key = "%s/%s" % (subject, q.get("topic"))
            if key not in topics:
                print(
                    "%s: topic %r not in syllabus - it will never be picked by a "
                    "topic quiz" % (where, key)
                )
                problems += 1

            qtype = q.get("type", "mcq")
            if qtype == "nat":
                if "answer_value" not in q:
                    print("%s: nat without answer_value" % where)
                    problems += 1
            else:
                opts = q.get("options") or []
                ans = q.get("answer")
                if len(opts) < 2:
                    print("%s: %s with %d options" % (where, qtype, len(opts)))
                    problems += 1
                if not ans:
                    print("%s: %s with no answer" % (where, qtype))
                    problems += 1
                elif max(ans) >= len(opts):
                    print(
                        "%s: answer index %d out of range for %d options"
                        % (where, max(ans), len(opts))
                    )
                    problems += 1
                elif qtype == "mcq" and len(ans) != 1:
                    print(
                        "%s: mcq with %d answers - should this be msq?"
                        % (where, len(ans))
                    )
                    problems += 1
            if q.get("marks") not in (1, 2):
                print("%s: marks is %r, GATE uses 1 or 2" % (where, q.get("marks")))
                problems += 1
            if not str(q.get("text", "")).strip():
                print("%s: empty text" % where)
                problems += 1

    print()
    print(
        "checked %d question(s) across %d file(s): %s"
        % (len(seen), len(paths), "%d problem(s)" % problems if problems else "clean")
    )
    return 1 if problems else 0


# ===========================================================================
# main
# ===========================================================================
def main():
    ap = argparse.ArgumentParser(
        description="Import GATE papers into the question bank.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("inputs", nargs="*", help="paper files (.pdf or .txt)")
    ap.add_argument("--answers", help="official answer key (.pdf, .txt, .csv or .json)")
    ap.add_argument("--year", type=int, help="paper year, stored on each question")
    ap.add_argument(
        "--kind",
        default="pyq",
        choices=["pyq", "dpp"],
        help="drives the PYQ-only / practice-only filter (default pyq)",
    )
    ap.add_argument(
        "--format",
        default="gate",
        choices=["gate", "go"],
        help="gate = official paper layout (default); "
        "go = GATE Overflow book, uses GO's own tags",
    )
    ap.add_argument(
        "--marks",
        type=int,
        choices=[1, 2],
        help="marks per question when the source does not say (GO books)",
    )
    ap.add_argument(
        "--probe",
        metavar="FILE",
        help="report what the extracted text looks like and exit",
    )
    ap.add_argument(
        "--audit-tags",
        action="store_true",
        help="with --format go: list GO tags missing from go_tag_map.json",
    )
    ap.add_argument(
        "--subject",
        help="force every question into this subject slug, "
        "so only its topics are considered",
    )
    ap.add_argument(
        "--min-score",
        type=float,
        default=DEFAULT_MIN_SCORE,
        help="classification threshold (default %.1f)" % DEFAULT_MIN_SCORE,
    )
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    ap.add_argument("--review", action="store_true", help="work through the review queue")
    ap.add_argument(
        "--validate", nargs="+", metavar="FILE", help="check question files and exit"
    )
    ap.add_argument(
        "--source",
        metavar="SLUG",
        help="record this import against a source slug "
        "(registered automatically if new)",
    )
    ap.add_argument("--source-name", metavar="NAME", help="display name for --source")
    ap.add_argument(
        "--source-kind",
        default="manual",
        choices=ingest.SOURCE_KINDS,
        help="what kind of source this is (default manual)",
    )
    ap.add_argument("--source-url", default="", help="where the material came from")
    ap.add_argument(
        "--source-licence",
        default="",
        help="licence or permission note stored with the source",
    )
    ap.add_argument(
        "--min-confidence",
        type=float,
        default=ingest.CONFIDENCE_FLOOR,
        help="questions below this confidence go to review "
        "(default %.2f)" % ingest.CONFIDENCE_FLOOR,
    )
    ap.add_argument(
        "--no-near-dupes", action="store_true", help="skip the slower near-duplicate scan"
    )
    ap.add_argument(
        "--to-db-review",
        action="store_true",
        help="send review items to the app's review panel instead of "
        "content/review-queue.json",
    )
    args = ap.parse_args()

    topics = load_syllabus()
    if not topics:
        raise SystemExit("content/syllabus.json is missing or empty.")

    if args.probe:
        if not os.path.isfile(args.probe):
            raise SystemExit("Not found: %s" % args.probe)
        return probe(args.probe)

    if args.validate:
        return validate(args.validate, topics)

    matchers, missing = compile_lexicon(topics)
    if not matchers:
        raise SystemExit("content/topic_keywords.json is missing or empty.")

    if args.review:
        return review_mode(matchers, topics)

    if not args.inputs:
        ap.print_help()
        return 1
    if args.subject and not any(m["subject"] == args.subject for m in topics.values()):
        raise SystemExit("--subject %r is not in syllabus.json" % args.subject)

    all_accepted, all_review = [], []
    unknown_tags = Counter()
    for path in args.inputs:
        if not os.path.isfile(path):
            print("skipping %s (not found)" % path)
            continue
        print("\n%s" % path)
        if args.format == "go":
            accepted, review, unknown = build_go(path, args, matchers, topics)
            unknown_tags.update(unknown)
        else:
            accepted, review = build(path, args, matchers, topics)
        all_accepted.extend(accepted)
        all_review.extend(review)

    if args.audit_tags:
        print("\n  GO tags not present in content/go_tag_map.json, most frequent first.")
        print(
            "  Add the ones that matter to 'topics' (best) or 'subjects', then rerun.\n"
        )
        if not unknown_tags:
            print("    none - every tag was recognised")
        for tag, n in unknown_tags.most_common(60):
            print("    %-46s %5d" % (tag, n))
        print("\n  (nothing was written; drop --audit-tags to import)")
        return 0

    # ---- confidence, duplicate detection, gap analysis -------------------
    conn = database.init()
    try:
        registry.seed(conn)
        if args.source:
            ingest.register_source(
                conn,
                args.source,
                args.source_name or args.source,
                kind=args.source_kind,
                url=args.source_url,
                licence_note=args.source_licence,
            )

        import_id = ingest.open_import(
            conn, args.source, " ".join(args.inputs), dry_run=args.dry_run
        )

        for q in all_accepted + all_review:
            conf, why = ingest.score_confidence(
                q, keyword_score=q.get("_score"), tag_source=q.get("_tag_source")
            )
            q["confidence"] = conf
            q["_confidence_why"] = why
            if args.source:
                q["source"] = args.source

        # Anything below the floor is demoted to review even if it classified.
        demoted = [q for q in all_accepted if q["confidence"] < args.min_confidence]
        if demoted:
            keep = {id(q) for q in demoted}
            all_accepted = [q for q in all_accepted if id(q) not in keep]
            for q in demoted:
                q["_review_reason"] = q.get(
                    "_review_reason"
                ) or "confidence %.2f below floor %.2f" % (
                    q["confidence"],
                    args.min_confidence,
                )
            all_review.extend(demoted)

        verdicts = ingest.find_duplicates(
            all_accepted + all_review, near=not args.no_near_dupes
        )
        by_id = {v["id"]: v for v in verdicts}
        dupes = [v for v in verdicts if v["status"] != "new"]
        dupe_ids = {v["id"] for v in dupes if v["status"] == "exact"}
        rejected = [q for q in all_accepted if q["id"] in dupe_ids]
        all_accepted = [q for q in all_accepted if q["id"] not in dupe_ids]

        report(all_accepted, all_review, topics, missing)
        report_extra(all_accepted, all_review, dupes, by_id, args)

        counts = dict(
            found=len(all_accepted) + len(all_review) + len(rejected),
            matched=len(all_accepted),
            needs_review=len(all_review),
            rejected=len(rejected),
            duplicates=len(dupes),
            promoted=0,
        )

        manifest = ingest.write_manifest(
            dict(
                started_at=datetime.now().isoformat(timespec="seconds"),
                inputs=args.inputs,
                answers=args.answers,
                format=args.format,
                source=args.source,
                dry_run=bool(args.dry_run),
                min_score=args.min_score,
                min_confidence=args.min_confidence,
                counts=counts,
                accepted=[
                    dict(
                        id=q["id"],
                        subject=q.get("subject"),
                        topic=q.get("topic"),
                        confidence=q["confidence"],
                        score=q.get("_score"),
                        tag_source=q.get("_tag_source"),
                    )
                    for q in all_accepted
                ],
                review=[
                    dict(
                        id=q["id"],
                        reason=q.get("_review_reason"),
                        confidence=q["confidence"],
                        why=q.get("_confidence_why"),
                    )
                    for q in all_review
                ],
                duplicates=dupes,
                gaps=ingest.gaps_report(limit=15),
            )
        )
        print("\n  manifest: %s" % manifest)

        if args.dry_run:
            ingest.close_import(conn, import_id, counts, manifest, status="dry-run")
            print("  dry run: nothing written.")
            return 0

        written = merge_into_subject_files(all_accepted)
        if args.to_db_review and all_review:
            queued = ingest.queue_for_review(
                conn,
                [
                    dict(
                        question=q,
                        confidence=q["confidence"],
                        issues=[q.get("_review_reason", "")],
                    )
                    for q in all_review
                ],
                import_id=import_id,
                source_slug=args.source,
            )
            print("  %d item(s) queued in the app's review panel" % queued)
        else:
            queued = append_review(all_review)

        counts["promoted"] = sum(a for _, a, _, _ in written.values())
        ingest.close_import(conn, import_id, counts, manifest)
        if args.source:
            ingest.touch_source(conn, args.source)
        ingest.prune_backups()
    finally:
        conn.close()
    print()
    for subject, (path, added, replaced, total) in written.items():
        print(
            "  %-42s +%d new, %d replaced, %d total"
            % (os.path.relpath(path, ROOT), added, replaced, total)
        )
    if queued:
        print("  %-42s +%d waiting" % (os.path.relpath(REVIEW_PATH, ROOT), queued))
        print("\n  Next: python tools/import_questions.py --review")
    if written:
        print("\n  Restart the app to pick up the new questions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
