"""Readiness index, estimated GATE score, cutoff distance and cohort position.

READ THIS BEFORE TRUSTING A NUMBER ON THE READINESS TAB.

There is no server here and there are no other users. Every "rank" and "people
ahead of you" figure comes from a statistical cohort generated on this machine
from a fixed seed. It is a yardstick that behaves consistently so you can pace
yourself against it - it is not a measurement of real candidates, and passing
1,000 simulated people does not mean 1,000 real people fell behind you.

What IS real: your logged hours, your topic coverage, your quiz accuracy. The
readiness index is a weighted combination of those, and it is honest about what
it measures. The mapping from index to "estimated GATE score" is a rough curve
in content/targets.json - a real score depends on paper difficulty and
normalisation that no local model can predict.

EXPLAINABILITY
--------------
Every number the readiness tab shows now comes with its derivation:

* ``contributions`` - each component's raw value, its weight, and the index
  points it is actually contributing right now.
* ``why_moved`` - the index delta since the last snapshot, decomposed per
  component, so "up 0.8" becomes "coverage +0.6, accuracy +0.2".
* ``estimate_confidence`` - how much evidence sits behind the number. A high
  index built on twelve questions is labelled as such.
* ``risk`` / ``recovery`` - the topic most likely to cost marks, and the one
  that would pay back fastest.
* ``projection`` - what finishing today's plan would plausibly do, computed
  from the same weights rather than invented.

Nothing here is presented as a prediction of a real GATE score.
"""

import bisect
import random
from datetime import date, datetime, timedelta

from . import content, db

# Weights of the four inputs to the readiness index. They sum to 1.
WEIGHTS = dict(coverage=0.40, accuracy=0.30, volume=0.20, consistency=0.10)

# Hours of logged study treated as a "full" preparation for the volume term.
VOLUME_REFERENCE_HOURS = 700

COMPONENT_LABELS = dict(
    coverage="Coverage",
    accuracy="Accuracy",
    volume="Volume",
    consistency="Consistency",
)

# Whether each term is a direct measurement or a heuristic over measurements.
# The UI shows this so nothing looks more precise than it is.
COMPONENT_SOURCE = dict(
    coverage="measured: weighted topics you marked done",
    accuracy="measured, then damped until the sample is large enough",
    volume="measured hours against a 700-hour reference (the reference is a guess)",
    consistency="heuristic over streak length and active days",
)

BANDS = (
    (78, "exam-ready", "The syllabus is not the bottleneck any more. Protect accuracy."),
    (62, "strong", "Solid base. The remaining marks are in revision and speed."),
    (44, "building", "The shape is right. Coverage and volume are still the levers."),
    (26, "early", "Foundations. Consistency matters more than optimisation right now."),
    (0, "starting out", "Not enough history to say much. Log sessions and questions."),
)


def index_band(index_value):
    for floor, label, note in BANDS:
        if index_value >= floor:
            return dict(label=label, note=note, floor=floor)
    return dict(label="starting out", note="", floor=0)


_cohort_cache = {}


# ---------------------------------------------------------------------------
# cohort
# ---------------------------------------------------------------------------
def _cohort(cfg):
    """Sorted array of simulated readiness indices. Built once, then cached."""
    key = (
        cfg.get("size"),
        cfg.get("seed"),
        cfg.get("shape_alpha"),
        cfg.get("shape_beta"),
        cfg.get("serious_fraction"),
        cfg.get("serious_shift"),
    )
    if key in _cohort_cache:
        return _cohort_cache[key]

    size = max(1000, min(int(cfg.get("size", 150000)), 400000))
    rng = random.Random(int(cfg.get("seed", 20260728)))
    alpha = float(cfg.get("shape_alpha", 2.1))
    beta = float(cfg.get("shape_beta", 4.4))
    serious_frac = float(cfg.get("serious_fraction", 0.34))
    shift = float(cfg.get("serious_shift", 14))

    samples = []
    for _ in range(size):
        base = rng.betavariate(alpha, beta) * 100.0
        if rng.random() < serious_frac:
            base = min(100.0, base + rng.uniform(0.35, 1.0) * shift)
        samples.append(base)
    samples.sort()
    _cohort_cache[key] = samples
    return samples


def cohort_position(index_value, cfg):
    pool = _cohort(cfg)
    n = len(pool)
    below = bisect.bisect_left(pool, index_value)
    return dict(
        simulated=True,
        sample=n,
        percentile=round(below / n * 100, 2),
        behind_you=below,
        ahead_of_you=n - below,
        note="Simulated cohort of %s generated locally from a fixed seed. "
        "Not real candidates." % f"{n:,}",
    )


# ---------------------------------------------------------------------------
# index and score
# ---------------------------------------------------------------------------
def _interp(anchors, x):
    """Piecewise linear interpolation through (input, output) anchor pairs."""
    pts = sorted((float(a), float(b)) for a, b in anchors)
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        if x <= x1:
            span = (x1 - x0) or 1.0
            return y0 + (y1 - y0) * (x - x0) / span
    return pts[-1][1]


def components(metrics):
    """The four real inputs, each on a 0-100 scale."""
    coverage = min(100.0, float(metrics.get("coverage_pct", 0)))

    attempted = metrics.get("questions_attempted", 0)
    raw_acc = float(metrics.get("accuracy", 0))
    # Accuracy on five questions means nothing. Ramp confidence with volume and
    # pull the estimate toward a neutral 40 until there is enough evidence.
    confidence = min(1.0, attempted / 150.0)
    accuracy = raw_acc * confidence

    volume = min(
        100.0, float(metrics.get("total_hours", 0)) / VOLUME_REFERENCE_HOURS * 100.0
    )

    streak = float(metrics.get("current_streak", 0))
    active = float(metrics.get("active_days", 0))
    consistency = min(100.0, streak / 45.0 * 60.0 + min(active, 180.0) / 180.0 * 40.0)

    return dict(
        coverage=round(coverage, 1),
        accuracy=round(accuracy, 1),
        volume=round(volume, 1),
        consistency=round(consistency, 1),
        accuracy_confidence=round(confidence * 100),
        accuracy_raw=round(raw_acc, 1),
    )


def contributions(parts):
    """Each component's share of the index, in index points."""
    rows = []
    for key in ("coverage", "accuracy", "volume", "consistency"):
        weight = WEIGHTS[key]
        value = float(parts[key])
        rows.append(
            dict(
                key=key,
                label=COMPONENT_LABELS[key],
                value=round(value, 1),
                weight=round(weight * 100),
                points=round(value * weight, 2),
                max_points=round(weight * 100, 1),
                headroom=round((100.0 - value) * weight, 2),
                measured=COMPONENT_SOURCE[key],
            )
        )
    rows.sort(key=lambda r: -r["headroom"])
    return rows


def estimate_confidence(metrics):
    """How much evidence is behind the index. 0..100, plus a plain-English band."""
    attempted = float(metrics.get("questions_attempted", 0) or 0)
    active = float(metrics.get("active_days", 0) or 0)
    hours = float(metrics.get("total_hours", 0) or 0)

    q_term = min(1.0, attempted / 150.0)
    day_term = min(1.0, active / 45.0)
    hour_term = min(1.0, hours / 120.0)
    score = (q_term * 0.5 + day_term * 0.3 + hour_term * 0.2) * 100

    if score >= 75:
        band, note = (
            "high",
            "Enough history that the index moves slowly and means something.",
        )
    elif score >= 45:
        band, note = "medium", (
            "Reasonable history. Coverage is solid; accuracy is still "
            "sensitive to a bad session."
        )
    elif score >= 18:
        band, note = "low", (
            "Thin history. Treat the index as a direction, not a " "measurement."
        )
    else:
        band, note = "very low", (
            "Almost no history yet. This number will swing wildly "
            "for the first couple of weeks."
        )
    return dict(
        score=round(score),
        band=band,
        note=note,
        questions=int(attempted),
        active_days=int(active),
        hours=hours,
    )


def risk_and_recovery(bundle):
    """The topic most likely to cost marks, and the one that pays back fastest."""
    health = (bundle or {}).get("topic_health") or []
    if not health:
        return None, None

    covered = [r for r in health if r["status"] in ("done", "learning")]
    risk_pool = covered or health
    risk = max(risk_pool, key=lambda r: r["risk"] * (0.6 + r["marks"] / 25.0))

    # Recovery: partially learnt, decent bank coverage, high marks. Cheapest lift.
    def payback(r):
        if r["bank"] < 2:
            return -1
        gap = max(0, 78 - (r["accuracy"] if r["accuracy"] is not None else 40))
        started = 1.25 if r["status"] != "pending" else 0.7
        return gap * started * (0.5 + r["marks"] / 20.0) * (0.6 + r["weight"] / 6.0)

    ranked = sorted(health, key=payback, reverse=True)
    recovery = next((r for r in ranked if payback(r) > 0), None)

    def view(r, kind):
        if not r:
            return None
        return dict(
            kind=kind,
            subject=r["subject"],
            subject_name=r["subject_name"],
            subject_id=r["subject_id"],
            topic=r["topic"],
            topic_id=r["topic_id"],
            name=r["name"],
            marks=r["marks"],
            weight=r["weight"],
            risk=r["risk"],
            health=r["health"],
            band=r["band"],
            status=r["status"],
            accuracy=r["accuracy"],
            attempts=r["attempts"],
            bank=r["bank"],
            strength=r["strength"],
            due_day=r.get("due_day"),
        )

    risk_v = view(risk, "risk")
    if risk_v:
        risk_v["why"] = "%d/100 risk in a %d-mark subject%s." % (
            risk["risk"],
            risk["marks"],
            (
                ", accuracy %d%%" % risk["accuracy"]
                if risk["accuracy"] is not None
                else ", never tested"
            ),
        )
    rec_v = view(recovery, "recovery")
    if rec_v:
        rec_v["why"] = (
            "%d questions in the bank and only %s accuracy so far - the "
            "cheapest marks available."
            % (
                recovery["bank"],
                (
                    "%d%%" % recovery["accuracy"]
                    if recovery["accuracy"] is not None
                    else "no"
                ),
            )
        )
    return risk_v, rec_v


def projection(metrics, parts, plan, anchors):
    """What today's plan would plausibly be worth, using the same weights.

    Deliberately modest: it assumes the plan is completed as written and that
    concept blocks land, which is optimistic. Labelled as an estimate everywhere.
    """
    if not plan or not plan.get("blocks"):
        return None

    total_w = max(1, metrics.get("topic_weight_total", 1))
    coverage_gain = 0.0
    accuracy_gain = 0.0
    volume_gain = 0.0
    questions = 0

    for b in plan["blocks"]:
        if b.get("done"):
            continue
        questions += b.get("count", 0)
        if b["kind"] == "concept":
            coverage_gain += (2.0 / total_w) * 100.0 * WEIGHTS["coverage"]
        elif b["kind"] in ("revise",):
            accuracy_gain += 0.25
        elif b.get("count"):
            accuracy_gain += b["count"] * 0.035
        volume_gain += (
            (b.get("minutes", 0) / 60.0)
            / VOLUME_REFERENCE_HOURS
            * 100.0
            * WEIGHTS["volume"]
        )

    consistency_gain = 0.0
    if plan.get("total_minutes", 0) >= 25:
        consistency_gain = 0.35

    delta = coverage_gain + accuracy_gain + volume_gain + consistency_gain
    index_now = (
        parts["coverage"] * WEIGHTS["coverage"]
        + parts["accuracy"] * WEIGHTS["accuracy"]
        + parts["volume"] * WEIGHTS["volume"]
        + parts["consistency"] * WEIGHTS["consistency"]
    )
    score_now = _interp(anchors, min(100.0, index_now))
    score_then = _interp(anchors, min(100.0, index_now + delta))

    return dict(
        estimate=True,
        index_delta=round(delta, 2),
        score_delta=round(score_then - score_now, 1),
        questions=questions,
        minutes=plan.get("total_minutes", 0),
        breakdown=[
            dict(key="coverage", label="Coverage", points=round(coverage_gain, 2)),
            dict(key="accuracy", label="Accuracy", points=round(accuracy_gain, 2)),
            dict(key="volume", label="Volume", points=round(volume_gain, 2)),
            dict(
                key="consistency", label="Consistency", points=round(consistency_gain, 2)
            ),
        ],
        note=(
            "Assumes today's plan is completed as written. It is arithmetic on the "
            "same weights, not a forecast."
        ),
    )


def compute(conn, metrics, bundle=None, plan=None):
    cfg = content.targets()
    parts = components(metrics)
    index_value = (
        parts["coverage"] * WEIGHTS["coverage"]
        + parts["accuracy"] * WEIGHTS["accuracy"]
        + parts["volume"] * WEIGHTS["volume"]
        + parts["consistency"] * WEIGHTS["consistency"]
    )
    index_value = round(min(100.0, max(0.0, index_value)), 2)

    anchors = (cfg.get("score_model") or {}).get("anchors") or [[0, 0], [100, 1000]]
    est_score = round(_interp(anchors, index_value), 1)

    position = cohort_position(index_value, cfg.get("cohort_model") or {})
    confidence = estimate_confidence(metrics)
    movement = _record_and_diff(
        conn, index_value, est_score, position, parts, confidence, metrics
    )

    settings = db.get_settings(conn)
    primary = settings.get("primary_target", "barc-gate")
    goals = []
    for t in cfg.get("targets", []):
        goals.append(_target_view(t, index_value, est_score, anchors, primary))

    risk, recovery = risk_and_recovery(bundle)
    return dict(
        index=index_value,
        components=parts,
        contributions=contributions(parts),
        component_labels=COMPONENT_LABELS,
        weights=WEIGHTS,
        estimate_confidence=confidence,
        risk=risk,
        recovery=recovery,
        projection=projection(metrics, parts, plan, anchors),
        band=index_band(index_value),
        est_score=est_score,
        score_max=cfg.get("gate_score_max", 1000),
        position=position,
        movement=movement,
        targets=goals,
        primary_target=primary,
        volume_reference_hours=VOLUME_REFERENCE_HOURS,
        disclaimer="Cohort figures are a locally generated model, not real candidates. "
        "Cutoffs in content/targets.json are unofficial - verify and edit them.",
    )


def _target_view(t, index_value, est_score, anchors, primary):
    metric = t.get("metric", "gate_score")
    cutoff = float(t.get("cutoff", 0))
    stretch = float(t.get("stretch", cutoff))

    view = dict(
        slug=t.get("slug"),
        name=t.get("name"),
        org=t.get("org", ""),
        metric=metric,
        cutoff=cutoff,
        stretch=stretch,
        note=t.get("note", ""),
        source=t.get("source", ""),
        history=t.get("history", []),
        is_primary=t.get("slug") == primary,
        out_of=t.get("out_of"),
    )

    if metric == "gate_score":
        view["your_value"] = est_score
        view["gap"] = round(cutoff - est_score, 1)
        view["progress"] = round(min(100.0, est_score / cutoff * 100), 1) if cutoff else 0
        view["cleared"] = est_score >= cutoff
        needed_index = _inverse(anchors, cutoff)
        view["index_needed"] = round(needed_index, 1)
        view["index_gap"] = round(max(0.0, needed_index - index_value), 1)
        view["comparable"] = True
    else:
        # A CBT out of 300 is not on the GATE scale, so do not pretend to map it.
        view["your_value"] = None
        view["comparable"] = False
        view["progress"] = None
        view["hint"] = (
            "Scored out of %s on BARC's own paper. This tracker cannot "
            "estimate it from GATE-scale inputs, so treat the number as a "
            "reminder that a second route exists." % (t.get("out_of") or "300")
        )
    return view


def _inverse(anchors, target_output):
    pts = sorted((float(a), float(b)) for a, b in anchors)
    if target_output <= pts[0][1]:
        return pts[0][0]
    if target_output >= pts[-1][1]:
        return pts[-1][0]
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        if target_output <= y1:
            span = (y1 - y0) or 1.0
            return x0 + (x1 - x0) * (target_output - y0) / span
    return pts[-1][0]


# ---------------------------------------------------------------------------
# daily movement -- "how many did I move past today"
# ---------------------------------------------------------------------------
def _record_and_diff(
    conn, index_value, est_score, position, parts=None, confidence=None, metrics=None
):
    """Snapshot today's reading and explain the change since the last one."""
    today = date.today().isoformat()
    now = datetime.now().isoformat(timespec="seconds")
    parts = parts or {}
    mastery = float((metrics or {}).get("mastery_pct") or 0)
    conf_score = float((confidence or {}).get("score") or 0)

    prior = conn.execute(
        "SELECT * FROM readiness_log WHERE day < ? ORDER BY day DESC LIMIT 1", (today,)
    ).fetchone()
    start_of_today = conn.execute(
        "SELECT * FROM readiness_log WHERE day = ?", (today,)
    ).fetchone()

    with conn:
        if start_of_today is None:
            conn.execute(
                "INSERT INTO readiness_log (day, index_value, est_score, percentile,"
                " behind_you, ahead_of_you, coverage, accuracy, volume, consistency,"
                " confidence, mastery, created_at, updated_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    today,
                    index_value,
                    est_score,
                    position["percentile"],
                    position["behind_you"],
                    position["ahead_of_you"],
                    parts.get("coverage"),
                    parts.get("accuracy"),
                    parts.get("volume"),
                    parts.get("consistency"),
                    conf_score,
                    mastery,
                    now,
                    now,
                ),
            )
        else:
            conn.execute(
                "UPDATE readiness_log SET index_value = ?, est_score = ?, percentile = ?,"
                " behind_you = ?, ahead_of_you = ?, coverage = ?, accuracy = ?,"
                " volume = ?, consistency = ?, confidence = ?, mastery = ?,"
                " updated_at = ? WHERE day = ?",
                (
                    index_value,
                    est_score,
                    position["percentile"],
                    position["behind_you"],
                    position["ahead_of_you"],
                    parts.get("coverage"),
                    parts.get("accuracy"),
                    parts.get("volume"),
                    parts.get("consistency"),
                    conf_score,
                    mastery,
                    now,
                    today,
                ),
            )

    # Baseline for "today" is where the day started, which is the previous
    # snapshot if one exists, otherwise the first reading of today.
    base = prior if prior is not None else start_of_today
    if base is None:
        return dict(
            available=False,
            why_moved=[],
            headline="First reading recorded.",
            note="Movement shows up from your next session.",
        )

    passed = position["behind_you"] - base["behind_you"]
    index_delta = round(index_value - base["index_value"], 2)

    # ---- decompose the index delta per component ------------------------
    why = []
    keys = base.keys()
    for key in ("coverage", "accuracy", "volume", "consistency"):
        if key not in keys or base[key] is None or parts.get(key) is None:
            continue
        raw = float(parts[key]) - float(base[key])
        pts = round(raw * WEIGHTS[key], 2)
        if abs(pts) < 0.01:
            continue
        why.append(
            dict(
                key=key,
                label=COMPONENT_LABELS[key],
                raw_delta=round(raw, 1),
                points=pts,
                direction="up" if pts > 0 else "down",
            )
        )
    why.sort(key=lambda w: -abs(w["points"]))

    if not why:
        headline = "Index is flat since %s - nothing measured has changed." % base["day"]
    else:
        bits = [
            "%s %s%.2f" % (w["label"], "+" if w["points"] > 0 else "", w["points"])
            for w in why[:3]
        ]
        headline = "%s%.2f since %s: %s." % (
            "+" if index_delta > 0 else "",
            index_delta,
            base["day"],
            ", ".join(bits),
        )

    return dict(
        available=True,
        since=base["day"],
        passed_today=passed,
        index_delta=index_delta,
        score_delta=round(est_score - base["est_score"], 1),
        percentile_delta=round(position["percentile"] - base["percentile"], 2),
        still_ahead=position["ahead_of_you"],
        why_moved=why,
        headline=headline,
        confidence_delta=(
            round(conf_score - float(base["confidence"] or 0), 1)
            if "confidence" in keys and base["confidence"] is not None
            else None
        ),
        mastery_delta=(
            round(mastery - float(base["mastery"] or 0), 1)
            if "mastery" in keys and base["mastery"] is not None
            else None
        ),
        simulated=True,
    )


def history(conn, days=60):
    since = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT day, index_value, est_score, percentile, coverage, accuracy,"
        " volume, consistency, mastery FROM readiness_log"
        " WHERE day >= ? ORDER BY day ASC",
        (since,),
    ).fetchall()
    return [dict(r) for r in rows]


def next_actions(metrics, subjects, parts):
    """Concrete levers, ordered by how much index they would move."""
    out = []

    weak_cover = sorted(
        (s for s in subjects if s["topic_count"]),
        key=lambda s: (s["topic_progress"], -s["marks"]),
    )[:3]
    for s in weak_cover:
        if s["topic_progress"] >= 95:
            continue
        pending = [t for t in s["topics"] if t["status"] != "done"]
        if not pending:
            continue
        out.append(
            dict(
                kind="coverage",
                title="Close out %s" % s["name"],
                detail="%d of %d topics still open, worth about %d marks in the paper. "
                "Next up: %s."
                % (len(pending), s["topic_count"], s["marks"], pending[0]["name"]),
                lever="Coverage carries %d%% of the index."
                % round(WEIGHTS["coverage"] * 100),
            )
        )

    if parts["accuracy_confidence"] < 100:
        out.append(
            dict(
                kind="accuracy",
                title="Build an accuracy sample",
                detail="Accuracy is only %d%% confident right now - it needs about 150 "
                "attempted questions before it stops being pulled toward neutral. "
                "You are at %d."
                % (parts["accuracy_confidence"], metrics.get("questions_attempted", 0)),
                lever="Accuracy carries %d%% of the index."
                % round(WEIGHTS["accuracy"] * 100),
            )
        )
    elif parts["accuracy_raw"] < 70:
        weak = sorted(
            (s for s in subjects if s["attempts"] >= 5 and s["accuracy"] is not None),
            key=lambda s: s["accuracy"],
        )[:2]
        if weak:
            out.append(
                dict(
                    kind="accuracy",
                    title="Fix accuracy in %s" % weak[0]["name"],
                    detail="%d%% correct over %d attempts. Redo the topics you got wrong "
                    "before adding new ones."
                    % (weak[0]["accuracy"], weak[0]["attempts"]),
                    lever="Accuracy carries %d%% of the index."
                    % round(WEIGHTS["accuracy"] * 100),
                )
            )

    if parts["volume"] < 60:
        hours = metrics.get("total_hours", 0)
        out.append(
            dict(
                kind="volume",
                title="Keep stacking hours",
                detail="%gh logged against a %dh reference. This term rises slowly and "
                "cannot be rushed." % (hours, VOLUME_REFERENCE_HOURS),
                lever="Volume carries %d%% of the index."
                % round(WEIGHTS["volume"] * 100),
            )
        )

    if metrics.get("current_streak", 0) < 7:
        out.append(
            dict(
                kind="consistency",
                title="Rebuild the streak",
                detail="Current streak is %d days. The consistency term rewards an "
                "unbroken run more than a heavy single day."
                % metrics.get("current_streak", 0),
                lever="Consistency carries %d%% of the index."
                % round(WEIGHTS["consistency"] * 100),
            )
        )

    return out[:5]
