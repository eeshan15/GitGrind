"""The daily plan and DPP generator.

Every morning the app has to answer one question: *what should today look like?*
This module answers it from the data rather than from a fixed template.

Input signals (section 10 of the spec):
  weakest topics, overdue revision, recent wrong answers, low-confidence
  questions, stale concepts, available time, streak status, exam horizon.

Output: an ordered list of blocks. Each block carries three sentences of
justification - why it was selected, what it is fixing, what improvement it
aims for - because a plan you do not believe is a plan you will not follow.

Blocks are generated but not materialised. Questions are only pulled from the
bank when the user actually starts a block, so a plan sitting unopened for three
days does not serve stale questions.
"""

import json
from datetime import date, datetime

from . import db, feedback, quiz, revision

# Minutes budgeted per question, by block purpose.
PACE = {
    "review": 2.5,
    "weak": 3.5,
    "mixed": 3.0,
    "speed": 1.4,
    "boss": 8.0,
    "fresh": 3.2,
}

BLOCK_ICONS = {
    "revise": "R",
    "concept": "C",
    "practice": "P",
    "speed": "S",
    "boss": "B",
    "mock": "M",
}


def _today():
    return date.today().isoformat()


def _horizon(conn):
    settings = db.get_settings(conn)
    raw = settings.get("exam_date")
    if not raw:
        return None
    try:
        return (date.fromisoformat(raw) - date.today()).days
    except ValueError:
        return None


def _scale_for_time(available, base_total):
    """Return a multiplier so the plan fits the time the user actually has."""
    if not base_total:
        return 1.0
    return max(0.35, min(1.6, available / float(base_total)))


# ---------------------------------------------------------------------------
# generation
# ---------------------------------------------------------------------------
def generate(conn, bundle, day=None, available_mins=None):
    """Build today's plan from the analytics bundle. Pure - does not write."""
    day = day or _today()
    metrics = bundle["metrics"]
    health = bundle.get("topic_health") or []
    debt = bundle.get("debt") or {}
    vel = bundle.get("velocity") or {}
    subjects = bundle["subjects"]
    target = int(available_mins or bundle.get("daily_target") or 240)
    horizon = _horizon(conn)

    length_dial = feedback.length_dial(conn)  # -1 shorter .. +1 longer
    size_mult = 1.0 + length_dial * 0.30

    covered = {
        (r["subject"], r["topic"]) for r in health if r["status"] in ("done", "learning")
    }
    by_key = {(r["subject"], r["topic"]): r for r in health}

    blocks = []
    notes = []

    # ---- 1. revision debt comes first -----------------------------------
    overdue_items = [
        i
        for i in revision.queue(conn, day, limit=40, include_future=False)
        if i["overdue_days"] > 0
    ]
    overdue_topics = [i for i in overdue_items if i["item_type"] == "topic"]

    if overdue_topics:
        worst = overdue_topics[0]
        blocks.append(
            dict(
                key="revise-topic",
                kind="revise",
                label="Revise %s" % worst["topic_name"],
                purpose="review",
                subject=worst["subject_slug"],
                subject_name=worst["subject_name"],
                topic=worst["topic_slug"],
                topic_name=worst["topic_name"],
                minutes=int(round(min(45, 20 + worst["overdue_days"] * 1.5))),
                count=0,
                reason="Scheduled review was due %d day%s ago and retention decays fastest "
                "right after the due date."
                % (worst["overdue_days"], "s" if worst["overdue_days"] != 1 else ""),
                fixing="Forgetting on a topic you already paid for once.",
                aim="Push the next review out to about %d days and stop the strength "
                "sliding further." % max(3, int(worst["interval_days"] * 1.8)),
            )
        )
        notes.append(
            "%d topic%s overdue for revision"
            % (len(overdue_topics), "s" if len(overdue_topics) != 1 else "")
        )

    review_n = 0
    if overdue_items:
        review_n = int(round(min(10, max(3, len(overdue_items) * 0.8)) * size_mult))
        blocks.append(
            dict(
                key="dpp-review",
                kind="practice",
                label="Revision questions",
                purpose="review",
                count=review_n,
                minutes=int(round(review_n * PACE["review"])),
                reason="%d item%s in the revision queue are past due, including %d question%s "
                "you previously got wrong."
                % (
                    len(overdue_items),
                    "s" if len(overdue_items) != 1 else "",
                    debt.get("overdue_questions", 0),
                    "s" if debt.get("overdue_questions", 0) != 1 else "",
                ),
                fixing="Revision debt sitting at %d/100 pressure."
                % debt.get("pressure", 0),
                aim="Clear the oldest cards and drop revision pressure below 30.",
            )
        )

    # ---- 2. the weakest covered topic -----------------------------------
    weak = [
        r
        for r in health
        if (r["subject"], r["topic"]) in covered and r["band"] in ("critical", "weak")
    ]
    weak.sort(key=lambda r: -r["risk"])
    weak = [r for r in weak if feedback.topic_multiplier(conn, r["topic"]) > 0.55]

    if weak:
        w = weak[0]
        weak_n = int(round(max(5, min(12, 6 + w["risk"] / 14.0)) * size_mult))
        acc_line = (
            "accuracy is %d%% over %d attempts" % (w["accuracy"], w["attempts"])
            if w["accuracy"] is not None
            else "no accuracy sample yet"
        )
        blocks.append(
            dict(
                key="dpp-weak",
                kind="practice",
                label="%s drill" % w["name"],
                purpose="weak",
                subject=w["subject"],
                subject_name=w["subject_name"],
                topic=w["topic"],
                topic_name=w["name"],
                topic_id=w["topic_id"],
                subject_id=w["subject_id"],
                count=weak_n,
                minutes=int(round(weak_n * PACE["weak"])),
                reason="Highest-risk topic you have already studied: %s, and %s carries "
                "%d marks in the paper." % (acc_line, w["subject_name"], w["marks"]),
                fixing="A %s topic at %d/100 risk." % (w["band"], w["risk"]),
                aim="Lift this topic out of the %s band; that is worth roughly %.1f points "
                "of coverage-weighted readiness."
                % (w["band"], w["weight"] * w["marks"] / 40.0),
            )
        )
        notes.append("%s is the weakest covered topic" % w["name"])

    # ---- 3. coverage: the next concept worth opening ---------------------
    pending = [r for r in health if r["status"] == "pending"]
    pending.sort(key=lambda r: (-r["marks"], -r["weight"], r["name"]))
    if pending and (horizon is None or horizon > 25):
        p = pending[0]
        blocks.append(
            dict(
                key="concept",
                kind="concept",
                label="Start %s" % p["name"],
                purpose=None,
                subject=p["subject"],
                subject_name=p["subject_name"],
                topic=p["topic"],
                topic_name=p["name"],
                topic_id=p["topic_id"],
                subject_id=p["subject_id"],
                minutes=int(round(min(90, max(35, 20 + p["weight"] * 12)))),
                count=0,
                reason="Untouched topic in %s, which is worth %d marks. Coverage is the "
                "single heaviest term in the readiness index."
                % (p["subject_name"], p["marks"]),
                fixing="A gap in the syllabus, not a weakness in what you know.",
                aim="Move coverage up by about %.1f%% once this is marked done."
                % (p["weight"] / max(1, metrics.get("topic_weight_total", 1)) * 100),
            )
        )

    # ---- 4. mixed previous-year spread ----------------------------------
    if metrics.get("questions_attempted", 0) >= 10 or not weak:
        mixed_n = int(
            round(max(4, min(8, 5 + (metrics.get("coverage_pct", 0) / 25))) * size_mult)
        )
        blocks.append(
            dict(
                key="dpp-mixed",
                kind="practice",
                label="Mixed PYQ set",
                purpose="mixed",
                count=mixed_n,
                minutes=int(round(mixed_n * PACE["mixed"])),
                reason="Single-topic practice flatters you. Mixed sets are the only way to "
                "find out whether you can still pick the right method under doubt.",
                fixing="Topic-shaped confidence that does not survive a real paper.",
                aim="Keep overall accuracy honest; currently %d%%."
                % metrics.get("accuracy", 0),
            )
        )

    # ---- 5. speed, when pace is the problem -----------------------------
    avg_secs = metrics.get("avg_seconds_per_question") or 0
    slow = avg_secs and avg_secs > 105
    near_exam = horizon is not None and horizon <= 90
    if slow or near_exam:
        speed_n = int(round((6 if near_exam else 5) * size_mult))
        why = (
            (
                "You are averaging %ds per question, which does not fit a 180-minute "
                "paper." % round(avg_secs)
            )
            if slow
            else (
                "%d days to the exam - pace now matters as much as knowledge." % horizon
            )
        )
        blocks.append(
            dict(
                key="dpp-speed",
                kind="speed",
                label="Speed drill",
                purpose="speed",
                count=speed_n,
                minutes=int(round(speed_n * PACE["speed"])),
                reason=why,
                fixing="Time per question, not correctness.",
                aim="Get one-mark questions under 45 seconds without dropping accuracy.",
            )
        )

    # ---- 6. one boss question -------------------------------------------
    if len(covered) >= 6 and metrics.get("questions_attempted", 0) >= 20:
        blocks.append(
            dict(
                key="boss",
                kind="boss",
                label="Boss question",
                purpose="boss",
                count=1,
                minutes=int(PACE["boss"]),
                reason="One deliberately hard question from ground you have covered. This is "
                "where the top few marks in the paper actually live.",
                fixing="The habit of stopping at medium difficulty.",
                aim="Clear it and the boss-battle badge track moves; fail it and you get a "
                "precise gap to study.",
            )
        )

    # ---- fit the plan to the available time -----------------------------
    base_total = sum(b["minutes"] for b in blocks)
    scale = _scale_for_time(target, base_total)
    if scale < 0.98 or scale > 1.02:
        # Trim from the back: revision and the weakest topic are never cut first.
        priority = [
            "revise-topic",
            "dpp-review",
            "dpp-weak",
            "concept",
            "dpp-mixed",
            "dpp-speed",
            "boss",
        ]
        order = {k: i for i, k in enumerate(priority)}
        blocks.sort(key=lambda b: order.get(b["key"], 99))
        budget = target
        kept = []
        for b in blocks:
            if budget <= 4 and kept:
                break
            mins = b["minutes"]
            if mins > budget and kept:
                if b["count"]:
                    ratio = max(0.34, budget / float(mins))
                    b["count"] = max(1, int(round(b["count"] * ratio)))
                    b["minutes"] = max(
                        4, int(round(b["count"] * PACE.get(b["purpose"] or "weak", 3.0)))
                    )
                else:
                    b["minutes"] = max(10, budget)
            budget -= b["minutes"]
            kept.append(b)
        blocks = kept

    for i, b in enumerate(blocks):
        b["order"] = i
        b["icon"] = BLOCK_ICONS.get(b["kind"], "P")
        b.setdefault("count", 0)
        b.setdefault("subject", "")
        b.setdefault("topic", "")
        b["done"] = False
        b["dpp_set_id"] = None

    reason = (
        "Today is built around "
        + (
            ", ".join(notes[:2])
            if notes
            else "coverage and a mixed set, because nothing is overdue yet"
        )
        + "."
    )
    return dict(
        day=day,
        target_mins=target,
        horizon_days=horizon,
        blocks=blocks,
        reason=reason,
        total_minutes=sum(b["minutes"] for b in blocks),
        total_questions=sum(b["count"] for b in blocks),
        status="open",
        done_blocks=[],
        generated_at=datetime.now().isoformat(timespec="seconds"),
        signals=dict(
            revision_pressure=debt.get("pressure", 0),
            overdue=debt.get("overdue", 0),
            weak_topics=metrics.get("weak_topics", 0),
            velocity_trend=vel.get("trend"),
            streak=metrics.get("current_streak", 0),
            horizon_days=horizon,
            accuracy=metrics.get("accuracy", 0),
            length_dial=length_dial,
        ),
    )


# ---------------------------------------------------------------------------
# persistence
# ---------------------------------------------------------------------------
def _load(conn, day):
    row = conn.execute("SELECT * FROM daily_plans WHERE day = ?", (day,)).fetchone()
    if not row:
        return None
    try:
        blocks = json.loads(row["blocks"])
        done = json.loads(row["done_blocks"])
    except ValueError:
        return None
    plan = dict(
        day=row["day"],
        target_mins=row["target_mins"],
        horizon_days=row["horizon_days"],
        blocks=blocks,
        reason=row["reason"],
        status=row["status"],
        done_blocks=done,
        generated_at=row["generated_at"],
        rating=row["rating"],
        notes=row["notes"],
    )
    for b in blocks:
        b["done"] = b["key"] in done
    plan["total_minutes"] = sum(b["minutes"] for b in blocks)
    plan["total_questions"] = sum(b.get("count", 0) for b in blocks)
    plan["done_count"] = len(done)
    plan["block_count"] = len(blocks)
    plan["progress_pct"] = round(len(done) / len(blocks) * 100) if blocks else 0
    return plan


def save(conn, plan):
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "INSERT INTO daily_plans (day, generated_at, target_mins, horizon_days,"
            " blocks, reason, status, done_blocks, updated_at)"
            " VALUES (?,?,?,?,?,?,?,?,?)"
            " ON CONFLICT(day) DO UPDATE SET blocks = excluded.blocks,"
            " reason = excluded.reason, target_mins = excluded.target_mins,"
            " horizon_days = excluded.horizon_days, status = excluded.status,"
            " updated_at = excluded.updated_at",
            (
                plan["day"],
                plan.get("generated_at", now),
                plan["target_mins"],
                plan.get("horizon_days"),
                json.dumps(plan["blocks"]),
                plan["reason"],
                plan.get("status", "open"),
                json.dumps(plan.get("done_blocks", [])),
                now,
            ),
        )
    return _load(conn, plan["day"])


def plan_for(conn, bundle, day=None, regenerate=False, available_mins=None):
    """Load today's plan, generating it once if it does not exist yet."""
    day = day or _today()
    existing = None if regenerate else _load(conn, day)
    if existing:
        return existing
    settings = db.get_settings(conn)
    if not regenerate and not db.setting_bool(settings, "plan_auto_generate", True):
        fresh = generate(conn, bundle, day, available_mins)
        fresh["persisted"] = False
        fresh["done_count"] = 0
        fresh["block_count"] = len(fresh["blocks"])
        fresh["progress_pct"] = 0
        return fresh
    return save(conn, generate(conn, bundle, day, available_mins))


def complete_block(conn, day, block_key, done=True):
    plan = _load(conn, day)
    if not plan:
        raise LookupError("No plan for %s." % day)
    keys = [b["key"] for b in plan["blocks"]]
    if block_key not in keys:
        raise ValueError("That block is not in today's plan.")
    done_set = set(plan["done_blocks"])
    if done:
        done_set.add(block_key)
    else:
        done_set.discard(block_key)
    status = "done" if len(done_set) >= len(keys) else "open"
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "UPDATE daily_plans SET done_blocks = ?, status = ?, updated_at = ?"
            " WHERE day = ?",
            (json.dumps(sorted(done_set)), status, now, day),
        )
    return _load(conn, day)


def rate_plan(conn, day, rating, note=""):
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "UPDATE daily_plans SET rating = ?, notes = ?, updated_at = ? WHERE day = ?",
            (int(rating) if rating is not None else None, note[:280], now, day),
        )
    feedback.record(
        conn,
        "daily_plan",
        "helpful" if (rating or 0) >= 4 else "not_helpful" if (rating or 0) <= 2 else "",
        target_id=day,
        target_slug="plan",
        rating=rating,
        reason=note,
        day=day,
    )
    return _load(conn, day)


# ---------------------------------------------------------------------------
# starting a block
# ---------------------------------------------------------------------------
def start_block(conn, bundle, day, block_key):
    """Materialise a practice block into a real quiz plus a dpp_sets row."""
    plan = _load(conn, day)
    if not plan:
        plan = plan_for(conn, bundle, day)
    block = next((b for b in plan["blocks"] if b["key"] == block_key), None)
    if not block:
        raise ValueError("That block is not in today's plan.")
    if not block.get("count"):
        raise ValueError(
            "This block is study time, not a question set. "
            "Log it as a session when you are done."
        )

    picked = quiz.select(
        conn,
        block.get("purpose") or "weak",
        block["count"],
        subject_slug=block.get("subject") or None,
        topic_slugs=[block["topic"]] if block.get("topic") else None,
        metrics=bundle["metrics"],
        topic_health=bundle.get("topic_health"),
    )
    if not picked and block.get("topic"):
        # Fall back to the whole subject rather than serving an empty block.
        picked = quiz.select(
            conn,
            block.get("purpose") or "weak",
            block["count"],
            subject_slug=block.get("subject") or None,
            metrics=bundle["metrics"],
            topic_health=bundle.get("topic_health"),
        )
    if not picked:
        picked = quiz.select(
            conn,
            "mixed",
            block["count"],
            metrics=bundle["metrics"],
            topic_health=bundle.get("topic_health"),
        )
    if not picked:
        raise ValueError(
            "The bank has nothing left for this block today. "
            "Import more questions, or lower the repeat cooldown "
            "in settings."
        )

    qids = [q["id"] for q, _ in picked]
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        cur = conn.execute(
            "INSERT INTO dpp_sets (plan_day, block_key, mode, label, reason, fixing,"
            " aim, target_topic, question_ids, total, generated_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                day,
                block_key,
                block.get("purpose") or block["kind"],
                block["label"],
                block.get("reason", ""),
                block.get("fixing", ""),
                block.get("aim", ""),
                block.get("topic", ""),
                json.dumps(qids),
                len(qids),
                now,
            ),
        )
        set_id = cur.lastrowid

    built, err = quiz.build_quiz(
        conn,
        subject_id=block.get("subject_id"),
        count=len(qids),
        mode=block.get("purpose") or "dpp",
        plan_day=day,
        dpp_set_id=set_id,
        reason=block.get("reason", ""),
        question_ids=qids,
        metrics=bundle["metrics"],
        topic_health=bundle.get("topic_health"),
    )
    if err:
        return None, err
    built["block"] = block
    built["label"] = block["label"]
    return built, None


def dpp_history(conn, limit=25):
    rows = conn.execute(
        "SELECT * FROM dpp_sets ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        try:
            item["question_ids"] = json.loads(r["question_ids"])
        except ValueError:
            item["question_ids"] = []
        item["accuracy"] = round(r["correct"] / r["total"] * 100) if r["total"] else None
        out.append(item)
    return out


def plan_history(conn, limit=21):
    rows = conn.execute(
        "SELECT day, target_mins, status, rating, blocks, done_blocks"
        " FROM daily_plans ORDER BY day DESC LIMIT ?",
        (limit,),
    ).fetchall()
    out = []
    for r in rows:
        try:
            blocks = json.loads(r["blocks"])
            done = json.loads(r["done_blocks"])
        except ValueError:
            blocks, done = [], []
        out.append(
            dict(
                day=r["day"],
                status=r["status"],
                rating=r["rating"],
                blocks=len(blocks),
                done=len(done),
                pct=round(len(done) / len(blocks) * 100) if blocks else 0,
            )
        )
    return out
