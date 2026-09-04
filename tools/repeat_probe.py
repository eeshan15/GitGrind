#!/usr/bin/env python3
"""Measure how often a freshly built set repeats a question, and why.

Two theories have already been wrong about this. Topic-level cooldown bypass
turned out to affect 2 questions; served-but-unsubmitted sets turned out to
hold 9. Reading the scoring code does not settle it either, because the rules
pull in opposite directions:

  _days_since(None) returns 9999, so an unseen question collects the full
  +min(10, since/30) bonus that a question answered yesterday never gets.
  That works against repeats.

  In "weak" mode a question last answered wrongly collects +14, while the
  repeat penalty is -min(18, seen * 4.5), which is only -4.5 at one sighting.
  A once-wrong question therefore scores about the same as a fresh one. That
  works for repeats.

  is_due bypasses the cooldown entirely, and 272 of the 303 questions ever
  attempted here are overdue question-level revision rows.

Which of those dominates is an empirical question, so this samples it. It calls
quiz.select the same way build_quiz does - weak, then mixed, then fresh - and
for every question that comes back reports whether it has been answered before,
how long ago, how many times, whether it was last answered wrongly, and which
rule let it past the cooldown.

Then it runs the same selection again with the cooldown bypass narrowed to
question-level-due only, and with it removed altogether, so the effect of each
is a number rather than an argument.

Read-only: select() does not write, and no quiz row is created.

    python tools/repeat_probe.py            10 samples per purpose
    python tools/repeat_probe.py 30         more samples
"""
import collections
import os
import sys

sys.path.insert(0, os.getcwd())

try:
    from core import content, db, quiz
except ImportError as exc:
    sys.exit("cannot import core - run this from the repo root (%s)" % exc)


def gather(conn):
    stats = quiz.question_stats(conn)
    due_q, due_t = set(), set()
    for r in conn.execute(
        "SELECT item_type, item_key, subject_slug, topic_slug FROM revision_queue"
        " WHERE active = 1 AND due_day <= date('now')"
    ):
        if r["item_type"] == "question":
            due_q.add(r["item_key"])
        else:
            due_t.add((r["subject_slug"], r["topic_slug"]))
    return stats, due_q, due_t


def sample(conn, purposes, samples, cooldown=None):
    """Run select repeatedly and return every (purpose, question) picked."""
    out = []
    for purpose in purposes:
        for i in range(samples):
            kw = dict(seed="probe-%s-%d" % (purpose, i))
            if cooldown is not None:
                kw["cooldown_days"] = cooldown
            for q, reason in quiz.select(conn, purpose, count=5, **kw):
                out.append((purpose, q, reason))
    return out


def main():
    samples = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    conn = db.connect()
    try:
        bank = content.question_bank()
        stats, due_q, due_t = gather(conn)
        settings = db.get_settings(conn)
        cooldown = db.setting_int(settings, "repeat_cooldown_days",
                                  quiz.DEFAULT_COOLDOWN_DAYS)
        purposes = ["weak", "mixed", "fresh"]

        print("\n  bank %d, attempted %d, cooldown %d day(s), %d sample set(s)"
              " per purpose" % (len(bank), len(stats), cooldown, samples))

        picks = sample(conn, purposes, samples)
        by_purpose = collections.defaultdict(lambda: collections.Counter())
        repeats = []

        for purpose, q, reason in picks:
            qid = q["id"]
            st = stats.get(qid) or {}
            seen = int(st.get("usage_count") or 0)
            by_purpose[purpose]["picked"] += 1
            if not seen:
                by_purpose[purpose]["fresh"] += 1
                continue
            since = quiz._days_since(st.get("last_attempt_day"))
            by_purpose[purpose]["repeat"] += 1
            if since < cooldown:
                by_purpose[purpose]["inside cooldown"] += 1
                if qid in due_q:
                    why = "question is due"
                elif (q["subject"], q.get("topic", "")) in due_t:
                    why = "topic is due"
                else:
                    why = "UNEXPLAINED - cooldown should have held this"
                wrong_last = bool(st.get("last_wrong_day")) and (
                    st.get("last_wrong_day") or "") >= (st.get("last_correct_day") or "")
                repeats.append((purpose, qid, seen, since, wrong_last, why, reason))

        print("\n=== what each purpose returns ===")
        print("  %-8s %7s %7s %8s %16s" % ("purpose", "picked", "fresh",
                                           "repeat", "inside cooldown"))
        for purpose in purposes:
            c = by_purpose[purpose]
            print("  %-8s %7d %7d %8d %16d"
                  % (purpose, c["picked"], c["fresh"], c["repeat"],
                     c["inside cooldown"]))

        print("\n=== repeats served inside the cooldown window ===")
        if not repeats:
            print("  none. Every repeat was older than the cooldown, which is")
            print("  the cooldown working as designed.")
        else:
            print("  %-8s %-34s %4s %5s %6s %s"
                  % ("purpose", "question", "seen", "days", "wrong?", "why it got through"))
            for purpose, qid, seen, since, wrong, why, _reason in repeats[:25]:
                print("  %-8s %-34s %4d %5d %6s %s"
                      % (purpose, qid[:34], seen, since, "yes" if wrong else "no", why))
            if len(repeats) > 25:
                print("  ... and %d more" % (len(repeats) - 25))
            print()
            for why, n in collections.Counter(r[5] for r in repeats).most_common():
                print("    %-46s %d" % (why, n))
            wrongs = sum(1 for r in repeats if r[4])
            print("\n    of those, %d were last answered wrongly and %d correctly"
                  % (wrongs, len(repeats) - wrongs))
            if wrongs == len(repeats):
                print("    Every one was previously wrong, so re-serving them is")
                print("    spaced repetition doing its job, not a fault.")
            elif wrongs == 0:
                print("    None was previously wrong. Re-serving questions you")
                print("    got right is not revision, it is repetition.")

        print("\n=== counterfactual ===")
        # Cooldown 0 means no cooldown at all; a very large one means the
        # bypass is the only way through, which isolates its contribution.
        for label, cd in (("cooldown ignored", 0), ("cooldown 365 days", 365)):
            alt = sample(conn, purposes, samples, cooldown=cd)
            rep = sum(
                1 for _p, q, _r in alt
                if int((stats.get(q["id"]) or {}).get("usage_count") or 0)
            )
            print("  %-20s %d of %d picks were repeats"
                  % (label, rep, len(alt)))
        base_rep = sum(c["repeat"] for c in by_purpose.values())
        base_all = sum(c["picked"] for c in by_purpose.values())
        print("  %-20s %d of %d picks were repeats"
              % ("as configured", base_rep, base_all))
        print("\n  If the 365-day row is close to the configured row, the")
        print("  cooldown is being bypassed rather than applied, and is_due is")
        print("  the reason. If it is much lower, the cooldown is working and")
        print("  the repeats are coming from the scoring instead.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())