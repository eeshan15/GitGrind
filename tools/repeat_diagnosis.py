#!/usr/bin/env python3
"""Why already-answered questions come back in freshly built sets.

quiz.select has a per-question repeat cooldown, 9 days by default:

    is_due = qid in due_questions or key in due_topics
    if seen and since < cooldown and not is_due:
        continue

There are two ways that stops working, and they need different fixes, so this
measures both rather than guessing.

  history missing   question_stats is what "seen" and "since" are read from,
                    and it is only written by _record_attempt. _ensure_stat_rows
                    exists to backfill it from the attempts table and has no
                    callers anywhere in the codebase. If attempts covers more
                    questions than question_stats does, the cooldown simply has
                    no record of those and lets them straight back through.

  blanket bypass    due_topics is keyed by (subject, topic), and is_due tests
                    membership. So one overdue topic-level revision row makes
                    every question in that topic exempt from cooldown, however
                    recently it was answered. With a large overdue queue that
                    is not an exception any more, it is the rule.

Read-only. Run from the repo root:  python tools/repeat_diagnosis.py
"""
import os
import sys

sys.path.insert(0, os.getcwd())

try:
    from core import content, db, quiz
except ImportError as exc:
    sys.exit("cannot import core - run this from the repo root (%s)" % exc)


def one(conn, sql, args=()):
    row = conn.execute(sql, args).fetchone()
    return row[0] if row else 0


def main():
    conn = db.connect()
    try:
        bank = content.question_bank()
        settings = db.get_settings(conn)
        cooldown = db.setting_int(settings, "repeat_cooldown_days",
                                  quiz.DEFAULT_COOLDOWN_DAYS)

        attempted = one(conn, "SELECT COUNT(DISTINCT question_id) FROM attempts")
        stat_rows = one(conn, "SELECT COUNT(*) FROM question_stats")
        recent = one(
            conn,
            "SELECT COUNT(DISTINCT question_id) FROM attempts"
            " WHERE day >= date('now', ?)", ("-%d days" % cooldown,),
        )

        print("\n=== history ===")
        print("  cooldown setting            %d day(s)" % cooldown)
        print("  questions ever attempted    %d" % attempted)
        print("  rows in question_stats      %d" % stat_rows)
        print("  attempted within cooldown   %d" % recent)
        gap = attempted - stat_rows
        if gap > 0:
            print("\n  %d attempted question(s) have no question_stats row." % gap)
            print("  For those, select() reads seen=0 and lets them back in")
            print("  immediately. _ensure_stat_rows(conn) fixes this and is")
            print("  already written - it is just never called.")
        else:
            print("\n  question_stats covers every attempted question.")

        print("\n=== revision queue ===")
        due_q = one(
            conn,
            "SELECT COUNT(*) FROM revision_queue WHERE active = 1"
            " AND item_type = 'question' AND due_day <= date('now')")
        due_t = one(
            conn,
            "SELECT COUNT(DISTINCT subject_slug || '/' || topic_slug)"
            " FROM revision_queue WHERE active = 1"
            " AND item_type != 'question' AND due_day <= date('now')")
        topics_total = len({(q["subject"], q.get("topic", "")) for q in bank.values()})
        print("  due question-level rows     %d" % due_q)
        print("  due topic-level rows        %d distinct topic(s)" % due_t)
        print("  topics present in the bank  %d" % topics_total)

        # How much of the bank is exempt right now, and why.
        due_topics = set()
        due_questions = set()
        for r in conn.execute(
            "SELECT item_type, item_key, subject_slug, topic_slug FROM revision_queue"
            " WHERE active = 1 AND due_day <= date('now')"
        ):
            if r["item_type"] == "question":
                due_questions.add(r["item_key"])
            else:
                due_topics.add((r["subject_slug"], r["topic_slug"]))

        stats = quiz.question_stats(conn)
        seen_recently = exempt_by_topic = exempt_by_question = 0
        for qid, q in bank.items():
            st = stats.get(qid) or {}
            if not int(st.get("usage_count") or 0):
                continue
            if quiz._days_since(st.get("last_attempt_day")) >= cooldown:
                continue
            seen_recently += 1
            if qid in due_questions:
                exempt_by_question += 1
            elif (q["subject"], q.get("topic", "")) in due_topics:
                exempt_by_topic += 1

        print("\n=== who escapes the cooldown ===")
        print("  answered inside the cooldown window   %d" % seen_recently)
        print("    exempt because the question is due  %d" % exempt_by_question)
        print("    exempt because the topic is due     %d" % exempt_by_topic)
        held = seen_recently - exempt_by_question - exempt_by_topic
        print("    actually held back                  %d" % held)

        print("\n=== verdict ===")
        if seen_recently == 0:
            print("  Nothing has been answered inside the cooldown window, so")
            print("  the cooldown has had nothing to do. If sets still repeat,")
            print("  the history gap above is the cause.")
        elif exempt_by_topic > held:
            print("  The topic-level exemption is the cause. %d of %d recently"
                  % (exempt_by_topic, seen_recently))
            print("  answered questions are being let back in because their")
            print("  topic is overdue, not because the question is. A topic's")
            print("  revision debt is a reason to revisit the topic, not a")
            print("  licence to re-serve the exact question from yesterday.")
        elif gap > 0:
            print("  The cooldown is working for what it knows about, but %d"
                  % gap)
            print("  attempted question(s) are missing from question_stats.")
        else:
            print("  The cooldown appears to be holding. If sets still repeat,")
            print("  send this output and describe which screen it happens on.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())