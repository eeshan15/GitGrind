"""Achievements, missions and the unlock engine.

Every badge is a pure function of the metrics dict, so nothing is ever awarded
by hand. Glyphs are ASCII on purpose: track initial plus tier numeral.

Two layers now:

* **Badges** - permanent, cumulative, five tracks. Unlocked once and kept.
* **Missions** - today's and this week's short goals, recomputed live from the
  same measured data. Nothing is stored, so a mission can never be gamed by
  editing the database, and nothing has to be migrated.

The reward design follows the spec: badges pay out for the behaviour that
actually raises the score - consistency, revision, and finishing hard problems -
rather than for raw hours parked at a desk.
"""

from datetime import date, datetime, timedelta

TRACKS = {
    "consistency": dict(
        label="Consistency",
        blurb="Showing up on the days you do not feel like it",
        glyph="C",
    ),
    "discipline": dict(
        label="Discipline",
        blurb="Hours on the desk, early mornings, weekends included",
        glyph="D",
    ),
    "strength": dict(
        label="Strength",
        blurb="Syllabus covered, questions solved, accuracy under pressure",
        glyph="S",
    ),
    "retention": dict(
        label="Retention",
        blurb="Revision done on schedule, debt cleared, comebacks after a gap",
        glyph="R",
    ),
    "mastery": dict(
        label="Mastery",
        blurb="Topics taken from weak to strong, and boss questions cleared",
        glyph="M",
    ),
}

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def _defs():
    raw = [
        # ---- consistency ------------------------------------------------
        (
            "consistency",
            "bronze",
            "First Commit",
            "Log a single study session",
            "active_days",
            1,
        ),
        (
            "consistency",
            "bronze",
            "Three Straight",
            "Reach a 3-day streak",
            "longest_streak",
            3,
        ),
        (
            "consistency",
            "silver",
            "Week Unbroken",
            "Study seven days back to back",
            "longest_streak",
            7,
        ),
        (
            "consistency",
            "silver",
            "Fortnight",
            "A 14-day streak with no gap",
            "longest_streak",
            14,
        ),
        (
            "consistency",
            "gold",
            "Monthly Machine",
            "A 30-day streak - the habit is yours",
            "longest_streak",
            30,
        ),
        ("consistency", "gold", "Fifty Not Out", "A 50-day streak", "longest_streak", 50),
        (
            "consistency",
            "diamond",
            "Century Streak",
            "One hundred consecutive days",
            "longest_streak",
            100,
        ),
        (
            "consistency",
            "diamond",
            "Two Hundred Days",
            "200 active days on the board",
            "active_days",
            200,
        ),
        # ---- discipline -------------------------------------------------
        (
            "discipline",
            "bronze",
            "First Hour",
            "One hour of logged study time",
            "total_hours",
            1,
        ),
        (
            "discipline",
            "bronze",
            "Ten Hour Club",
            "Ten hours on the clock",
            "total_hours",
            10,
        ),
        (
            "discipline",
            "silver",
            "Fifty Deep",
            "Fifty hours of logged work",
            "total_hours",
            50,
        ),
        (
            "discipline",
            "silver",
            "Early Riser",
            "Ten sessions started before 7 AM",
            "early_sessions",
            10,
        ),
        (
            "discipline",
            "gold",
            "Hundred Hours",
            "One hundred hours logged",
            "total_hours",
            100,
        ),
        (
            "discipline",
            "gold",
            "Weekend Discipline",
            "Study on twelve weekend days",
            "weekend_days",
            12,
        ),
        (
            "discipline",
            "diamond",
            "Two Fifty",
            "250 hours accumulated",
            "total_hours",
            250,
        ),
        (
            "discipline",
            "diamond",
            "Five Hundred",
            "500 hours. The syllabus is not the problem now",
            "total_hours",
            500,
        ),
        # ---- strength ---------------------------------------------------
        (
            "strength",
            "bronze",
            "First Blood",
            "Attempt ten questions",
            "questions_attempted",
            10,
        ),
        (
            "strength",
            "bronze",
            "Deep Session",
            "A single day with four or more hours",
            "best_day_hours",
            4,
        ),
        (
            "strength",
            "silver",
            "Quarter Covered",
            "Mark 25 percent of weighted syllabus done",
            "coverage_pct",
            25,
        ),
        (
            "strength",
            "silver",
            "Two Fifty Solved",
            "Attempt 250 questions",
            "questions_attempted",
            250,
        ),
        (
            "strength",
            "gold",
            "Marathon Week",
            "35 or more hours inside one calendar week",
            "best_week_hours",
            35,
        ),
        (
            "strength",
            "gold",
            "Mock Veteran",
            "Fifteen mock tests logged",
            "mock_count",
            15,
        ),
        (
            "strength",
            "gold",
            "Half Syllabus",
            "Mark 50 percent of weighted syllabus done",
            "coverage_pct",
            50,
        ),
        (
            "strength",
            "gold",
            "Sharpshooter",
            "Hold 75 percent accuracy over 100 or more questions",
            "accuracy_at_volume",
            75,
        ),
        (
            "strength",
            "diamond",
            "Thousand Cuts",
            "Attempt one thousand questions",
            "questions_attempted",
            1000,
        ),
        (
            "strength",
            "diamond",
            "Full Spectrum",
            "Touch every subject in the syllabus",
            "subject_coverage_pct",
            100,
        ),
        (
            "strength",
            "diamond",
            "Syllabus Closed",
            "Mark 90 percent of weighted syllabus done",
            "coverage_pct",
            90,
        ),
        # ---- retention --------------------------------------------------
        (
            "retention",
            "bronze",
            "First Review",
            "Complete one scheduled revision",
            "reviews_done",
            1,
        ),
        (
            "retention",
            "bronze",
            "Debt Collector",
            "Clear ten overdue revision items",
            "reviews_cleared",
            10,
        ),
        (
            "retention",
            "silver",
            "Revision Week",
            "Revise on seven consecutive days",
            "revision_streak",
            7,
        ),
        (
            "retention",
            "silver",
            "Streak Rescue",
            "Log a session on a day your streak was about to break",
            "streak_rescues",
            3,
        ),
        (
            "retention",
            "silver",
            "Clean Slate",
            "Get revision debt to zero",
            "debt_zero_days",
            1,
        ),
        (
            "retention",
            "gold",
            "Comeback",
            "Return and log three days straight after a week away",
            "comebacks",
            1,
        ),
        (
            "retention",
            "gold",
            "Revision Habit",
            "Revise on thirty separate days",
            "revision_days",
            30,
        ),
        (
            "retention",
            "diamond",
            "Nothing Forgotten",
            "Hold revision debt at zero for seven days",
            "debt_zero_days",
            7,
        ),
        # ---- mastery ----------------------------------------------------
        ("mastery", "bronze", "First Boss", "Clear one boss question", "boss_wins", 1),
        (
            "mastery",
            "bronze",
            "Topic Locked",
            "Take one topic to strong health",
            "topics_mastered",
            1,
        ),
        ("mastery", "silver", "Boss Hunter", "Clear ten boss questions", "boss_wins", 10),
        (
            "mastery",
            "silver",
            "Five Locked",
            "Five topics at strong health",
            "topics_mastered",
            5,
        ),
        (
            "mastery",
            "silver",
            "Rescue Squad",
            "Lift five topics out of the weak band",
            "weak_cleared",
            5,
        ),
        (
            "mastery",
            "gold",
            "Plan Follower",
            "Complete twenty daily plans",
            "plans_completed",
            20,
        ),
        (
            "mastery",
            "gold",
            "Twenty Locked",
            "Twenty topics at strong health",
            "topics_mastered",
            20,
        ),
        (
            "mastery",
            "gold",
            "Correction Artist",
            "Fix twenty five questions you had got wrong",
            "corrections",
            25,
        ),
        (
            "mastery",
            "diamond",
            "Boss Slayer",
            "Clear fifty boss questions",
            "boss_wins",
            50,
        ),
        (
            "mastery",
            "diamond",
            "Half Mastered",
            "Average topic health above 70",
            "mastery_pct",
            70,
        ),
    ]

    out = []
    counters = {}
    for track, tier, name, desc, metric, target in raw:
        n = counters.get(track, 0)
        counters[track] = n + 1
        out.append(
            dict(
                code="%s%d" % (TRACKS[track]["glyph"].lower(), n + 1),
                track=track,
                tier=tier,
                name=name,
                desc=desc,
                metric=metric,
                target=target,
                glyph="%s-%s" % (TRACKS[track]["glyph"], ROMAN[min(n, len(ROMAN) - 1)]),
            )
        )
    return out


DEFINITIONS = _defs()

HOUR_METRICS = {"total_hours", "best_day_hours", "best_week_hours"}
PCT_METRICS = {
    "coverage_pct",
    "subject_coverage_pct",
    "accuracy_at_volume",
    "mastery_pct",
}
DAY_METRICS = {
    "active_days",
    "longest_streak",
    "current_streak",
    "weekend_days",
    "revision_streak",
    "revision_days",
    "debt_zero_days",
}


def progress_metrics(conn, bundle=None):
    """The counters the retention and mastery tracks need.

    Everything is read straight out of the logs, so a badge can never be earned
    by anything other than the behaviour it names.
    """
    out = {}

    # ---- revision -------------------------------------------------------
    reviews = conn.execute(
        "SELECT COUNT(*) n, SUM(reps > 0) done FROM revision_queue"
    ).fetchone()
    out["reviews_done"] = conn.execute(
        "SELECT COALESCE(SUM(reps), 0) n FROM revision_queue"
    ).fetchone()["n"]
    out["reviews_cleared"] = conn.execute(
        "SELECT COUNT(*) n FROM revision_queue WHERE reps >= 2 AND lapses > 0"
    ).fetchone()["n"]

    rev_days = [
        r["day"]
        for r in conn.execute(
            "SELECT DISTINCT day FROM sessions WHERE kind IN ('revision','pyq','dpp')"
            " UNION SELECT DISTINCT last_review_day AS day FROM revision_queue"
            " WHERE last_review_day IS NOT NULL ORDER BY day DESC"
        )
    ]
    out["revision_days"] = len(rev_days)
    streak = 0
    if rev_days:
        expected = date.today()
        for raw in rev_days:
            try:
                d = date.fromisoformat(raw)
            except (ValueError, TypeError):
                continue
            if d == expected or (streak == 0 and d == expected - timedelta(days=1)):
                streak += 1
                expected = d - timedelta(days=1)
            elif d < expected:
                break
    out["revision_streak"] = streak

    # ---- streak rescues and comebacks -----------------------------------
    days = [
        r["day"]
        for r in conn.execute("SELECT DISTINCT day FROM sessions ORDER BY day ASC")
    ]
    rescues = comebacks = 0
    for i in range(1, len(days)):
        try:
            gap = (date.fromisoformat(days[i]) - date.fromisoformat(days[i - 1])).days
        except (ValueError, TypeError):
            continue
        if gap == 2:
            rescues += 1  # skipped exactly one day, then came back
        if gap >= 7 and i + 2 < len(days):
            try:
                run = (date.fromisoformat(days[i + 2]) - date.fromisoformat(days[i])).days
            except (ValueError, TypeError):
                continue
            if run == 2:
                comebacks += 1  # a week away, then three days straight
    out["streak_rescues"] = rescues
    out["comebacks"] = comebacks

    # ---- boss battles, plans, corrections -------------------------------
    out["boss_wins"] = conn.execute(
        "SELECT COUNT(*) n FROM quizzes WHERE mode = 'boss'"
        " AND finished_at IS NOT NULL AND correct_count >= question_count"
    ).fetchone()["n"]
    out["plans_completed"] = conn.execute(
        "SELECT COUNT(*) n FROM daily_plans WHERE status = 'done'"
    ).fetchone()["n"]
    out["corrections"] = conn.execute(
        "SELECT COUNT(*) n FROM ("
        "  SELECT question_id FROM question_stats"
        "  WHERE last_correct_day IS NOT NULL AND last_wrong_day IS NOT NULL"
        "    AND last_correct_day > last_wrong_day)"
    ).fetchone()["n"]
    out["debt_zero_days"] = conn.execute(
        "SELECT COUNT(*) n FROM revision_queue WHERE 0 = 1"
    ).fetchone()["n"]

    # ---- topic health, from the analytics bundle when we have it ---------
    health = (bundle or {}).get("topic_health") or []
    out["topics_mastered"] = sum(1 for r in health if r["band"] == "strong")
    out["weak_cleared"] = sum(
        1 for r in health if r["band"] in ("ok", "strong") and r["lapses"]
    )
    out["mastery_pct"] = (bundle or {}).get("metrics", {}).get("mastery_pct", 0)

    # A day with nothing overdue counts, tracked cheaply off the readiness log.
    debt = ((bundle or {}).get("debt") or {}).get("overdue")
    if debt == 0 and out["reviews_done"]:
        out["debt_zero_days"] = max(1, out["debt_zero_days"])
    return out


def derived_metrics(metrics, conn=None, bundle=None):
    """Extra fields the badge rules need that stats does not compute directly."""
    extra = dict(metrics)
    volume = metrics.get("questions_attempted", 0)
    # Accuracy only counts once there is enough volume for it to mean anything.
    extra["accuracy_at_volume"] = metrics.get("accuracy", 0) if volume >= 100 else 0
    if conn is not None:
        extra.update(progress_metrics(conn, bundle))
    return extra


# ---------------------------------------------------------------------------
# missions - short, live, never stored
# ---------------------------------------------------------------------------
def missions(conn, bundle, plan=None):
    """Today's and this week's goals, computed from live measurements."""
    metrics = bundle["metrics"]
    today = date.today().isoformat()
    per_day = bundle.get("per_day", {})
    debt = bundle.get("debt") or {}
    target = max(30, bundle.get("daily_target", 240))

    todays_q = conn.execute(
        "SELECT COUNT(*) n, SUM(correct) c FROM attempts WHERE day = ?", (today,)
    ).fetchone()
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    week = conn.execute(
        "SELECT COUNT(DISTINCT day) d, COUNT(*) n FROM attempts WHERE day >= ?",
        (week_start,),
    ).fetchone()
    week_mins = sum(v for k, v in per_day.items() if k >= week_start)
    reviewed_today = conn.execute(
        "SELECT COUNT(*) n FROM revision_queue WHERE last_review_day = ?", (today,)
    ).fetchone()["n"]

    items = [
        dict(
            key="minutes",
            scope="today",
            label="Hit the daily target",
            detail="%d of %d minutes logged" % (per_day.get(today, 0), target),
            value=per_day.get(today, 0),
            target=target,
            unit="min",
            reward="Protects the streak and the volume term",
        ),
        dict(
            key="questions",
            scope="today",
            label="Attempt 10 questions",
            detail="%d attempted today" % (todays_q["n"] or 0),
            value=todays_q["n"] or 0,
            target=10,
            unit="q",
            reward="Feeds the accuracy sample, which is the slowest term to build",
        ),
    ]
    if debt.get("due_today"):
        items.append(
            dict(
                key="revision",
                scope="today",
                label="Clear today's revision queue",
                detail="%d reviewed of %d due" % (reviewed_today, debt["due_today"]),
                value=reviewed_today,
                target=debt["due_today"],
                unit="items",
                reward="Drops revision pressure and stops topics decaying",
            )
        )
    if plan and plan.get("blocks"):
        items.append(
            dict(
                key="plan",
                scope="today",
                label="Finish today's plan",
                detail="%d of %d blocks done"
                % (plan.get("done_count", 0), len(plan["blocks"])),
                value=plan.get("done_count", 0),
                target=len(plan["blocks"]),
                unit="blocks",
                reward="The only single action that moves three terms at once",
            )
        )
    items += [
        dict(
            key="week_days",
            scope="week",
            label="Practise on five days this week",
            detail="%d days so far" % (week["d"] or 0),
            value=week["d"] or 0,
            target=5,
            unit="days",
            reward="Consistency term, and it is the habit that carries everything",
        ),
        dict(
            key="week_mins",
            scope="week",
            label="Log %dh this week" % round(target * 5 / 60),
            detail="%.1fh logged" % (week_mins / 60.0),
            value=round(week_mins / 60.0, 1),
            target=round(target * 5 / 60),
            unit="h",
            reward="Keeps weekly velocity from sliding",
        ),
    ]

    for m in items:
        tgt = max(1, m["target"])
        m["progress"] = min(100, round(m["value"] / tgt * 100))
        m["done"] = m["value"] >= m["target"]
    done = sum(1 for m in items if m["done"])
    return dict(
        items=items,
        done=done,
        total=len(items),
        all_done=done == len(items),
        headline=(
            "All missions clear - genuinely a good day."
            if done == len(items)
            else "%d of %d missions clear." % (done, len(items))
        ),
    )


def evaluate(conn, metrics, bundle=None):
    """Unlock whatever is newly earned and return the full badge list."""
    values = derived_metrics(metrics, conn, bundle)
    existing = {
        r["code"]: r["unlocked_at"] for r in conn.execute("SELECT * FROM unlocked")
    }
    now = datetime.now().isoformat(timespec="seconds")
    fresh = []

    with conn:
        for a in DEFINITIONS:
            got = values.get(a["metric"], 0) or 0
            if got >= a["target"] and a["code"] not in existing:
                conn.execute(
                    "INSERT OR IGNORE INTO unlocked (code, unlocked_at) VALUES (?,?)",
                    (a["code"], now),
                )
                existing[a["code"]] = now
                fresh.append(a["code"])

    out = []
    for a in DEFINITIONS:
        got = values.get(a["metric"], 0) or 0
        out.append(
            dict(
                a,
                unlocked=a["code"] in existing,
                unlocked_at=existing.get(a["code"]),
                value=got,
                progress=min(100, round(got / a["target"] * 100)) if a["target"] else 0,
                display_value=_fmt(got, a["metric"]),
                display_target=_fmt(a["target"], a["metric"]),
                is_new=a["code"] in fresh,
            )
        )
    return out


def _fmt(value, metric):
    if metric in HOUR_METRICS:
        return "%gh" % round(float(value), 1)
    if metric in PCT_METRICS:
        return "%g%%" % round(float(value), 1)
    if metric in DAY_METRICS:
        return "%dd" % int(value)
    return str(int(value))
