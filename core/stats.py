"""The analytics engine: everything that answers "what actually happened".

``gather`` is still the single pass the dashboard reads, but it now also builds
the deeper signals the recommendation engine needs:

* topic health matrix (accuracy x recency x strength) for the mastery heatmap
* revision debt, pulled from the spaced-repetition queue
* study velocity, and whether it is rising or falling
* consistency and focus scores
* guessed-answer rate and correction rate
* time per question and a session quality score
* confidence drift: the gap between how sure you felt and how right you were

Every number here is measured, not modelled. Anything speculative lives in
readiness.py and is labelled as such.
"""

from datetime import date, timedelta

from . import content, db, revision


def level_for_minutes(minutes, daily_target):
    """GitHub-style intensity 0..4, scaled to the user's own daily target."""
    if minutes <= 0:
        return 0
    target = max(int(daily_target or 240), 30)
    if minutes < target * 0.34:
        return 1
    if minutes < target * 0.67:
        return 2
    if minutes < target:
        return 3
    return 4


def iso_week(d):
    y, w, _ = d.isocalendar()
    return "%d-W%02d" % (y, w)


def build_calendar(per_day, per_day_q, daily_target, weeks=53, end=None):
    """Rows are days (Sun..Sat), columns are weeks - same shape as GitHub."""
    end = end or date.today()
    end_of_week = end + timedelta(days=(6 - ((end.weekday() + 1) % 7)))
    start = end_of_week - timedelta(days=weeks * 7 - 1)

    cells = []
    cur = start
    while cur <= end_of_week:
        key = cur.isoformat()
        mins = per_day.get(key, 0)
        cells.append(
            dict(
                day=key,
                minutes=mins,
                questions=per_day_q.get(key, 0),
                level=level_for_minutes(mins, daily_target),
                future=cur > end,
                label=cur.strftime("%b %d, %Y"),
                month=cur.month,
            )
        )
        cur += timedelta(days=1)

    grid = [cells[i : i + 7] for i in range(0, len(cells), 7)]
    months = []
    for idx, week in enumerate(grid):
        m = week[0]["month"]
        if not months or months[-1]["month"] != m:
            months.append(dict(month=m, week=idx, name=date(2000, m, 1).strftime("%b")))
    return dict(
        weeks=grid, months=months, start=start.isoformat(), end=end_of_week.isoformat()
    )


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def _window(per_day, days, end=None):
    """Total minutes in the last ``days`` calendar days, ending today."""
    end = end or date.today()
    total = 0
    active = 0
    for i in range(days):
        key = (end - timedelta(days=i)).isoformat()
        m = per_day.get(key, 0)
        total += m
        if m:
            active += 1
    return total, active


def _pct(a, b):
    return round(a / b * 100) if b else None


def _safe_div(a, b, default=0.0):
    return a / b if b else default


# ---------------------------------------------------------------------------
# derived analytics
# ---------------------------------------------------------------------------
def velocity(per_day, daily_target):
    """Minutes per day over three windows, plus the direction of travel."""
    w7, a7 = _window(per_day, 7)
    w28, a28 = _window(per_day, 28)
    prev7, _ = _window(per_day, 7, date.today() - timedelta(days=7))
    prev28, _ = _window(per_day, 28, date.today() - timedelta(days=28))

    per7 = round(w7 / 7.0)
    per28 = round(w28 / 28.0)
    delta = per7 - round(prev7 / 7.0)
    if abs(delta) < 6:
        trend = "flat"
    elif delta > 0:
        trend = "rising"
    else:
        trend = "falling"

    return dict(
        last7_mins=w7,
        last7_active=a7,
        last7_per_day=per7,
        last28_mins=w28,
        last28_active=a28,
        last28_per_day=per28,
        prev7_per_day=round(prev7 / 7.0),
        prev28_per_day=round(prev28 / 28.0),
        delta_per_day=delta,
        delta_pct=_pct(w7 - prev7, prev7) if prev7 else None,
        trend=trend,
        target_hit_pct=_pct(w7, daily_target * 7) if daily_target else None,
        on_pace=bool(daily_target and per7 >= daily_target * 0.85),
    )


def consistency_score(per_day, current_streak, longest_streak):
    """0..100. Rewards showing up often, and evenly, over the last 28 days."""
    _, active28 = _window(per_day, 28)
    _, active7 = _window(per_day, 7)
    density = active28 / 28.0
    recent = active7 / 7.0
    streak = min(1.0, current_streak / 21.0)
    score = density * 45 + recent * 30 + streak * 25
    return round(min(100.0, score), 1)


def focus_score(sessions, per_day):
    """0..100. Long unbroken blocks beat many scattered fragments."""
    if not sessions:
        return 0.0, dict(avg_len=0, per_active_day=0, fragments=0)
    recent = [
        s for s in sessions if s["day"] >= (date.today() - timedelta(days=28)).isoformat()
    ]
    if not recent:
        recent = sessions[-20:]
    total = sum(s["minutes"] for s in recent)
    days = len({s["day"] for s in recent})
    avg_len = _safe_div(total, len(recent))
    per_active_day = _safe_div(len(recent), days)
    fragments = sum(1 for s in recent if s["minutes"] < 25)

    # 75-minute blocks are treated as the healthy shape.
    length_term = min(1.0, avg_len / 75.0)
    frag_penalty = min(0.45, fragments / max(1, len(recent)) * 0.9)
    score = (
        max(
            0.0, (length_term * 0.8 + min(1.0, per_active_day / 2.2) * 0.2 - frag_penalty)
        )
        * 100
    )
    return round(min(100.0, score), 1), dict(
        avg_len=round(avg_len),
        per_active_day=round(per_active_day, 2),
        fragments=fragments,
        window_sessions=len(recent),
    )


def attempt_quality(attempts):
    """Guess rate, correction rate, pace and confidence drift.

    * guess rate - answered fast with low or no stated confidence
    * correction rate - a question you got wrong and later got right
    * confidence drift - stated confidence minus actual accuracy
    """
    if not attempts:
        return dict(
            available=False,
            guess_rate=None,
            correction_rate=None,
            avg_seconds=None,
            confidence_drift=None,
            confidence_n=0,
            fast_wrong=0,
            slow_correct=0,
            reattempts=0,
            corrected=0,
            timed_n=0,
        )

    timed = [a for a in attempts if (a["seconds"] or 0) > 0]
    with_conf = [a for a in attempts if a["confidence"] is not None]

    guesses = 0
    fast_wrong = 0
    slow_correct = 0
    for a in timed:
        par = 45.0 * max(1.0, float(a["marks_total"] or 2) / 2.0)
        quick = a["seconds"] < par * 0.35
        if quick and (a["confidence"] is None or a["confidence"] <= 2):
            guesses += 1
        if quick and not a["correct"]:
            fast_wrong += 1
        if a["seconds"] > par * 2.0 and a["correct"]:
            slow_correct += 1

    # correction: same question wrong once, right later
    seen = {}
    for a in attempts:
        seen.setdefault(a["question_id"], []).append(1 if a["correct"] else 0)
    repeated = {k: v for k, v in seen.items() if len(v) > 1}
    corrected = sum(1 for v in repeated.values() if v[0] == 0 and v[-1] == 1)

    drift = None
    if with_conf:
        # confidence is 1..5, map to a 0..100 expectation
        expected = (
            sum((a["confidence"] - 1) / 4.0 for a in with_conf) / len(with_conf) * 100
        )
        actual = sum(1 for a in with_conf if a["correct"]) / len(with_conf) * 100
        drift = round(expected - actual, 1)

    return dict(
        available=True,
        timed_n=len(timed),
        avg_seconds=(
            round(sum(a["seconds"] for a in timed) / len(timed), 1) if timed else None
        ),
        guess_rate=_pct(guesses, len(timed)) if timed else None,
        fast_wrong=fast_wrong,
        slow_correct=slow_correct,
        reattempts=len(repeated),
        corrected=corrected,
        correction_rate=_pct(corrected, len(repeated)) if repeated else None,
        confidence_drift=drift,
        confidence_n=len(with_conf),
        overconfident=bool(drift is not None and drift > 12),
        underconfident=bool(drift is not None and drift < -12),
    )


def session_quality(sessions, attempts, per_day, daily_target):
    """One 0..100 number for "was today's work any good".

    Blends: minutes against target, share of the day spent on revision/practice
    rather than only new concepts, and accuracy on anything attempted today.
    """
    today = date.today().isoformat()
    todays = [s for s in sessions if s["day"] == today]
    todays_q = [a for a in attempts if a["day"] == today]
    mins = sum(s["minutes"] for s in todays)
    if not mins and not todays_q:
        return dict(
            available=False,
            score=None,
            minutes=0,
            questions=0,
            note="Nothing logged today yet.",
        )

    time_term = min(1.0, _safe_div(mins, max(daily_target, 30)))
    mixed = sum(
        s["minutes"] for s in todays if s["kind"] in ("revision", "pyq", "dpp", "mock")
    )
    mix_term = min(1.0, _safe_div(mixed, mins, 0.0) / 0.45) if mins else 0.0
    acc_term = _safe_div(sum(1 for a in todays_q if a["correct"]), len(todays_q), 0.0)
    q_term = min(1.0, len(todays_q) / 12.0)

    score = (time_term * 0.42 + mix_term * 0.20 + q_term * 0.18 + acc_term * 0.20) * 100
    notes = []
    if time_term < 0.5:
        notes.append("under half the daily target")
    if mins and mix_term < 0.4:
        notes.append("all new concept, no revision")
    if not todays_q:
        notes.append("no questions attempted")
    elif acc_term < 0.5:
        notes.append("accuracy below 50% today")
    return dict(
        available=True,
        score=round(score),
        minutes=mins,
        questions=len(todays_q),
        accuracy=_pct(sum(1 for a in todays_q if a["correct"]), len(todays_q)),
        revision_share=_pct(mixed, mins),
        note="; ".join(notes) if notes else "Balanced session.",
    )


def topic_health(subjects, strengths, day=None):
    """One row per topic, ranked by how much it is at risk.

    ``risk`` 0..100 is the number the heatmap colours and the recommendation
    engine sorts by. It combines low accuracy, decayed strength, days since the
    topic was touched, and how many marks the subject is worth.
    """
    day = day or date.today().isoformat()
    rows = []
    for s in subjects:
        for t in s["topics"]:
            key = (s["slug"], t["slug"])
            sched = strengths.get(key) or {}
            strength = float(sched.get("strength", 0.0))
            acc = t["accuracy"]
            attempts = t["attempts"]

            stale_days = None
            if t.get("updated_at"):
                try:
                    stale_days = (
                        date.fromisoformat(day) - date.fromisoformat(t["updated_at"][:10])
                    ).days
                except ValueError:
                    stale_days = None

            # ---- risk ------------------------------------------------------
            risk = 0.0
            if t["status"] == "pending":
                risk += 42.0
            elif t["status"] == "learning":
                risk += 22.0
            if acc is None:
                risk += 14.0 if t["status"] != "pending" else 0.0
            else:
                risk += max(0.0, (72.0 - acc)) * 0.55
                if attempts < 4:
                    risk += 6.0
            if sched:
                risk += (1.0 - strength) * 24.0
                overdue = 0
                try:
                    overdue = max(
                        0,
                        (
                            date.fromisoformat(day) - date.fromisoformat(sched["due_day"])
                        ).days,
                    )
                except (ValueError, KeyError, TypeError):
                    overdue = 0
                risk += min(20.0, overdue * 1.7)
                risk += min(10.0, (sched.get("lapses") or 0) * 2.5)
            elif stale_days is not None:
                risk += min(18.0, stale_days * 0.25)

            risk *= 0.75 + (s["marks"] / 40.0) + (t["weight"] / 30.0)
            risk = max(0.0, min(100.0, risk))

            health = round(100 - risk)
            rows.append(
                dict(
                    subject=s["slug"],
                    subject_name=s["name"],
                    subject_id=s["id"],
                    marks=s["marks"],
                    topic=t["slug"],
                    topic_id=t["id"],
                    name=t["name"],
                    weight=t["weight"],
                    status=t["status"],
                    attempts=attempts,
                    accuracy=acc,
                    bank=t["bank"],
                    strength=round(strength * 100),
                    due_day=sched.get("due_day"),
                    lapses=sched.get("lapses", 0),
                    reps=sched.get("reps", 0),
                    stale_days=stale_days,
                    risk=round(risk),
                    health=health,
                    band=(
                        "critical"
                        if risk >= 68
                        else "weak" if risk >= 46 else "ok" if risk >= 24 else "strong"
                    ),
                )
            )
    rows.sort(key=lambda r: -r["risk"])
    return rows


def trend_changes(conn, days=28):
    """Accuracy per subject, this window versus the one before it.

    This is what powers "Operating Systems accuracy has dropped" instead of the
    vaguer "Operating Systems is weak".
    """
    today = date.today()
    mid = (today - timedelta(days=days)).isoformat()
    start = (today - timedelta(days=days * 2)).isoformat()

    def block(lo, hi):
        rows = conn.execute(
            "SELECT subject_slug, topic_slug, COUNT(*) n, SUM(correct) c"
            " FROM attempts WHERE day >= ? AND day < ? GROUP BY subject_slug, topic_slug",
            (lo, hi),
        ).fetchall()
        by_sub, by_topic = {}, {}
        for r in rows:
            s = by_sub.setdefault(r["subject_slug"], dict(n=0, c=0))
            s["n"] += r["n"]
            s["c"] += r["c"] or 0
            by_topic[(r["subject_slug"], r["topic_slug"])] = dict(n=r["n"], c=r["c"] or 0)
        return by_sub, by_topic

    prev_sub, prev_topic = block(start, mid)
    now_sub, now_topic = block(mid, (today + timedelta(days=1)).isoformat())

    out = []
    for slug, cur in now_sub.items():
        if cur["n"] < 4:
            continue
        old = prev_sub.get(slug)
        if not old or old["n"] < 4:
            continue
        a_now = cur["c"] / cur["n"] * 100
        a_old = old["c"] / old["n"] * 100
        delta = a_now - a_old
        if abs(delta) < 8:
            continue
        out.append(
            dict(
                scope="subject",
                slug=slug,
                now=round(a_now),
                before=round(a_old),
                delta=round(delta),
                n_now=cur["n"],
                n_before=old["n"],
                direction="up" if delta > 0 else "down",
            )
        )

    for (sub, top), cur in now_topic.items():
        if cur["n"] < 3 or not top:
            continue
        old = prev_topic.get((sub, top))
        if not old or old["n"] < 3:
            continue
        a_now = cur["c"] / cur["n"] * 100
        a_old = old["c"] / old["n"] * 100
        delta = a_now - a_old
        if abs(delta) < 15:
            continue
        out.append(
            dict(
                scope="topic",
                slug=top,
                subject=sub,
                now=round(a_now),
                before=round(a_old),
                delta=round(delta),
                n_now=cur["n"],
                n_before=old["n"],
                direction="up" if delta > 0 else "down",
            )
        )

    out.sort(key=lambda x: (x["direction"] == "up", -abs(x["delta"])))
    return out[:8]


# ---------------------------------------------------------------------------
# the main pass
# ---------------------------------------------------------------------------
def gather(conn, with_analytics=True):
    """Single pass over sessions and attempts, returning everything the UI needs."""
    settings = db.get_settings(conn)
    daily_target = db.setting_int(settings, "daily_target_mins", 240)

    sessions = conn.execute(
        "SELECT s.*, sub.slug AS subject_slug, sub.name AS subject_name"
        " FROM sessions s JOIN subjects sub ON sub.id = s.subject_id"
        " ORDER BY s.day ASC, s.id ASC"
    ).fetchall()

    per_day = {}
    per_week = {}
    per_subject = {}
    kind_minutes = {k: 0 for k in content.SESSION_KINDS}
    total_minutes = 0
    early_sessions = 0
    weekend_days = set()
    mock_count = 0
    revision_minutes = 0

    for row in sessions:
        day = row["day"]
        per_day[day] = per_day.get(day, 0) + row["minutes"]
        try:
            d = date.fromisoformat(day)
        except ValueError:
            continue
        wk = iso_week(d)
        per_week[wk] = per_week.get(wk, 0) + row["minutes"]
        if d.weekday() >= 5:
            weekend_days.add(day)
        acc = per_subject.setdefault(
            row["subject_id"], dict(minutes=0, sessions=0, days=set(), last=None)
        )
        acc["minutes"] += row["minutes"]
        acc["sessions"] += 1
        acc["days"].add(day)
        acc["last"] = day
        total_minutes += row["minutes"]
        if row["hour"] < 7:
            early_sessions += 1
        if row["kind"] == "mock":
            mock_count += 1
        if row["kind"] in ("revision", "pyq", "dpp"):
            revision_minutes += row["minutes"]
        if row["kind"] in kind_minutes:
            kind_minutes[row["kind"]] += row["minutes"]

    # ---- attempts -------------------------------------------------------
    attempts = conn.execute("SELECT * FROM attempts ORDER BY id ASC").fetchall()
    per_day_q = {}
    acc_by_topic = {}
    acc_by_subject = {}
    total_q = correct_q = 0
    marks_total = marks_got = 0.0
    for a in attempts:
        per_day_q[a["day"]] = per_day_q.get(a["day"], 0) + 1
        total_q += 1
        correct_q += 1 if a["correct"] else 0
        marks_total += a["marks_total"]
        marks_got += a["marks_got"]
        for bucket, key in (
            (acc_by_topic, a["topic_slug"]),
            (acc_by_subject, a["subject_slug"]),
        ):
            if not key:
                continue
            b = bucket.setdefault(key, dict(n=0, correct=0))
            b["n"] += 1
            b["correct"] += 1 if a["correct"] else 0

    quizzes = conn.execute(
        "SELECT * FROM quizzes WHERE finished_at IS NOT NULL"
    ).fetchall()

    # ---- streaks --------------------------------------------------------
    active = sorted(per_day.keys())
    longest = current = 0
    if active:
        run = longest = 1
        for i in range(1, len(active)):
            prev = date.fromisoformat(active[i - 1])
            cur = date.fromisoformat(active[i])
            run = run + 1 if (cur - prev).days == 1 else 1
            longest = max(longest, run)
        last = date.fromisoformat(active[-1])
        if (date.today() - last).days <= 1:
            current = 1
            i = len(active) - 1
            while i > 0:
                a_d = date.fromisoformat(active[i - 1])
                b_d = date.fromisoformat(active[i])
                if (b_d - a_d).days == 1:
                    current += 1
                    i -= 1
                else:
                    break

    # ---- subjects and topics -------------------------------------------
    subject_rows = conn.execute(
        "SELECT * FROM subjects WHERE archived = 0 ORDER BY sort_order, id"
    ).fetchall()
    topic_rows = conn.execute(
        "SELECT * FROM topics ORDER BY subject_id, sort_order, id"
    ).fetchall()

    topics_by_subject = {}
    for t in topic_rows:
        topics_by_subject.setdefault(t["subject_id"], []).append(t)

    bank = content.question_bank()
    bank_by_topic = {}
    for q in bank.values():
        bank_by_topic[(q["subject"], q.get("topic", ""))] = (
            bank_by_topic.get((q["subject"], q.get("topic", "")), 0) + 1
        )

    subjects = []
    topics_done_weight = 0
    topics_total_weight = 0
    coverage_numer = 0.0
    coverage_denom = 0.0

    for s in subject_rows:
        acc = per_subject.get(s["id"], dict(minutes=0, sessions=0, days=set(), last=None))
        tlist = topics_by_subject.get(s["id"], [])
        t_out = []
        w_done = w_total = 0
        n_done = 0
        for t in tlist:
            weight = t["weight"]
            w_total += weight
            credit = {"done": 1.0, "learning": 0.4, "pending": 0.0}.get(t["status"], 0.0)
            w_done += weight * credit
            if t["status"] == "done":
                n_done += 1
            ta = acc_by_topic.get(t["slug"], dict(n=0, correct=0))
            t_out.append(
                dict(
                    id=t["id"],
                    slug=t["slug"],
                    name=t["name"],
                    weight=weight,
                    status=t["status"],
                    updated_at=t["updated_at"],
                    last_revised=(
                        t["last_revised"] if "last_revised" in t.keys() else None
                    ),
                    attempts=ta["n"],
                    correct=ta["correct"],
                    accuracy=round(ta["correct"] / ta["n"] * 100) if ta["n"] else None,
                    bank=bank_by_topic.get((s["slug"], t["slug"]), 0),
                )
            )
        topics_done_weight += w_done
        topics_total_weight += w_total
        coverage_numer += (w_done / w_total if w_total else 0) * s["marks"]
        coverage_denom += s["marks"]

        sa = acc_by_subject.get(s["slug"], dict(n=0, correct=0))
        subjects.append(
            dict(
                id=s["id"],
                slug=s["slug"],
                name=s["name"],
                group=s["grp"],
                marks=s["marks"],
                target_mins=s["target_mins"],
                minutes=acc["minutes"],
                sessions=acc["sessions"],
                days=len(acc["days"]),
                last=acc["last"],
                hours_progress=(
                    min(100, round(acc["minutes"] / s["target_mins"] * 100))
                    if s["target_mins"]
                    else 0
                ),
                topics=t_out,
                topic_count=len(t_out),
                topics_done=n_done,
                topic_progress=round(w_done / w_total * 100) if w_total else 0,
                attempts=sa["n"],
                correct=sa["correct"],
                accuracy=round(sa["correct"] / sa["n"] * 100) if sa["n"] else None,
                bank=sum(bank_by_topic.get((s["slug"], t["slug"]), 0) for t in tlist),
            )
        )

    calendar = build_calendar(per_day, per_day_q, daily_target)
    year_days = [d for d in per_day if d >= calendar["start"]]

    metrics = dict(
        active_days=len(active),
        total_minutes=total_minutes,
        total_hours=round(total_minutes / 60, 1),
        total_sessions=len(sessions),
        current_streak=current,
        longest_streak=longest,
        early_sessions=early_sessions,
        weekend_days=len(weekend_days),
        mock_count=mock_count,
        revision_minutes=revision_minutes,
        revision_share=_pct(revision_minutes, total_minutes) or 0,
        best_day_hours=round(max(per_day.values()) / 60, 1) if per_day else 0,
        best_week_hours=round(max(per_week.values()) / 60, 1) if per_week else 0,
        avg_mins_per_active_day=round(total_minutes / len(active)) if active else 0,
        questions_attempted=total_q,
        questions_correct=correct_q,
        accuracy=round(correct_q / total_q * 100) if total_q else 0,
        marks_total=round(marks_total, 1),
        marks_got=round(marks_got, 1),
        mark_accuracy=round(marks_got / marks_total * 100) if marks_total else 0,
        quizzes_done=len(quizzes),
        topics_done=sum(s["topics_done"] for s in subjects),
        topics_total=sum(s["topic_count"] for s in subjects),
        topic_weight_done=round(topics_done_weight, 1),
        topic_weight_total=topics_total_weight,
        coverage_pct=(
            round(coverage_numer / coverage_denom * 100, 1) if coverage_denom else 0
        ),
        subjects_total=len(subjects),
        subjects_started=sum(1 for s in subjects if s["sessions"] > 0),
        subject_coverage_pct=(
            round(sum(1 for s in subjects if s["sessions"] > 0) / len(subjects) * 100)
            if subjects
            else 0
        ),
        year_minutes=sum(per_day[d] for d in year_days),
        year_active_days=len(year_days),
        bank_size=len(bank),
    )

    bundle = dict(
        metrics=metrics,
        subjects=subjects,
        calendar=calendar,
        per_day=per_day,
        per_day_q=per_day_q,
        kind_minutes=kind_minutes,
        accuracy_by_topic=acc_by_topic,
        accuracy_by_subject=acc_by_subject,
        settings=settings,
        daily_target=daily_target,
    )

    if not with_analytics:
        return bundle

    # ---- the deeper layer ----------------------------------------------
    revision.sync_from_activity(conn)
    strengths = revision.strength_map(conn)
    vel = velocity(per_day, daily_target)
    foc, foc_meta = focus_score(sessions, per_day)
    quality = attempt_quality(attempts)
    debt = revision.debt(conn)
    health_rows = topic_health(subjects, strengths)

    metrics.update(
        velocity_per_day=vel["last7_per_day"],
        velocity_trend=vel["trend"],
        consistency_score=consistency_score(per_day, current, longest),
        focus_score=foc,
        guess_rate=quality["guess_rate"] or 0,
        correction_rate=quality["correction_rate"] or 0,
        avg_seconds_per_question=quality["avg_seconds"] or 0,
        confidence_drift=quality["confidence_drift"],
        revision_debt=debt["overdue"],
        revision_pressure=debt["pressure"],
        due_today=debt["due_today"],
        critical_topics=sum(1 for r in health_rows if r["band"] == "critical"),
        weak_topics=sum(1 for r in health_rows if r["band"] in ("critical", "weak")),
        strong_topics=sum(1 for r in health_rows if r["band"] == "strong"),
        mastery_pct=(
            round(sum(r["health"] for r in health_rows) / len(health_rows))
            if health_rows
            else 0
        ),
    )

    bundle.update(
        velocity=vel,
        focus=dict(score=foc, **foc_meta),
        quality=quality,
        debt=debt,
        topic_health=health_rows,
        strengths={"%s/%s" % k: v for k, v in strengths.items()},
        session_quality=session_quality(sessions, attempts, per_day, daily_target),
        trends=trend_changes(conn),
    )
    return bundle


def weekly_minutes(conn, weeks=12):
    """Minutes logged per ISO week, oldest first.

    Sessions carry the minutes, not attempts: time spent reading and working a
    topic counts the same as time spent answering, and the bar chart is about
    effort rather than throughput.
    """
    rows = conn.execute(
        "SELECT day, SUM(minutes) AS mins FROM sessions"
        " WHERE day IS NOT NULL AND day != '' GROUP BY day"
    ).fetchall()
    buckets = {}
    for r in rows:
        try:
            d = date.fromisoformat(r["day"])
        except (TypeError, ValueError):
            continue
        iso = d.isocalendar()
        start = d - timedelta(days=d.weekday())
        key = start.isoformat()
        b = buckets.setdefault(
            key, dict(week_start=key, label="W%02d" % iso[1], minutes=0)
        )
        b["minutes"] += int(r["mins"] or 0)
    out = [buckets[k] for k in sorted(buckets)][-weeks:]
    # Fill the gap weeks so a fortnight off reads as two empty bars rather than
    # silently closing up and making the streak look unbroken.
    if out:
        first = date.fromisoformat(out[0]["week_start"])
        last = date.fromisoformat(out[-1]["week_start"])
        filled, cur = [], first
        by_key = {b["week_start"]: b for b in out}
        while cur <= last:
            key = cur.isoformat()
            filled.append(
                by_key.get(key, dict(week_start=key,
                                     label="W%02d" % cur.isocalendar()[1],
                                     minutes=0))
            )
            cur += timedelta(days=7)
        out = filled[-weeks:]
    return out


def difficulty_split(conn, bank):
    """Attempts by question difficulty, with accuracy for each band.

    Difficulty lives on the question, not the attempt, so this joins through the
    bank. An attempt whose question has since left the bank is counted as
    unknown rather than dropped - the practice happened either way.
    """
    order = ("easy", "medium", "hard")
    tally = {k: dict(band=k, attempts=0, correct=0) for k in order}
    tally["unknown"] = dict(band="unknown", attempts=0, correct=0)
    for r in conn.execute(
        "SELECT question_id, correct FROM attempts WHERE question_id IS NOT NULL"
    ):
        q = bank.get(r["question_id"])
        band = (q or {}).get("difficulty") or "unknown"
        if band not in tally:
            band = "unknown"
        tally[band]["attempts"] += 1
        if r["correct"]:
            tally[band]["correct"] += 1
    out = []
    total = sum(t["attempts"] for t in tally.values())
    for k in order + ("unknown",):
        t = tally[k]
        if not t["attempts"] and k == "unknown":
            continue
        t["share"] = round(100.0 * t["attempts"] / total, 1) if total else 0.0
        t["accuracy"] = (
            round(100.0 * t["correct"] / t["attempts"]) if t["attempts"] else 0
        )
        out.append(t)
    return out


def heatmap(subjects, health_rows):
    """Subject x topic grid for the mastery panel, in syllabus order."""
    by_subject = {}
    for r in health_rows:
        by_subject.setdefault(r["subject"], []).append(r)
    out = []
    for s in subjects:
        rows = by_subject.get(s["slug"], [])
        order = {t["slug"]: i for i, t in enumerate(s["topics"])}
        rows = sorted(rows, key=lambda r: order.get(r["topic"], 99))
        out.append(
            dict(
                subject=s["slug"],
                name=s["name"],
                marks=s["marks"],
                id=s["id"],
                avg_health=(
                    round(sum(r["health"] for r in rows) / len(rows)) if rows else 0
                ),
                cells=[
                    dict(
                        topic=r["topic"],
                        name=r["name"],
                        health=r["health"],
                        band=r["band"],
                        status=r["status"],
                        accuracy=r["accuracy"],
                        attempts=r["attempts"],
                        strength=r["strength"],
                        risk=r["risk"],
                        weight=r["weight"],
                        bank=r["bank"],
                        topic_id=r["topic_id"],
                    )
                    for r in rows
                ],
            )
        )
    return out


def recent_sessions(conn, limit=40):
    rows = conn.execute(
        "SELECT s.*, sub.name AS subject_name, sub.slug AS subject_slug"
        " FROM sessions s JOIN subjects sub ON sub.id = s.subject_id"
        " ORDER BY s.day DESC, s.id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    out = []
    for r in rows:
        topics = [
            x["name"]
            for x in conn.execute(
                "SELECT t.name FROM session_topics st JOIN topics t ON t.id = st.topic_id"
                " WHERE st.session_id = ? ORDER BY t.sort_order",
                (r["id"],),
            )
        ]
        item = dict(r)
        item["topics"] = topics
        out.append(item)
    return out
