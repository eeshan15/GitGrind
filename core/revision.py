"""Spaced repetition: the engine that pushes weak topics back at you.

The scheduler is an SM-2 variant. Every reviewable thing - a syllabus topic or
an individual question you got wrong - gets a row in ``revision_queue`` holding
an interval, an ease factor and a due date. Reviewing an item with a quality
score moves those three numbers; a lapse collapses the interval so the item
comes back tomorrow.

Why SM-2 and not something newer: it needs three numbers per item, no training,
no server, and it is well understood. It is exactly the right amount of
machinery for a local app.

Quality scale (SM-2 convention, 0 worst, 5 best):
    0  blank / no idea
    1  wrong, and it felt wrong
    2  wrong, but close
    3  correct with effort
    4  correct
    5  correct and instant
"""

from datetime import date, datetime, timedelta

from . import content

MIN_EASE = 1.3
MAX_EASE = 2.9
START_EASE = 2.5
FIRST_INTERVAL = 1.0
SECOND_INTERVAL = 3.0
MAX_INTERVAL = 180.0
LAPSE_INTERVAL = 1.0

# Anything at or below this quality is treated as a failure.
FAIL_AT = 2


def _today():
    return date.today().isoformat()


def _iso(d):
    return d.isoformat() if hasattr(d, "isoformat") else str(d)


def _days_between(a, b):
    try:
        return (date.fromisoformat(str(b)[:10]) - date.fromisoformat(str(a)[:10])).days
    except (ValueError, TypeError):
        return 0


# ---------------------------------------------------------------------------
# enrolment
# ---------------------------------------------------------------------------
def ensure(
    conn,
    item_type,
    item_key,
    subject_slug="",
    topic_slug="",
    label="",
    due_day=None,
    interval=FIRST_INTERVAL,
    strength=0.5,
):
    """Create the queue row if it is missing. Never resets an existing schedule."""
    now = datetime.now().isoformat(timespec="seconds")
    due = due_day or (date.today() + timedelta(days=int(interval))).isoformat()
    conn.execute(
        "INSERT OR IGNORE INTO revision_queue (item_type, item_key, subject_slug,"
        " topic_slug, label, due_day, interval_days, ease, strength, created_at, updated_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (
            item_type,
            item_key,
            subject_slug,
            topic_slug,
            label,
            due,
            float(interval),
            START_EASE,
            float(strength),
            now,
            now,
        ),
    )
    return conn.execute(
        "SELECT * FROM revision_queue WHERE item_type = ? AND item_key = ?",
        (item_type, item_key),
    ).fetchone()


def enrol_topic(conn, subject_slug, topic_slug, name="", first_interval=FIRST_INTERVAL):
    key = "%s/%s" % (subject_slug, topic_slug)
    return ensure(
        conn,
        "topic",
        key,
        subject_slug,
        topic_slug,
        name or topic_slug,
        interval=first_interval,
    )


def enrol_question(conn, question, quality=1):
    """A question you got wrong becomes its own review item."""
    row = ensure(
        conn,
        "question",
        question["id"],
        question.get("subject", ""),
        question.get("topic", ""),
        (question.get("text") or "")[:90],
        interval=LAPSE_INTERVAL,
    )
    return row


def drop(conn, item_type, item_key):
    conn.execute(
        "UPDATE revision_queue SET active = 0, updated_at = ?"
        " WHERE item_type = ? AND item_key = ?",
        (datetime.now().isoformat(timespec="seconds"), item_type, item_key),
    )


# ---------------------------------------------------------------------------
# scheduling
# ---------------------------------------------------------------------------
def quality_from_attempt(correct, seconds=0, confidence=None, marks=2):
    """Map a graded attempt onto the 0..5 SM-2 scale.

    Confidence matters: getting it right while unsure is a weaker signal than
    getting it right instantly, and should not earn a long interval.
    """
    par = 45.0 * max(1.0, float(marks) / 2.0)
    if not correct:
        if confidence is not None and confidence >= 4:
            return 0  # confidently wrong is the worst possible signal
        return 1 if seconds and seconds > par else 2
    q = 4
    if seconds and seconds < par * 0.6:
        q = 5
    elif seconds and seconds > par * 1.8:
        q = 3
    if confidence is not None:
        if confidence <= 2:
            q = min(q, 3)
        elif confidence >= 5 and q >= 4:
            q = 5
    return q


def review(
    conn, item_type, item_key, quality, day=None, subject_slug="", topic_slug="", label=""
):
    """Apply one review outcome and return the updated row as a dict."""
    day = day or _today()
    now = datetime.now().isoformat(timespec="seconds")
    row = conn.execute(
        "SELECT * FROM revision_queue WHERE item_type = ? AND item_key = ?",
        (item_type, item_key),
    ).fetchone()
    if row is None:
        row = ensure(conn, item_type, item_key, subject_slug, topic_slug, label)

    ease = float(row["ease"] or START_EASE)
    interval = float(row["interval_days"] or FIRST_INTERVAL)
    reps = int(row["reps"] or 0)
    lapses = int(row["lapses"] or 0)
    strength = float(row["strength"] or 0.5)
    quality = max(0, min(5, int(quality)))

    if quality <= FAIL_AT:
        reps = 0
        lapses += 1
        interval = LAPSE_INTERVAL
        ease = max(MIN_EASE, ease - 0.20)
        strength = max(0.0, strength - 0.22)
        result = "lapse"
    else:
        reps += 1
        # classic SM-2 ease adjustment
        ease = max(
            MIN_EASE,
            min(MAX_EASE, ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))),
        )
        if reps == 1:
            interval = FIRST_INTERVAL
        elif reps == 2:
            interval = SECOND_INTERVAL
        else:
            interval = min(MAX_INTERVAL, interval * ease)
        strength = min(1.0, strength + (0.06 if quality == 3 else 0.13))
        result = "pass"

    due = (
        date.fromisoformat(day) + timedelta(days=max(1, int(round(interval))))
    ).isoformat()
    conn.execute(
        "UPDATE revision_queue SET interval_days = ?, ease = ?, reps = ?, lapses = ?,"
        " due_day = ?, last_review_day = ?, last_result = ?, strength = ?, active = 1,"
        " updated_at = ? WHERE item_type = ? AND item_key = ?",
        (
            interval,
            ease,
            reps,
            lapses,
            due,
            day,
            result,
            strength,
            now,
            item_type,
            item_key,
        ),
    )
    if item_type == "topic" and topic_slug:
        conn.execute(
            "UPDATE topics SET last_revised = ? WHERE slug = ?", (day, topic_slug)
        )

    out = dict(
        conn.execute(
            "SELECT * FROM revision_queue WHERE item_type = ? AND item_key = ?",
            (item_type, item_key),
        ).fetchone()
    )
    out["quality"] = quality
    out["result"] = result
    return out


def record_attempt(conn, question, correct, seconds=0, confidence=None, day=None):
    """Feed one graded question into both the question and the topic schedule."""
    q = quality_from_attempt(correct, seconds, confidence, question.get("marks", 2))
    subject = question.get("subject", "")
    topic = question.get("topic", "")

    if correct and q >= 4:
        # A clean solve retires the question-level card, if there was one.
        existing = conn.execute(
            "SELECT reps FROM revision_queue WHERE item_type = 'question' AND item_key = ?",
            (question["id"],),
        ).fetchone()
        if existing:
            row = review(conn, "question", question["id"], q, day, subject, topic)
            if row["reps"] >= 2:
                drop(conn, "question", question["id"])
    else:
        enrol_question(conn, question)
        review(
            conn,
            "question",
            question["id"],
            q,
            day,
            subject,
            topic,
            (question.get("text") or "")[:90],
        )

    if topic:
        key = "%s/%s" % (subject, topic)
        meta = content.topic_index().get((subject, topic))
        review(
            conn, "topic", key, q, day, subject, topic, meta["name"] if meta else topic
        )
    return q


# ---------------------------------------------------------------------------
# reading the queue
# ---------------------------------------------------------------------------
def _priority(row, day, weight, marks):
    """Higher means "do this first"."""
    overdue = max(0, _days_between(row["due_day"], day))
    fresh = max(0, -_days_between(row["due_day"], day))
    p = overdue * 1.6
    p += (1.0 - float(row["strength"] or 0.5)) * 6.0
    p += int(row["lapses"] or 0) * 1.4
    p += (float(weight) / 3.0) + (float(marks) / 10.0)
    p -= fresh * 0.4
    if row["item_type"] == "question":
        p *= 0.75  # topics outrank single questions
    return round(p, 3)


def queue(conn, day=None, limit=40, include_future=True, item_type=None):
    day = day or _today()
    sql = "SELECT * FROM revision_queue WHERE active = 1"
    args = []
    if item_type:
        sql += " AND item_type = ?"
        args.append(item_type)
    if not include_future:
        sql += " AND due_day <= ?"
        args.append(day)
    rows = conn.execute(sql, tuple(args)).fetchall()

    idx = content.topic_index()
    out = []
    for r in rows:
        meta = idx.get((r["subject_slug"], r["topic_slug"])) or {}
        overdue = max(0, _days_between(r["due_day"], day))
        item = dict(r)
        item["overdue_days"] = overdue
        item["due_in_days"] = max(0, -_days_between(r["due_day"], day))
        item["is_due"] = r["due_day"] <= day
        item["topic_name"] = meta.get("name") or r["label"] or r["topic_slug"]
        item["subject_name"] = meta.get("subject_name", r["subject_slug"])
        item["weight"] = meta.get("weight", 1)
        item["marks"] = meta.get("marks", 5)
        item["strength_pct"] = round(float(r["strength"] or 0) * 100)
        item["priority"] = _priority(r, day, item["weight"], item["marks"])
        item["state"] = (
            "overdue" if overdue > 0 else "due" if item["is_due"] else "scheduled"
        )
        out.append(item)

    out.sort(key=lambda x: (-x["priority"], x["due_day"]))
    return out[:limit]


def debt(conn, day=None):
    """Revision debt: how much overdue material is sitting on the pile."""
    day = day or _today()
    items = queue(conn, day, limit=500, include_future=False)
    overdue = [i for i in items if i["overdue_days"] > 0]
    topics = [i for i in overdue if i["item_type"] == "topic"]
    weighted = sum(i["overdue_days"] * (i["weight"] / 2.0 + 1) for i in overdue)
    worst = topics[0] if topics else (overdue[0] if overdue else None)
    return dict(
        due_today=len([i for i in items if i["is_due"]]),
        overdue=len(overdue),
        overdue_topics=len(topics),
        overdue_questions=len(overdue) - len(topics),
        oldest_days=max([i["overdue_days"] for i in overdue], default=0),
        weighted=round(weighted, 1),
        # 0..100, saturating around "twenty topic-days behind"
        pressure=min(100, round(weighted / 40.0 * 100)) if weighted else 0,
        worst=(
            dict(
                topic=worst["topic_slug"],
                name=worst["topic_name"],
                subject=worst["subject_slug"],
                days=worst["overdue_days"],
            )
            if worst
            else None
        ),
    )


def strength_map(conn):
    """{(subject, topic): strength 0..1} for the mastery heatmap."""
    out = {}
    for r in conn.execute(
        "SELECT subject_slug, topic_slug, strength, due_day, lapses, reps"
        " FROM revision_queue WHERE item_type = 'topic' AND active = 1"
    ):
        out[(r["subject_slug"], r["topic_slug"])] = dict(
            strength=float(r["strength"] or 0),
            due_day=r["due_day"],
            lapses=r["lapses"],
            reps=r["reps"],
        )
    return out


# ---------------------------------------------------------------------------
# backfill
# ---------------------------------------------------------------------------
def sync_from_activity(conn, day=None):
    """Enrol anything the user has touched but that has no schedule yet.

    Runs cheaply on every state build so an existing v2 database grows a
    revision queue on its own, with intervals inferred from how long ago the
    topic was last actually studied.
    """
    day = day or _today()
    have = {
        (r["item_type"], r["item_key"])
        for r in conn.execute("SELECT item_type, item_key FROM revision_queue")
    }
    idx = content.topic_index()
    now = datetime.now().isoformat(timespec="seconds")
    added = 0

    rows = conn.execute(
        "SELECT t.slug AS topic_slug, t.name, t.status, t.updated_at, t.last_revised,"
        " sub.slug AS subject_slug,"
        " (SELECT MAX(s.day) FROM session_topics st JOIN sessions s ON s.id = st.session_id"
        "   WHERE st.topic_id = t.id) AS last_session,"
        " (SELECT MAX(a.day) FROM attempts a WHERE a.topic_slug = t.slug) AS last_attempt,"
        " (SELECT AVG(a.correct) FROM attempts a WHERE a.topic_slug = t.slug) AS acc"
        " FROM topics t JOIN subjects sub ON sub.id = t.subject_id"
        " WHERE t.status IN ('learning','done')"
    ).fetchall()

    with conn:
        for r in rows:
            key = "%s/%s" % (r["subject_slug"], r["topic_slug"])
            if ("topic", key) in have:
                continue
            seen = max(
                [
                    x
                    for x in (
                        r["last_session"],
                        r["last_attempt"],
                        r["last_revised"],
                        (r["updated_at"] or "")[:10],
                    )
                    if x
                ]
                or [day]
            )
            acc = r["acc"]
            strength = 0.55 if r["status"] == "done" else 0.35
            if acc is not None:
                strength = max(0.05, min(0.95, 0.25 + float(acc) * 0.6))
            # Someone who last touched this two months ago is overdue now.
            gap = max(0, _days_between(seen, day))
            interval = 3.0 if r["status"] == "done" else 1.0
            due = (date.fromisoformat(seen) + timedelta(days=int(interval))).isoformat()
            meta = idx.get((r["subject_slug"], r["topic_slug"])) or {}
            conn.execute(
                "INSERT OR IGNORE INTO revision_queue (item_type, item_key, subject_slug,"
                " topic_slug, label, due_day, interval_days, ease, reps, strength,"
                " last_review_day, created_at, updated_at)"
                " VALUES ('topic',?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    key,
                    r["subject_slug"],
                    r["topic_slug"],
                    meta.get("name") or r["name"],
                    due,
                    interval,
                    START_EASE,
                    1 if r["status"] == "done" else 0,
                    strength,
                    seen,
                    now,
                    now,
                ),
            )
            added += 1

        # questions answered wrong and never revisited become review cards
        wrong = conn.execute(
            "SELECT a.question_id, a.subject_slug, a.topic_slug, MAX(a.day) AS day,"
            " SUM(a.correct) AS ok, COUNT(*) AS n FROM attempts a"
            " GROUP BY a.question_id HAVING ok = 0"
        ).fetchall()
        for r in wrong:
            if ("question", r["question_id"]) in have:
                continue
            conn.execute(
                "INSERT OR IGNORE INTO revision_queue (item_type, item_key, subject_slug,"
                " topic_slug, label, due_day, interval_days, ease, lapses, strength,"
                " last_review_day, created_at, updated_at)"
                " VALUES ('question',?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    r["question_id"],
                    r["subject_slug"],
                    r["topic_slug"],
                    "",
                    r["day"],
                    LAPSE_INTERVAL,
                    START_EASE,
                    r["n"],
                    0.2,
                    r["day"],
                    now,
                    now,
                ),
            )
            added += 1
    return added
