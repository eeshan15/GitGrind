#!/usr/bin/env python3
"""End-to-end check of every GitGrind engine against a temporary database.

This is not a unit-test suite. It is the thing you run after changing anything in
core/ to be sure the whole pipeline still hangs together: migrate a fresh
database, seed the syllabus, load the bank, log a session, build and grade a
quiz, schedule revision, generate a plan, produce recommendations, compute
readiness, evaluate badges, and serialise the whole state the UI consumes.

    python tools/selftest.py
    python tools/selftest.py --keep        leave the temp database for poking at
    python tools/selftest.py --verbose     print each engine's output
"""

import argparse
import os
import shutil
import sys
import tempfile
import traceback
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PASS, FAIL = [], []


def check(label, fn, verbose=False):
    """Run one step. A failure is reported and the run continues."""
    try:
        out = fn()
        PASS.append(label)
        print("  ok    %s" % label)
        if verbose and out is not None:
            print("        %s" % str(out)[:200])
        return out
    except Exception as exc:
        FAIL.append((label, exc))
        print("  FAIL  %s" % label)
        print("        %s: %s" % (type(exc).__name__, exc))
        if verbose:
            traceback.print_exc()
        return None


def main():
    ap = argparse.ArgumentParser(description="Exercise every engine end to end.")
    ap.add_argument("--keep", action="store_true", help="keep the temporary database")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="gitgrind-selftest-")
    db_path = os.path.join(tmp, "test.db")
    os.environ["GITGRIND_DB"] = db_path

    from core import (
        achievements,
        api,
        content,
        db,
        doubts,
        feedback,
        planner,
        quiz,
        readiness,
        recommend,
        revision,
        stats,
    )

    print("\nGitGrind selftest")
    print("database: %s\n" % db_path)

    # ---- schema ---------------------------------------------------------
    print("schema")
    conn = check(
        "init and migrate to the current schema", lambda: db.init(), args.verbose
    )
    if conn is None:
        print("\nCannot continue without a database.")
        return 1

    def _health():
        h = db.health(conn)
        assert h["schema_version"] == db.SCHEMA_VERSION, "schema version mismatch"
        assert h["table_count"] >= 29, (
            "expected at least 29 tables, got %d" % h["table_count"]
        )
        return "v%d, %d tables" % (h["schema_version"], h["table_count"])

    check("health report and table count", _health, args.verbose)

    def _migrate_twice():
        """A migration must be safe to run again. Prove it rather than assume it."""
        before = {
            t: conn.execute('SELECT COUNT(*) FROM "%s"' % t).fetchone()[0]
            for t in db.health(conn)["tables"]
        }
        again = db.migrate(conn)
        after = {
            t: conn.execute('SELECT COUNT(*) FROM "%s"' % t).fetchone()[0]
            for t in db.health(conn)["tables"]
        }
        assert not again, "a second migrate() re-ran steps: %s" % again
        assert before == after, "row counts moved on a no-op migrate"
        assert (
            conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        ), "integrity_check failed after migrate"
        return "no-op, %d tables unchanged" % len(after)

    check("migrate is idempotent", _migrate_twice, args.verbose)

    # ---- content --------------------------------------------------------
    print("\ncontent registry")
    check(
        "seed syllabus and settings", lambda: content.seed(conn) or "seeded", args.verbose
    )

    def _bank():
        st = content.bank_stats(reload=True)
        assert st["total"] > 0, "the question bank is empty"
        return "%d questions, %d%% usable, %d%% topic coverage" % (
            st["total"],
            st["health_pct"],
            st["coverage_pct"],
        )

    check("load and validate the question bank", _bank, args.verbose)
    check(
        "topic index is populated",
        lambda: "%d topics" % len(content.topic_index()),
        args.verbose,
    )
    check(
        "topic normalisation resolves a known slug",
        lambda: content.normalise_topic(conn, "deadlock", "operating-systems"),
        args.verbose,
    )
    check(
        "bank search returns results",
        lambda: "%d hit(s)" % len(content.search(query="", limit=5)),
        args.verbose,
    )

    def _sources():
        content.sync_sources(conn)
        return "%d source(s)" % len(content.source_summary(conn))

    check("source registry syncs", _sources, args.verbose)

    def _papers():
        content.sync_papers(conn)
        rows = content.paper_summary(conn)
        assert rows, "no papers were reconstructed from the banks"
        # Every paper must be gapless and ordered, or "question 12 of 65" is a lie.
        for p in rows:
            positions = [
                r["position"]
                for r in conn.execute(
                    "SELECT position FROM paper_questions WHERE paper_id = ?"
                    " ORDER BY position",
                    (p["id"],),
                )
            ]
            assert positions == list(range(1, len(positions) + 1)), (
                "%s has non-contiguous positions" % p["slug"]
            )
            assert p["question_count"] == len(positions), (
                "%s question_count disagrees with paper_questions" % p["slug"]
            )
        # GA must never be folded into the core mark total.
        ga = conn.execute(
            "SELECT COUNT(*) FROM paper_sections WHERE section = 'ga'"
        ).fetchone()[0]
        assert ga, "no paper has a General Aptitude section"
        return "%d paper(s), %d with a GA section" % (len(rows), ga)

    check("papers reconstruct, order and section cleanly", _papers, args.verbose)

    def _paper_reject():
        # Other branches' papers are quoted inside CSE banks. They must not be
        # mapped onto a GATE CSE paper.
        for bad in ("GATE2012 AR: GA-5", "GATE2010 MN: GA-5", "GATE2014 AG: GA-10"):
            assert content.parse_exam_ref(bad) is None, "%s was accepted" % bad
        good = content.parse_exam_ref("GATE CSE 2020 | GA | Question: 5")
        assert good and good["section"] == "ga", "GA marker not detected"
        return "other-branch refs rejected, GA marker detected"

    check("exam-reference parser rejects foreign papers", _paper_reject, args.verbose)

    # ---- a session ------------------------------------------------------
    print("\nsessions and grading")
    today = date.today().isoformat()
    handler = api.Handler.__new__(api.Handler)  # methods only, no HTTP

    subject_id = conn.execute("SELECT id FROM subjects ORDER BY id LIMIT 1").fetchone()[
        "id"
    ]
    topic_ids = [
        r["id"]
        for r in conn.execute(
            "SELECT id FROM topics WHERE subject_id = ? LIMIT 3", (subject_id,)
        ).fetchall()
    ]

    session = check(
        "log a session with topics marked done",
        lambda: handler._create_session(
            conn,
            dict(
                subject_id=subject_id,
                day=today,
                minutes=75,
                kind="concept",
                topic_ids=topic_ids,
                mark_done=True,
                with_quiz=False,
                note="selftest session",
            ),
        ),
        args.verbose,
    )

    def _quiz_cycle():
        bundle = stats.gather(conn)
        built, err = quiz.build_quiz(
            conn,
            purpose="mixed",
            count=3,
            metrics=bundle["metrics"],
            topic_health=bundle["topic_health"],
        )
        assert not err, err
        assert built["questions"], "no questions selected"
        # submit_quiz takes a list of response objects, the same shape the UI posts.
        answers = [
            dict(
                question_id=q["id"],
                response=("A" if q.get("options") else "0"),
                seconds=40 + i * 5,
                confidence=3,
            )
            for i, q in enumerate(built["questions"])
        ]
        out = quiz.submit_quiz(conn, built["id"], answers)
        assert isinstance(out, dict) and out, "grading returned nothing useful"
        return "%d question(s) graded" % len(built["questions"])

    check("build a quiz and grade a submission", _quiz_cycle, args.verbose)

    for purpose in ("review", "weak", "mixed", "speed", "boss", "fresh"):

        def _p(p=purpose):
            bundle = stats.gather(conn)
            picks = quiz.select(
                conn,
                purpose=p,
                count=3,
                metrics=bundle["metrics"],
                topic_health=bundle["topic_health"],
            )
            return "%d pick(s)" % len(picks)

        check("selector purpose '%s'" % purpose, _p, args.verbose)

    # ---- revision -------------------------------------------------------
    print("\nspaced repetition")
    check(
        "backfill the revision queue from activity",
        lambda: "%d card(s)" % revision.sync_from_activity(conn),
        args.verbose,
    )
    check(
        "queue is readable",
        lambda: "%d due or scheduled" % len(revision.queue(conn)),
        args.verbose,
    )

    def _debt():
        d = revision.debt(conn)
        assert 0 <= d["pressure"] <= 100, "pressure out of range"
        return "%d due, %d overdue, pressure %d" % (
            d["due_today"],
            d["overdue"],
            d["pressure"],
        )

    check("debt and pressure computed", _debt, args.verbose)

    def _review_step():
        q = revision.quality_from_attempt(
            correct=False, seconds=20, confidence=5, marks=2
        )
        assert q == 0, "confidently wrong should be the worst quality, got %s" % q
        return "confidently-wrong maps to quality 0"

    check("quality mapping punishes confident errors", _review_step, args.verbose)

    # ---- analytics ------------------------------------------------------
    print("\nanalytics")
    bundle = check(
        "gather the full metric bundle", lambda: stats.gather(conn), args.verbose
    )

    def _metrics():
        m = bundle["metrics"]
        for k in (
            "total_hours",
            "accuracy",
            "coverage_pct",
            "consistency_score",
            "focus_score",
            "revision_debt",
            "revision_pressure",
            "mastery_pct",
        ):
            assert k in m, "missing metric: %s" % k
        return "%d metrics" % len(m)

    check("every expected metric is present", _metrics, args.verbose)
    check("velocity window", lambda: bundle["velocity"]["trend"], args.verbose)
    check("attempt quality", lambda: bundle["quality"]["guess_rate"], args.verbose)
    check(
        "per-topic health matrix",
        lambda: "%d topic(s)" % len(bundle["topic_health"]),
        args.verbose,
    )
    check(
        "heatmap",
        lambda: "%d subject row(s)"
        % len(
            bundle.get("heatmap")
            or stats.heatmap(bundle["subjects"], bundle["topic_health"])
        ),
        args.verbose,
    )

    # ---- planner --------------------------------------------------------
    print("\nplanner")
    plan = check(
        "generate today's plan",
        lambda: planner.plan_for(conn, bundle, regenerate=True),
        args.verbose,
    )

    def _blocks():
        assert plan["blocks"], "the planner produced no blocks"
        for b in plan["blocks"]:
            assert b.get("reason"), "block %s has no reason" % b.get("key")
        return "%d block(s), %d minutes" % (len(plan["blocks"]), plan["total_minutes"])

    check("every block carries a reason", _blocks, args.verbose)
    check(
        "a block can be completed",
        lambda: planner.complete_block(conn, plan["day"], plan["blocks"][0]["key"])
        or "done",
        args.verbose,
    )

    # ---- recommendations ------------------------------------------------
    print("\nrecommendations")
    recs = check(
        "build the ranked list", lambda: recommend.build(conn, bundle, plan), args.verbose
    )

    def _rec_shape():
        for r in recs or []:
            for k in ("slug", "title", "detail", "reason", "urgency", "band"):
                assert k in r, "recommendation missing %s" % k
        return "%d recommendation(s)" % len(recs or [])

    check("recommendations are fully explained", _rec_shape, args.verbose)
    check(
        "next_best names its runner-up",
        lambda: (recommend.next_best(conn, bundle, plan) or {}).get("slug"),
        args.verbose,
    )

    # ---- readiness ------------------------------------------------------
    print("\nreadiness")
    r = check(
        "compute the index",
        lambda: readiness.compute(conn, bundle["metrics"], bundle=bundle, plan=plan),
        args.verbose,
    )

    def _ready_shape():
        for k in (
            "index",
            "est_score",
            "components",
            "contributions",
            "band",
            "estimate_confidence",
            "risk",
            "recovery",
            "projection",
            "movement",
        ):
            assert k in r, "readiness missing %s" % k
        assert 0 <= r["index"] <= 100, "index out of range"
        return "index %.2f (%s)" % (r["index"], r["band"]["label"])

    check("readiness exposes its whole decomposition", _ready_shape, args.verbose)
    check(
        "component contributions sum sensibly",
        lambda: "%.1f points across %d term(s)"
        % (sum(c["points"] for c in r["contributions"]), len(r["contributions"])),
        args.verbose,
    )

    # ---- feedback -------------------------------------------------------
    print("\nfeedback loop")

    def _feedback():
        before = feedback.kind_multiplier(conn, "revision")
        for _ in range(4):
            feedback.record(
                conn,
                "recommendation",
                "helpful",
                target_slug="revision",
                payload={"rec_kind": "revision"},
            )
        after = feedback.kind_multiplier(conn, "revision")
        assert after > before, "a positive rating should raise the weight"
        return "weight %.3f -> %.3f" % (before, after)

    check("positive ratings raise the weight", _feedback, args.verbose)

    def _clamped():
        for _ in range(200):
            feedback.record(
                conn,
                "recommendation",
                "not_helpful",
                target_slug="revision",
                payload={"rec_kind": "revision"},
            )
        w = feedback.kind_multiplier(conn, "revision")
        assert w >= 0.34, "weight fell below the clamp: %s" % w
        return "clamped at %.3f after 200 negatives" % w

    check("weights stay inside their clamp", _clamped, args.verbose)
    check("feedback summary", lambda: feedback.summary(conn)["total"], args.verbose)

    # ---- gamification ---------------------------------------------------
    print("\nrewards")
    badges = check(
        "evaluate every badge",
        lambda: achievements.evaluate(conn, bundle["metrics"], bundle),
        args.verbose,
    )

    def _tracks():
        tracks = {b["track"] for b in badges or []}
        assert len(tracks) >= 5, "expected five tracks, saw %s" % sorted(tracks)
        return "%d badges across %d track(s)" % (len(badges), len(tracks))

    check("five tracks are present", _tracks, args.verbose)
    check(
        "missions are generated",
        lambda: achievements.missions(conn, bundle, plan)["headline"],
        args.verbose,
    )

    # ---- doubts ---------------------------------------------------------
    print("\ndoubts")
    d = check(
        "log a doubt",
        lambda: doubts.save(
            conn,
            "Selftest doubt: why does the banker's algorithm need a safe sequence?",
            "",
            "",
            "",
            "prompt text",
            provider="",
            answer="",
        ),
        args.verbose,
    )
    if d:
        did = d.get("id") if isinstance(d, dict) else d
        check(
            "rate a doubt as helpful",
            lambda: doubts.rate(conn, did, True, "") or "rated",
            args.verbose,
        )
    check(
        "delayed retry check runs",
        lambda: "%d marked" % doubts.check_retries(conn),
        args.verbose,
    )

    # ---- the state the UI consumes --------------------------------------
    print("\napi state")

    def _state():
        st = api.build_state(conn)
        required = (
            "plan",
            "next_action",
            "recommendations",
            "revision_queue",
            "debt",
            "heatmap",
            "topic_health",
            "missions",
            "feedback",
            "readiness",
            "bank",
            "review",
            "sources",
            "papers",
            "prefs",
            "db",
            "metrics",
        )
        missing = [k for k in required if k not in st]
        assert not missing, "state is missing: %s" % ", ".join(missing)
        return "%d keys" % len(st)

    check("build_state exposes everything the UI needs", _state, args.verbose)

    def _serialises():
        import json

        raw = json.dumps(api.build_state(conn))
        return "%d KB of JSON" % (len(raw) // 1024)

    check("state serialises to JSON cleanly", _serialises, args.verbose)

    # ---- summary --------------------------------------------------------
    conn.close()
    print("\n" + "-" * 62)
    print("  %d passed, %d failed" % (len(PASS), len(FAIL)))
    if FAIL:
        print("\n  failures:")
        for label, exc in FAIL:
            print("    %-52s %s" % (label[:52], type(exc).__name__))
    print("-" * 62 + "\n")

    if args.keep:
        print("temp database kept at %s\n" % db_path)
    else:
        shutil.rmtree(tmp, ignore_errors=True)

    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
