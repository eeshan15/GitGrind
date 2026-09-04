#!/usr/bin/env python3
"""Trace one question's whole history, to settle a repeat report with facts.

Five mechanisms have been ruled out by measurement - topic-level cooldown
bypass (2 questions), served-but-unsubmitted sets (14), the scoring (4 repeats
in 150 picks, none inside cooldown), consecutive-build overlap (0 outside one
retry set), and resume (an explicit modal, offered once per load). The build
path does not repeat, and the whole quiz_questions history has 8 questions in
two sets and none in three.

That does not prove nothing is wrong; it proves the guessing should stop. So
this exists for the next time it happens: give it the question, and it says
exactly how many times that question has been served, in which sets, under
which purpose, whether it was answered, whether it is enrolled for revision and
overdue, and which rule would let it past the cooldown right now.

    python tools/trace_question.py mineru-filter1-volume3-5-25-16
    python tools/trace_question.py "carry lookahead adder"

A search term matches against question text and picks the single hit, or lists
the candidates if there are several.

Note one limitation up front: quiz_questions arrived in migration M10, so sets
built before it have a quizzes row but no question rows. Here that is 36 of 52
quizzes. "Served in N sets" therefore counts only what is recorded, and for
anything older the attempts table is the better witness.

Read-only. Run from the repo root.
"""
import os
import sys

sys.path.insert(0, os.getcwd())

try:
    from core import content, db, quiz
except ImportError as exc:
    sys.exit("cannot import core - run this from the repo root (%s)" % exc)


def columns(conn, table):
    """Column names actually present, so a query cannot ask for a missing one.

    quizzes gained mode, purpose, plan_day and dpp_set_id in later migrations,
    and a database that has not run them all should still be traceable rather
    than crashing on a SELECT.
    """
    return {r["name"] for r in conn.execute("PRAGMA table_info(%s)" % table)}


def find(bank, term):
    if term in bank:
        return term
    needle = term.lower()
    hits = [
        qid for qid, q in bank.items()
        if needle in (q.get("text") or "").lower() or needle in qid.lower()
    ]
    if not hits:
        sys.exit("nothing matches %r" % term)
    if len(hits) > 1:
        print("  %d questions match. Pick one:\n" % len(hits))
        for qid in hits[:15]:
            print("  %-38s %s" % (qid, (bank[qid].get("text") or "")[:70]))
        sys.exit(0)
    return hits[0]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip().splitlines()[0] + "\n\nUsage: "
                 "python tools/trace_question.py <question-id or search text>")
    bank = content.question_bank()
    if not bank:
        sys.exit("question bank is empty")
    qid = find(bank, " ".join(sys.argv[1:]))
    q = bank[qid]

    conn = db.connect()
    try:
        settings = db.get_settings(conn)
        cooldown = db.setting_int(settings, "repeat_cooldown_days",
                                  quiz.DEFAULT_COOLDOWN_DAYS)

        print("\n=== question ===")
        print("  id        %s" % qid)
        print("  where     %s / %s / %s"
              % (q["subject"], q.get("topic") or "-", q.get("subtopic") or "-"))
        print("  kind      %s, %s, %s marks"
              % (q.get("kind"), q.get("difficulty"), q.get("marks")))
        print("  text      %s" % (q.get("text") or "")[:90].replace("\n", " "))

        st = (quiz.question_stats(conn)).get(qid) or {}
        print("\n=== attempts ===")
        if not st:
            print("  never answered. No question_stats row, so the cooldown has")
            print("  no record of it and will not hold it back.")
        else:
            print("  times answered      %s" % st.get("usage_count"))
            print("  correct             %s" % st.get("correct_count"))
            print("  last attempt        %s  (%d day(s) ago)"
                  % (st.get("last_attempt_day"),
                     quiz._days_since(st.get("last_attempt_day"))))
            print("  last correct        %s" % (st.get("last_correct_day") or "-"))
            print("  last wrong          %s" % (st.get("last_wrong_day") or "-"))
        acols = columns(conn, "attempts")
        pick = [c for c in ("day", "correct", "seconds", "quiz_id", "source")
                if c in acols]
        order = " ORDER BY day" if "day" in acols else ""
        rows = list(conn.execute(
            "SELECT %s FROM attempts WHERE question_id = ?%s"
            % (", ".join(pick), order), (qid,)))
        for r in rows:
            bits = []
            for c in pick:
                if c == "correct":
                    bits.append("correct" if r[c] else "wrong")
                else:
                    bits.append("%s=%s" % (c, r[c]))
            print("    " + "  ".join(bits))

        print("\n=== served in these sets ===")
        have = columns(conn, "quizzes")
        extra = [c for c in ("mode", "purpose", "source") if c in have]
        cols = ", ".join("z." + c for c in ["id", "created_at", "finished_at"] + extra)
        served = list(conn.execute(
            "SELECT %s, qq.position FROM quiz_questions qq"
            " JOIN quizzes z ON z.id = qq.quiz_id"
            " WHERE qq.question_id = ? ORDER BY z.id" % cols, (qid,)))
        if not served:
            print("  none recorded. Either it has never been served, or every")
            print("  set that held it predates the quiz_questions table.")
        for r in served:
            tags = " ".join(str(r[c] or "-") for c in extra)
            print("  quiz %-5d pos %-3s %-16s %-10s %s"
                  % (r["id"], r["position"], (r["created_at"] or "")[:16],
                     "finished" if r["finished_at"] else "ABANDONED", tags))

        print("\n=== revision queue ===")
        rq = list(conn.execute(
            "SELECT item_type, item_key, subject_slug, topic_slug, due_day,"
            " strength, lapses, active FROM revision_queue"
            " WHERE (item_type = 'question' AND item_key = ?)"
            "    OR (item_type != 'question' AND subject_slug = ? AND topic_slug = ?)",
            (qid, q["subject"], q.get("topic", ""))))
        if not rq:
            print("  neither the question nor its topic is enrolled.")
        for r in rq:
            overdue = quiz._days_since(r["due_day"])
            scope = "this question" if r["item_type"] == "question" else "its topic"
            print("  %-14s due %s  %s  strength %s  lapses %s  %s"
                  % (scope, r["due_day"],
                     ("%d day(s) overdue" % overdue) if overdue > 0 else "not yet due",
                     r["strength"], r["lapses"],
                     "active" if r["active"] else "inactive"))

        print("\n=== would the cooldown hold it right now ===")
        seen = int(st.get("usage_count") or 0)
        since = quiz._days_since(st.get("last_attempt_day"))
        due_q = {r["item_key"] for r in conn.execute(
            "SELECT item_key FROM revision_queue WHERE active = 1"
            " AND item_type = 'question' AND due_day <= date('now')")}
        due_t = {(r["subject_slug"], r["topic_slug"]) for r in conn.execute(
            "SELECT subject_slug, topic_slug FROM revision_queue WHERE active = 1"
            " AND item_type != 'question' AND due_day <= date('now')")}
        is_due = qid in due_q or (q["subject"], q.get("topic", "")) in due_t
        reserved = qid in quiz.reserved_for_mocks(conn)

        print("  cooldown            %d day(s)" % cooldown)
        print("  seen / days since   %d / %s" % (seen, since if seen else "n/a"))
        print("  exempt as due       %s%s" % (
            is_due,
            "  (question)" if qid in due_q else
            "  (topic only)" if is_due else ""))
        print("  held by a mock      %s" % reserved)
        if reserved:
            print("\n  Reserved for a mock paper, so practice will not serve it.")
        elif not seen:
            print("\n  Never answered, so nothing is holding it - it can appear.")
        elif since >= cooldown:
            print("\n  Older than the cooldown, so it is eligible again. That is")
            print("  the cooldown expiring, not a fault.")
        elif is_due:
            print("\n  Inside the cooldown but exempt because it is due for")
            print("  revision. If it was answered wrongly, re-serving it is the")
            print("  point. If it was answered correctly, that is worth a look.")
        else:
            print("\n  Inside the cooldown and not exempt, so select() will skip")
            print("  it. If you are still seeing it, whatever served it did not")
            print("  go through select().")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())