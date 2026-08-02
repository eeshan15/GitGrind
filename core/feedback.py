"""The RLHF-inspired loop, minus the pretending.

There is no reward model here and no gradient descent. What there is:

1. **Preference logging.** Every recommendation, DPP block and doubt answer can
   be rated. The rating, the reason, the time spent and whether the user
   actually followed the suggestion all land in the ``feedback`` table.

2. **Online re-ranking.** Those signals move a small set of multiplicative
   weights in ``learned_weights``. A recommendation kind that keeps getting
   "not helpful" drops down the list. A topic tagged "wrong topic" stops being
   surfaced so eagerly. Difficulty and length preferences shift the DPP mix.

3. **Nothing blocks on it.** Every weight defaults to 1.0, so an empty feedback
   table means the engine behaves exactly like a plain rules engine. The app is
   fully useful on day one and gets a little more personal from week two.

That is the whole design. If enough feedback ever accumulates, this table is
also the training set for a real ranker - but that is a later problem, and the
app must never depend on it.
"""

import json
from datetime import date, datetime, timedelta

# Learning rate for the online weight update. Deliberately small: one grumpy
# afternoon should not permanently delete a whole recommendation kind.
LR = 0.08
MIN_W = 0.35
MAX_W = 1.90

# Ratings arrive as words from the UI; these are their numeric signals.
RATING_SIGNAL = {
    "helpful": 1.0,
    "not_helpful": -1.0,
    "too_easy": -0.35,
    "too_hard": -0.35,
    "too_long": -0.30,
    "too_short": -0.20,
    "wrong_topic": -0.85,
    "wrong_priority": -0.45,
    "chose_other": -0.55,
    "followed": 0.65,
    "skipped": -0.40,
    "helped": 1.0,
    "did_not_help": -0.9,
}

ANSWER_LABELS = {
    "helpful": "Helpful",
    "not_helpful": "Not helpful",
    "too_easy": "Too easy",
    "too_hard": "Too hard",
    "too_long": "Too long",
    "too_short": "Too short",
    "wrong_topic": "Wrong topic",
    "wrong_priority": "Right topic, wrong priority",
    "chose_other": "I did something else",
}

SCOPES = ("rec_kind", "topic", "difficulty", "length", "block_kind")


# ---------------------------------------------------------------------------
# weights
# ---------------------------------------------------------------------------
def weights(conn, scope):
    return {
        r["key"]: dict(weight=float(r["weight"]), samples=int(r["samples"]))
        for r in conn.execute(
            "SELECT key, weight, samples FROM learned_weights WHERE scope = ?", (scope,)
        )
    }


def weight_of(conn, scope, key, default=1.0):
    row = conn.execute(
        "SELECT weight FROM learned_weights WHERE scope = ? AND key = ?",
        (scope, str(key)),
    ).fetchone()
    return float(row["weight"]) if row else default


def bump(conn, scope, key, signal, lr=LR):
    """Move one weight by ``lr * signal`` and clamp it. Idempotent and cheap."""
    key = str(key or "")
    if not key or scope not in SCOPES:
        return None
    now = datetime.now().isoformat(timespec="seconds")
    row = conn.execute(
        "SELECT weight, samples FROM learned_weights WHERE scope = ? AND key = ?",
        (scope, key),
    ).fetchone()
    current = float(row["weight"]) if row else 1.0
    samples = int(row["samples"]) if row else 0
    # Later samples move the weight less, so it settles instead of oscillating.
    step = lr / (1.0 + samples / 24.0)
    new = max(MIN_W, min(MAX_W, current + step * float(signal)))
    conn.execute(
        "INSERT INTO learned_weights (scope, key, weight, samples, updated_at)"
        " VALUES (?,?,?,?,?) ON CONFLICT(scope, key) DO UPDATE SET"
        " weight = excluded.weight, samples = learned_weights.samples + 1,"
        " updated_at = excluded.updated_at",
        (scope, key, new, samples + 1, now),
    )
    return new


# ---------------------------------------------------------------------------
# recording
# ---------------------------------------------------------------------------
def record(
    conn,
    target_type,
    answer,
    target_slug="",
    target_id="",
    rating=None,
    subject_slug="",
    topic_slug="",
    reason="",
    time_spent_s=0,
    completed=None,
    followed=None,
    correction="",
    payload=None,
    day=None,
):
    """Log one preference signal and let it move the weights.

    ``answer`` is the button the user pressed (see ANSWER_LABELS). ``rating`` is
    an optional 1..5 star value. Either is enough on its own.
    """
    day = day or date.today().isoformat()
    now = datetime.now().isoformat(timespec="seconds")
    answer = str(answer or "").strip()

    difficulty = ""
    length = ""
    if answer in ("too_easy", "too_hard"):
        difficulty = answer
    if answer in ("too_long", "too_short"):
        length = answer

    with conn:
        cur = conn.execute(
            "INSERT INTO feedback (target_type, target_id, target_slug, subject_slug,"
            " topic_slug, rating, answer, reason, difficulty, length, followed, completed,"
            " time_spent_s, correction, day, payload, created_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                target_type,
                str(target_id or ""),
                target_slug,
                subject_slug,
                topic_slug,
                rating,
                answer,
                reason,
                difficulty,
                length,
                None if followed is None else int(bool(followed)),
                None if completed is None else int(bool(completed)),
                int(time_spent_s or 0),
                correction,
                day,
                json.dumps(payload or {}),
                now,
            ),
        )
        fid = cur.lastrowid

        signal = RATING_SIGNAL.get(answer, 0.0)
        if rating is not None:
            try:
                signal += (float(rating) - 3.0) / 2.0
            except (TypeError, ValueError):
                pass
        if followed is not None:
            signal += 0.4 if followed else -0.3

        if signal:
            if target_type in ("recommendation", "next_action") and target_slug:
                bump(conn, "rec_kind", target_slug, signal)
            if target_type in ("dpp_block", "plan_block") and target_slug:
                bump(conn, "block_kind", target_slug, signal)
            if topic_slug and answer in ("wrong_topic", "wrong_priority", "helpful"):
                bump(conn, "topic", topic_slug, signal)
            if difficulty:
                # "too easy" should push the difficulty dial up, not down.
                bump(
                    conn, "difficulty", "level", 0.9 if difficulty == "too_easy" else -0.9
                )
            if length:
                bump(conn, "length", "size", 0.8 if length == "too_short" else -0.8)

        # Close the loop on the recommendation itself.
        if target_type == "recommendation" and target_id:
            conn.execute(
                "UPDATE recommendations SET outcome = ?,"
                " acted_at = COALESCE(acted_at, CASE WHEN ? = 1 THEN ? ELSE NULL END),"
                " dismissed_at = COALESCE(dismissed_at, CASE WHEN ? = 'not_helpful'"
                "   THEN ? ELSE NULL END) WHERE id = ?",
                (answer, 1 if followed else 0, now, answer, now, int(target_id)),
            )

    return fid


def mark_shown(conn, recs, day=None):
    """Persist the recommendations we put in front of the user this render.

    Without this there is nothing to attach a rating to later, and no way to
    ask "did following this actually help".
    """
    day = day or date.today().isoformat()
    now = datetime.now().isoformat(timespec="seconds")
    out = []
    with conn:
        for r in recs:
            row = conn.execute(
                "SELECT id FROM recommendations WHERE day = ? AND slug = ?",
                (day, r["slug"]),
            ).fetchone()
            if row:
                rid = row["id"]
                conn.execute(
                    "UPDATE recommendations SET title = ?, detail = ?, reason = ?,"
                    " expected = ?, urgency = ?, score = ?, topic_slug = ?,"
                    " subject_slug = ?, payload = ? WHERE id = ?",
                    (
                        r.get("title", ""),
                        r.get("detail", ""),
                        r.get("reason", ""),
                        r.get("expected", ""),
                        r.get("urgency", 0),
                        r.get("score", 0),
                        r.get("topic_slug", ""),
                        r.get("subject_slug", ""),
                        json.dumps(r.get("payload") or {}),
                        rid,
                    ),
                )
            else:
                cur = conn.execute(
                    "INSERT INTO recommendations (day, slug, kind, title, detail, reason,"
                    " expected, subject_slug, topic_slug, urgency, score, payload, shown_at)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        day,
                        r["slug"],
                        r.get("kind", "study"),
                        r.get("title", ""),
                        r.get("detail", ""),
                        r.get("reason", ""),
                        r.get("expected", ""),
                        r.get("subject_slug", ""),
                        r.get("topic_slug", ""),
                        r.get("urgency", 0),
                        r.get("score", 0),
                        json.dumps(r.get("payload") or {}),
                        now,
                    ),
                )
                rid = cur.lastrowid
            r["id"] = rid
            out.append(r)
    return out


# ---------------------------------------------------------------------------
# reading it back
# ---------------------------------------------------------------------------
def difficulty_dial(conn):
    """-1 (wants easier) .. +1 (wants harder). Zero when nobody has said anything."""
    w = weight_of(conn, "difficulty", "level", 1.0)
    return round(max(-1.0, min(1.0, (w - 1.0) / 0.9)), 3)


def length_dial(conn):
    w = weight_of(conn, "length", "size", 1.0)
    return round(max(-1.0, min(1.0, (w - 1.0) / 0.8)), 3)


def topic_multiplier(conn, topic_slug):
    return weight_of(conn, "topic", topic_slug, 1.0)


def kind_multiplier(conn, slug):
    return weight_of(conn, "rec_kind", slug, 1.0)


def block_multiplier(conn, block_kind):
    return weight_of(conn, "block_kind", block_kind, 1.0)


def followed_rate(conn, slug=None, days=45):
    since = (date.today() - timedelta(days=days)).isoformat()
    sql = (
        "SELECT COUNT(*) n, SUM(COALESCE(followed,0)) f FROM feedback"
        " WHERE target_type IN ('recommendation','next_action') AND day >= ?"
    )
    args = [since]
    if slug:
        sql += " AND target_slug = ?"
        args.append(slug)
    row = conn.execute(sql, tuple(args)).fetchone()
    if not row["n"]:
        return None
    return round((row["f"] or 0) / row["n"] * 100)


def summary(conn, days=60):
    """Small honest report for the UI: what the loop has actually learnt."""
    since = (date.today() - timedelta(days=days)).isoformat()
    total = conn.execute("SELECT COUNT(*) n FROM feedback").fetchone()["n"]
    recent = conn.execute(
        "SELECT COUNT(*) n FROM feedback WHERE day >= ?", (since,)
    ).fetchone()["n"]
    by_answer = {
        r["answer"]: r["n"]
        for r in conn.execute(
            "SELECT answer, COUNT(*) n FROM feedback WHERE answer != ''"
            " GROUP BY answer ORDER BY n DESC"
        )
    }
    helpful = by_answer.get("helpful", 0) + by_answer.get("helped", 0)
    unhelpful = by_answer.get("not_helpful", 0) + by_answer.get("did_not_help", 0)

    learned = []
    for scope in SCOPES:
        for key, meta in weights(conn, scope).items():
            if abs(meta["weight"] - 1.0) < 0.03:
                continue
            learned.append(
                dict(
                    scope=scope,
                    key=key,
                    weight=round(meta["weight"], 3),
                    samples=meta["samples"],
                    direction="up" if meta["weight"] > 1 else "down",
                )
            )
    learned.sort(key=lambda x: -abs(x["weight"] - 1.0))

    return dict(
        total=total,
        recent=recent,
        active=total >= 5,
        by_answer=by_answer,
        helpful=helpful,
        unhelpful=unhelpful,
        helpful_pct=(
            round(helpful / (helpful + unhelpful) * 100)
            if (helpful + unhelpful)
            else None
        ),
        followed_pct=followed_rate(conn),
        difficulty_dial=difficulty_dial(conn),
        length_dial=length_dial(conn),
        learned=learned[:12],
        note=(
            "Ranking is still pure rules - rate a few suggestions and it starts "
            "adapting."
            if total < 5
            else "%d signals logged. Recommendation order is now partly learned from "
            "your ratings." % total
        ),
        answer_labels=ANSWER_LABELS,
    )


def history(conn, limit=40):
    rows = conn.execute(
        "SELECT * FROM feedback ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["answer_label"] = ANSWER_LABELS.get(r["answer"], r["answer"])
        out.append(item)
    return out
