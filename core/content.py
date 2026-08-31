"""The content registry.

This module used to be a file loader. It is now the registry that owns
everything GitGrind knows about *content* as opposed to *activity*:

* the syllabus tree (subjects, topics, weights)
* the cutoff targets
* every question bank on disk, across multiple directories
* source metadata for each bank file
* the topic normalisation map that makes questions from different sources
  agree on a single subject/topic vocabulary
* bank health: how much of the bank is actually usable

Activity lives in SQLite. Content lives in files, so it stays diffable and a
bad import can be reverted with git or a file copy.
"""

import json
import os
import re
import sqlite3
from datetime import date, datetime, timedelta

from . import db

# content/ has to be writable, because approving a review item and logging a
# looked-up answer both rewrite bank files. In a packaged build the shipped copy
# lives read-only inside the bundle, so materialise() below copies it out next to
# the executable on first run and everything after that works normally.
CONTENT_DIR = os.path.join(db.BASE_DIR, "content")
BUNDLED_CONTENT = os.path.join(db.ASSET_DIR, "content")
QUESTIONS_DIR = os.path.join(CONTENT_DIR, "questions")
BANKS_DIR = os.path.join(CONTENT_DIR, "banks")
REVIEW_DIR = os.path.join(CONTENT_DIR, "review")


def materialise(verbose=False):
    """Copy the bundled content/ out of a frozen build so it can be edited.

    Returns a short status string, or "" when there was nothing to do (which is
    every run from source, and every run after the first from an executable).
    """
    if os.path.normpath(BUNDLED_CONTENT) == os.path.normpath(CONTENT_DIR):
        return ""
    if not os.path.isdir(BUNDLED_CONTENT):
        return ""

    import shutil

    copied = 0
    for root, _dirs, files in os.walk(BUNDLED_CONTENT):
        rel = os.path.relpath(root, BUNDLED_CONTENT)
        dest_root = CONTENT_DIR if rel == "." else os.path.join(CONTENT_DIR, rel)
        os.makedirs(dest_root, exist_ok=True)
        for name in files:
            dest = os.path.join(dest_root, name)
            # Never overwrite: an answer you logged beats the shipped default.
            if os.path.exists(dest):
                continue
            shutil.copy2(os.path.join(root, name), dest)
            copied += 1
    if copied and verbose:
        print("  content    unpacked %d file(s) to %s" % (copied, CONTENT_DIR))
    return "unpacked %d file(s)" % copied if copied else ""


SESSION_KINDS = ["concept", "revision", "pyq", "dpp", "mock", "notes"]
KIND_LABELS = {
    "concept": "New concept",
    "revision": "Revision",
    "pyq": "Previous year questions",
    "dpp": "Daily practice problems",
    "mock": "Mock test",
    "notes": "Notes and formula sheet",
}

QUESTION_TYPES = ("mcq", "msq", "nat")
DIFFICULTIES = ("easy", "medium", "hard")

# A question needs these to be servable at all.
REQUIRED_FIELDS = ("id", "text")

# Figures extracted from a source PDF live on disk as sidecar files and are
# referenced from a question's ``figure_assets``. Only paths under this prefix
# are ever handed to the UI: a bank file is editable by hand and shipped in
# releases, so an asset src is untrusted input, and letting an arbitrary URL or
# a "javascript:" string reach an <img> would turn a content edit into a way to
# execute code in the app. Anything else is dropped and reported as a defect.
ASSET_URL_PREFIX = "/content/assets/"
ASSETS_DIR = os.path.join(CONTENT_DIR, "assets")

_cache = {}


# ---------------------------------------------------------------------------
# low level
# ---------------------------------------------------------------------------
def _read_json(path, fallback=None):
    if not os.path.isfile(path):
        return fallback
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (ValueError, OSError):
        return fallback


def invalidate():
    """Drop every cached read. Called after an import or a content edit."""
    _cache.clear()


def syllabus(reload=False):
    if reload or "syllabus" not in _cache:
        _cache["syllabus"] = _read_json(
            os.path.join(CONTENT_DIR, "syllabus.json"), {"subjects": []}
        )
    return _cache["syllabus"]


def targets(reload=False):
    if reload or "targets" not in _cache:
        _cache["targets"] = _read_json(os.path.join(CONTENT_DIR, "targets.json"), {})
    return _cache["targets"]


def topic_index(reload=False):
    """{(subject_slug, topic_slug): {...}} straight from the syllabus."""
    if reload or "topic_index" not in _cache:
        idx = {}
        for subj in syllabus(reload).get("subjects", []):
            for order, t in enumerate(subj.get("topics", [])):
                idx[(subj["slug"], t["slug"])] = dict(
                    subject=subj["slug"],
                    subject_name=subj["name"],
                    topic=t["slug"],
                    name=t["name"],
                    weight=int(t.get("weight", 1)),
                    marks=int(subj.get("marks", 5)),
                    order=order,
                )
        _cache["topic_index"] = idx
    return _cache["topic_index"]


def topic_map(reload=False):
    """Alias -> (subject, topic). Merges the file map with the DB alias table."""
    if reload or "topic_map" not in _cache:
        data = _read_json(os.path.join(CONTENT_DIR, "topic_map.json"), {}) or {}
        out = {}
        for alias, pair in (data.get("aliases") or {}).items():
            if isinstance(pair, dict):
                out[_norm_key(alias)] = (pair.get("subject", ""), pair.get("topic", ""))
            elif isinstance(pair, str) and "/" in pair:
                s, t = pair.split("/", 1)
                out[_norm_key(alias)] = (s, t)
        # every real topic maps to itself, under a few spellings
        for (subj, topic), meta in topic_index(reload).items():
            out.setdefault(_norm_key(topic), (subj, topic))
            out.setdefault(_norm_key(meta["name"]), (subj, topic))
        _cache["topic_map"] = out
    return _cache["topic_map"]


def _norm_key(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").strip().lower()).strip("-")


def overrides(reload=False):
    """Block key -> correction, from content/subtopic_overrides.json.

    Keyed "<volume>|<chapter>.<block>" so a correction outlives the
    re-import that would renumber or rename individual questions. Entries
    with apply false are ignored, so a freshly generated file is inert
    until somebody has read it.
    """
    if reload or "overrides" not in _cache:
        data = _read_json(
            os.path.join(CONTENT_DIR, "subtopic_overrides.json"), {}
        ) or {}
        out = {}
        for key, spec in (data.get("overrides") or {}).items():
            if not isinstance(spec, dict) or not spec.get("apply"):
                continue
            entry = {}
            if "subtopic" in spec:
                entry["subtopic"] = _norm_key(spec.get("subtopic") or "")
            topic = (spec.get("topic") or "").strip()
            if "/" in topic:
                subject, tslug = topic.split("/", 1)
                entry["subject"] = subject
                entry["topic"] = tslug
            if entry:
                out[key] = entry
        _cache["overrides"] = out
    return _cache["overrides"]


def _block_key(origin):
    """"<volume>|<chapter>.<block>" for a question's origin, or ""."""
    if not isinstance(origin, dict):
        return ""
    parts = (origin.get("ref") or "").split(".")
    if len(parts) < 3 or not parts[1].isdigit():
        return ""
    return "%s|%s.%d" % (origin.get("volume") or "", parts[0], int(parts[1]))


def normalise_topic(conn, subject_slug, topic_slug, name=""):
    """Resolve whatever a source called a topic into our own vocabulary.

    Order of trust: exact syllabus match, DB alias table (user corrections),
    file alias map, then a slugified guess. Returns (subject, topic, matched).
    """
    idx = topic_index()
    if (subject_slug, topic_slug) in idx:
        return subject_slug, topic_slug, True

    for candidate in (topic_slug, name):
        key = _norm_key(candidate)
        if not key:
            continue
        if conn is not None:
            row = conn.execute(
                "SELECT subject_slug, topic_slug FROM topic_alias"
                " WHERE alias = ? AND (subject_slug = ? OR subject_slug = '')"
                " ORDER BY subject_slug DESC LIMIT 1",
                (key, subject_slug or ""),
            ).fetchone()
            if row and (row["subject_slug"], row["topic_slug"]) in idx:
                return row["subject_slug"], row["topic_slug"], True
        hit = topic_map().get(key)
        if hit and hit in idx:
            return hit[0], hit[1], True

    return subject_slug, _norm_key(topic_slug) or "", False


def remember_alias(conn, alias, subject_slug, topic_slug, source_slug=""):
    """Persist a human correction so the next import gets it right."""
    conn.execute(
        "INSERT INTO topic_alias (alias, subject_slug, topic_slug, source_slug)"
        " VALUES (?,?,?,?) ON CONFLICT(alias, subject_slug) DO UPDATE SET"
        " topic_slug = excluded.topic_slug, source_slug = excluded.source_slug",
        (_norm_key(alias), subject_slug or "", topic_slug or "", source_slug or ""),
    )
    invalidate()


# ---------------------------------------------------------------------------
# banks
# ---------------------------------------------------------------------------
def bank_files():
    """Every bank file on disk, newest directory layout first.

    ``content/questions/*.json``            - the original single-folder layout
    ``content/banks/<bank>/*.json``         - multiple named banks
    """
    found = []
    if os.path.isdir(QUESTIONS_DIR):
        for fname in sorted(os.listdir(QUESTIONS_DIR)):
            if fname.endswith(".json"):
                found.append(("questions", os.path.join(QUESTIONS_DIR, fname), fname))
    if os.path.isdir(BANKS_DIR):
        for bank in sorted(os.listdir(BANKS_DIR)):
            bdir = os.path.join(BANKS_DIR, bank)
            if not os.path.isdir(bdir):
                continue
            for fname in sorted(os.listdir(bdir)):
                if fname.endswith(".json"):
                    found.append(
                        (bank, os.path.join(bdir, fname), "%s/%s" % (bank, fname))
                    )
    return found


def _hydrate(q, subject_slug, bank, rel, source_meta):
    item = dict(q)
    item["subject"] = q.get("subject") or subject_slug
    item["bank"] = bank
    item["file"] = rel
    item.setdefault("topic", "")
    # The importer derived the syllabus topic from the source volume's
    # section heading and then left the heading in origin, so the finest
    # grain the app could offer was the topic - one bucket for everything
    # under it. The heading is a real label on real questions, so promote
    # it. A question that arrived without one keeps the empty string it
    # has today; an explicit subtopic in the bank file always wins.
    if not q.get("subtopic"):
        origin = q.get("origin") or {}
        if isinstance(origin, dict) and origin.get("section"):
            item["subtopic"] = _norm_key(origin["section"])
    item.setdefault("subtopic", "")
    # Last word on both fields. A blank subtopic here is deliberate and
    # not a failure: where the heading is wrong but nobody knows the right
    # one, empty costs granularity while wrong misroutes every search that
    # would otherwise have found the question.
    fix = overrides().get(_block_key(q.get("origin")))
    if fix:
        item.update(fix)
    item.setdefault("kind", "dpp")
    item.setdefault("difficulty", "medium")
    item.setdefault("type", "mcq")
    item.setdefault("marks", 2)
    item.setdefault("options", [])
    item.setdefault("figure_assets", [])
    item.setdefault("code_blocks", [])
    item.setdefault("explain", "")
    item.setdefault("tags", [])
    item.setdefault("confidence", 1.0)
    item.setdefault("import_status", "approved")
    if item["difficulty"] not in DIFFICULTIES:
        item["difficulty"] = "medium"
    if item["type"] not in QUESTION_TYPES:
        item["type"] = "mcq"
    # source metadata, either per-question or inherited from the file header
    item["source"] = q.get("source") or source_meta.get("slug", bank)
    item["source_name"] = q.get("source_name") or source_meta.get("name", "")
    item["source_url"] = q.get("source_url") or source_meta.get("url", "")
    if q.get("year") and not item.get("paper_year"):
        item["paper_year"] = q["year"]
    return item


def question_bank(reload=False):
    """{question_id: question dict} across every bank file."""
    if not reload and "bank" in _cache:
        return _cache["bank"]

    bank = {}
    sources = {}
    for bank_name, path, rel in bank_files():
        data = _read_json(path)
        if not data:
            continue
        if isinstance(data, list):
            data = {"questions": data}
        subject_slug = data.get("subject") or os.path.splitext(os.path.basename(path))[0]
        source_meta = data.get("source") or {}
        if isinstance(source_meta, str):
            source_meta = {"slug": source_meta, "name": source_meta}
        slug = source_meta.get("slug") or bank_name
        entry = sources.setdefault(
            slug,
            dict(
                slug=slug,
                name=source_meta.get("name") or bank_name.replace("-", " ").title(),
                kind=source_meta.get("kind", "manual"),
                url=source_meta.get("url", ""),
                licence_note=source_meta.get("licence_note", ""),
                files=[],
                questions=0,
            ),
        )
        entry["files"].append(rel)

        for q in data.get("questions", []):
            qid = q.get("id")
            if not qid or qid in bank:
                continue
            bank[qid] = _hydrate(q, subject_slug, bank_name, rel, source_meta)
            entry["questions"] += 1

    _cache["bank"] = bank
    _cache["sources"] = sources
    # Paper membership is a property of the whole bank, not of one file: a
    # question's position depends on every other question in the same paper. So
    # it is stamped here, after every bank file has been read, rather than in
    # _hydrate() which only ever sees one question at a time.
    _cache.pop("papers", None)
    _cache.pop("question_paper_index", None)
    for qid, (slug, pos, section) in question_paper_index().items():
        q = bank.get(qid)
        if q is not None:
            q["paper"] = slug
            q["position_in_paper"] = pos
            q["paper_section"] = section
    return bank


def sources(reload=False):
    if reload or "sources" not in _cache:
        question_bank(reload=True)
    return _cache.get("sources", {})


def by_topic(reload=False):
    """{(subject, topic): [question, ...]}"""
    if reload or "by_topic" not in _cache:
        out = {}
        for q in question_bank(reload).values():
            out.setdefault((q["subject"], q.get("topic", "")), []).append(q)
        _cache["by_topic"] = out
    return _cache["by_topic"]


# ---------------------------------------------------------------------------
# bank health
# ---------------------------------------------------------------------------
def safe_asset_src(src):
    """The src to hand the UI, or "" when it is not a local content asset.

    Rejects anything that is not an app-owned relative path: absolute URLs,
    scheme-like strings, backslashes and any traversal out of content/assets.
    """
    src = str(src or "").strip()
    if not src or "\\" in src or "\n" in src or "\r" in src:
        return ""
    if not src.startswith(ASSET_URL_PREFIX):
        return ""
    rel = src[len(ASSET_URL_PREFIX):]
    if not rel or rel.startswith("/"):
        return ""
    # Normalise first, then confirm the result is still inside the prefix.
    if any(part in ("..", "") for part in rel.split("/")):
        return ""
    return ASSET_URL_PREFIX + rel


def figure_asset_issues(q):
    """Problems with a question's figure_assets. Empty list means it is fine."""
    figs = q.get("figure_assets")
    if figs in (None, "", []):
        return []
    if not isinstance(figs, list):
        return ["figure_assets is not a list"]
    issues = []
    for i, asset in enumerate(figs):
        if not isinstance(asset, dict):
            issues.append("figure_assets[%d] is not an object" % i)
            continue
        if not asset.get("src"):
            issues.append("figure_assets[%d] has no src" % i)
        elif not safe_asset_src(asset["src"]):
            issues.append("figure_assets[%d] src is not a content/assets path" % i)
        bbox = asset.get("bbox")
        if bbox is not None and (not isinstance(bbox, list) or len(bbox) != 4):
            issues.append("figure_assets[%d] bbox is not four numbers" % i)
    return issues


def public_figures(q):
    """figure_assets as the UI should see them: safe srcs, no private fields."""
    out = []
    figs = q.get("figure_assets")
    if not isinstance(figs, list):
        return out
    for i, asset in enumerate(figs):
        if not isinstance(asset, dict):
            continue
        src = safe_asset_src(asset.get("src"))
        if not src:
            continue
        view = dict(src=src, alt=str(asset.get("alt") or "Figure %d" % (i + 1))[:300])
        if asset.get("page_idx") is not None:
            view["page_idx"] = asset["page_idx"]
        if asset.get("kind"):
            view["kind"] = str(asset["kind"])[:40]
        out.append(view)
    return out


def public_code(q):
    """Code listings as the UI should see them.

    A listing is data, not markup: it is handed over as a plain string and the
    UI puts it in a text node, so nothing inside a program can become markup.
    """
    out = []
    blocks = q.get("code_blocks")
    if not isinstance(blocks, list):
        return out
    for b in blocks:
        if not isinstance(b, dict):
            continue
        code = str(b.get("code") or "")
        if not code.strip():
            continue
        out.append(dict(code=code[:4000], lang=str(b.get("lang") or "")[:20]))
    return out


def validate_question(q):
    """Return a list of problems. Empty list means the question is servable.

    ``answer_pending`` is a deliberate state, not a defect: the question was
    extracted from a source that did not print its answer. Such a question is
    kept in the bank so it counts towards coverage and can be filled in later,
    but it is reported as pending rather than broken and the quiz selector will
    not serve it until an answer exists.
    """
    issues = []
    for field in REQUIRED_FIELDS:
        if not q.get(field):
            issues.append("missing %s" % field)
    if not q.get("topic"):
        issues.append("no topic tag")
    elif (q.get("subject"), q.get("topic")) not in topic_index():
        issues.append("topic not in syllabus")

    # Figure problems are checked before the answer_pending shortcut below,
    # because a malformed asset list is a defect in its own right and has
    # nothing to do with whether an answer is known yet.
    issues.extend(figure_asset_issues(q))

    if q.get("answer_pending"):
        # Skip every answer- and option-shaped check: by definition those are the
        # parts that are missing, and reporting them again is just noise.
        issues.append("answer pending")
        return issues

    qtype = q.get("type", "mcq")
    if qtype == "nat":
        if q.get("answer_value") is None:
            issues.append("NAT without answer_value")
    else:
        answer = q.get("answer") or []
        opts = q.get("options") or []
        if not answer:
            issues.append("no answer key")
        if len(opts) < 2:
            issues.append("fewer than two options")
        elif any((not isinstance(a, int)) or a < 0 or a >= len(opts) for a in answer):
            issues.append("answer index out of range")
        if qtype == "mcq" and len(answer) > 1:
            issues.append("MCQ with multiple correct answers (should be msq)")
    # A missing explanation is a quality gap, not a correctness one: the question
    # can still be served and graded. It is counted separately in bank_stats as
    # missing_explanation, so it shows up in the health report without making
    # thousands of otherwise-fine imported questions unservable.
    try:
        if float(q.get("marks", 2)) <= 0:
            issues.append("marks must be positive")
    except (TypeError, ValueError):
        issues.append("marks is not a number")
    return issues


def bank_stats(reload=False):
    """The summary the dashboard, banner and API all read."""
    bank = question_bank(reload)
    by_subject, by_topic_counts, by_type, by_diff, by_kind, by_year = (
        {},
        {},
        {},
        {},
        {},
        {},
    )
    broken, no_explain, untagged, pending = 0, 0, 0, 0
    by_paper, no_paper = {}, 0
    with_figures, figure_defects, figure_count = 0, 0, 0
    pending_by_subject = {}
    src = sources()

    for q in bank.values():
        by_subject[q["subject"]] = by_subject.get(q["subject"], 0) + 1
        key = "%s/%s" % (q["subject"], q.get("topic", ""))
        by_topic_counts[key] = by_topic_counts.get(key, 0) + 1
        by_type[q["type"]] = by_type.get(q["type"], 0) + 1
        by_diff[q["difficulty"]] = by_diff.get(q["difficulty"], 0) + 1
        by_kind[q["kind"]] = by_kind.get(q["kind"], 0) + 1
        year = q.get("paper_year") or q.get("year")
        if year:
            by_year[str(year)] = by_year.get(str(year), 0) + 1
        if q.get("paper"):
            by_paper[q["paper"]] = by_paper.get(q["paper"], 0) + 1
        else:
            no_paper += 1
        figs = q.get("figure_assets") or []
        if isinstance(figs, list) and figs:
            with_figures += 1
            figure_count += len(figs)
        issues = validate_question(q)
        if [i for i in issues if i.startswith("figure_assets")]:
            figure_defects += 1
        if not q.get("topic") or (q["subject"], q.get("topic")) not in topic_index():
            untagged += 1
        if "no explanation" in issues:
            no_explain += 1
        if "answer pending" in issues:
            pending += 1
            pending_by_subject[q["subject"]] = pending_by_subject.get(q["subject"], 0) + 1
        elif [i for i in issues if i != "no explanation"]:
            broken += 1

    idx = topic_index()
    empty_topics = [
        dict(
            subject=s,
            topic=t,
            name=meta["name"],
            weight=meta["weight"],
            marks=meta["marks"],
        )
        for (s, t), meta in idx.items()
        if by_topic_counts.get("%s/%s" % (s, t), 0) == 0
    ]
    thin_topics = [
        dict(
            subject=s,
            topic=t,
            name=meta["name"],
            count=by_topic_counts.get("%s/%s" % (s, t), 0),
            weight=meta["weight"],
        )
        for (s, t), meta in idx.items()
        if 0 < by_topic_counts.get("%s/%s" % (s, t), 0) < 4
    ]
    empty_topics.sort(key=lambda x: (-x["marks"], -x["weight"], x["name"]))
    thin_topics.sort(key=lambda x: (x["count"], -x["weight"]))

    total = len(bank)
    # Pending questions are neither usable nor broken - they are waiting on you.
    usable = total - broken - pending
    return dict(
        total=total,
        usable=usable,
        broken=broken,
        pending=pending,
        pending_by_subject=pending_by_subject,
        untagged=untagged,
        missing_explanation=no_explain,
        with_figures=with_figures,
        figures_total=figure_count,
        figure_defects=figure_defects,
        health_pct=round(usable / total * 100) if total else 0,
        pending_pct=round(pending / total * 100) if total else 0,
        coverage_pct=round((len(idx) - len(empty_topics)) / len(idx) * 100) if idx else 0,
        subjects=by_subject,
        topics=by_topic_counts,
        types=by_type,
        difficulties=by_diff,
        kinds=by_kind,
        years=dict(sorted(by_year.items())),
        papers_total=len(by_paper),
        papers=dict(sorted(by_paper.items())),
        unmapped_to_paper=no_paper,
        files=sorted({q["file"] for q in bank.values()}),
        banks=sorted({q["bank"] for q in bank.values()}),
        sources=[dict(s, files=len(s["files"])) for s in src.values()],
        topics_total=len(idx),
        topics_empty=len(empty_topics),
        empty_topics=empty_topics[:24],
        thin_topics=thin_topics[:24],
    )


# ---------------------------------------------------------------------------
# papers
#
# A paper is an examination unit: one sitting of one exam, with its own mark
# total, duration and official answer key. Papers are content, not activity, so
# content/papers.json is the source of truth for the things that cannot be
# derived - paper code, printed mark total, duration, key URL - and everything
# else is read back out of the banks, where each question's ``origin`` block
# already records which exam and question number it came from.
#
# The DB tables (papers, paper_sections, paper_questions) are a mirror, filled by
# sync_papers(). That keeps paper metadata diffable and shippable, and means a
# user's database never holds paper facts that would be lost if it were rebuilt.
# ---------------------------------------------------------------------------
PAPERS_FILE = os.path.join(CONTENT_DIR, "papers.json")
# Generated mock papers. They are papers in every sense the app cares about, so
# they are merged into papers() rather than bolted on as a parallel concept.
MOCKS_FILE = os.path.join(CONTENT_DIR, "mocks.json")

# The two sections every GATE paper has. GA is 15 marks of the 100; the rest is
# the subject core. Stored per paper rather than derived from subjects.marks,
# because the syllabus weights in subjects are an estimate that does not add to
# 100 and must never be mistaken for what a paper actually printed.
SECTION_LABELS = {"ga": "General Aptitude", "core": "Core"}
SECTION_ORDER = {"ga": 0, "core": 1}
DEFAULT_SECTION_MARKS = {"ga": 15, "core": 85}

# Exam prefixes we accept. Anything else is a different branch's paper that
# happens to be quoted in a CSE-facing bank, and folding it into a GATE CSE
# paper would silently corrupt the reconstruction. Reject rather than guess.
KNOWN_EXAMS = {
    "gate cse": "GATE CSE",
    "gate it": "GATE IT",
    "gate da": "GATE DA",
    "gate ds&ai": "GATE DS&AI",
    "gate data science and artificial intelligence": "GATE DS&AI",
}

_EXAM_PIPE = re.compile(
    r"^(?P<exam>[A-Za-z&.\s]+?)\s+(?P<year>(?:19|20)\d\d)"
    r"(?P<mids>(?:\s*\|[^|]+)*?)\s*\|\s*Question:\s*(?P<qno>.+)$"
)
_SET = re.compile(r"Set[-\s]*(\d+)", re.I)
_GA_MARK = re.compile(r"\|\s*GA\b", re.I)
_LEADING_NUM = re.compile(r"(\d+(?:\.\d+)?)")


def parse_exam_ref(raw):
    """Turn an ``origin.exam`` string into paper coordinates, or None.

    Handles the shapes the GO volumes actually use::

        GATE CSE 2006 | Question: 17
        GATE CSE 2015 | Set 2 | Question: 36
        GATE CSE 2020 | GA | Question: 5
        GATE Data Science and Artificial Intelligence 2024 | Sample Paper | ...

    Returns None for anything else, and that is deliberate. Strings like
    ``GATE2012 AR: GA-5`` are Architecture papers, ``GATE2010 MN`` is Mining;
    a looser regex maps those onto GATE CSE and quietly invents questions that
    were never in the CSE paper. An unmapped question keeps its bank entry and
    simply belongs to no paper.
    """
    raw = (raw or "").strip()
    if not raw or "Practice" in raw:
        return None
    m = _EXAM_PIPE.match(raw)
    if not m:
        return None
    exam = KNOWN_EXAMS.get(" ".join(m.group("exam").split()).lower())
    if not exam:
        return None

    mids = m.group("mids") or ""
    session = ""
    hit = _SET.search(mids)
    if hit:
        session = "set-%s" % hit.group(1)
    if "Sample" in mids:
        session = "sample"

    return dict(
        exam=exam,
        year=int(m.group("year")),
        session=session,
        section="ga" if _GA_MARK.search(mids) else "core",
        qno=m.group("qno").strip(),
    )


def paper_slug(exam, year, session=""):
    bits = [exam.lower().replace("&", "and").replace(" ", "-"), str(year)]
    if session:
        bits.append(session)
    return "-".join(bits)


def paper_overrides(reload=False):
    """{slug: {...}} from content/papers.json - the hand-maintained facts."""
    if reload or "paper_overrides" not in _cache:
        data = _read_json(PAPERS_FILE, {}) or {}
        rows = data.get("papers", data if isinstance(data, list) else [])
        out = {}
        for row in rows:
            slug = row.get("slug") or paper_slug(
                row.get("exam", "GATE CSE"), row.get("year", 0), row.get("session", "")
            )
            out[slug] = dict(row, slug=slug)
        _cache["paper_overrides"] = out
    return _cache["paper_overrides"]


def _qno_sort_key(qno):
    """Order questions the way the paper printed them.

    Question numbers are messy: 17, 1.19, 2-vii, 12b, "1.19, ISRO2016-31". The
    leading number is the only part that orders reliably, so sort on that and
    fall back to the id for a stable, reproducible order.
    """
    hit = _LEADING_NUM.search(qno or "")
    return float(hit.group(1)) if hit else 9999.0


def papers(reload=False):
    """{slug: paper} reconstructed from the banks, enriched by papers.json.

    Each paper carries ``questions``: the ordered list of
    (question_id, section, paper_qno, marks) that make it up.
    """
    if not reload and "papers" in _cache:
        return _cache["papers"]

    bank = question_bank(reload)
    over = paper_overrides(reload)
    built = {}
    for q in bank.values():
        ref = parse_exam_ref((q.get("origin") or {}).get("exam"))
        if not ref:
            continue
        slug = paper_slug(ref["exam"], ref["year"], ref["session"])
        entry = built.setdefault(
            slug,
            dict(
                slug=slug,
                exam=ref["exam"],
                year=ref["year"],
                session=ref["session"],
                source_slug=q.get("source", ""),
                questions=[],
                sections={},
            ),
        )
        qno = (q.get("origin") or {}).get("paper_question") or ref["qno"]
        entry["questions"].append(
            dict(
                id=q["id"],
                # The "| GA" marker only appears from about 2014 onward. Before
                # that the subject slug is the only signal, and a GA question
                # filed under core inflates the core mark total.
                section=(
                    "ga" if q["subject"] == "general-aptitude" else ref["section"]
                ),
                paper_qno=str(qno),
                marks=float(q.get("marks") or 0),
            )
        )

    for slug, p in built.items():
        p["questions"].sort(
            key=lambda r: (
                SECTION_ORDER.get(r["section"], 9),
                _qno_sort_key(r["paper_qno"]),
                r["id"],
            )
        )
        for pos, row in enumerate(p["questions"], 1):
            row["position"] = pos
            p["sections"].setdefault(row["section"], 0)
            p["sections"][row["section"]] += 1

        o = over.get(slug, {})
        p["name"] = o.get("name") or (
            "%s %d%s"
            % (
                p["exam"],
                p["year"],
                " " + p["session"].replace("-", " ").title() if p["session"] else "",
            )
        )
        p["code"] = o.get("code", "")
        p["total_marks"] = int(o.get("total_marks", 100))
        p["duration_mins"] = int(o.get("duration_mins", 180))
        p["key_url"] = o.get("key_url", "")
        p["key_note"] = o.get("key_note", "")
        p["question_count"] = len(p["questions"])
        p["section_marks"] = dict(DEFAULT_SECTION_MARKS, **(o.get("section_marks") or {}))
        # A paper is complete when the bank holds as many questions as the paper
        # printed. Most do not: the GO volumes are subject-sliced, so a 65-mark
        # paper often arrives with 50 questions. Serving an incomplete paper as a
        # mock and calling it "out of 100" would be a lie, so flag it here and
        # let the caller decide.
        printed = o.get("printed_questions")
        p["complete"] = 1 if printed and p["question_count"] >= int(printed) else 0
        p["printed_questions"] = int(printed) if printed else 0

    # Mocks are assembled from bank questions rather than parsed out of an exam
    # reference, so they are read from their own file and appended here. Anything
    # whose questions have gone missing from the bank is skipped instead of being
    # served short.
    mock_data = _read_json(MOCKS_FILE, {}) or {}
    for row in mock_data.get("mocks", []):
        items = [r for r in row.get("questions", []) if r.get("id") in bank]
        if not items:
            continue
        p = dict(row)
        p["questions"] = []
        p["sections"] = {}
        items.sort(key=lambda r: (SECTION_ORDER.get(r.get("section"), 9), r["id"]))
        for pos, r in enumerate(items, 1):
            p["questions"].append(
                dict(
                    id=r["id"],
                    section=r.get("section", "core"),
                    paper_qno=str(pos),
                    marks=float(r.get("marks") or 0),
                    position=pos,
                )
            )
            p["sections"][r.get("section", "core")] = (
                p["sections"].get(r.get("section", "core"), 0) + 1
            )
        p["question_count"] = len(p["questions"])
        p["source_slug"] = ""
        p["key_url"] = row.get("key_url", "")
        p["section_marks"] = dict(
            DEFAULT_SECTION_MARKS, **(row.get("section_marks") or {})
        )
        printed = row.get("printed_questions") or 0
        p["printed_questions"] = int(printed)
        p["complete"] = 1 if printed and p["question_count"] >= int(printed) else 0
        built[p["slug"]] = p

    _cache["papers"] = built
    return built


def question_paper_index(reload=False):
    """{question_id: (paper_slug, position, section)} for cheap lookups."""
    if reload or "question_paper_index" not in _cache:
        idx = {}
        for slug, p in papers(reload).items():
            for row in p["questions"]:
                idx[row["id"]] = (slug, row["position"], row["section"])
        _cache["question_paper_index"] = idx
    return _cache["question_paper_index"]


def sync_papers(conn):
    """Mirror the file-derived paper list into papers/paper_sections/paper_questions.

    Runs the same way sync_sources() does: upsert everything, never delete a row
    a user's database already has. Safe to call repeatedly.
    """
    now = datetime.now().isoformat(timespec="seconds")
    live = papers()
    with conn:
        for slug, p in live.items():
            conn.execute(
                "INSERT INTO papers (slug, exam, year, session, code, name,"
                " total_marks, duration_mins, question_count, key_url, key_note,"
                " source_slug, complete, created_at, updated_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                " ON CONFLICT(slug) DO UPDATE SET exam = excluded.exam,"
                " year = excluded.year, session = excluded.session,"
                " code = excluded.code, name = excluded.name,"
                " total_marks = excluded.total_marks,"
                " duration_mins = excluded.duration_mins,"
                " question_count = excluded.question_count,"
                " key_url = excluded.key_url, key_note = excluded.key_note,"
                " source_slug = excluded.source_slug, complete = excluded.complete,"
                " updated_at = excluded.updated_at",
                (
                    slug,
                    p["exam"],
                    p["year"],
                    p["session"],
                    p["code"],
                    p["name"],
                    p["total_marks"],
                    p["duration_mins"],
                    p["question_count"],
                    p["key_url"],
                    p["key_note"],
                    p["source_slug"],
                    p["complete"],
                    now,
                    now,
                ),
            )
        ids = {r["slug"]: r["id"] for r in conn.execute("SELECT slug, id FROM papers")}

        for slug, p in live.items():
            pid = ids[slug]
            for section, count in p["sections"].items():
                conn.execute(
                    "INSERT INTO paper_sections (paper_id, section, label,"
                    " total_marks, question_count, sort_order) VALUES (?,?,?,?,?,?)"
                    " ON CONFLICT(paper_id, section) DO UPDATE SET"
                    " label = excluded.label, total_marks = excluded.total_marks,"
                    " question_count = excluded.question_count,"
                    " sort_order = excluded.sort_order",
                    (
                        pid,
                        section,
                        SECTION_LABELS.get(section, section.title()),
                        int(p["section_marks"].get(section, 0)),
                        count,
                        SECTION_ORDER.get(section, 9),
                    ),
                )
            # Drop rows this paper no longer holds. Upserting alone would leave
            # stale membership behind - regenerating a mock would accumulate both
            # the old and the new picks, so a 65-question paper would serve 129.
            keep = [r["id"] for r in p["questions"]]
            if keep:
                conn.execute(
                    "DELETE FROM paper_questions WHERE paper_id = ?"
                    " AND question_id NOT IN (%s)" % ",".join("?" * len(keep)),
                    [pid] + keep,
                )
            for row in p["questions"]:
                conn.execute(
                    "INSERT INTO paper_questions (paper_id, question_id, position,"
                    " section, paper_qno, marks) VALUES (?,?,?,?,?,?)"
                    " ON CONFLICT(paper_id, question_id) DO UPDATE SET"
                    " position = excluded.position, section = excluded.section,"
                    " paper_qno = excluded.paper_qno, marks = excluded.marks",
                    (
                        pid,
                        row["id"],
                        row["position"],
                        row["section"],
                        row["paper_qno"],
                        row["marks"],
                    ),
                )


# Bank prefixes an id may have gained. The mineru extraction replaced an earlier
# one that used bare filter1-* ids, keeping the same suffix, so history recorded
# under the old scheme is recoverable by prefixing.
ID_PREFIXES = ("mineru-",)


def remap_orphaned_question_ids(conn, prefixes=ID_PREFIXES):
    """Re-point activity rows at ids that still exist in the bank.

    A question_id is a content value, not a database key. Replacing a bank
    changes the ids, and every attempt referencing the old scheme becomes an
    orphan: the row survives, but nothing resolves it, so it stops counting
    towards a topic and disappears from the heatmap. The data is not lost, it is
    disconnected - and the person cannot tell the difference from the outside.

    A row is only rewritten when the candidate id actually exists in the bank. An
    orphan with no candidate is left alone and counted, because a wrong remap
    would credit a result to a question that was never answered.
    """
    bank = question_bank()
    tables = []
    for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ):
        cols = {r[1] for r in conn.execute('PRAGMA table_info("%s")' % row[0])}
        if "question_id" in cols:
            tables.append(row[0])

    remapped, rows_touched = 0, 0
    stuck = set()
    with conn:
        for table in sorted(tables):
            ids = [
                r[0]
                for r in conn.execute(
                    'SELECT DISTINCT question_id FROM "%s"'
                    " WHERE question_id IS NOT NULL" % table
                )
            ]
            for old in ids:
                if not old or old in bank:
                    continue
                new = next((p + old for p in prefixes if p + old in bank), None)
                if not new:
                    stuck.add(old)
                    continue
                try:
                    cur = conn.execute(
                        'UPDATE "%s" SET question_id = ? WHERE question_id = ?' % table,
                        (new, old),
                    )
                    rows_touched += cur.rowcount
                    remapped += 1
                except sqlite3.IntegrityError:
                    # A row already exists under the new id: keep it, drop the stale one.
                    conn.execute(
                        'DELETE FROM "%s" WHERE question_id = ?' % table, (old,)
                    )
    return dict(
        remapped=remapped, rows=rows_touched, unresolved=sorted(stuck)
    )


def paper_summary(conn):
    """Every paper with its sections, newest first. Mirrors source_summary()."""
    rows = [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM papers ORDER BY year DESC, session, exam"
        )
    ]
    secs = {}
    for r in conn.execute(
        "SELECT * FROM paper_sections ORDER BY paper_id, sort_order"
    ):
        secs.setdefault(r["paper_id"], []).append(dict(r))
    live = papers()
    for r in rows:
        r["sections"] = secs.get(r["id"], [])
        r["on_disk"] = r["slug"] in live
    return rows


def paper_questions(conn, slug, reveal=False):
    """The ordered questions of one paper, ready to serve as a mock."""
    row = conn.execute("SELECT * FROM papers WHERE slug = ?", (slug,)).fetchone()
    if not row:
        return None
    bank = question_bank()
    items = []
    for r in conn.execute(
        "SELECT * FROM paper_questions WHERE paper_id = ? ORDER BY position",
        (row["id"],),
    ):
        q = bank.get(r["question_id"])
        if not q:
            continue
        view = public_question(q, reveal=reveal)
        view["position_in_paper"] = r["position"]
        view["section"] = r["section"]
        view["paper_qno"] = r["paper_qno"]
        items.append(view)
    out = dict(row)
    out["questions"] = items
    out["sections"] = [
        dict(s)
        for s in conn.execute(
            "SELECT * FROM paper_sections WHERE paper_id = ? ORDER BY sort_order",
            (row["id"],),
        )
    ]
    return out


def sync_sources(conn):
    """Mirror the file-derived source list into question_sources."""
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        for s in sources().values():
            conn.execute(
                "INSERT INTO question_sources (slug, name, kind, url, licence_note,"
                " questions, created_at) VALUES (?,?,?,?,?,?,?)"
                " ON CONFLICT(slug) DO UPDATE SET name = excluded.name,"
                " kind = excluded.kind, url = excluded.url,"
                " licence_note = excluded.licence_note, questions = excluded.questions",
                (
                    s["slug"],
                    s["name"],
                    s["kind"],
                    s["url"],
                    s["licence_note"],
                    s["questions"],
                    now,
                ),
            )


def source_summary(conn):
    rows = [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM question_sources ORDER BY questions DESC, slug"
        )
    ]
    live = sources()
    for r in rows:
        r["on_disk"] = r["slug"] in live
        r["files"] = live.get(r["slug"], {}).get("files", [])
    return rows


def import_history(conn, limit=20):
    return [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM question_imports ORDER BY id DESC LIMIT ?", (limit,)
        )
    ]


def review_pending(conn, limit=50):
    rows = conn.execute(
        "SELECT * FROM question_review WHERE status = 'pending'"
        " ORDER BY confidence ASC, id ASC LIMIT ?",
        (limit,),
    ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        try:
            item["payload"] = json.loads(r["payload"])
        except ValueError:
            item["payload"] = {}
        item["issues"] = [x for x in (r["issues"] or "").split("|") if x]
        out.append(item)
    return out


def review_counts(conn):
    row = conn.execute(
        "SELECT SUM(status = 'pending') p, SUM(status = 'approved') a,"
        " SUM(status = 'rejected') r, COUNT(*) n FROM question_review"
    ).fetchone()
    return dict(
        pending=row["p"] or 0,
        approved=row["a"] or 0,
        rejected=row["r"] or 0,
        total=row["n"] or 0,
    )


# ---------------------------------------------------------------------------
# serving questions to the UI
# ---------------------------------------------------------------------------
def public_question(q, reveal=False):
    """Strip the answer unless we are showing the result."""
    out = dict(
        id=q["id"],
        subject=q["subject"],
        topic=q.get("topic", ""),
        subtopic=q.get("subtopic", ""),
        kind=q.get("kind", "dpp"),
        difficulty=q.get("difficulty", "medium"),
        type=q.get("type", "mcq"),
        marks=q.get("marks", 2),
        text=q.get("text", ""),
        options=q.get("options", []),
        tags=q.get("tags", []),
        source=q.get("source", ""),
    )
    # Image metadata, so a figure-dependent question is answerable in the UI.
    # Only ever paths: image bytes are never carried in a question payload.
    figures = public_figures(q)
    if figures:
        out["figure_assets"] = figures
    code = public_code(q)
    if code:
        out["code_blocks"] = code
    year = q.get("paper_year") or q.get("year")
    if year:
        out["year"] = year
    if q.get("paper"):
        out["paper"] = q["paper"]
        out["position_in_paper"] = q.get("position_in_paper")
        out["paper_section"] = q.get("paper_section", "core")
    if reveal:
        out["explain"] = q.get("explain", "")
        if q.get("type") == "nat":
            out["answer_value"] = q.get("answer_value")
            out["tolerance"] = q.get("tolerance", 0)
        else:
            out["answer"] = q.get("answer", [])
    return out


# ---------------------------------------------------------------------------
# seeding
# ---------------------------------------------------------------------------
DEFAULT_SETTINGS = {
    "display_name": "GATE Aspirant",
    "handle": "gate-cse",
    "bio": "One session a day. Everything else follows.",
    "location": "India",
    "exam_name": "GATE CSE",
    "daily_target_mins": "240",
    "primary_target": "barc-gate",
    "ai_provider": "none",
    "ai_model": "",
    "ai_key": "",
    "ollama_url": "http://127.0.0.1:11434",
    # planner / recommendation knobs, all user-editable from the UI
    "weak_accuracy_threshold": "62",
    "revision_grace_days": "2",
    "plan_auto_generate": "1",
    "reduced_motion": "0",
    "adaptive_difficulty": "1",
    "repeat_cooldown_days": "9",
}


def seed(conn):
    """Insert subjects/topics from syllabus.json without disturbing progress."""
    now = datetime.now().isoformat(timespec="seconds")
    data = syllabus()

    with conn:
        for order, subj in enumerate(data.get("subjects", [])):
            slug = subj["slug"]
            row = conn.execute(
                "SELECT id FROM subjects WHERE slug = ?", (slug,)
            ).fetchone()
            target_mins = int(subj.get("target_hours", 50)) * 60
            if row is None:
                cur = conn.execute(
                    "INSERT INTO subjects (slug, name, grp, marks, target_mins, sort_order, created_at)"
                    " VALUES (?,?,?,?,?,?,?)",
                    (
                        slug,
                        subj["name"],
                        subj.get("group", "core"),
                        int(subj.get("marks", 5)),
                        target_mins,
                        order,
                        now,
                    ),
                )
                subject_id = cur.lastrowid
            else:
                subject_id = row["id"]
                conn.execute(
                    "UPDATE subjects SET name = ?, grp = ?, marks = ?, sort_order = ? WHERE id = ?",
                    (
                        subj["name"],
                        subj.get("group", "core"),
                        int(subj.get("marks", 5)),
                        order,
                        subject_id,
                    ),
                )

            for t_order, topic in enumerate(subj.get("topics", [])):
                exists = conn.execute(
                    "SELECT 1 FROM topics WHERE subject_id = ? AND slug = ?",
                    (subject_id, topic["slug"]),
                ).fetchone()
                if exists:
                    conn.execute(
                        "UPDATE topics SET name = ?, weight = ?, sort_order = ?"
                        " WHERE subject_id = ? AND slug = ?",
                        (
                            topic["name"],
                            int(topic.get("weight", 1)),
                            t_order,
                            subject_id,
                            topic["slug"],
                        ),
                    )
                else:
                    conn.execute(
                        "INSERT INTO topics (subject_id, slug, name, weight, sort_order)"
                        " VALUES (?,?,?,?,?)",
                        (
                            subject_id,
                            topic["slug"],
                            topic["name"],
                            int(topic.get("weight", 1)),
                            t_order,
                        ),
                    )

                for prereq in topic.get("prereq", []) or []:
                    conn.execute(
                        "INSERT OR IGNORE INTO topic_prerequisites (topic_slug, prereq_slug,"
                        " strength) VALUES (?,?,?)",
                        (topic["slug"], prereq, 1.0),
                    )

        for key, value in DEFAULT_SETTINGS.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", (key, value)
            )

        if not conn.execute("SELECT 1 FROM settings WHERE key = 'exam_date'").fetchone():
            guess = (date.today() + timedelta(days=200)).isoformat()
            conn.execute(
                "INSERT INTO settings (key, value) VALUES ('exam_date', ?)", (guess,)
            )

    sync_sources(conn)
    sync_papers(conn)


# ---------------------------------------------------------------------------
# promotion: review queue -> live bank
# ---------------------------------------------------------------------------
REVIEWED_BANK = os.path.join(BANKS_DIR, "reviewed")


def promote_review(conn, review_id, patch=None, notes=""):
    """Approve one reviewed question and write it into the live bank.

    Approved questions land in ``content/banks/reviewed/<subject>.json`` rather
    than being edited into the original import file. That keeps the raw import
    reproducible and means a bad approval can be undone by deleting one file.
    """
    row = conn.execute(
        "SELECT * FROM question_review WHERE id = ?", (int(review_id),)
    ).fetchone()
    if not row:
        raise LookupError("That review item does not exist.")
    if row["status"] != "pending":
        raise ValueError("This item has already been %s." % row["status"])

    try:
        item = json.loads(row["payload"])
    except ValueError:
        raise ValueError("The stored payload is not readable JSON.")
    if patch:
        item.update({k: v for k, v in patch.items() if v is not None})

    subject = item.get("subject") or "misc"
    topic = item.get("topic") or ""
    subject, topic, matched = normalise_topic(
        conn, subject, topic, item.get("topic_name", "")
    )
    item["subject"] = subject
    item["topic"] = topic

    issues = validate_question(dict(item, bank="reviewed", file=""))
    blocking = [i for i in issues if i != "no explanation"]
    if blocking:
        raise ValueError("Still not servable: %s." % "; ".join(blocking))

    os.makedirs(REVIEWED_BANK, exist_ok=True)
    path = os.path.join(REVIEWED_BANK, "%s.json" % subject)
    data = _read_json(path) or {
        "subject": subject,
        "source": {
            "slug": "reviewed",
            "name": "Human-reviewed imports",
            "kind": "review",
        },
        "questions": [],
    }
    existing = {q.get("id") for q in data["questions"]}
    if item.get("id") in existing:
        data["questions"] = [q for q in data["questions"] if q.get("id") != item["id"]]
    data["questions"].append(item)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, path)

    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "UPDATE question_review SET status = 'approved', decided_at = ?,"
            " notes = ?, question_id = ? WHERE id = ?",
            (now, notes[:500], item.get("id", ""), int(review_id)),
        )
        if topic and matched:
            remember_alias(
                conn, item.get("topic_raw") or topic, subject, topic, row["source_slug"]
            )
    invalidate()
    sync_sources(conn)
    return dict(
        id=int(review_id),
        question_id=item.get("id"),
        subject=subject,
        topic=topic,
        file=os.path.relpath(path, db.BASE_DIR),
    )


def reject_review(conn, review_id, notes=""):
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        cur = conn.execute(
            "UPDATE question_review SET status = 'rejected', decided_at = ?, notes = ?"
            " WHERE id = ? AND status = 'pending'",
            (now, notes[:500], int(review_id)),
        )
    if not cur.rowcount:
        raise LookupError("Nothing pending with that id.")
    return dict(id=int(review_id), status="rejected")


def search(
    query="", subject="", topic="", qtype="", difficulty="", kind="", source="",
    paper="", subtopic="", limit=40
):
    """Bank search for the practice tab. Case-insensitive substring match."""
    q = (query or "").strip().lower()
    out = []
    for item in question_bank().values():
        if subject and item["subject"] != subject:
            continue
        if topic and item.get("topic") != topic:
            continue
        if subtopic and item.get("subtopic") != subtopic:
            continue
        if qtype and item["type"] != qtype:
            continue
        if difficulty and item["difficulty"] != difficulty:
            continue
        if kind and item["kind"] != kind:
            continue
        if source and item.get("source") != source:
            continue
        if paper and item.get("paper") != paper:
            continue
        if q:
            haystack = " ".join(
                [
                    item.get("text", ""),
                    item.get("topic", ""),
                    # Free-text search reaches the section heading too, so
                    # "banker" finds the Banker's questions whose stems only
                    # ever show an allocation table.
                    item.get("subtopic", ""),
                    item.get("subject", ""),
                    " ".join(str(t) for t in item.get("tags", [])),
                ]
            ).lower()
            if q not in haystack:
                continue
        view = public_question(item)
        view["issues"] = validate_question(item)
        view["usable"] = not [i for i in view["issues"] if i != "no explanation"]
        out.append(view)
        if len(out) >= limit:
            break
    if paper:
        # Inside one paper the printed order is the only order that makes sense.
        out.sort(key=lambda x: (x.get("position_in_paper") or 9999, x["id"]))
    else:
        out.sort(key=lambda x: (x["subject"], x["topic"], x["id"]))
    return out


def topic_graph(conn, health_rows=None):
    """Nodes and edges for the topic map: prerequisites plus current health."""
    idx = topic_index()
    health = {(r["subject"], r["topic"]): r for r in (health_rows or [])}
    nodes = []
    for (subject, topic), meta in idx.items():
        h = health.get((subject, topic)) or {}
        nodes.append(
            dict(
                id="%s/%s" % (subject, topic),
                subject=subject,
                topic=topic,
                name=meta["name"],
                subject_name=meta["subject_name"],
                weight=meta["weight"],
                marks=meta["marks"],
                health=h.get("health"),
                band=h.get("band"),
                status=h.get("status"),
                bank=h.get("bank", 0),
            )
        )
    edges = []
    for r in conn.execute("SELECT * FROM topic_prerequisites"):
        edges.append(
            dict(source=r["prereq_slug"], target=r["topic_slug"], strength=r["strength"])
        )
    return dict(
        nodes=nodes,
        edges=edges,
        note="Prerequisites come from the optional 'prereq' list on each "
        "topic in content/syllabus.json.",
    )


# ---------------------------------------------------------------------------
# pending answers
# ---------------------------------------------------------------------------
# Questions extracted from a source that did not print its answer. They live in
# the bank marked ``answer_pending`` so they count towards coverage, but the quiz
# selector will not serve them. Filling one in rewrites its bank file in place,
# which means the fix is permanent and survives a re-import.


def pending_answers(subject="", topic="", limit=50, offset=0):
    """The questions waiting on an answer, newest source first."""
    rows = []
    for q in question_bank().values():
        if not q.get("answer_pending"):
            continue
        if subject and q.get("subject") != subject:
            continue
        if topic and q.get("topic") != topic:
            continue
        rows.append(
            dict(
                id=q["id"],
                subject=q.get("subject", ""),
                topic=q.get("topic", ""),
                type=q.get("type", "mcq"),
                marks=q.get("marks", 2),
                text=q.get("text", ""),
                options=q.get("options") or [],
                figure_assets=public_figures(q),
                code_blocks=public_code(q),
                year=q.get("year") or q.get("paper_year"),
                exam=(q.get("origin") or {}).get("exam", "") or q.get("exam", ""),
                source_ref=(q.get("origin") or {}).get("ref", "")
                or q.get("source_ref", ""),
                source_file=(q.get("origin") or {}).get("file", "")
                or q.get("source_file", ""),
                needs_options=bool(q.get("needs_options")),
                note=q.get("explain") or q.get("answer_note") or "",
                file=q.get("file", ""),
                search_url=_lookup_url(q),
            )
        )
    rows.sort(key=lambda r: (r["subject"], r["topic"], r["id"]))
    return rows[offset : offset + limit] if limit else rows


def pending_counts():
    """Totals for the Bank tab header."""
    rows = pending_answers(limit=0)
    by_subject = {}
    needs_options = 0
    for r in rows:
        by_subject[r["subject"]] = by_subject.get(r["subject"], 0) + 1
        if r["needs_options"]:
            needs_options += 1
    return dict(total=len(rows), by_subject=by_subject, needs_options=needs_options)


def _lookup_url(q):
    """A ready-made search so looking the answer up is one click, not a retype."""
    bits = []
    if q.get("exam") or (q.get("origin") or {}).get("exam"):
        bits.append((q.get("origin") or {}).get("exam") or q.get("exam"))
    bits.append(" ".join((q.get("text") or "").split()[:14]))
    query = " ".join(b for b in bits if b).strip()
    try:
        from urllib.parse import quote_plus
    except ImportError:  # pragma: no cover
        from urllib import quote_plus  # type: ignore
    return "https://www.google.com/search?q=" + quote_plus(query)


def set_answer(question_id, answer=None, answer_value=None, explain="", options=None):
    """Write a looked-up answer back into the bank file that owns the question.

    Returns the updated question. Raises ValueError if the question is unknown or
    the answer does not fit the question's shape, because a silently wrong answer
    key is worse than no answer at all.
    """
    bank = question_bank()
    q = bank.get(question_id)
    if not q:
        raise ValueError("No question with id %s." % question_id)

    path = _resolve_bank_file(q.get("file", ""))
    if not path:
        raise ValueError("Cannot find the bank file for %s." % question_id)

    data = _read_json(path)
    questions = data.get("questions") if isinstance(data, dict) else data
    if not isinstance(questions, list):
        raise ValueError("Unexpected bank file layout in %s." % q.get("file"))

    target = None
    for row in questions:
        if row.get("id") == question_id:
            target = row
            break
    if target is None:
        raise ValueError("%s is not in %s any more." % (question_id, q.get("file")))

    if options:
        target["options"] = [str(o) for o in options]

    opts = target.get("options") or []
    qtype = target.get("type", "mcq")

    if answer_value is not None and str(answer_value) != "":
        target["answer_value"] = float(answer_value)
        target["type"] = "nat"
        target.pop("answer", None)
    else:
        if not opts or len(opts) < 2:
            raise ValueError(
                "This question has no options in the extracted text. Paste the "
                "options in as well, or give a numeric answer value."
            )
        idx = _answer_indices(answer, len(opts))
        if not idx:
            raise ValueError(
                "Could not read '%s' as an answer for %d options." % (answer, len(opts))
            )
        target["answer"] = idx
        target["type"] = "msq" if len(idx) > 1 else ("nat" if qtype == "nat" else "mcq")

    if explain:
        target["explain"] = explain
    elif str(target.get("explain", "")).startswith("Answer not printed"):
        target["explain"] = ""

    target.pop("answer_pending", None)
    target.pop("answer_note", None)
    target.pop("needs_options", None)

    # Back up before writing, and write atomically: filling in one answer must
    # never risk the other few hundred questions in the same file.
    _backup(path)
    _write_json_atomic(path, data)
    invalidate()
    return question_bank(reload=True).get(question_id)


def _resolve_bank_file(rel):
    """A question's ``file`` is relative to whichever bank root it came from."""
    if not rel:
        return ""
    for root in (os.path.join(CONTENT_DIR, "banks"), CONTENT_DIR, db.BASE_DIR):
        candidate = os.path.join(root, rel)
        if os.path.isfile(candidate):
            return candidate
    return ""


def _answer_indices(answer, option_count):
    """Accept 'B', 'b', '2', 'B,C', 'B;D', [1], ['B'] and so on."""
    if answer is None:
        return []
    raw = (
        answer if isinstance(answer, (list, tuple)) else re.split(r"[,;/ ]+", str(answer))
    )
    out = []
    for item in raw:
        token = str(item).strip().upper()
        if not token:
            continue
        if token.isdigit():
            n = int(token)
            # Accept both 0-based and 1-based; 1-based is what people type.
            idx = n if n < option_count and n != option_count else n - 1
            if 0 <= n < option_count and option_count > n:
                idx = n if str(item).strip().startswith("0") else (n - 1 if n >= 1 else n)
            idx = n - 1 if 1 <= n <= option_count else n
        elif len(token) == 1 and "A" <= token <= "Z":
            idx = ord(token) - ord("A")
        else:
            continue
        if 0 <= idx < option_count and idx not in out:
            out.append(idx)
    return sorted(out)


def _backup(path):
    """Timestamped copy under content/backups/ before any in-place edit."""
    import shutil
    from datetime import datetime as _dt

    backup_dir = os.path.join(db.BASE_DIR, "content", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    dest = os.path.join(
        backup_dir,
        "%s.%s.bak" % (os.path.basename(path), _dt.now().strftime("%Y%m%d-%H%M%S")),
    )
    shutil.copy2(path, dest)
    return dest


def _write_json_atomic(path, payload):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    return path
