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
    item.setdefault("subtopic", "")
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
        files=sorted({q["file"] for q in bank.values()}),
        banks=sorted({q["bank"] for q in bank.values()}),
        sources=[dict(s, files=len(s["files"])) for s in src.values()],
        topics_total=len(idx),
        topics_empty=len(empty_topics),
        empty_topics=empty_topics[:24],
        thin_topics=thin_topics[:24],
    )


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
    query="", subject="", topic="", qtype="", difficulty="", kind="", source="", limit=40
):
    """Bank search for the practice tab. Case-insensitive substring match."""
    q = (query or "").strip().lower()
    out = []
    for item in question_bank().values():
        if subject and item["subject"] != subject:
            continue
        if topic and item.get("topic") != topic:
            continue
        if qtype and item["type"] != qtype:
            continue
        if difficulty and item["difficulty"] != difficulty:
            continue
        if kind and item["kind"] != kind:
            continue
        if source and item.get("source") != source:
            continue
        if q:
            haystack = " ".join(
                [
                    item.get("text", ""),
                    item.get("topic", ""),
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
