#!/usr/bin/env python3
"""Ingestion backbone shared by the importer and the review tools.

``import_questions.py`` knows how to *parse* a paper. This module knows how to
get parsed questions safely into the bank:

* **Source registry** - every import declares where it came from, and that
  source is recorded in ``question_sources`` with a trust level and a URL.
* **Manifests** - each run writes ``content/imports/<stamp>.json`` describing
  exactly what was found, matched, rejected and written. An import is therefore
  reproducible and reviewable after the fact.
* **Duplicate detection** - exact match on a normalised text hash, plus a
  near-duplicate check using token shingles, run against the live bank *and*
  against the batch itself.
* **Review queue in the database** - low-confidence items go to
  ``question_review`` where the UI can approve or reject them, instead of a
  loose JSON file nobody opens.
* **Safety** - target files are backed up before being touched and written
  atomically, so a crashed or bad import can never leave a half-written bank.

Run standalone for maintenance:

    python tools/ingest.py --sources                list registered sources
    python tools/ingest.py --register go-pdfs "GO PDFs" --kind release --url ...
    python tools/ingest.py --review                 show the pending review queue
    python tools/ingest.py --approve 12             approve one review item
    python tools/ingest.py --reject 12 --note "bad OCR"
    python tools/ingest.py --imports                show the import log
    python tools/ingest.py --dedupe                 report duplicates in the bank
    python tools/ingest.py --gaps                   underrepresented topics
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core import content, db

IMPORT_DIR = os.path.join(ROOT, "content", "imports")
BACKUP_DIR = os.path.join(ROOT, "content", "backups")

# Below this, an item goes to review instead of the live bank.
CONFIDENCE_FLOOR = 0.55
# Jaccard similarity above this counts as a near-duplicate.
NEAR_DUPLICATE = 0.86

SOURCE_KINDS = ("official", "release", "manual", "review", "book", "other")


# ---------------------------------------------------------------------------
# normalisation and hashing
# ---------------------------------------------------------------------------
def normalise_text(text):
    """Collapse whitespace, strip punctuation and digits-in-words for hashing."""
    t = str(text or "").lower()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[^a-z0-9 ]+", "", t)
    return t.strip()


def text_hash(question):
    """Stable fingerprint of a question's identity: stem plus its options."""
    parts = [normalise_text(question.get("text", ""))]
    for opt in question.get("options") or []:
        parts.append(normalise_text(opt))
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()


def shingles(text, size=4):
    words = normalise_text(text).split()
    if len(words) < size:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i : i + size]) for i in range(len(words) - size + 1)}


def similarity(a, b):
    sa, sb = shingles(a), shingles(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / float(len(sa | sb))


# ---------------------------------------------------------------------------
# source registry
# ---------------------------------------------------------------------------
def register_source(conn, slug, name, kind="manual", url="", licence_note="", trust=0.7):
    if kind not in SOURCE_KINDS:
        raise ValueError("kind must be one of: %s" % ", ".join(SOURCE_KINDS))
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "INSERT INTO question_sources (slug, name, kind, url, licence_note,"
            " trust, created_at) VALUES (?,?,?,?,?,?,?)"
            " ON CONFLICT(slug) DO UPDATE SET name = excluded.name,"
            " kind = excluded.kind, url = excluded.url,"
            " licence_note = excluded.licence_note, trust = excluded.trust",
            (slug, name, kind, url, licence_note, float(trust), now),
        )
    return dict(slug=slug, name=name, kind=kind, url=url, trust=trust)


def touch_source(conn, slug, field="last_import_at"):
    if field not in ("last_import_at", "last_fetch_at"):
        return
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "UPDATE question_sources SET %s = ? WHERE slug = ?" % field, (now, slug)
        )


def list_sources(conn):
    return content.source_summary(conn)


# ---------------------------------------------------------------------------
# import logging
# ---------------------------------------------------------------------------
def open_import(conn, source_slug, input_path, dry_run=True):
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        cur = conn.execute(
            "INSERT INTO question_imports (source_slug, input_path, dry_run, status,"
            " started_at) VALUES (?,?,?,?,?)",
            (source_slug or "", input_path or "", 1 if dry_run else 0, "running", now),
        )
    return cur.lastrowid


def close_import(conn, import_id, counts, manifest_path="", log="", status="done"):
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "UPDATE question_imports SET found = ?, matched = ?, needs_review = ?,"
            " rejected = ?, duplicates = ?, promoted = ?, manifest = ?, log = ?,"
            " status = ?, finished_at = ? WHERE id = ?",
            (
                counts.get("found", 0),
                counts.get("matched", 0),
                counts.get("needs_review", 0),
                counts.get("rejected", 0),
                counts.get("duplicates", 0),
                counts.get("promoted", 0),
                manifest_path,
                log[:8000],
                status,
                now,
                int(import_id),
            ),
        )


def write_manifest(payload, stamp=None):
    """Persist the full record of one import run. Returns the relative path."""
    os.makedirs(IMPORT_DIR, exist_ok=True)
    stamp = stamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(IMPORT_DIR, "%s.json" % stamp)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, path)
    return os.path.relpath(path, ROOT)


def import_log(conn, limit=30):
    return content.import_history(conn, limit)


# ---------------------------------------------------------------------------
# duplicate detection
# ---------------------------------------------------------------------------
def bank_fingerprints():
    """{hash: question_id} and [(id, text)] for the live bank."""
    by_hash = {}
    texts = []
    for q in content.question_bank().values():
        by_hash.setdefault(text_hash(q), q["id"])
        texts.append((q["id"], q.get("text", ""), q.get("subject", "")))
    return by_hash, texts


def find_duplicates(items, by_hash=None, texts=None, near=True):
    """Tag each item as new / exact-duplicate / near-duplicate.

    Checks the live bank and the incoming batch, so importing the same PDF twice
    in one command is caught too.
    """
    if by_hash is None or texts is None:
        by_hash, texts = bank_fingerprints()
    by_hash = dict(by_hash)
    texts = list(texts)

    out = []
    for q in items:
        h = text_hash(q)
        verdict = dict(id=q.get("id"), status="new", duplicate_of=None, similarity=None)
        if h in by_hash:
            verdict.update(status="exact", duplicate_of=by_hash[h], similarity=1.0)
        elif near and q.get("text"):
            best, score = None, 0.0
            subject = q.get("subject", "")
            for qid, text, qsubject in texts:
                # Only compare within a subject when we know one; it is 30x faster
                # and cross-subject near-duplicates are almost always false.
                if subject and qsubject and subject != qsubject:
                    continue
                s = similarity(q["text"], text)
                if s > score:
                    best, score = qid, s
            if score >= NEAR_DUPLICATE:
                verdict.update(
                    status="near", duplicate_of=best, similarity=round(score, 3)
                )
        if verdict["status"] == "new":
            by_hash[h] = q.get("id")
            texts.append((q.get("id"), q.get("text", ""), q.get("subject", "")))
        out.append(verdict)
    return out


def dedupe_report():
    """Duplicates already sitting inside the live bank."""
    seen = {}
    dupes = []
    for q in content.question_bank().values():
        h = text_hash(q)
        if h in seen:
            dupes.append(
                dict(id=q["id"], same_as=seen[h], file=q["file"], subject=q["subject"])
            )
        else:
            seen[h] = q["id"]
    return dupes


# ---------------------------------------------------------------------------
# confidence
# ---------------------------------------------------------------------------
def score_confidence(q, keyword_score=None, tag_source=None):
    """0..1 confidence that this question is correctly parsed and tagged.

    Written as an explicit additive model rather than a magic number so the
    dry-run report can explain why something went to review.
    """
    reasons = []
    c = 0.5

    if tag_source in ("section", "title", "chapter", "tag"):
        c += 0.30
        reasons.append("topic came from the source's own structure")
    elif keyword_score is not None:
        if keyword_score >= 8:
            c += 0.22
            reasons.append("strong keyword match (%.1f)" % keyword_score)
        elif keyword_score >= 5:
            c += 0.10
            reasons.append("moderate keyword match (%.1f)" % keyword_score)
        else:
            c -= 0.12
            reasons.append("thin keyword match (%.1f)" % keyword_score)
    else:
        c -= 0.20
        reasons.append("no topic evidence at all")

    qtype = q.get("type", "mcq")
    if qtype == "nat":
        if q.get("answer_value") is not None:
            c += 0.10
            reasons.append("NAT with a parsed answer value")
        else:
            c -= 0.28
            reasons.append("NAT with no answer value")
    else:
        opts = q.get("options") or []
        if len(opts) >= 4:
            c += 0.10
            reasons.append("four options extracted")
        elif len(opts) < 2:
            c -= 0.30
            reasons.append("fewer than two options")
        if q.get("answer"):
            c += 0.12
            reasons.append("answer key matched")
        else:
            c -= 0.18
            reasons.append("no answer key")

    text = q.get("text") or ""
    if len(text) < 40:
        c -= 0.20
        reasons.append("suspiciously short stem")
    if re.search(r"(figure|diagram|table|graph shown|following circuit)", text, re.I):
        c -= 0.22
        reasons.append("refers to a figure that text extraction drops")
    if text.count("$") > 3 or "\\frac" in text:
        c -= 0.10
        reasons.append("maths markup may have survived badly")

    return max(0.0, min(1.0, round(c, 3))), reasons


# ---------------------------------------------------------------------------
# review queue (database)
# ---------------------------------------------------------------------------
def queue_for_review(conn, items, import_id=None, source_slug=""):
    """Push low-confidence items into question_review. Returns how many landed."""
    now = datetime.now().isoformat(timespec="seconds")
    added = 0
    with conn:
        for entry in items:
            q = (
                entry["question"]
                if isinstance(entry, dict) and "question" in entry
                else entry
            )
            issues = entry.get("issues", []) if isinstance(entry, dict) else []
            conf = entry.get("confidence", 0.0) if isinstance(entry, dict) else 0.0
            qid = q.get("id", "")
            exists = conn.execute(
                "SELECT 1 FROM question_review WHERE question_id = ? AND status = 'pending'",
                (qid,),
            ).fetchone()
            if exists:
                continue
            conn.execute(
                "INSERT INTO question_review (import_id, source_slug, question_id,"
                " payload, confidence, issues, status, created_at)"
                " VALUES (?,?,?,?,?,?, 'pending', ?)",
                (
                    import_id,
                    source_slug,
                    qid,
                    json.dumps(q),
                    float(conf),
                    "|".join(issues)[:1000],
                    now,
                ),
            )
            added += 1
    return added


def show_review(conn, limit=20):
    items = content.review_pending(conn, limit)
    if not items:
        print("Review queue is empty.")
        return 0
    counts = content.review_counts(conn)
    print(
        "\n  %d pending, %d approved, %d rejected\n"
        % (counts["pending"], counts["approved"], counts["rejected"])
    )
    for it in items:
        q = it["payload"]
        print(
            "  [%d] %-24s conf %.2f  %s"
            % (
                it["id"],
                it["question_id"] or "-",
                it["confidence"],
                ", ".join(it["issues"])[:60],
            )
        )
        print("      %s" % (q.get("text", "")[:120]))
        for i, opt in enumerate(q.get("options") or []):
            print("        %s) %s" % ("ABCD"[i] if i < 4 else i, str(opt)[:70]))
        print()
    print("  Approve with:  python tools/ingest.py --approve <id>")
    print('  Reject with:   python tools/ingest.py --reject <id> --note "why"')
    print()
    return 0


# ---------------------------------------------------------------------------
# safe writing
# ---------------------------------------------------------------------------
def backup_file(path):
    """Copy a bank file aside before it is modified. Returns the backup path."""
    if not os.path.isfile(path):
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = os.path.join(BACKUP_DIR, "%s.%s.bak" % (os.path.basename(path), stamp))
    shutil.copy2(path, dest)
    return os.path.relpath(dest, ROOT)


def write_json_atomic(path, payload):
    """Write to a temp file then rename, so a crash never truncates the bank."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    return path


def prune_backups(keep=20):
    if not os.path.isdir(BACKUP_DIR):
        return 0
    files = sorted(
        (
            os.path.join(BACKUP_DIR, f)
            for f in os.listdir(BACKUP_DIR)
            if f.endswith(".bak")
        ),
        key=os.path.getmtime,
        reverse=True,
    )
    removed = 0
    for path in files[keep:]:
        try:
            os.remove(path)
            removed += 1
        except OSError:
            pass
    return removed


# ---------------------------------------------------------------------------
# gaps
# ---------------------------------------------------------------------------
def gaps_report(limit=25):
    """Which syllabus topics the bank under-serves, weighted by exam marks."""
    stats = content.bank_stats(reload=True)
    return dict(
        total=stats["total"],
        health_pct=stats["health_pct"],
        coverage_pct=stats["coverage_pct"],
        empty=stats["empty_topics"][:limit],
        thin=stats["thin_topics"][:limit],
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="GitGrind ingestion backbone.")
    ap.add_argument("--sources", action="store_true", help="list registered sources")
    ap.add_argument(
        "--register",
        nargs=2,
        metavar=("SLUG", "NAME"),
        help="register or update a source",
    )
    ap.add_argument("--kind", default="manual", choices=SOURCE_KINDS)
    ap.add_argument("--url", default="")
    ap.add_argument("--licence", default="", help="licence or permission note")
    ap.add_argument("--trust", type=float, default=0.7)
    ap.add_argument("--review", action="store_true", help="show the pending review queue")
    ap.add_argument("--approve", type=int, metavar="ID")
    ap.add_argument("--reject", type=int, metavar="ID")
    ap.add_argument("--note", default="", help="note stored with an approve/reject")
    ap.add_argument("--imports", action="store_true", help="show the import log")
    ap.add_argument("--dedupe", action="store_true", help="report duplicates in the bank")
    ap.add_argument("--gaps", action="store_true", help="report underrepresented topics")
    ap.add_argument("--prune-backups", type=int, nargs="?", const=20, metavar="KEEP")
    args = ap.parse_args()

    conn = db.init()
    try:
        content.seed(conn)

        if args.register:
            slug, name = args.register
            out = register_source(
                conn, slug, name, args.kind, args.url, args.licence, args.trust
            )
            print("Registered %s (%s)." % (out["name"], out["slug"]))
            return 0

        if args.sources:
            rows = list_sources(conn)
            if not rows:
                print("No sources registered yet.")
                return 0
            print()
            print("  %-16s %-30s %-9s %6s  %s" % ("slug", "name", "kind", "qs", "url"))
            for r in rows:
                print(
                    "  %-16s %-30s %-9s %6d  %s"
                    % (
                        r["slug"][:16],
                        r["name"][:30],
                        r["kind"],
                        r["questions"],
                        (r["url"] or "")[:40],
                    )
                )
            print()
            return 0

        if args.review:
            return show_review(conn)

        if args.approve:
            out = content.promote_review(conn, args.approve, notes=args.note)
            print(
                "Approved %s -> %s/%s (%s)"
                % (out["question_id"], out["subject"], out["topic"], out["file"])
            )
            return 0

        if args.reject:
            content.reject_review(conn, args.reject, notes=args.note)
            print("Rejected review item %d." % args.reject)
            return 0

        if args.imports:
            rows = import_log(conn)
            if not rows:
                print("No imports logged yet.")
                return 0
            print()
            print(
                "  %-4s %-14s %-18s %6s %6s %6s %6s %5s"
                % ("id", "source", "started", "found", "ok", "review", "dupes", "dry")
            )
            for r in rows:
                print(
                    "  %-4d %-14s %-18s %6d %6d %6d %6d %5s"
                    % (
                        r["id"],
                        (r["source_slug"] or "-")[:14],
                        (r["started_at"] or "")[:16],
                        r["found"],
                        r["matched"],
                        r["needs_review"],
                        r["duplicates"],
                        "yes" if r["dry_run"] else "no",
                    )
                )
            print()
            return 0

        if args.dedupe:
            dupes = dedupe_report()
            if not dupes:
                print("No duplicate questions found in the bank.")
                return 0
            print("\n  %d duplicate question(s):\n" % len(dupes))
            for d in dupes:
                print("    %-24s same as %-24s (%s)" % (d["id"], d["same_as"], d["file"]))
            print()
            return 0

        if args.gaps:
            rep = gaps_report()
            print()
            print(
                "  bank %d questions, %d%% health, %d%% topic coverage"
                % (rep["total"], rep["health_pct"], rep["coverage_pct"])
            )
            if rep["empty"]:
                print("\n  topics with no questions (highest exam weight first):")
                for t in rep["empty"]:
                    print(
                        "    %-46s %2d marks, weight %d"
                        % ("%s/%s" % (t["subject"], t["topic"]), t["marks"], t["weight"])
                    )
            if rep["thin"]:
                print("\n  topics with fewer than four questions:")
                for t in rep["thin"]:
                    print(
                        "    %-46s %d question(s)"
                        % ("%s/%s" % (t["subject"], t["topic"]), t["count"])
                    )
            print()
            return 0

        if args.prune_backups is not None:
            n = prune_backups(args.prune_backups)
            print("Removed %d old backup(s)." % n)
            return 0

        ap.print_help()
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
