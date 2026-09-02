"""The practice engine: adaptive selection, grading, and everything a quiz logs.

Scoring follows GATE marking rules: MCQ carries negative marking (one third of
the marks), MSQ and NAT do not. MSQ is all-or-nothing.

Selection is no longer "random from the bank". Every question is scored against
a *purpose*:

    review   questions and topics the spaced-repetition queue says are due
    weak     the topics with the highest risk score
    mixed    previous-year spread across what has been covered
    speed    short, low-mark questions to build pace
    boss     the hardest thing in a covered topic, one at a time
    fresh    material that has never been served

Cooldown keeps a question from reappearing for a few days unless it is genuinely
due for review. Difficulty drifts with measured accuracy and with the user's own
"too easy / too hard" feedback.

The peer curve is a MODEL, not real students. Nothing here talks to a server or
to other people. Each question is given a solve probability from its difficulty,
a virtual cohort is sampled with a per-student ability factor, and your score is
placed against that. It is a yardstick, not a leaderboard.
"""

import json
import random
import sqlite3
from datetime import date, datetime, timedelta

from . import content, db, feedback, revision

SOLVE_PROB = {"easy": 0.74, "medium": 0.50, "hard": 0.28}
PEER_SAMPLE = 4000
RECENT_WINDOW_DAYS = 7
DEFAULT_COOLDOWN_DAYS = 9

DIFFICULTY_RANK = {"easy": 0, "medium": 1, "hard": 2}

MISTAKE_KINDS = {
    "concept": "Concept not clear",
    "silly": "Silly / arithmetic slip",
    "misread": "Misread the question",
    "time": "Ran out of time",
    "guess": "Guessed",
    "formula": "Forgot the formula",
}

PURPOSES = ("review", "weak", "mixed", "speed", "boss", "fresh")

PURPOSE_LABELS = {
    "review": "Revision",
    "weak": "Weak topic",
    "mixed": "Mixed PYQ",
    "speed": "Speed drill",
    "boss": "Boss question",
    "fresh": "New ground",
}


# ---------------------------------------------------------------------------
# context the selector needs
# ---------------------------------------------------------------------------
def _recent_focus(conn, days=RECENT_WINDOW_DAYS):
    """Subjects and topics the user has actually been working on lately."""
    since = (date.today() - timedelta(days=days)).isoformat()
    subj = [
        r["slug"]
        for r in conn.execute(
            "SELECT DISTINCT sub.slug AS slug FROM sessions s"
            " JOIN subjects sub ON sub.id = s.subject_id WHERE s.day >= ?",
            (since,),
        )
    ]
    topics = [
        r["slug"]
        for r in conn.execute(
            "SELECT DISTINCT t.slug AS slug FROM session_topics st"
            " JOIN topics t ON t.id = st.topic_id"
            " JOIN sessions s ON s.id = st.session_id WHERE s.day >= ?",
            (since,),
        )
    ]
    studied = [
        r["slug"]
        for r in conn.execute(
            "SELECT slug FROM topics WHERE status IN ('done', 'learning')"
        )
    ]
    return subj, topics, studied


def _attempt_counts(conn):
    return {
        r["question_id"]: r["n"]
        for r in conn.execute(
            "SELECT question_id, COUNT(*) AS n FROM attempts GROUP BY question_id"
        )
    }


def question_stats(conn):
    """{question_id: {...}} of measured per-question history."""
    out = {}
    for r in conn.execute("SELECT * FROM question_stats"):
        out[r["question_id"]] = dict(r)
    return out


def _ensure_stat_rows(conn, attempts_only=True):
    """Backfill question_stats from the attempts table (idempotent, cheap)."""
    now = datetime.now().isoformat(timespec="seconds")
    rows = conn.execute(
        "SELECT question_id, subject_slug, topic_slug, COUNT(*) n, SUM(correct) c,"
        " MAX(day) last_day,"
        " MAX(CASE WHEN correct = 1 THEN day END) last_ok,"
        " MAX(CASE WHEN correct = 0 THEN day END) last_bad,"
        " AVG(NULLIF(seconds,0)) secs, AVG(confidence) conf"
        " FROM attempts GROUP BY question_id"
    ).fetchall()
    with conn:
        for r in rows:
            conn.execute(
                "INSERT INTO question_stats (question_id, subject_slug, topic_slug,"
                " usage_count, correct_count, last_attempt_day, last_correct_day,"
                " last_wrong_day, avg_seconds, avg_confidence, updated_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?)"
                " ON CONFLICT(question_id) DO UPDATE SET usage_count = excluded.usage_count,"
                " correct_count = excluded.correct_count,"
                " last_attempt_day = excluded.last_attempt_day,"
                " last_correct_day = excluded.last_correct_day,"
                " last_wrong_day = excluded.last_wrong_day,"
                " avg_seconds = excluded.avg_seconds,"
                " avg_confidence = excluded.avg_confidence,"
                " subject_slug = excluded.subject_slug,"
                " topic_slug = excluded.topic_slug,"
                " updated_at = excluded.updated_at",
                (
                    r["question_id"],
                    r["subject_slug"] or "",
                    r["topic_slug"] or "",
                    r["n"],
                    r["c"] or 0,
                    r["last_day"],
                    r["last_ok"],
                    r["last_bad"],
                    float(r["secs"] or 0),
                    float(r["conf"] or 0),
                    now,
                ),
            )


def _days_since(day, today=None):
    if not day:
        return 9999
    try:
        return (
            date.fromisoformat(str(today or date.today().isoformat()))
            - date.fromisoformat(str(day)[:10])
        ).days
    except ValueError:
        return 9999


def target_difficulty(conn, metrics=None, purpose="weak"):
    """Where the difficulty dial currently sits, 0 easy .. 2 hard.

    Driven by measured accuracy first, nudged by explicit user feedback.
    """
    settings = db.get_settings(conn)
    if not db.setting_bool(settings, "adaptive_difficulty", True):
        return 1.0
    acc = float((metrics or {}).get("accuracy") or 0)
    attempted = int((metrics or {}).get("questions_attempted") or 0)

    base = 1.0
    if attempted >= 25:
        if acc >= 80:
            base = 1.7
        elif acc >= 68:
            base = 1.3
        elif acc >= 52:
            base = 1.0
        elif acc >= 38:
            base = 0.65
        else:
            base = 0.35
    base += feedback.difficulty_dial(conn) * 0.55

    if purpose == "speed":
        base -= 0.6
    elif purpose == "boss":
        base = 2.0
    elif purpose == "review":
        base -= 0.15
    return max(0.0, min(2.0, base))


# ---------------------------------------------------------------------------
# the selector
# ---------------------------------------------------------------------------
def reserved_for_mocks(conn):
    """Question ids belonging to a generated mock paper."""
    try:
        return {
            r["question_id"]
            for r in conn.execute(
                "SELECT pq.question_id FROM paper_questions pq"
                " JOIN papers p ON p.id = pq.paper_id"
                " WHERE p.exam = 'GitGrind Mock'"
            )
        }
    except sqlite3.Error:
        # A database that predates the papers tables must still serve practice.
        return set()


def select(
    conn,
    purpose="weak",
    count=5,
    subject_slug=None,
    topic_slugs=None,
    kinds=None,
    exclude=None,
    metrics=None,
    topic_health=None,
    cooldown_days=None,
    seed=None,
    # Last on purpose. build_quiz calls this function positionally, so a
    # parameter inserted anywhere earlier silently captures the argument
    # meant for the one after it - which is exactly what happened when
    # this sat between topic_slugs and kinds. Keyword-only in practice.
    subtopic_slugs=None,
):
    """Return [(question, reason)] chosen for one purpose. Never raises on empty."""
    # Questions held by a mock paper stay out of practice, so sitting a mock is
    # not a re-run of what you already saw. This is a query, not a partition:
    # delete a mock and its questions come straight back into the pool.
    exclude = set(exclude or []) | reserved_for_mocks(conn)
    bank = content.question_bank()
    if not bank:
        return []

    exclude = set(exclude or [])
    settings = db.get_settings(conn)
    cooldown = (
        cooldown_days
        if cooldown_days is not None
        else db.setting_int(settings, "repeat_cooldown_days", DEFAULT_COOLDOWN_DAYS)
    )

    stats = question_stats(conn)
    focus_subj, focus_topics, studied = _recent_focus(conn)
    studied_set = set(studied)
    want_diff = target_difficulty(conn, metrics, purpose)

    # risk per topic, from the analytics layer when available
    risk = {}
    if topic_health:
        for r in topic_health:
            risk[(r["subject"], r["topic"])] = r["risk"]

    # what the revision queue says is due
    due_questions = {}
    due_topics = {}
    today = date.today().isoformat()
    for r in conn.execute(
        "SELECT item_type, item_key, topic_slug, subject_slug, due_day, strength, lapses"
        " FROM revision_queue WHERE active = 1 AND due_day <= ?",
        (today,),
    ):
        overdue = _days_since(r["due_day"])
        if r["item_type"] == "question":
            due_questions[r["item_key"]] = overdue
        else:
            due_topics[(r["subject_slug"], r["topic_slug"])] = overdue

    topic_filter = set(topic_slugs or [])
    # Narrower than topic_filter and independent of it: passing only
    # subtopics selects across whatever topics carry them, which is what a
    # user typing one concept name is asking for.
    subtopic_filter = set(subtopic_slugs or [])
    rng = random.Random(seed or "sel-%s-%s" % (purpose, datetime.now().isoformat()))
    scored = []

    for q in bank.values():
        qid = q["id"]
        if qid in exclude:
            continue
        if content.validate_question(q):
            issues = content.validate_question(q)
            if [i for i in issues if i != "no explanation"]:
                continue  # never serve a structurally broken question
        if subject_slug and q["subject"] != subject_slug:
            continue
        if topic_filter and q.get("topic") not in topic_filter:
            continue
        if subtopic_filter and q.get("subtopic") not in subtopic_filter:
            continue
        if kinds and q.get("kind") not in kinds:
            continue

        st = stats.get(qid) or {}
        seen = int(st.get("usage_count") or 0)
        since = _days_since(st.get("last_attempt_day"))
        key = (q["subject"], q.get("topic", ""))
        topic_risk = risk.get(key, 45)
        is_due = qid in due_questions or key in due_topics
        wrong_last = bool(st.get("last_wrong_day")) and (
            st.get("last_wrong_day") or ""
        ) >= (st.get("last_correct_day") or "")

        # ---- cooldown --------------------------------------------------
        if seen and since < cooldown and not is_due:
            continue

        # ---- base score by purpose -------------------------------------
        s = 0.0
        reason = "picked from the bank"

        if purpose == "review":
            if qid in due_questions:
                s = 60 + due_questions[qid] * 2.2
                reason = "you got this wrong before and it is due again"
            elif key in due_topics:
                s = 34 + due_topics[key] * 1.4
                reason = "%s revision is due" % (q.get("topic") or q["subject"])
            elif wrong_last:
                s = 20
                reason = "last attempt on this was wrong"
            else:
                continue

        elif purpose == "weak":
            if key not in risk and q.get("topic") not in studied_set:
                continue
            s = topic_risk * 0.7
            if wrong_last:
                s += 14
            if q.get("topic") in focus_topics:
                s += 8
            reason = "high-risk topic (%d/100 risk)" % topic_risk

        elif purpose == "mixed":
            if q.get("kind") != "pyq":
                s -= 18
            if q.get("topic") in studied_set:
                s += 26
                reason = "previous-year question on covered ground"
            else:
                s += 4
                reason = "previous-year question, mixed spread"
            s += topic_risk * 0.12

        elif purpose == "speed":
            if float(q.get("marks", 2)) > 1.5:
                s -= 12
            if q.get("difficulty") == "easy":
                s += 22
            if q.get("topic") in studied_set:
                s += 16
            reason = "short question to build pace"

        elif purpose == "boss":
            if q.get("difficulty") != "hard":
                continue
            if q.get("topic") not in studied_set:
                s -= 20
            s += 30 + float(q.get("marks", 2)) * 3 + topic_risk * 0.2
            reason = "hardest thing in a topic you have covered"

        else:  # fresh
            if seen:
                continue
            s = 24 + topic_risk * 0.25
            if q["subject"] in focus_subj:
                s += 12
            reason = "not served before"

        # ---- shared modifiers ------------------------------------------
        gap = abs(DIFFICULTY_RANK.get(q.get("difficulty", "medium"), 1) - want_diff)
        s -= gap * 9.0
        s -= min(18.0, seen * 4.5)
        s += min(10.0, since / 30.0)
        s *= feedback.topic_multiplier(conn, q.get("topic", ""))
        s += rng.random() * 4.0

        scored.append((s, qid, reason))

    scored.sort(key=lambda x: -x[0])

    # Spread across topics so a set is not five questions from one topic.
    picked, used_topic = [], {}
    cap = max(2, (count + 2) // 2)
    for s, qid, reason in scored:
        q = bank[qid]
        t = q.get("topic", "")
        if purpose != "weak" and used_topic.get(t, 0) >= cap:
            continue
        used_topic[t] = used_topic.get(t, 0) + 1
        picked.append((q, reason))
        if len(picked) >= count:
            break
    # Top up ignoring the spread rule rather than returning a short set.
    if len(picked) < count:
        have = {q["id"] for q, _ in picked}
        for s, qid, reason in scored:
            if qid in have:
                continue
            picked.append((bank[qid], reason))
            if len(picked) >= count:
                break
    return picked


# ---------------------------------------------------------------------------
# question of the day
# ---------------------------------------------------------------------------
def pick_question_of_day(conn, day=None, force=False):
    """Deterministic per calendar day, biased toward what needs attention.

    Stored on first request so a refresh does not reroll it.
    """
    day = day or date.today().isoformat()
    row = conn.execute("SELECT * FROM daily_question WHERE day = ?", (day,)).fetchone()
    bank = content.question_bank()
    if row and not force and row["question_id"] in bank:
        return dict(row), bank[row["question_id"]]

    if not bank:
        return None, None

    # Review first, then weak, then anything. Seeded so it is stable per day.
    picked = []
    for purpose in ("review", "weak", "mixed", "fresh"):
        picked = select(conn, purpose, count=1, seed="qotd-%s-%s" % (day, purpose))
        if picked:
            break
    if not picked:
        focus_subj, focus_topics, studied = _recent_focus(conn)
        rng = random.Random("qotd-fallback-%s" % day)
        q = rng.choice(list(bank.values()))
        picked = [(q, "syllabus-wide pick")]

    q, reason = picked[0]
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "INSERT INTO daily_question (day, question_id, reason, served_at) VALUES (?,?,?,?)"
            " ON CONFLICT(day) DO UPDATE SET question_id = excluded.question_id,"
            " reason = excluded.reason, served_at = excluded.served_at,"
            " answered_at = NULL, response = NULL, correct = NULL",
            (day, q["id"], reason, now),
        )
    row = conn.execute("SELECT * FROM daily_question WHERE day = ?", (day,)).fetchone()
    return dict(row), bank[q["id"]]


# ---------------------------------------------------------------------------
# building a quiz
# ---------------------------------------------------------------------------
def build_quiz(
    conn,
    subject_id=None,
    topic_ids=None,
    count=5,
    kinds=None,
    session_id=None,
    mode="practice",
    purpose=None,
    plan_day="",
    dpp_set_id=None,
    reason="",
    metrics=None,
    topic_health=None,
    question_ids=None,
    paper_id=None,
):
    """Assemble a quiz. ``mode`` drives how the questions are chosen.

    modes: practice (default), review, weak, dpp, boss, speed, mock
    """
    bank = content.question_bank()
    if not bank:
        return None, "The question bank is empty. Add files under content/questions."

    subject_slug = None
    if subject_id:
        row = conn.execute(
            "SELECT slug FROM subjects WHERE id = ?", (subject_id,)
        ).fetchone()
        subject_slug = row["slug"] if row else None

    topic_slugs = []
    if topic_ids:
        marks = ",".join("?" * len(topic_ids))
        topic_slugs = [
            r["slug"]
            for r in conn.execute(
                "SELECT slug FROM topics WHERE id IN (%s)" % marks, tuple(topic_ids)
            )
        ]

    count = max(1, min(int(count or 5), 30))
    chosen = []
    reasons = {}

    if question_ids:
        for qid in question_ids:
            if qid in bank:
                chosen.append(bank[qid])
                reasons[qid] = reason or "part of today's plan"
    else:
        purpose = purpose or {
            "review": "review",
            "weak": "weak",
            "boss": "boss",
            "speed": "speed",
            "dpp": "weak",
            "mock": "mixed",
        }.get(mode, None)

        if purpose:
            picked = select(
                conn,
                purpose,
                count,
                subject_slug,
                topic_slugs,
                kinds,
                metrics=metrics,
                topic_health=topic_health,
            )
        else:
            # Plain practice: topic/subject first, but still weakness-aware.
            picked = select(
                conn,
                "weak",
                count,
                subject_slug,
                topic_slugs,
                kinds,
                metrics=metrics,
                topic_health=topic_health,
            )
            if len(picked) < count:
                have = {q["id"] for q, _ in picked}
                picked += select(
                    conn,
                    "mixed",
                    count - len(picked),
                    subject_slug,
                    topic_slugs,
                    kinds,
                    exclude=have,
                    metrics=metrics,
                    topic_health=topic_health,
                )
            if len(picked) < count:
                have = {q["id"] for q, _ in picked}
                picked += select(
                    conn,
                    "fresh",
                    count - len(picked),
                    subject_slug,
                    topic_slugs,
                    kinds,
                    exclude=have,
                    metrics=metrics,
                    topic_health=topic_health,
                )
        for q, why in picked:
            chosen.append(q)
            reasons[q["id"]] = why

    if not chosen:
        if subject_slug:
            return None, (
                "No questions available for that subject right now - either "
                "the bank has none, or everything is inside its repeat cooldown."
            )
        return None, "Nothing to serve. The bank may be too small for this mode."

    now = datetime.now().isoformat(timespec="seconds")
    if paper_id:
        # A paper carries its own mark per question. For a mock those values were
        # assigned to make the paper total 100, which the bank's own marks field
        # cannot do - most of it is an importer default. Sitting the paper must
        # score against the paper, not against the bank.
        paper_marks = {
            r["question_id"]: r["marks"]
            for r in conn.execute(
                "SELECT question_id, marks FROM paper_questions WHERE paper_id = ?",
                (paper_id,),
            )
        }
        for q in chosen:
            if q["id"] in paper_marks:
                q["marks"] = paper_marks[q["id"]]
    total_marks = sum(q.get("marks", 2) for q in chosen)
    with conn:
        cur = conn.execute(
            "INSERT INTO quizzes (source, subject_id, session_id, day, topic_slugs,"
            " total_marks, question_count, mode, plan_day, dpp_set_id, reason,"
            " paper_id, created_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "session" if session_id else "practice",
                subject_id,
                session_id,
                date.today().isoformat(),
                ",".join(topic_slugs),
                total_marks,
                len(chosen),
                mode,
                plan_day or "",
                dpp_set_id,
                reason,
                paper_id,
                now,
            ),
        )
        quiz_id = cur.lastrowid
        # Without this row set an unfinished quiz cannot be reopened: the quizzes
        # row survives a crash but says nothing about which questions were in it,
        # and attempts are only written at submit time.
        conn.executemany(
            "INSERT OR IGNORE INTO quiz_questions (quiz_id, question_id, position)"
            " VALUES (?,?,?)",
            [(quiz_id, q["id"], i) for i, q in enumerate(chosen)],
        )
        if dpp_set_id:
            conn.execute(
                "UPDATE dpp_sets SET quiz_id = ?, started_at = ? WHERE id = ?",
                (quiz_id, now, dpp_set_id),
            )

    out_questions = []
    for q in chosen:
        pub = content.public_question(q)
        pub["why"] = reasons.get(q["id"], "")
        out_questions.append(pub)

    return (
        dict(
            id=quiz_id,
            mode=mode,
            mode_label=PURPOSE_LABELS.get(purpose or mode, mode.title()),
            reason=reason,
            subject_id=subject_id,
            subject_slug=subject_slug,
            topic_slugs=topic_slugs,
            total_marks=total_marks,
            dpp_set_id=dpp_set_id,
            paper_id=paper_id,
            plan_day=plan_day,
            questions=out_questions,
            mistake_kinds=MISTAKE_KINDS,
        ),
        None,
    )


# ---------------------------------------------------------------------------
# scoring
# ---------------------------------------------------------------------------
def _normalise_response(q, response):
    if q.get("type") == "nat":
        if response in (None, "", []):
            return None
        try:
            return float(response)
        except (TypeError, ValueError):
            return None
    if isinstance(response, (int, float)):
        return [int(response)]
    if isinstance(response, list):
        out = []
        for x in response:
            try:
                out.append(int(x))
            except (TypeError, ValueError):
                continue
        return sorted(set(out))
    return []


def grade_one(q, response):
    """Return (correct, marks_awarded) following GATE marking rules."""
    marks = float(q.get("marks", 2))
    given = _normalise_response(q, response)
    qtype = q.get("type", "mcq")

    if qtype == "nat":
        if given is None:
            return False, 0.0
        target = float(q.get("answer_value", 0))
        tol = float(q.get("tolerance", 0) or 0)
        ok = abs(given - target) <= max(tol, 1e-9)
        return ok, marks if ok else 0.0

    key = sorted(set(int(x) for x in q.get("answer", [])))
    if not given:
        return False, 0.0

    if qtype == "msq":
        ok = given == key
        return ok, marks if ok else 0.0

    ok = given == key
    if ok:
        return True, marks
    # GATE deducts one third of the marks for a wrong MCQ.
    return False, -round(marks / 3.0, 4)


def _record_attempt(conn, q, item, ok, awarded, quiz, day, now, prior_attempts):
    seconds = int(item.get("seconds") or 0)
    conf = item.get("confidence")
    try:
        conf = None if conf in (None, "") else max(1, min(5, int(conf)))
    except (TypeError, ValueError):
        conf = None
    mistake = str(item.get("mistake_kind") or "")
    if mistake not in MISTAKE_KINDS:
        mistake = "" if ok else mistake if mistake else ""
    reattempt = 1 if prior_attempts.get(q["id"]) else 0

    conn.execute(
        "INSERT INTO attempts (quiz_id, question_id, subject_slug, topic_slug, source,"
        " response, correct, marks_total, marks_got, day, created_at, seconds,"
        " confidence, mistake_kind, reattempt, dpp_set_id, plan_day,"
        " paper_id, position_in_paper)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            quiz["id"] if quiz else None,
            q["id"],
            q["subject"],
            q.get("topic", ""),
            quiz["source"] if quiz else "quiz",
            json.dumps(item.get("response")),
            1 if ok else 0,
            float(q.get("marks", 2)),
            awarded,
            day,
            now,
            seconds,
            conf,
            mistake,
            reattempt,
            quiz["dpp_set_id"] if quiz and "dpp_set_id" in quiz.keys() else None,
            (quiz["plan_day"] if quiz and "plan_day" in quiz.keys() else "") or "",
            quiz["paper_id"] if quiz and "paper_id" in quiz.keys() else None,
            q.get("position_in_paper"),
        ),
    )

    # per-question rollup
    conn.execute(
        "INSERT INTO question_stats (question_id, subject_slug, topic_slug, usage_count,"
        " correct_count, reattempts, last_attempt_day, last_correct_day, last_wrong_day,"
        " avg_seconds, avg_confidence, mistake_kind, updated_at)"
        " VALUES (?,?,?,1,?,?,?,?,?,?,?,?,?)"
        " ON CONFLICT(question_id) DO UPDATE SET"
        " usage_count = question_stats.usage_count + 1,"
        " correct_count = question_stats.correct_count + ?,"
        " reattempts = question_stats.reattempts + ?,"
        " last_attempt_day = ?,"
        " last_correct_day = CASE WHEN ? = 1 THEN ? ELSE question_stats.last_correct_day END,"
        " last_wrong_day = CASE WHEN ? = 0 THEN ? ELSE question_stats.last_wrong_day END,"
        " avg_seconds = CASE WHEN ? > 0 THEN"
        "   (question_stats.avg_seconds * question_stats.usage_count + ?) /"
        "   (question_stats.usage_count + 1) ELSE question_stats.avg_seconds END,"
        " mistake_kind = CASE WHEN ? != '' THEN ? ELSE question_stats.mistake_kind END,"
        " updated_at = ?",
        (
            q["id"],
            q["subject"],
            q.get("topic", ""),
            1 if ok else 0,
            reattempt,
            day,
            day if ok else None,
            None if ok else day,
            float(seconds),
            float(conf or 0),
            mistake,
            now,
            1 if ok else 0,
            reattempt,
            day,
            1 if ok else 0,
            day,
            1 if ok else 0,
            day,
            seconds,
            float(seconds),
            mistake,
            mistake,
            now,
        ),
    )

    revision.record_attempt(conn, q, ok, seconds, conf, day)
    return dict(
        seconds=seconds, confidence=conf, mistake_kind=mistake, reattempt=bool(reattempt)
    )


def resume_quiz(conn, quiz_id):
    """Re-serve an unfinished set: same questions, same order, still unrevealed.

    Returns the same shape as ``build_quiz`` so the UI's open() needs no new
    branch - a resumed set is just a set it has seen before.
    """
    row = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if not row:
        raise LookupError("That set no longer exists.")
    if row["finished_at"]:
        raise ValueError("That set has already been submitted.")

    ids = [
        r["question_id"]
        for r in conn.execute(
            "SELECT question_id FROM quiz_questions WHERE quiz_id = ? ORDER BY position",
            (quiz_id,),
        )
    ]
    bank = content.question_bank()
    questions = [content.public_question(bank[qid]) for qid in ids if qid in bank]
    if not questions or len(questions) != len(ids):
        # Either the set predates the quiz_questions table, or the bank has
        # changed under it. Saying so is better than serving a set that is
        # quietly missing two questions and scoring it out of the wrong total.
        raise ValueError("That set cannot be rebuilt from the current bank.")

    subject_slug = None
    if row["subject_id"]:
        srow = conn.execute(
            "SELECT slug FROM subjects WHERE id = ?", (row["subject_id"],)
        ).fetchone()
        subject_slug = srow["slug"] if srow else None

    mode = row["mode"] or "practice"
    return dict(
        id=row["id"],
        mode=mode,
        mode_label=PURPOSE_LABELS.get(mode, mode.title()),
        reason=row["reason"],
        subject_id=row["subject_id"],
        subject_slug=subject_slug,
        topic_slugs=[s for s in (row["topic_slugs"] or "").split(",") if s],
        total_marks=row["total_marks"],
        dpp_set_id=row["dpp_set_id"],
        paper_id=row["paper_id"],
        plan_day=row["plan_day"],
        questions=questions,
        mistake_kinds=MISTAKE_KINDS,
        resumed=True,
    )


def submit_quiz(conn, quiz_id, responses, duration_s=0):
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if not quiz:
        raise ValueError("That quiz no longer exists.")
    if quiz["finished_at"]:
        raise ValueError("This quiz has already been submitted.")

    bank = content.question_bank()
    now = datetime.now().isoformat(timespec="seconds")
    today = date.today().isoformat()
    prior = _attempt_counts(conn)

    results = []
    got = 0.0
    correct_n = 0
    per_topic = {}
    with conn:
        for item in responses:
            qid = item.get("question_id")
            q = bank.get(qid)
            if not q:
                continue
            ok, awarded = grade_one(q, item.get("response"))
            got += awarded
            correct_n += 1 if ok else 0
            meta = _record_attempt(conn, q, item, ok, awarded, quiz, today, now, prior)

            t = per_topic.setdefault(
                q.get("topic", ""), dict(n=0, ok=0, subject=q["subject"])
            )
            t["n"] += 1
            t["ok"] += 1 if ok else 0

            results.append(
                dict(
                    question=content.public_question(q, reveal=True),
                    your_response=item.get("response"),
                    correct=ok,
                    marks_got=awarded,
                    why=item.get("why", ""),
                    **meta,
                )
            )

        conn.execute(
            "UPDATE quizzes SET scored_marks = ?, correct_count = ?, duration_s = ?,"
            " finished_at = ? WHERE id = ?",
            (round(got, 3), correct_n, int(duration_s or 0), now, quiz_id),
        )
        if quiz["dpp_set_id"]:
            conn.execute(
                "UPDATE dpp_sets SET finished_at = ?, correct = ?, total = ? WHERE id = ?",
                (now, correct_n, len(results), quiz["dpp_set_id"]),
            )

    peer = peer_curve(quiz_id, [r["question"] for r in results], got)
    breakdown = [
        dict(
            topic=k,
            subject=v["subject"],
            n=v["n"],
            correct=v["ok"],
            accuracy=round(v["ok"] / v["n"] * 100),
        )
        for k, v in sorted(per_topic.items(), key=lambda kv: -kv[1]["n"])
        if k
    ]
    wrong = [r for r in results if not r["correct"]]

    return dict(
        quiz_id=quiz_id,
        mode=quiz["mode"],
        total_marks=quiz["total_marks"],
        scored_marks=round(got, 2),
        correct_count=correct_n,
        question_count=len(results),
        accuracy=round(correct_n / len(results) * 100) if results else 0,
        results=results,
        breakdown=breakdown,
        wrong_ids=[r["question"]["id"] for r in wrong],
        retry_available=bool(wrong),
        mistake_kinds=MISTAKE_KINDS,
        peer=peer,
        dpp_set_id=quiz["dpp_set_id"],
        plan_day=quiz["plan_day"],
    )


def answer_question_of_day(conn, response, seconds=0, confidence=None):
    day = date.today().isoformat()
    row = conn.execute("SELECT * FROM daily_question WHERE day = ?", (day,)).fetchone()
    if not row:
        raise ValueError("No question has been served for today yet.")
    if row["answered_at"]:
        raise ValueError("Today's question has already been answered.")
    q = content.question_bank().get(row["question_id"])
    if not q:
        raise ValueError("That question is no longer in the bank.")

    ok, awarded = grade_one(q, response)
    now = datetime.now().isoformat(timespec="seconds")
    prior = _attempt_counts(conn)
    with conn:
        conn.execute(
            "UPDATE daily_question SET answered_at = ?, response = ?, correct = ? WHERE day = ?",
            (now, json.dumps(response), 1 if ok else 0, day),
        )
        _record_attempt(
            conn,
            q,
            dict(response=response, seconds=seconds, confidence=confidence),
            ok,
            awarded,
            None,
            day,
            now,
            prior,
        )
        conn.execute(
            "UPDATE attempts SET source = 'qotd' WHERE question_id = ? AND day = ?"
            " AND quiz_id IS NULL",
            (q["id"], day),
        )

    return dict(
        correct=ok,
        marks_got=awarded,
        question=content.public_question(q, reveal=True),
        peer=single_question_peer(q),
    )


# ---------------------------------------------------------------------------
# retry, saving, mistake tagging
# ---------------------------------------------------------------------------
def retry_set(conn, question_ids, reason="reattempt of what you just got wrong"):
    """Build an immediate-retry quiz from a list of question ids."""
    ids = [q for q in (question_ids or []) if q in content.question_bank()]
    if not ids:
        return None, "Nothing to retry."
    return build_quiz(
        conn, question_ids=ids, count=len(ids), mode="review", reason=reason
    )


def save_question(conn, question_id, saved=True):
    """Bookmark a question, and put it in (or take it out of) the revision queue.

    Bookmarking and enrolling used to be two separate things, which meant the
    star did nothing you could see later. There is only one thing a person means
    when they press it - "show me this again" - so the two now move together.
    Un-bookmarking deactivates the queue row rather than deleting it, so an
    accidental double-click does not throw away an interval you have earned.
    """
    q = content.question_bank().get(question_id)
    if not q:
        raise LookupError("Unknown question.")
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "INSERT INTO question_stats (question_id, subject_slug, topic_slug, saved,"
            " updated_at) VALUES (?,?,?,?,?)"
            " ON CONFLICT(question_id) DO UPDATE SET saved = excluded.saved,"
            " updated_at = excluded.updated_at",
            (question_id, q["subject"], q.get("topic", ""), 1 if saved else 0, now),
        )
        if saved:
            row = conn.execute(
                "SELECT id FROM revision_queue WHERE item_type = 'question'"
                " AND item_key = ?",
                (question_id,),
            ).fetchone()
            if row:
                # Already scheduled - reactivate without resetting the interval.
                conn.execute(
                    "UPDATE revision_queue SET active = 1, updated_at = ?"
                    " WHERE item_type = 'question' AND item_key = ?",
                    (now, question_id),
                )
            else:
                revision.enrol_question(conn, q)
        else:
            revision.drop(conn, "question", question_id)
    return dict(question_id=question_id, saved=bool(saved))


def revision_list(conn, day=None):
    """The user's revision list: bookmarked questions, and nothing else.

    Deliberately built from question_stats.saved rather than from
    revision_queue. The queue is the spacing engine - it also holds every topic
    you have started and every question you have got wrong, because the planner,
    the debt figure and the readiness score are all computed from it. Reading
    the list off the queue is what made the profile page show 300-odd rows the
    user never asked for.

    The schedule is still shown where one exists, via a LEFT JOIN: a bookmark
    that has been answered correctly twice has been retired from the queue, but
    it is still bookmarked, so it still belongs on this list.
    """
    day = day or date.today().isoformat()
    bank = content.question_bank()
    out = []
    for r in conn.execute(
        "SELECT qs.question_id AS qid, qs.updated_at AS saved_at,"
        "       rq.due_day, rq.reps, rq.lapses, rq.active, rq.interval_days"
        "  FROM question_stats qs"
        "  LEFT JOIN revision_queue rq"
        "    ON rq.item_type = 'question' AND rq.item_key = qs.question_id"
        " WHERE qs.saved = 1"
        " ORDER BY COALESCE(rq.due_day, '9999-12-31') ASC, qs.updated_at DESC"
    ):
        q = bank.get(r["qid"])
        if not q:
            # Bookmarked, then the question left the bank on a re-import. Say so
            # rather than dropping the row silently.
            out.append(
                dict(
                    question_id=r["qid"],
                    label=r["qid"],
                    missing=True,
                    subject_slug="",
                    topic_slug="",
                    difficulty="",
                    marks=0,
                    due_day=r["due_day"] or "",
                    reps=r["reps"] or 0,
                    lapses=r["lapses"] or 0,
                    scheduled=bool(r["active"]),
                    is_due=False,
                )
            )
            continue
        due = r["due_day"] or ""
        out.append(
            dict(
                question_id=r["qid"],
                label=(q.get("text") or r["qid"]).strip()[:110],
                missing=False,
                subject_slug=q.get("subject", ""),
                topic_slug=q.get("topic", ""),
                difficulty=q.get("difficulty", ""),
                marks=q.get("marks", 0),
                due_day=due,
                reps=r["reps"] or 0,
                lapses=r["lapses"] or 0,
                scheduled=bool(r["active"]),
                is_due=bool(due and r["active"] and due <= day),
            )
        )
    return out


def saved_ids(conn):
    """Every bookmarked question id, so the UI can draw the star correctly.

    A flat list rather than the full rows: the practice view only needs to know
    which stars are filled, and the payload already carries this state once.
    """
    return [
        r["question_id"]
        for r in conn.execute(
            "SELECT question_id FROM question_stats WHERE saved = 1"
        )
    ]


def saved_questions(conn, limit=40):
    bank = content.question_bank()
    out = []
    for r in conn.execute(
        "SELECT * FROM question_stats WHERE saved = 1 ORDER BY updated_at DESC LIMIT ?",
        (limit,),
    ):
        q = bank.get(r["question_id"])
        if not q:
            continue
        item = content.public_question(q)
        item["last_attempt_day"] = r["last_attempt_day"]
        item["usage_count"] = r["usage_count"]
        out.append(item)
    return out


def tag_mistake(conn, question_id, mistake_kind):
    if mistake_kind and mistake_kind not in MISTAKE_KINDS:
        raise ValueError("Unknown mistake category.")
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "UPDATE attempts SET mistake_kind = ? WHERE id = ("
            "  SELECT id FROM attempts WHERE question_id = ? ORDER BY id DESC LIMIT 1)",
            (mistake_kind, question_id),
        )
        conn.execute(
            "UPDATE question_stats SET mistake_kind = ?, updated_at = ?"
            " WHERE question_id = ?",
            (mistake_kind, now, question_id),
        )
    return mistake_breakdown(conn)


def mistake_breakdown(conn, days=90):
    since = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT mistake_kind, COUNT(*) n FROM attempts"
        " WHERE correct = 0 AND mistake_kind != '' AND day >= ?"
        " GROUP BY mistake_kind ORDER BY n DESC",
        (since,),
    ).fetchall()
    total = sum(r["n"] for r in rows)
    untagged = conn.execute(
        "SELECT COUNT(*) n FROM attempts WHERE correct = 0 AND mistake_kind = ''"
        " AND day >= ?",
        (since,),
    ).fetchone()["n"]
    return dict(
        items=[
            dict(
                kind=r["mistake_kind"],
                label=MISTAKE_KINDS[r["mistake_kind"]],
                n=r["n"],
                pct=round(r["n"] / total * 100),
            )
            for r in rows
        ],
        tagged=total,
        untagged=untagged,
        kinds=MISTAKE_KINDS,
    )


def confidence_report(conn, days=120):
    """Stated confidence against measured accuracy, bucket by bucket."""
    since = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT confidence, COUNT(*) n, SUM(correct) c FROM attempts"
        " WHERE confidence IS NOT NULL AND day >= ? GROUP BY confidence"
        " ORDER BY confidence",
        (since,),
    ).fetchall()
    buckets = []
    for r in rows:
        expected = (r["confidence"] - 1) / 4.0 * 100
        actual = (r["c"] or 0) / r["n"] * 100
        buckets.append(
            dict(
                confidence=r["confidence"],
                n=r["n"],
                accuracy=round(actual),
                expected=round(expected),
                gap=round(expected - actual),
            )
        )
    total = sum(b["n"] for b in buckets)
    return dict(
        available=total >= 8,
        n=total,
        buckets=buckets,
        note="Confidence is logged per question in practice mode. "
        "A positive gap means you feel surer than you are.",
    )


# ---------------------------------------------------------------------------
# simulated peer curve  (a model - see module docstring)
# ---------------------------------------------------------------------------
def single_question_peer(q):
    p = SOLVE_PROB.get(q.get("difficulty", "medium"), 0.5)
    return dict(
        simulated=True,
        solve_rate=round(p * 100),
        note="Modelled solve rate for a question of this difficulty. Not a live statistic.",
    )


def peer_curve(quiz_id, questions, your_score):
    """Sample a virtual cohort against the same paper and place your score."""
    if not questions:
        return None
    rng = random.Random("peer-%s" % quiz_id)
    probs = [SOLVE_PROB.get(q.get("difficulty", "medium"), 0.5) for q in questions]
    marks = [float(q.get("marks", 2)) for q in questions]
    total = sum(marks)

    scores = []
    for _ in range(PEER_SAMPLE):
        # Ability shifts every question's odds for that virtual student.
        ability = rng.gauss(0.0, 0.42)
        s = 0.0
        for p, m, q in zip(probs, marks, questions):
            adjusted = min(0.97, max(0.03, p + ability * 0.25))
            if rng.random() < adjusted:
                s += m
            elif q.get("type") == "mcq":
                # Model the same negative marking the user faces, applied when
                # a virtual student guesses rather than skipping.
                if rng.random() < 0.65:
                    s -= m / 3.0
        scores.append(s)

    scores.sort()
    below = sum(1 for s in scores if s < your_score)
    pct = below / len(scores) * 100
    mid = scores[len(scores) // 2]
    return dict(
        simulated=True,
        percentile=round(pct, 1),
        beat_count=below,
        sample=len(scores),
        median=round(mid, 2),
        top_decile=round(scores[int(len(scores) * 0.9)], 2),
        total_marks=round(total, 2),
        your_score=round(your_score, 2),
        note="Simulated cohort of %d virtual attempts, generated on this machine "
        "from question difficulty. No real students are involved." % len(scores),
    )


def quiz_history(conn, limit=25):
    rows = conn.execute(
        "SELECT q.*, s.name AS subject_name FROM quizzes q"
        " LEFT JOIN subjects s ON s.id = q.subject_id"
        " WHERE q.finished_at IS NOT NULL ORDER BY q.id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["mode_label"] = PURPOSE_LABELS.get(
            r["mode"], (r["mode"] or "practice").title()
        )
        item["secs_per_q"] = (
            round(r["duration_s"] / r["question_count"], 1)
            if r["question_count"] and r["duration_s"]
            else None
        )
        out.append(item)
    return out


def qotd_history(conn, limit=30):
    rows = conn.execute(
        "SELECT * FROM daily_question ORDER BY day DESC LIMIT ?", (limit,)
    ).fetchall()
    bank = content.question_bank()
    out = []
    for r in rows:
        q = bank.get(r["question_id"])
        out.append(
            dict(
                day=r["day"],
                answered=bool(r["answered_at"]),
                correct=bool(r["correct"]) if r["correct"] is not None else None,
                subject=q["subject"] if q else "",
                topic=q.get("topic", "") if q else "",
                reason=r["reason"],
            )
        )
    return out


def streak_of_daily_questions(conn):
    rows = conn.execute(
        "SELECT day, correct FROM daily_question WHERE answered_at IS NOT NULL ORDER BY day DESC"
    ).fetchall()
    if not rows:
        return 0
    streak = 0
    expected = date.today()
    for r in rows:
        d = date.fromisoformat(r["day"])
        if d == expected or (streak == 0 and d == expected - timedelta(days=1)):
            streak += 1
            expected = d - timedelta(days=1)
        else:
            break
    return streak
