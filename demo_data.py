#!/usr/bin/env python3
"""Fill the tracker with plausible activity so every panel can be seen populated.

Four profiles, because a dashboard that only looks right for a perfect student is
a dashboard that has not been tested:

    disciplined   six months, few gaps, accuracy climbing            (the ideal)
    patchy        six months, poor consistency, flat accuracy        (the common case)
    comeback      three months, a five-week hole, strong recent run  (streak rescue)
    sprint        last 60 days only, heavy volume, thin coverage     (exam panic)

Usage:

    python demo_data.py                          disciplined, asks first
    python demo_data.py --profile patchy
    python demo_data.py --profile comeback --yes
    python demo_data.py --clear                  remove everything and start clean
    python demo_data.py --list                   describe the profiles

This writes straight to data/gitgrind.db, so the server does not need to be
running. Badges, readiness and the revision queue are derived on the next page
load, not inserted here - except the parts of the revision queue that need a
history, which are backfilled so the queue is not empty on first open.
"""

import argparse
import os
import random
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import content, db, feedback, quiz as quizmod, revision

HOURS = [6, 7, 8, 10, 11, 14, 16, 18, 20, 21, 22, 23]
NOTES = [
    "",
    "",
    "",
    "worked through the standard problems",
    "revisited the derivation from scratch",
    "PYQ set, 2019 to 2023",
    "made a formula sheet for this",
    "got stuck on one case, flagged it",
    "second pass, much faster this time",
    "redid the ones I got wrong last week",
]

MISTAKES = ["concept", "silly", "misread", "time", "guess", "formula"]

# ---------------------------------------------------------------------------
# profiles
# ---------------------------------------------------------------------------
PROFILES = {
    "disciplined": dict(
        label="Disciplined student",
        blurb="Six months, almost no gaps, accuracy climbing from 55% to 78%.",
        days_back=184,
        gaps=[(96, 100), (41, 43)],
        skip_chance=0.10,
        two_session_chance=0.42,
        minutes=[60, 75, 90, 90, 120, 150, 180],
        accuracy=(0.55, 0.78),
        done_chance=0.62,
        quizzes=44,
        kinds=[
            "concept",
            "concept",
            "concept",
            "revision",
            "revision",
            "pyq",
            "dpp",
            "mock",
            "notes",
        ],
        target=240,
        feedback_n=14,
        doubts=6,
    ),
    "patchy": dict(
        label="Weak consistency",
        blurb="Six months on paper, but half the days are blank and accuracy is flat.",
        days_back=184,
        gaps=[(150, 168), (110, 121), (78, 88), (52, 58), (20, 26)],
        skip_chance=0.44,
        two_session_chance=0.12,
        minutes=[30, 40, 45, 60, 60, 75, 90],
        accuracy=(0.48, 0.54),
        done_chance=0.30,
        quizzes=18,
        kinds=["concept", "concept", "concept", "concept", "notes", "revision", "pyq"],
        target=180,
        feedback_n=6,
        doubts=9,
    ),
    "comeback": dict(
        label="Comeback user",
        blurb="Three months in, then five weeks away, now three solid weeks back.",
        days_back=104,
        gaps=[(58, 93)],
        skip_chance=0.16,
        two_session_chance=0.34,
        minutes=[45, 60, 75, 90, 120, 150],
        accuracy=(0.50, 0.70),
        done_chance=0.48,
        quizzes=26,
        kinds=["concept", "revision", "revision", "pyq", "dpp", "concept", "mock"],
        target=210,
        feedback_n=9,
        doubts=5,
    ),
    "sprint": dict(
        label="Last-60-days sprint",
        blurb="Nothing older than two months, very heavy volume, coverage still thin.",
        days_back=60,
        gaps=[],
        skip_chance=0.06,
        two_session_chance=0.72,
        minutes=[90, 120, 150, 180, 210, 240],
        accuracy=(0.52, 0.74),
        done_chance=0.55,
        quizzes=52,
        kinds=["pyq", "pyq", "dpp", "mock", "revision", "concept"],
        target=330,
        feedback_n=18,
        doubts=11,
    ),
}

ACTIVITY_TABLES = (
    "session_topics",
    "sessions",
    "attempts",
    "quizzes",
    "daily_question",
    "readiness_log",
    "unlocked",
    "doubts",
    "question_stats",
    "revision_queue",
    "daily_plans",
    "dpp_sets",
    "recommendations",
    "feedback",
    "learned_weights",
)


def clear(conn, quiet=False):
    with conn:
        for t in ACTIVITY_TABLES:
            conn.execute("DELETE FROM %s" % t)
        conn.execute(
            "UPDATE topics SET status = 'pending', updated_at = NULL,"
            " confidence = NULL, last_revised = NULL"
        )
    if not quiet:
        print("Cleared all activity. Subjects and topics are intact.")


def in_gap(back, gaps):
    return any(lo <= back <= hi for lo, hi in gaps)


def _ramp(profile, back):
    """0 at the oldest day, 1 today - used to make accuracy improve over time."""
    span = max(1, profile["days_back"])
    return max(0.0, min(1.0, (span - back) / float(span)))


def _accuracy_at(profile, back):
    lo, hi = profile["accuracy"]
    return lo + (hi - lo) * _ramp(profile, back)


# ---------------------------------------------------------------------------
# seeding
# ---------------------------------------------------------------------------
def seed_profile(conn, name, profile):
    exam_gap = 90 if name == "sprint" else 196
    with conn:
        for key, value in (
            ("display_name", "Demo: %s" % profile["label"]),
            ("handle", "demo-%s" % name),
            (
                "bio",
                "Sample data (%s). Clear it with: python demo_data.py --clear"
                % profile["label"].lower(),
            ),
            ("location", "India"),
            ("exam_name", "GATE CSE"),
            ("exam_date", (date.today() + timedelta(days=exam_gap)).isoformat()),
            ("daily_target_mins", str(profile["target"])),
            ("primary_target", "dgfs-iitb"),
        ):
            db.put_setting(conn, key, value)


def seed_sessions(conn, profile, rng):
    subjects = conn.execute(
        "SELECT id, slug, marks FROM subjects WHERE archived = 0 ORDER BY sort_order"
    ).fetchall()
    if not subjects:
        print("No subjects found. Run the app once so content/syllabus.json is seeded.")
        return [], {}

    topics_by_subject = {}
    for s in subjects:
        topics_by_subject[s["id"]] = [
            dict(id=r["id"], slug=r["slug"], name=r["name"])
            for r in conn.execute(
                "SELECT id, slug, name FROM topics WHERE subject_id = ? ORDER BY sort_order",
                (s["id"],),
            )
        ]

    weights = [s["marks"] for s in subjects]
    today = date.today()
    made = 0
    touched = {}

    with conn:
        for back in range(profile["days_back"], -1, -1):
            if in_gap(back, profile["gaps"]) or rng.random() < profile["skip_chance"]:
                continue
            day = (today - timedelta(days=back)).isoformat()
            n_sessions = 2 if rng.random() < profile["two_session_chance"] else 1
            for _ in range(n_sessions):
                s = rng.choices(subjects, weights=weights)[0]
                minutes = rng.choice(profile["minutes"])
                kind = rng.choice(profile["kinds"])
                stamp = datetime.now().isoformat(timespec="seconds")
                cur = conn.execute(
                    "INSERT INTO sessions (subject_id, day, minutes, kind, note, hour, created_at)"
                    " VALUES (?,?,?,?,?,?,?)",
                    (
                        s["id"],
                        day,
                        minutes,
                        kind,
                        rng.choice(NOTES),
                        rng.choice(HOURS),
                        stamp,
                    ),
                )
                session_id = cur.lastrowid
                made += 1

                pool = topics_by_subject.get(s["id"]) or []
                if not pool:
                    continue
                for t in rng.sample(pool, min(len(pool), rng.randint(1, 2))):
                    conn.execute(
                        "INSERT OR IGNORE INTO session_topics (session_id, topic_id)"
                        " VALUES (?,?)",
                        (session_id, t["id"]),
                    )
                    status = (
                        "done" if rng.random() < profile["done_chance"] else "learning"
                    )
                    conn.execute(
                        "UPDATE topics SET status = ?, updated_at = ?"
                        " WHERE id = ? AND (status != 'done' OR ? = 'done')",
                        (status, day, t["id"], status),
                    )
                    touched[(s["slug"], t["slug"])] = dict(
                        day=day, name=t["name"], kind=kind
                    )
    return subjects, touched


def seed_quizzes(conn, subjects, profile, rng):
    bank = content.question_bank()
    if not bank:
        print("Question bank is empty, skipping quizzes.")
        return 0

    by_subject = {}
    for q in bank.values():
        by_subject.setdefault(q["subject"], []).append(q)

    today = date.today()
    made = 0
    modes = ["practice", "review", "weak", "dpp", "mixed", "boss", "speed"]
    with conn:
        for i in range(profile["quizzes"]):
            s = rng.choice(subjects)
            pool = by_subject.get(s["slug"]) or []
            if not pool:
                continue
            back = rng.randint(0, min(profile["days_back"], 150))
            if in_gap(back, profile["gaps"]):
                continue
            mode = rng.choice(modes)
            size = 1 if mode == "boss" else rng.choice([4, 5, 5, 6, 8])
            picked = rng.sample(pool, min(len(pool), size))
            day = (today - timedelta(days=back)).isoformat()
            stamp = datetime.now().isoformat(timespec="seconds")
            total = sum(q.get("marks", 2) for q in picked)
            rate = _accuracy_at(profile, back)
            if mode == "boss":
                rate *= 0.6
            elif mode == "speed":
                rate = min(0.95, rate + 0.12)

            cur = conn.execute(
                "INSERT INTO quizzes (source, subject_id, day, topic_slugs, total_marks,"
                " question_count, mode, created_at) VALUES (?,?,?,?,?,?,?,?)",
                ("practice", s["id"], day, "", total, len(picked), mode, stamp),
            )
            quiz_id = cur.lastrowid

            got = 0.0
            right = 0
            duration = 0
            for q in picked:
                correct = rng.random() < rate
                if correct:
                    response = (
                        q.get("answer_value") if q["type"] == "nat" else q.get("answer")
                    )
                else:
                    if q["type"] == "nat":
                        response = float(q.get("answer_value", 0)) + 7
                    else:
                        key = q.get("answer", [0])
                        others = [
                            x
                            for x in range(len(q.get("options", [0, 1])))
                            if x not in key
                        ]
                        response = others[:1] or [0]
                ok, awarded = quizmod.grade_one(q, response)
                got += awarded
                right += 1 if ok else 0

                par = 45 * max(1, q.get("marks", 2) / 2)
                seconds = int(rng.gauss(par * (0.8 if ok else 1.25), par * 0.35))
                seconds = max(8, min(420, seconds))
                duration += seconds
                # Confidence correlates with correctness, but imperfectly - which
                # is exactly what makes the drift chart interesting.
                if ok:
                    conf = rng.choice([3, 4, 4, 5, 5])
                else:
                    conf = rng.choice([1, 2, 2, 3, 4])
                mistake = "" if ok else rng.choice(MISTAKES)

                conn.execute(
                    "INSERT INTO attempts (quiz_id, question_id, subject_slug, topic_slug,"
                    " source, response, correct, marks_total, marks_got, day, created_at,"
                    " seconds, confidence, mistake_kind, reattempt)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        quiz_id,
                        q["id"],
                        q["subject"],
                        q.get("topic", ""),
                        "practice",
                        "[demo]",
                        1 if ok else 0,
                        float(q.get("marks", 2)),
                        awarded,
                        day,
                        stamp,
                        seconds,
                        conf,
                        mistake,
                        0,
                    ),
                )

            conn.execute(
                "UPDATE quizzes SET scored_marks = ?, correct_count = ?, duration_s = ?,"
                " finished_at = ? WHERE id = ?",
                (round(got, 3), right, duration, stamp, quiz_id),
            )
            made += 1
    return made


def seed_qotd(conn, profile, rng):
    """A few weeks of answered daily questions, so the QOTD streak is not zero."""
    bank = list(content.question_bank().values())
    if not bank:
        return 0
    today = date.today()
    made = 0
    with conn:
        for back in range(min(30, profile["days_back"]), -1, -1):
            if in_gap(back, profile["gaps"]):
                continue
            if rng.random() < profile["skip_chance"] + 0.1:
                continue
            day = (today - timedelta(days=back)).isoformat()
            q = rng.choice(bank)
            ok = rng.random() < _accuracy_at(profile, back)
            stamp = datetime.now().isoformat(timespec="seconds")
            conn.execute(
                "INSERT OR REPLACE INTO daily_question (day, question_id, reason,"
                " served_at, answered_at, response, correct) VALUES (?,?,?,?,?,?,?)",
                (day, q["id"], "demo data", stamp, stamp, "[demo]", 1 if ok else 0),
            )
            made += 1
    return made


def seed_revision(conn, touched, profile, rng):
    """Give the queue a believable spread of due, overdue and scheduled items."""
    revision.sync_from_activity(conn)
    today = date.today()
    keys = list(touched.items())
    rng.shuffle(keys)
    with conn:
        for i, ((subject, topic), meta) in enumerate(keys):
            key = "%s/%s" % (subject, topic)
            row = conn.execute(
                "SELECT * FROM revision_queue WHERE item_type = 'topic' AND item_key = ?",
                (key,),
            ).fetchone()
            if not row:
                continue
            # A third overdue, a third due soon, a third comfortably scheduled.
            bucket = i % 3
            if bucket == 0:
                due = today - timedelta(days=rng.randint(1, 21))
                strength, reps, lapses = (
                    rng.uniform(0.12, 0.42),
                    rng.randint(1, 3),
                    rng.randint(1, 3),
                )
            elif bucket == 1:
                due = today + timedelta(days=rng.randint(0, 3))
                strength, reps, lapses = (
                    rng.uniform(0.40, 0.68),
                    rng.randint(2, 5),
                    rng.randint(0, 1),
                )
            else:
                due = today + timedelta(days=rng.randint(6, 40))
                strength, reps, lapses = rng.uniform(0.68, 0.96), rng.randint(4, 9), 0
            conn.execute(
                "UPDATE revision_queue SET due_day = ?, strength = ?, reps = ?,"
                " lapses = ?, interval_days = ?, ease = ?, last_review_day = ?"
                " WHERE item_type = 'topic' AND item_key = ?",
                (
                    due.isoformat(),
                    round(strength, 3),
                    reps,
                    lapses,
                    round(rng.uniform(1, 30), 1),
                    round(rng.uniform(1.8, 2.8), 2),
                    meta["day"],
                    key,
                ),
            )
    return conn.execute("SELECT COUNT(*) n FROM revision_queue").fetchone()["n"]


def seed_feedback(conn, profile, rng):
    """Some preference signals, so the learned-weights panel is not empty."""
    slugs = ["revision", "coverage", "accuracy_drop", "sample", "mistakes", "velocity"]
    answers = [
        "helpful",
        "helpful",
        "helpful",
        "not_helpful",
        "too_easy",
        "too_hard",
        "wrong_priority",
        "chose_other",
    ]
    made = 0
    for _ in range(profile["feedback_n"]):
        back = rng.randint(0, min(45, profile["days_back"]))
        feedback.record(
            conn,
            "recommendation",
            rng.choice(answers),
            target_slug=rng.choice(slugs),
            rating=rng.choice([None, 2, 3, 4, 5]),
            followed=rng.choice([True, True, False, None]),
            day=(date.today() - timedelta(days=back)).isoformat(),
        )
        made += 1
    return made


def seed_doubts(conn, touched, profile, rng):
    questions = [
        "why does the safe sequence check need the need matrix and not just allocation",
        "how do I decide between LR(1) and LALR(1) when the states merge",
        "is the closure of a relation always transitive here",
        "when do I use master theorem case 2 versus case 3",
        "why is this schedule conflict serialisable but not view serialisable",
        "how does the subnet mask change the broadcast address here",
        "what makes this grammar ambiguous, I cannot see the second parse tree",
        "why does the pumping lemma fail for this language",
        "how many comparisons does build-heap actually do in the worst case",
        "is this normal form BCNF or only 3NF",
        "why does write-back need a dirty bit at all",
    ]
    keys = list(touched.keys())
    made = 0
    with conn:
        for i in range(min(profile["doubts"], len(questions))):
            back = rng.randint(0, min(60, profile["days_back"]))
            stamp = (datetime.now() - timedelta(days=back)).isoformat(timespec="seconds")
            subject, topic = rng.choice(keys) if keys else ("", "")
            helped = rng.choice([1, 1, 1, 0, None])
            conn.execute(
                "INSERT INTO doubts (subject_slug, topic_slug, question_id, body, prompt,"
                " provider, answer, resolved, created_at, helped)"
                " VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    subject,
                    topic,
                    "",
                    questions[i],
                    "[demo prompt]",
                    rng.choice(["handoff", "ollama", "handoff"]),
                    "[demo answer]",
                    1 if helped else 0,
                    stamp,
                    helped,
                ),
            )
            made += 1
    return made


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------
def summarise(conn, profile_name):
    row = conn.execute(
        "SELECT COUNT(*) n, COALESCE(SUM(minutes), 0) m,"
        " COUNT(DISTINCT day) d FROM sessions"
    ).fetchone()
    topics = conn.execute(
        "SELECT COUNT(*) n FROM topics WHERE status = 'done'"
    ).fetchone()["n"]
    learning = conn.execute(
        "SELECT COUNT(*) n FROM topics WHERE status = 'learning'"
    ).fetchone()["n"]
    attempts = conn.execute("SELECT COUNT(*) n, SUM(correct) c FROM attempts").fetchone()
    rev = conn.execute(
        "SELECT COUNT(*) n, SUM(due_day <= date('now')) due FROM revision_queue"
    ).fetchone()
    print()
    print("  profile       %s" % profile_name)
    print("  sessions      %d across %d active days" % (row["n"], row["d"]))
    print("  hours         %.1f" % (row["m"] / 60.0))
    print("  topics        %d done, %d in progress" % (topics, learning))
    if attempts["n"]:
        print(
            "  questions     %d, %d correct (%.0f%%)"
            % (
                attempts["n"],
                attempts["c"] or 0,
                (attempts["c"] or 0) / attempts["n"] * 100,
            )
        )
    print("  revision      %d cards, %d due now" % (rev["n"] or 0, rev["due"] or 0))
    print()
    print("  Start the app to see it: python app.py")
    print()


def load(profile="disciplined", confirm=True, seed=4242, wipe=True):
    """Programmatic entry point, also used by ``app.py --demo``."""
    if profile not in PROFILES:
        raise ValueError(
            "Unknown profile %r. Choose from: %s" % (profile, ", ".join(PROFILES))
        )
    cfg = PROFILES[profile]
    conn = db.init()
    try:
        content.seed(conn)
        existing = conn.execute("SELECT COUNT(*) n FROM sessions").fetchone()["n"]
        if existing and confirm:
            print("There are already %d sessions in the database." % existing)
            print("Loading a demo profile replaces all activity.")
            if input("Type yes to continue: ").strip().lower() != "yes":
                print("Nothing changed.")
                return False
        if wipe:
            clear(conn, quiet=True)

        rng = random.Random(seed)
        seed_profile(conn, profile, cfg)
        subjects, touched = seed_sessions(conn, cfg, rng)
        if subjects:
            n = seed_quizzes(conn, subjects, cfg, rng)
            print("Generated %d practice sets." % n)
            print("Generated %d answered daily questions." % seed_qotd(conn, cfg, rng))
            print(
                "Backfilled %d revision cards." % seed_revision(conn, touched, cfg, rng)
            )
            print("Logged %d feedback signals." % seed_feedback(conn, cfg, rng))
            print("Logged %d doubts." % seed_doubts(conn, touched, cfg, rng))
        summarise(conn, "%s - %s" % (profile, cfg["label"]))
        return True
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser(description="Demo data for GitGrind.")
    ap.add_argument(
        "--profile",
        default="disciplined",
        choices=sorted(PROFILES),
        help="which student to simulate",
    )
    ap.add_argument("--clear", action="store_true", help="remove all activity and exit")
    ap.add_argument("--list", action="store_true", help="describe the profiles and exit")
    ap.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    ap.add_argument(
        "--keep",
        action="store_true",
        help="add on top of existing activity instead of replacing it",
    )
    ap.add_argument("--seed", type=int, default=4242, help="random seed")
    args = ap.parse_args()

    if args.list:
        print()
        for name, cfg in PROFILES.items():
            print("  %-12s %s" % (name, cfg["label"]))
            print("  %-12s %s" % ("", cfg["blurb"]))
            print()
        return 0

    if args.clear:
        conn = db.init()
        try:
            content.seed(conn)
            clear(conn)
        finally:
            conn.close()
        return 0

    load(profile=args.profile, confirm=not args.yes, seed=args.seed, wipe=not args.keep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
