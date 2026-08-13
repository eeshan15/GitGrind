#!/usr/bin/env python3
"""Apply mock-paper support to core/content.py and core/quiz.py.

CRLF-safe and idempotent: an edit already present is skipped, so re-running is
harmless. Run from the repo root:  python patch_mocks.py
"""
import io, os, sys

EDITS = [
    ('core/content.py',
     'PAPERS_FILE = os.path.join(CONTENT_DIR, "papers.json")',
     'PAPERS_FILE = os.path.join(CONTENT_DIR, "papers.json")\n# Generated mock papers. They are papers in every sense the app cares about, so\n# they are merged into papers() rather than bolted on as a parallel concept.\nMOCKS_FILE = os.path.join(CONTENT_DIR, "mocks.json")'),
    ('core/content.py',
     '    _cache["papers"] = built',
     '    # Mocks are assembled from bank questions rather than parsed out of an exam\n    # reference, so they are read from their own file and appended here. Anything\n    # whose questions have gone missing from the bank is skipped instead of being\n    # served short.\n    mock_data = _read_json(MOCKS_FILE, {}) or {}\n    for row in mock_data.get("mocks", []):\n        items = [r for r in row.get("questions", []) if r.get("id") in bank]\n        if not items:\n            continue\n        p = dict(row)\n        p["questions"] = []\n        p["sections"] = {}\n        items.sort(key=lambda r: (SECTION_ORDER.get(r.get("section"), 9), r["id"]))\n        for pos, r in enumerate(items, 1):\n            p["questions"].append(\n                dict(\n                    id=r["id"],\n                    section=r.get("section", "core"),\n                    paper_qno=str(pos),\n                    marks=float(r.get("marks") or 0),\n                    position=pos,\n                )\n            )\n            p["sections"][r.get("section", "core")] = (\n                p["sections"].get(r.get("section", "core"), 0) + 1\n            )\n        p["question_count"] = len(p["questions"])\n        p["source_slug"] = ""\n        p["key_url"] = row.get("key_url", "")\n        p["section_marks"] = dict(\n            DEFAULT_SECTION_MARKS, **(row.get("section_marks") or {})\n        )\n        printed = row.get("printed_questions") or 0\n        p["printed_questions"] = int(printed)\n        p["complete"] = 1 if printed and p["question_count"] >= int(printed) else 0\n        built[p["slug"]] = p\n\n    _cache["papers"] = built'),
    ('core/content.py',
     '            for row in p["questions"]:\n                conn.execute(\n                    "INSERT INTO paper_questions (paper_id, question_id, position,"',
     '            # Drop rows this paper no longer holds. Upserting alone would leave\n            # stale membership behind - regenerating a mock would accumulate both\n            # the old and the new picks, so a 65-question paper would serve 129.\n            keep = [r["id"] for r in p["questions"]]\n            if keep:\n                conn.execute(\n                    "DELETE FROM paper_questions WHERE paper_id = ?"\n                    " AND question_id NOT IN (%s)" % ",".join("?" * len(keep)),\n                    [pid] + keep,\n                )\n            for row in p["questions"]:\n                conn.execute(\n                    "INSERT INTO paper_questions (paper_id, question_id, position,"'),
    ('core/quiz.py',
     'import json\nimport random',
     'import json\nimport random\nimport sqlite3'),
    ('core/quiz.py',
     'def select(',
     'def reserved_for_mocks(conn):\n    """Question ids belonging to a generated mock paper."""\n    try:\n        return {\n            r["question_id"]\n            for r in conn.execute(\n                "SELECT pq.question_id FROM paper_questions pq"\n                " JOIN papers p ON p.id = pq.paper_id"\n                " WHERE p.exam = \'GitGrind Mock\'"\n            )\n        }\n    except sqlite3.Error:\n        # A database that predates the papers tables must still serve practice.\n        return set()\n\n\ndef select('),
    ('core/quiz.py',
     '    """Return [(question, reason)] chosen for one purpose. Never raises on empty."""',
     '    """Return [(question, reason)] chosen for one purpose. Never raises on empty."""\n    # Questions held by a mock paper stay out of practice, so sitting a mock is\n    # not a re-run of what you already saw. This is a query, not a partition:\n    # delete a mock and its questions come straight back into the pool.\n    exclude = set(exclude or []) | reserved_for_mocks(conn)'),
    ('core/quiz.py',
     '    total_marks = sum(q.get("marks", 2) for q in chosen)',
     '    if paper_id:\n        # A paper carries its own mark per question. For a mock those values were\n        # assigned to make the paper total 100, which the bank\'s own marks field\n        # cannot do - most of it is an importer default. Sitting the paper must\n        # score against the paper, not against the bank.\n        paper_marks = {\n            r["question_id"]: r["marks"]\n            for r in conn.execute(\n                "SELECT question_id, marks FROM paper_questions WHERE paper_id = ?",\n                (paper_id,),\n            )\n        }\n        for q in chosen:\n            if q["id"] in paper_marks:\n                q["marks"] = paper_marks[q["id"]]\n    total_marks = sum(q.get("marks", 2) for q in chosen)'),
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
            print("  skip    %-20s already applied" % path)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d times, expected 1" % (path, s.count(o)))
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-20s ok" % path)
        changed += 1
    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())