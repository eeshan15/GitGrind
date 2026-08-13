#!/usr/bin/env python3
"""Fill in the answers that the source PDFs never printed.

The GO volumes do not print an answer for every question. Those questions are
still extracted and kept, marked ``answer_pending``, and held out of quizzes so
nothing is ever graded against a missing answer. This tool is how you clear that
backlog: it shows one question at a time, you look the answer up, you type it in,
and it is written straight back to the bank file.

    python tools/answer_fill.py --next                  work through them one by one
    python tools/answer_fill.py --next --subject dbms   only one subject
    python tools/answer_fill.py --list                  how many are pending, by subject
    python tools/answer_fill.py --show <question-id>    print one question
    python tools/answer_fill.py --set <question-id> C   set an answer directly
    python tools/answer_fill.py --set <question-id> 4.5 numeric answer for a NAT
    python tools/answer_fill.py --skip <question-id>    never ask about this one again

At the prompt: type A/B/C/D (or AC for a multi-select), a number for a NAT
question, ``s`` to skip, ``o`` to open the source reference, or ``q`` to quit.
Everything is saved as you go, so quitting never loses work.
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import ingest
from core import content as registry
from core import db as database

BANK_DIRS = [
    os.path.join(ROOT, "content", "questions"),
    os.path.join(ROOT, "content", "banks"),
]
LETTERS = "ABCDEFGH"


def bank_files():
    """Every question JSON file, wherever it lives."""
    out = []
    for base in BANK_DIRS:
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            for name in sorted(filenames):
                if name.endswith(".json"):
                    out.append(os.path.join(dirpath, name))
    return out


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def pending_items(subject_filter=None, include_skipped=False):
    """Yield (path, payload, question) for everything still awaiting an answer."""
    items = []
    for path in bank_files():
        try:
            payload = load(path)
        except (ValueError, OSError):
            continue
        subject = payload.get("subject", "")
        if subject_filter and subject != subject_filter:
            continue
        for q in payload.get("questions", []):
            # Quarantined questions already have their answer; it is the option
            # list that was destroyed. Asking for an answer cannot help them.
            if q.get("options_quarantined"):
                continue
            if not q.get("answer_pending"):
                continue
            if q.get("answer_skipped") and not include_skipped:
                continue
            items.append((path, payload, q))
    return items


def save(path, payload):
    ingest.write_json_atomic(path, payload)


def show(q, payload, index=None, total=None):
    head = "  %s" % (q.get("id") or "?")
    if index is not None:
        head = "  [%d/%d] %s" % (index, total, q.get("id") or "?")
    print("\n" + "=" * 74)
    print(head)
    meta = [
        payload.get("subject", "?"),
        q.get("topic", "?"),
        q.get("type", "mcq"),
        "%s mark" % q.get("marks", 2),
        q.get("difficulty", "medium"),
    ]
    if q.get("year"):
        meta.append(str(q["year"]))
    print("  " + " | ".join(str(m) for m in meta))
    origin = q.get("origin") or {}
    if origin:
        bits = [
            origin.get("file", ""),
            origin.get("ref", ""),
            origin.get("section", ""),
            origin.get("exam", ""),
        ]
        print("  source: " + " / ".join(b for b in bits if b))
    print("-" * 74)
    print(q.get("text", "(no text)"))
    opts = q.get("options") or []
    if opts:
        print()
        for i, opt in enumerate(opts):
            print("   %s) %s" % (LETTERS[i] if i < len(LETTERS) else i + 1, opt))
    else:
        print(
            "\n  (no options extracted - if this should be multiple choice, add "
            "them to the file by hand)"
        )
    print("=" * 74)


def apply_answer(q, raw):
    """Interpret what the user typed. Returns a description, or None if invalid."""
    raw = (raw or "").strip()
    if not raw:
        return None
    opts = q.get("options") or []

    letters = raw.replace(",", "").replace(" ", "").upper()
    if letters and all(c in LETTERS for c in letters):
        idx = [LETTERS.index(c) for c in letters]
        if opts and any(i >= len(opts) for i in idx):
            print("  There are only %d options." % len(opts))
            return None
        # Bank files store zero-based indices, not letters.
        q["answer"] = idx
        q["type"] = "mcq" if len(idx) == 1 else "msq"
        q.pop("answer_value", None)
        q.pop("answer_pending", None)
        q.pop("answer_skipped", None)
        return "answer %s" % letters

    try:
        value = float(raw)
    except ValueError:
        print("  Type A-D, a number, s to skip, o for the source, or q to quit.")
        return None

    q["answer_value"] = int(value) if value == int(value) else value
    q["type"] = "nat"
    q.pop("answer", None)
    q.pop("options", None)
    q.pop("answer_pending", None)
    q.pop("answer_skipped", None)
    return "value %s" % q["answer_value"]


def clear_note(q):
    """Drop the placeholder explanation once a real answer is in."""
    text = str(q.get("explain") or "")
    if "Answer not printed in the source" in text or "answer_fill" in text:
        q["explain"] = ""


def run_next(subject=None, include_skipped=False):
    items = pending_items(subject, include_skipped)
    if not items:
        print("\nNothing pending. Every extracted question has an answer.\n")
        return 0

    print("\n%d question(s) awaiting an answer." % len(items))
    print("Look each one up, then type the answer. Saved as you go; q quits.\n")

    done = 0
    dirty = {}
    for n, (path, payload, q) in enumerate(items, start=1):
        show(q, payload, n, len(items))
        while True:
            try:
                raw = input("  answer > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  stopping.")
                for p, pl in dirty.items():
                    save(p, pl)
                print("  filled %d answer(s)." % done)
                return 0

            low = raw.lower()
            if low in ("q", "quit", "exit"):
                for p, pl in dirty.items():
                    save(p, pl)
                print("\n  filled %d answer(s). Run again any time.\n" % done)
                return 0
            if low in ("s", "skip", ""):
                break
            if low in ("x", "never"):
                q["answer_skipped"] = True
                dirty[path] = payload
                print("  will not ask again.")
                break
            if low in ("o", "open", "src", "source"):
                print("  %s" % json.dumps(q.get("origin") or {}, indent=2))
                continue

            result = apply_answer(q, raw)
            if result:
                clear_note(q)
                dirty[path] = payload
                save(path, payload)  # save immediately, not just at the end
                dirty.pop(path, None)
                done += 1
                print("  saved: %s" % result)
                break

    for p, pl in dirty.items():
        save(p, pl)
    print("\n  filled %d answer(s).\n" % done)
    return 0


def run_list():
    items = pending_items(include_skipped=True)
    if not items:
        print("\nNothing pending.\n")
        return 0
    by_subject = {}
    skipped = 0
    for _path, payload, q in items:
        if q.get("answer_skipped"):
            skipped += 1
            continue
        key = payload.get("subject") or "(unsorted)"
        by_subject[key] = by_subject.get(key, 0) + 1

    print("\n  questions awaiting an answer\n")
    for subject, n in sorted(by_subject.items(), key=lambda kv: -kv[1]):
        print("    %-32s %5d" % (subject, n))
    print("    %-32s %5d" % ("TOTAL", sum(by_subject.values())))
    if skipped:
        print(
            "\n    %d marked 'never ask again' (see --next --include-skipped)" % skipped
        )
    print("\n  fill them in with: python tools/answer_fill.py --next\n")
    return 0


def find_one(question_id):
    for path in bank_files():
        try:
            payload = load(path)
        except (ValueError, OSError):
            continue
        for q in payload.get("questions", []):
            if q.get("id") == question_id:
                return path, payload, q
    return None, None, None


def main():
    ap = argparse.ArgumentParser(
        description="Fill in answers the source PDFs did not print."
    )
    ap.add_argument("--next", action="store_true", help="work through them one by one")
    ap.add_argument("--list", action="store_true", help="counts by subject")
    ap.add_argument("--subject", help="restrict to one subject slug")
    ap.add_argument(
        "--include-skipped",
        action="store_true",
        help="also revisit ones marked 'never ask again'",
    )
    ap.add_argument("--show", metavar="ID", help="print one question")
    ap.add_argument(
        "--set",
        nargs=2,
        metavar=("ID", "ANSWER"),
        help="set an answer without the prompt",
    )
    ap.add_argument("--skip", metavar="ID", help="never ask about this one again")
    args = ap.parse_args()

    if args.show or args.set or args.skip:
        qid = args.show or args.skip or args.set[0]
        path, payload, q = find_one(qid)
        if not q:
            print("No question with id %r." % qid)
            return 1
        if args.show:
            show(q, payload)
            return 0
        if args.skip:
            q["answer_skipped"] = True
            save(path, payload)
            print("Skipped %s." % qid)
            return 0
        result = apply_answer(q, args.set[1])
        if not result:
            return 1
        clear_note(q)
        save(path, payload)
        print("%s: %s" % (qid, result))
        return 0

    if args.list:
        return run_list()
    if args.next:
        code = run_next(args.subject, args.include_skipped)
        # Report where the bank stands afterwards.
        conn = database.init()
        try:
            registry.seed(conn)
            registry.invalidate()
            stats = registry.bank_stats(reload=True)
            print(
                "  bank: %d questions, %d%% usable, %d%% topic coverage\n"
                % (stats["total"], stats["health_pct"], stats["coverage_pct"])
            )
        finally:
            conn.close()
        return code

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
