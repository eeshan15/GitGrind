"""HTTP layer: builds the state payload and routes every /api call.

This module stays thin on purpose. It validates input, calls one core service,
and returns JSON. Any logic that could be described as "deciding something"
belongs in planner.py, recommend.py, quiz.py or revision.py, not here.
"""

import json
import mimetypes
import os
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote, urlparse

from . import (
    achievements,
    content,
    db,
    doubts,
    feedback,
    live,
    planner,
    quiz,
    readiness,
    recommend,
    revision,
    stats,
)

# The UI is read-only, so it is served straight out of the bundle when frozen.
STATIC_DIR = os.path.join(db.ASSET_DIR, "static")

# Question figures. These are content, not code, so they live under content/
# rather than static/ and are served from the writable copy - a re-import drops
# new files in and they are live without rebuilding anything.
ASSETS_DIR = os.path.join(content.CONTENT_DIR, "assets")
ASSET_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}
VERSION = "1.0"
SHOW_WINDOW = None
# Settings the user is allowed to change from the UI, with their coercion.
TUNABLE = {
    "weak_accuracy_threshold": ("int", 30, 95),
    "revision_grace_days": ("int", 0, 14),
    "repeat_cooldown_days": ("int", 0, 60),
    "plan_auto_generate": ("bool", 0, 1),
    "adaptive_difficulty": ("bool", 0, 1),
    "reduced_motion": ("bool", 0, 1),
}


# ---------------------------------------------------------------------------
# state
# ---------------------------------------------------------------------------
def build_state(conn, celebrate=True):
    """One payload with everything the shell needs to render any tab."""
    bundle = stats.gather(conn)
    metrics = bundle["metrics"]
    settings = bundle["settings"]

    plan = planner.plan_for(conn, bundle)
    ready = readiness.compute(conn, metrics, bundle=bundle, plan=plan)
    badges = achievements.evaluate(conn, metrics, bundle)
    missions = achievements.missions(conn, bundle, plan)
    recs = recommend.build(conn, bundle, plan)
    next_action = recommend.next_best(conn, bundle, plan)
    rev_queue = revision.queue(conn, limit=25)

    qotd_row, qotd_q = quiz.pick_question_of_day(conn)
    qotd = None
    if qotd_q:
        subj = next(
            (s for s in bundle["subjects"] if s["slug"] == qotd_q["subject"]), None
        )
        qotd = dict(
            day=qotd_row["day"],
            reason=qotd_row["reason"],
            answered=bool(qotd_row["answered_at"]),
            correct=(
                bool(qotd_row["correct"]) if qotd_row["correct"] is not None else None
            ),
            subject_name=subj["name"] if subj else qotd_q["subject"],
            question=content.public_question(
                qotd_q, reveal=bool(qotd_row["answered_at"])
            ),
            streak=quiz.streak_of_daily_questions(conn),
        )
        if qotd_row["response"]:
            try:
                qotd["your_response"] = json.loads(qotd_row["response"])
            except ValueError:
                qotd["your_response"] = None

    exam_date = settings.get("exam_date")
    days_left = None
    if exam_date:
        try:
            days_left = (date.fromisoformat(exam_date) - date.today()).days
        except ValueError:
            days_left = None

    today = date.today().isoformat()
    bank = content.bank_stats()
    return dict(
        version=VERSION,
        profile=dict(
            display_name=settings.get("display_name", ""),
            handle=settings.get("handle", ""),
            bio=settings.get("bio", ""),
            location=settings.get("location", ""),
            exam_name=settings.get("exam_name", "GATE CSE"),
            exam_date=exam_date,
            days_left=days_left,
            daily_target_mins=bundle["daily_target"],
            primary_target=settings.get("primary_target", "barc-gate"),
            avatar=settings.get("avatar", ""),
            socials={
                k[7:]: settings[k]
                for k in settings
                if k.startswith("social_") and settings[k]
            },
        ),
        prefs={
            k: (
                db.setting_int(settings, k, 0)
                if TUNABLE[k][0] == "int"
                else db.setting_bool(settings, k)
            )
            for k in TUNABLE
        },
        metrics=metrics,
        subjects=bundle["subjects"],
        calendar=bundle["calendar"],
        kind_minutes=bundle["kind_minutes"],
        kinds=content.SESSION_KINDS,
        kind_labels=content.KIND_LABELS,
        # --- engines ------------------------------------------------------
        plan=plan,
        next_action=next_action,
        recommendations=recs,
        revision_queue=rev_queue,
        debt=bundle["debt"],
        heatmap=stats.heatmap(bundle["subjects"], bundle["topic_health"]),
        topic_health=bundle["topic_health"][:40],
        velocity=bundle["velocity"],
        focus=bundle["focus"],
        quality=bundle["quality"],
        session_quality=bundle["session_quality"],
        trends=bundle["trends"],
        missions=missions,
        achievements=badges,
        tracks=achievements.TRACKS,
        readiness=ready,
        next_actions=readiness.next_actions(
            metrics, bundle["subjects"], ready["components"]
        ),
        feedback=feedback.summary(conn),
        mistakes=quiz.mistake_breakdown(conn),
        confidence=quiz.confidence_report(conn),
        # --- history ------------------------------------------------------
        qotd=qotd,
        recent=stats.recent_sessions(conn, 40),
        quiz_history=quiz.quiz_history(conn, 20),
        qotd_history=quiz.qotd_history(conn, 30),
        readiness_history=readiness.history(conn, 90),
        plan_history=planner.plan_history(conn, 21),
        dpp_history=planner.dpp_history(conn, 15),
        saved_questions=quiz.saved_questions(conn, 20),
        saved_ids=quiz.saved_ids(conn),
        # The bookmark list, kept separate from revision_queue: that table is
        # the spacing engine and also feeds the planner, the debt figure and
        # readiness, so it cannot be narrowed to bookmarks.
        revision_list=quiz.revision_list(conn),
        # --- content ------------------------------------------------------
        bank=bank,
        bank_health=bank,
        sources=content.source_summary(conn),
        papers=content.paper_summary(conn),
        imports=content.import_history(conn, 10),
        profile_stats=dict(
            weekly_minutes=stats.weekly_minutes(conn),
            difficulty=stats.difficulty_split(conn, content.question_bank()),
        ),
        review=content.review_counts(conn),
        pending_answers=content.pending_counts(),
        mistake_kinds=quiz.MISTAKE_KINDS,
        purposes=quiz.PURPOSE_LABELS,
        db=db.health(conn),
        # Whatever was in flight when the app last stopped. The UI acts on this
        # once per load; carrying it on every state refresh costs one indexed
        # lookup and saves a second round trip on boot.
        live=live.resume_offer(conn),
        today=today,
        today_minutes=bundle["per_day"].get(today, 0),
    )


# ---------------------------------------------------------------------------
# handler
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "GitGrind/%s" % VERSION
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        if os.environ.get("GITGRIND_VERBOSE"):
            self.log_date_time_string()
            print("  %s" % (fmt % args))

    # -- plumbing --------------------------------------------------------
    def _json(self, payload, status=200):
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    def _asset(self, path):
        """Serve one file from content/assets/.

        Deliberately narrow: only the extensions in ASSET_TYPES, only below
        ASSETS_DIR, and a 404 rather than the app shell on a miss so a broken
        figure shows as a broken image instead of silently rendering HTML.
        """
        rel = unquote(path[len("/content/assets/"):])
        if not rel or ".." in rel.split("/") or rel.startswith("/") or "\\" in rel:
            return self.send_error(404, "Not found")
        root = os.path.realpath(ASSETS_DIR)
        full = os.path.realpath(os.path.join(root, rel))
        if not (full == root or full.startswith(root + os.sep)):
            return self.send_error(404, "Not found")
        ctype = ASSET_TYPES.get(os.path.splitext(full)[1].lower())
        if not ctype or not os.path.isfile(full):
            return self.send_error(404, "Not found")
        with open(full, "rb") as fh:
            data = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        # Figure files are content-addressed by the importer, so a long cache is
        # safe and keeps a question with several diagrams from refetching them.
        self.send_header("Cache-Control", "public, max-age=86400")
        self.end_headers()
        self.wfile.write(data)

    def _static(self, path):
        rel = "index.html" if path in ("", "/") else path.lstrip("/")
        full = os.path.normpath(os.path.join(STATIC_DIR, rel))
        if not full.startswith(STATIC_DIR) or not os.path.isfile(full):
            # Unknown paths fall back to the shell so hash routes survive a reload.
            full = os.path.join(STATIC_DIR, "index.html")
            if not os.path.isfile(full):
                self.send_error(404, "Not found")
                return
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        with open(full, "rb") as fh:
            data = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _run(self, fn):
        try:
            with db.LOCK:
                conn = db.connect()
                try:
                    result, status = fn(conn)
                    return self._json(result, status)
                finally:
                    conn.close()
        except ValueError as exc:
            return self._json(dict(error=str(exc)), 400)
        except LookupError as exc:
            return self._json(dict(error=str(exc)), 404)
        except Exception as exc:
            if os.environ.get("GITGRIND_VERBOSE"):
                import traceback

                traceback.print_exc()
            return self._json(dict(error="%s: %s" % (type(exc).__name__, exc)), 500)

    # -- verbs -----------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/content/assets/"):
            return self._asset(parsed.path)
        if not parsed.path.startswith("/api/"):
            return self._static(parsed.path)
        return self._run(
            lambda conn: self._get(conn, parsed.path, parse_qs(parsed.query))
        )

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._body()
        return self._run(lambda conn: self._post(conn, path, body))

    def do_DELETE(self):
        path = urlparse(self.path).path
        return self._run(lambda conn: self._delete(conn, path))

    # -- GET routes ------------------------------------------------------
    def _get(self, conn, path, qs):
        one = lambda k, d="": (qs.get(k) or [d])[0]

        if path == "/api/state":
            return build_state(conn), 200
        if path == "/api/health":
            return (
                dict(
                    app="gitgrind",
                    version=VERSION,
                    db=db.health(conn),
                    bank=content.bank_stats(),
                    review=content.review_counts(conn),
                ),
                200,
            )
        if path == "/api/live":
            return live.resume_offer(conn), 200
        if path == "/api/readiness":
            bundle = stats.gather(conn)
            plan = planner.plan_for(conn, bundle)
            return (
                readiness.compute(conn, bundle["metrics"], bundle=bundle, plan=plan),
                200,
            )
        if path == "/api/qotd":
            row, q = quiz.pick_question_of_day(conn)
            if not q:
                raise LookupError("The question bank is empty.")
            return (
                dict(
                    day=row["day"],
                    reason=row["reason"],
                    answered=bool(row["answered_at"]),
                    question=content.public_question(q, reveal=bool(row["answered_at"])),
                ),
                200,
            )

        # ---- planning ---------------------------------------------------
        if path == "/api/plan":
            bundle = stats.gather(conn)
            return planner.plan_for(conn, bundle, day=one("day") or None), 200
        if path == "/api/plan/history":
            return dict(items=planner.plan_history(conn, 60)), 200
        if path == "/api/revision":
            return (
                dict(
                    items=revision.queue(conn, limit=int(one("limit", "40"))),
                    debt=revision.debt(conn),
                ),
                200,
            )
        if path == "/api/recommendations":
            bundle = stats.gather(conn)
            plan = planner.plan_for(conn, bundle)
            return (
                dict(
                    items=recommend.build(conn, bundle, plan),
                    next=recommend.next_best(conn, bundle, plan),
                    ledger=recommend.ledger(conn),
                ),
                200,
            )
        if path == "/api/dpp":
            return dict(items=planner.dpp_history(conn, 40)), 200

        # ---- content ----------------------------------------------------
        if path == "/api/bank":
            return content.bank_stats(reload=one("reload") == "1"), 200
        if path == "/api/sources":
            return (
                dict(items=content.source_summary(conn), bank=content.bank_stats()),
                200,
            )
        if path == "/api/papers":
            slug = one("slug")
            if slug:
                paper = content.paper_questions(conn, slug, reveal=one("reveal") == "1")
                if not paper:
                    raise ValueError("No paper with slug %s." % slug)
                return paper, 200
            return dict(items=content.paper_summary(conn)), 200
        if path == "/api/imports":
            return (
                dict(
                    items=content.import_history(conn, 40),
                    review=content.review_counts(conn),
                ),
                200,
            )
        if path == "/api/questions/pending":
            return (
                dict(
                    items=content.pending_answers(
                        subject=qs.get("subject", [""])[0],
                        topic=qs.get("topic", [""])[0],
                        limit=int(qs.get("limit", ["40"])[0] or 40),
                        offset=int(qs.get("offset", ["0"])[0] or 0),
                    ),
                    counts=content.pending_counts(),
                ),
                200,
            )
        if path == "/api/review":
            return (
                dict(
                    items=content.review_pending(conn, int(one("limit", "40"))),
                    counts=content.review_counts(conn),
                ),
                200,
            )
        if path == "/api/questions":
            return (
                dict(
                    items=content.search(
                        query=one("q"),
                        subject=one("subject"),
                        topic=one("topic"),
                        qtype=one("type"),
                        difficulty=one("difficulty"),
                        kind=one("kind"),
                        source=one("source"),
                        paper=one("paper"),
                        limit=int(one("limit", "40")),
                    )
                ),
                200,
            )
        if path == "/api/topics/graph":
            bundle = stats.gather(conn)
            return content.topic_graph(conn, bundle["topic_health"]), 200
        if path == "/api/saved":
            return dict(items=quiz.saved_questions(conn, 60)), 200

        # ---- feedback ---------------------------------------------------
        if path == "/api/feedback":
            return (
                dict(summary=feedback.summary(conn), history=feedback.history(conn, 40)),
                200,
            )

        # ---- practice analytics ----------------------------------------
        if path == "/api/mistakes":
            return quiz.mistake_breakdown(conn), 200
        if path == "/api/confidence":
            return quiz.confidence_report(conn), 200

        # ---- doubts / misc ----------------------------------------------
        if path == "/api/doubts/status":
            return doubts.status(conn), 200
        if path == "/api/doubts":
            doubts.check_retries(conn)
            return (
                dict(
                    items=doubts.history(conn, 40), pressure=doubts.topic_pressure(conn)
                ),
                200,
            )
        # Reopen an unfinished set. Unambiguous against /api/quiz/<id>/submit,
        # which is POST only, so the segment count is enough to tell them apart.
        if path.startswith("/api/quiz/") and len(path.split("/")) == 4:
            return quiz.resume_quiz(conn, int(path.rsplit("/", 1)[-1])), 200
        if path == "/api/export":
            return self._export(conn), 200
        if path.startswith("/api/subjects/"):
            return self._subject_detail(conn, int(path.rsplit("/", 1)[-1])), 200
        raise LookupError("Unknown endpoint: %s" % path)

    # -- POST routes -----------------------------------------------------
    def _post(self, conn, path, body):
        if path == "/api/sessions":
            return self._create_session(conn, body), 201
        if path == "/api/topics/status":
            return self._set_topic_status(conn, body), 200
        if path == "/api/topics/confidence":
            return self._set_topic_confidence(conn, body), 200

        # ---- live checkpoint --------------------------------------------
        # Written by the UI on every change and at least every ten seconds while
        # a clock is running, so it must stay cheap: one upsert, no state rebuild
        # in the response. An empty payload is how the UI says "nothing is in
        # flight any more" - clearing on submit or discard goes through here too.
        if path == "/api/live":
            kind = str(body.get("kind") or "")
            payload = body.get("payload") or {}
            if not isinstance(payload, dict):
                raise ValueError("payload must be an object.")
            if not kind or not payload:
                live.clear(conn)
                return dict(ok=True, cleared=True), 200
            return dict(ok=True, **live.save(conn, kind, payload)), 200
        if path == "/api/live/clear":
            live.clear(conn)
            return dict(ok=True, cleared=True), 200

        # ---- quizzes ----------------------------------------------------
        if path == "/api/quiz":
            bundle = stats.gather(conn)
            # The UI speaks in slugs and purposes ("drill this weak topic"); the
            # selector speaks in ids. Translate here so neither side has to know
            # about the other.
            subject_id = body.get("subject_id")
            if not subject_id and body.get("subject"):
                row = conn.execute(
                    "SELECT id FROM subjects WHERE slug = ?", (body["subject"],)
                ).fetchone()
                if row:
                    subject_id = row["id"]
            topic_ids = list(body.get("topic_ids") or [])
            for slug in ([body["topic"]] if body.get("topic") else []) + list(
                body.get("topics") or []
            ):
                row = conn.execute(
                    "SELECT id FROM topics WHERE slug = ?", (slug,)
                ).fetchone()
                if row and row["id"] not in topic_ids:
                    topic_ids.append(row["id"])

            # "Sit this paper" is just a quiz whose question_ids are the paper's,
            # in printed order. The selector needs no new mode for it.
            paper_id = None
            question_ids = list(body.get("question_ids") or [])
            if body.get("paper"):
                paper = content.paper_questions(conn, body["paper"])
                if not paper:
                    raise ValueError("No paper with slug %s." % body["paper"])
                paper_id = paper["id"]
                question_ids = [q["id"] for q in paper["questions"]]

            purpose = body.get("purpose") or ""
            kinds = body.get("kinds")
            if not kinds and body.get("kind"):
                kinds = [body["kind"]]

            built, err = quiz.build_quiz(
                conn,
                subject_id=subject_id,
                topic_ids=topic_ids,
                count=int(body.get("count") or 0) or None,
                kinds=kinds,
                session_id=body.get("session_id"),
                mode=body.get("mode") or purpose or "practice",
                purpose=purpose or None,
                reason=body.get("reason") or "",
                question_ids=question_ids,
                paper_id=paper_id,
                metrics=bundle["metrics"],
                topic_health=bundle["topic_health"],
            )
            if err:
                raise ValueError(err)
            return built, 201
        if path == "/api/quiz/retry":
            built, err = quiz.retry_set(conn, body.get("question_ids") or [])
            if err:
                raise ValueError(err)
            return built, 201
        if path.startswith("/api/quiz/") and path.endswith("/submit"):
            quiz_id = int(path.split("/")[3])
            outcome = quiz.submit_quiz(
                conn, quiz_id, body.get("responses") or [], body.get("duration_s", 0)
            )
            outcome["state"] = build_state(conn)
            return outcome, 200
        if path == "/api/qotd/answer":
            outcome = quiz.answer_question_of_day(
                conn, body.get("response"), body.get("seconds", 0), body.get("confidence")
            )
            outcome["state"] = build_state(conn)
            return outcome, 200
        if path == "/api/questions/save":
            # Bookmarking now moves the revision queue, so the client needs the
            # whole state back or the profile page would keep showing the old
            # list until the next full refresh.
            outcome = quiz.save_question(
                conn, body.get("question_id"), bool(body.get("saved", True))
            )
            outcome["state"] = build_state(conn)
            return outcome, 200
        if path == "/api/questions/mistake":
            return (
                quiz.tag_mistake(
                    conn, body.get("question_id"), body.get("mistake_kind", "")
                ),
                200,
            )

        # ---- plan -------------------------------------------------------
        if path == "/api/plan/generate":
            bundle = stats.gather(conn)
            return (
                planner.plan_for(
                    conn,
                    bundle,
                    day=body.get("day"),
                    regenerate=True,
                    available_mins=body.get("minutes"),
                ),
                200,
            )
        if path == "/api/plan/block/start":
            bundle = stats.gather(conn)
            built, err = planner.start_block(
                conn,
                bundle,
                body.get("day") or date.today().isoformat(),
                body.get("block"),
            )
            if err:
                raise ValueError(err)
            return built, 201
        if path == "/api/plan/block/complete":
            plan = planner.complete_block(
                conn,
                body.get("day") or date.today().isoformat(),
                body.get("block"),
                bool(body.get("done", True)),
            )
            return dict(plan=plan, state=build_state(conn)), 200
        if path == "/api/plan/rate":
            plan = planner.rate_plan(
                conn,
                body.get("day") or date.today().isoformat(),
                body.get("rating"),
                body.get("note", ""),
            )
            return dict(plan=plan, state=build_state(conn)), 200

        # ---- revision ---------------------------------------------------
        if path == "/api/revision/review":
            item = revision.review(
                conn,
                body.get("item_type", "topic"),
                body.get("item_key", ""),
                body.get("quality", 4),
                subject_slug=body.get("subject_slug", ""),
                topic_slug=body.get("topic_slug", ""),
            )
            return dict(item=item, state=build_state(conn)), 200
        if path == "/api/revision/skip":
            revision.drop(conn, body.get("item_type", "topic"), body.get("item_key", ""))
            conn.commit()
            return dict(ok=True, items=revision.queue(conn, limit=25)), 200

        # ---- feedback ---------------------------------------------------
        if path == "/api/feedback":
            answer = str(body.get("answer") or "")
            if answer and answer not in feedback.RATING_SIGNAL:
                raise ValueError("Unknown feedback answer: %s" % answer)
            feedback.record(
                conn,
                body.get("target_type", "recommendation"),
                answer,
                target_slug=body.get("target_slug", ""),
                target_id=body.get("target_id", ""),
                rating=body.get("rating"),
                subject_slug=body.get("subject_slug", ""),
                topic_slug=body.get("topic_slug", ""),
                reason=str(body.get("reason") or "")[:500],
                time_spent_s=body.get("time_spent_s", 0),
                completed=body.get("completed"),
                followed=body.get("followed"),
                correction=str(body.get("correction") or "")[:280],
                payload=body.get("payload"),
            )
            return dict(summary=feedback.summary(conn), state=build_state(conn)), 200

        # ---- content ----------------------------------------------------
        if path == "/api/review/approve":
            out = content.promote_review(
                conn, body.get("id"), body.get("patch"), body.get("notes", "")
            )
            return (
                dict(
                    result=out,
                    counts=content.review_counts(conn),
                    bank=content.bank_stats(reload=True),
                ),
                200,
            )
        if path == "/api/review/reject":
            out = content.reject_review(conn, body.get("id"), body.get("notes", ""))
            return dict(result=out, counts=content.review_counts(conn)), 200
        if path == "/api/topics/alias":
            with conn:
                content.remember_alias(
                    conn,
                    body.get("alias", ""),
                    body.get("subject_slug", ""),
                    body.get("topic_slug", ""),
                    body.get("source_slug", ""),
                )
            return dict(ok=True), 200
        if path == "/api/questions/answer":
            q = content.set_answer(
                body.get("id") or "",
                answer=body.get("answer"),
                answer_value=body.get("answer_value"),
                explain=body.get("explain") or "",
                options=body.get("options") or None,
            )
            return (
                dict(
                    question=dict(
                        id=q["id"],
                        type=q["type"],
                        answer=q.get("answer"),
                        answer_value=q.get("answer_value"),
                    ),
                    counts=content.pending_counts(),
                    bank=content.bank_stats(),
                    state=build_state(conn),
                ),
                200,
            )
        if path == "/api/show":
            if SHOW_WINDOW:
                try:
                    SHOW_WINDOW()
                    return dict(shown=True), 200
                except Exception as exc:
                    return dict(shown=False, error=str(exc)), 200
            return dict(shown=False, reason="no window in this instance"), 200
        if path == "/api/bank/reload":
            content.invalidate()
            content.bank_stats(reload=True)
            content.sync_sources(conn)
            content.sync_papers(conn)
            return (
                dict(
                    bank=content.bank_stats(),
                    sources=content.source_summary(conn),
                    papers=content.paper_summary(conn),
                ),
                200,
            )

        # ---- settings ---------------------------------------------------
        if path == "/api/profile":
            return self._save_profile(conn, body), 200
        if path == "/api/settings/ai":
            return self._save_ai(conn, body), 200
        if path == "/api/settings":
            return self._save_prefs(conn, body), 200

        # ---- doubts -----------------------------------------------------
        if path == "/api/doubts/prompt":
            return self._doubt_prompt(conn, body), 200
        if path == "/api/doubts/ask":
            return self._doubt_ask(conn, body), 200
        if path == "/api/doubts/rate":
            out = doubts.rate(
                conn, body.get("id"), bool(body.get("helped")), body.get("note", "")
            )
            return dict(result=out, items=doubts.history(conn, 40)), 200

        # ---- backup -----------------------------------------------------
        if path == "/api/import":
            return self._import(conn, body), 200
        if path == "/api/reset":
            return self._reset(conn, body), 200
        raise LookupError("Unknown endpoint: %s" % path)

    def _delete(self, conn, path):
        if path.startswith("/api/sessions/"):
            with conn:
                conn.execute(
                    "DELETE FROM sessions WHERE id = ?", (int(path.rsplit("/", 1)[-1]),)
                )
            return build_state(conn), 200
        if path.startswith("/api/doubts/"):
            with conn:
                conn.execute(
                    "DELETE FROM doubts WHERE id = ?", (int(path.rsplit("/", 1)[-1]),)
                )
            return dict(items=doubts.history(conn, 40)), 200
        raise LookupError("Unknown endpoint: %s" % path)

    # -- operations ------------------------------------------------------
    def _create_session(self, conn, body):
        subject_id = body.get("subject_id")
        if not subject_id:
            raise ValueError("Pick a subject before saving the session.")
        if not conn.execute(
            "SELECT 1 FROM subjects WHERE id = ?", (int(subject_id),)
        ).fetchone():
            raise ValueError("That subject no longer exists.")

        day = (body.get("day") or date.today().isoformat())[:10]
        try:
            date.fromisoformat(day)
        except ValueError:
            raise ValueError("Date must look like YYYY-MM-DD.")

        minutes = max(0, min(1440, int(body.get("minutes") or 0)))
        if minutes == 0:
            raise ValueError("A session needs some minutes on it.")

        kind = (
            body.get("kind") if body.get("kind") in content.SESSION_KINDS else "concept"
        )
        note = str(body.get("note") or "")[:280]
        hour = body.get("hour")
        try:
            hour = max(0, min(23, int(hour)))
        except (TypeError, ValueError):
            hour = datetime.now().hour

        topic_ids = [int(t) for t in (body.get("topic_ids") or []) if str(t).isdigit()]
        mark_done = bool(body.get("mark_topics_done"))
        now = datetime.now().isoformat(timespec="seconds")

        with conn:
            cur = conn.execute(
                "INSERT INTO sessions (subject_id, day, minutes, kind, note, hour, created_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (int(subject_id), day, minutes, kind, note, hour, now),
            )
            session_id = cur.lastrowid
            subject_slug = conn.execute(
                "SELECT slug FROM subjects WHERE id = ?", (int(subject_id),)
            ).fetchone()["slug"]

            for tid in topic_ids:
                owned = conn.execute(
                    "SELECT slug, name FROM topics WHERE id = ? AND subject_id = ?",
                    (tid, int(subject_id)),
                ).fetchone()
                if not owned:
                    continue
                conn.execute(
                    "INSERT OR IGNORE INTO session_topics (session_id, topic_id) VALUES (?,?)",
                    (session_id, tid),
                )
                new_status = "done" if mark_done else "learning"
                conn.execute(
                    "UPDATE topics SET status = ?, updated_at = ?"
                    " WHERE id = ? AND (status != 'done' OR ? = 'done')",
                    (new_status, now, tid, new_status),
                )
                # Studying a topic enrols it in the revision schedule, and a
                # revision session counts as a review of it.
                revision.enrol_topic(conn, subject_slug, owned["slug"], owned["name"])
                if kind in ("revision", "pyq", "dpp"):
                    revision.review(
                        conn,
                        "topic",
                        "%s/%s" % (subject_slug, owned["slug"]),
                        4,
                        day,
                        subject_slug,
                        owned["slug"],
                        owned["name"],
                    )

        out = dict(session_id=session_id)
        if body.get("with_quiz") and topic_ids:
            bundle = stats.gather(conn)
            built, err = quiz.build_quiz(
                conn,
                subject_id=int(subject_id),
                topic_ids=topic_ids,
                count=body.get("quiz_count", 5),
                session_id=session_id,
                metrics=bundle["metrics"],
                topic_health=bundle["topic_health"],
            )
            out["quiz"] = built
            out["quiz_error"] = err
        out["state"] = build_state(conn)
        return out

    def _set_topic_status(self, conn, body):
        topic_id = body.get("topic_id")
        status = body.get("status")
        if status not in ("pending", "learning", "done"):
            raise ValueError("Status must be pending, learning or done.")
        if not topic_id:
            raise ValueError("No topic given.")
        now = datetime.now().isoformat(timespec="seconds")
        row = conn.execute(
            "SELECT t.slug, t.name, sub.slug AS subject_slug FROM topics t"
            " JOIN subjects sub ON sub.id = t.subject_id WHERE t.id = ?",
            (int(topic_id),),
        ).fetchone()
        with conn:
            conn.execute(
                "UPDATE topics SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, int(topic_id)),
            )
            if row and status in ("learning", "done"):
                revision.enrol_topic(conn, row["subject_slug"], row["slug"], row["name"])
            elif row:
                revision.drop(conn, "topic", "%s/%s" % (row["subject_slug"], row["slug"]))
        return build_state(conn)

    def _set_topic_confidence(self, conn, body):
        topic_id = body.get("topic_id")
        try:
            value = max(1, min(5, int(body.get("confidence"))))
        except (TypeError, ValueError):
            raise ValueError("Confidence must be 1 to 5.")
        with conn:
            conn.execute(
                "UPDATE topics SET confidence = ? WHERE id = ?", (value, int(topic_id))
            )
        return build_state(conn)

    def _subject_detail(self, conn, subject_id):
        row = conn.execute(
            "SELECT * FROM subjects WHERE id = ?", (subject_id,)
        ).fetchone()
        if not row:
            raise LookupError("Subject not found.")
        settings = db.get_settings(conn)
        target = max(30, db.setting_int(settings, "daily_target_mins", 240) // 3)

        sessions = conn.execute(
            "SELECT * FROM sessions WHERE subject_id = ? ORDER BY day DESC, id DESC LIMIT 200",
            (subject_id,),
        ).fetchall()
        per_day, per_day_q = {}, {}
        for s in conn.execute(
            "SELECT day, minutes FROM sessions WHERE subject_id = ?", (subject_id,)
        ):
            per_day[s["day"]] = per_day.get(s["day"], 0) + s["minutes"]
        for a in conn.execute(
            "SELECT day, COUNT(*) n FROM attempts WHERE subject_slug = ? GROUP BY day",
            (row["slug"],),
        ):
            per_day_q[a["day"]] = a["n"]

        out_sessions = []
        for s in sessions:
            topics = [
                t["name"]
                for t in conn.execute(
                    "SELECT t.name FROM session_topics st JOIN topics t ON t.id = st.topic_id"
                    " WHERE st.session_id = ?",
                    (s["id"],),
                )
            ]
            item = dict(s)
            item["topics"] = topics
            out_sessions.append(item)

        bundle = stats.gather(conn)
        subject = next((x for x in bundle["subjects"] if x["id"] == subject_id), None)
        health = [r for r in bundle["topic_health"] if r["subject_id"] == subject_id]
        return dict(
            subject=subject or dict(row),
            calendar=stats.build_calendar(per_day, per_day_q, target),
            sessions=out_sessions,
            health=health,
            revision=[
                i
                for i in revision.queue(conn, limit=200)
                if i["subject_slug"] == row["slug"]
            ],
        )

    def _save_profile(self, conn, body):
        allowed = (
            "display_name",
            "handle",
            "bio",
            "location",
            "exam_name",
            "exam_date",
            "daily_target_mins",
            "primary_target",
            "avatar",
            "social_github",
            "social_linkedin",
            "social_x",
            "social_website",
        )
        with conn:
            for key in allowed:
                if key in body:
                    db.put_setting(conn, key, body[key])
        return build_state(conn)

    def _save_prefs(self, conn, body):
        with conn:
            for key, (kind, lo, hi) in TUNABLE.items():
                if key not in body:
                    continue
                if kind == "bool":
                    db.put_setting(conn, key, 1 if body[key] else 0)
                else:
                    try:
                        db.put_setting(conn, key, max(lo, min(hi, int(body[key]))))
                    except (TypeError, ValueError):
                        raise ValueError(
                            "%s must be a number between %d and %d." % (key, lo, hi)
                        )
        return build_state(conn)

    def _save_ai(self, conn, body):
        with conn:
            for key in ("ai_provider", "ai_model", "ai_key", "ollama_url"):
                if key in body:
                    db.put_setting(conn, key, body[key])
        return doubts.status(conn)

    def _doubt_prompt(self, conn, body):
        text = str(body.get("body") or "").strip()
        if not text:
            raise ValueError("Write the doubt first - even one line is enough.")
        prompt = doubts.build_prompt(
            conn,
            text,
            subject_slug=body.get("subject_slug", ""),
            topic_slug=body.get("topic_slug", ""),
            question_id=body.get("question_id", ""),
        )
        qtext = ""
        if body.get("question_id"):
            q = content.question_bank().get(body["question_id"])
            if q:
                qtext = q.get("text", "")
        return dict(
            prompt=prompt,
            links=doubts.handoff_links(prompt, qtext),
            status=doubts.status(conn),
        )

    def _doubt_ask(self, conn, body):
        text = str(body.get("body") or "").strip()
        if not text:
            raise ValueError("Write the doubt first.")
        prompt = body.get("prompt") or doubts.build_prompt(
            conn,
            text,
            subject_slug=body.get("subject_slug", ""),
            topic_slug=body.get("topic_slug", ""),
            question_id=body.get("question_id", ""),
        )
        answer, provider = doubts.answer_inline(conn, prompt)
        doubt_id = doubts.save(
            conn,
            text,
            body.get("subject_slug", ""),
            body.get("topic_slug", ""),
            body.get("question_id", ""),
            prompt,
            provider,
            answer,
        )
        return dict(
            id=doubt_id, answer=answer, provider=provider, items=doubts.history(conn, 40)
        )

    # -- backup ----------------------------------------------------------
    EXPORT_TABLES = (
        "subjects",
        "topics",
        "sessions",
        "session_topics",
        "quizzes",
        "attempts",
        "daily_question",
        "readiness_log",
        "unlocked",
        "doubts",
        "settings",
        "question_sources",
        "question_tags",
        "question_imports",
        "question_review",
        "question_stats",
        "topic_alias",
        "revision_queue",
        "topic_prerequisites",
        "user_goals",
        "daily_plans",
        "dpp_sets",
        "recommendations",
        "feedback",
        "learned_weights",
    )

    def _export(self, conn):
        dump = {}
        for t in self.EXPORT_TABLES:
            if not db._table_exists(conn, t):
                continue
            dump[t] = [dict(r) for r in conn.execute("SELECT * FROM %s" % t)]
        # Never write the API key into a file the user might share.
        for row in dump.get("settings", []):
            if row.get("key") == "ai_key":
                row["value"] = ""
        return dict(
            version=1,
            schema_version=db.current_version(conn),
            exported_at=datetime.now().isoformat(timespec="seconds"),
            tables=dump,
        )

    def _import(self, conn, body):
        tables = body.get("tables")
        if not isinstance(tables, dict):
            raise ValueError("That file does not look like a GitGrind backup.")
        order = [t for t in self.EXPORT_TABLES if db._table_exists(conn, t)]
        with conn:
            for t in reversed(order):
                conn.execute("DELETE FROM %s" % t)
            for t in order:
                rows = tables.get(t) or []
                if not rows:
                    continue
                cols = [c["name"] for c in conn.execute("PRAGMA table_info(%s)" % t)]
                use = [c for c in cols if c in rows[0]]
                if not use:
                    continue
                sql = "INSERT OR REPLACE INTO %s (%s) VALUES (%s)" % (
                    t,
                    ",".join(use),
                    ",".join("?" * len(use)),
                )
                conn.executemany(sql, [tuple(r.get(c) for c in use) for r in rows])
        content.seed(conn)
        # A backup taken on an older bank references ids that no longer exist, so
        # the history would import intact and then read as empty on every
        # per-topic view. Reconnect it here rather than leaving the person to
        # conclude the import lost their data.
        repair = content.remap_orphaned_question_ids(conn)
        state = build_state(conn)
        state["import_repair"] = repair
        return state

    def _reset(self, conn, body):
        scope = body.get("scope", "activity")
        with conn:
            for t in (
                "session_topics",
                "sessions",
                "attempts",
                "quizzes",
                "daily_question",
                "readiness_log",
                "unlocked",
                "question_stats",
                "revision_queue",
                "daily_plans",
                "dpp_sets",
                "recommendations",
            ):
                conn.execute("DELETE FROM %s" % t)
            if scope == "all":
                conn.execute(
                    "UPDATE topics SET status = 'pending', updated_at = NULL,"
                    " confidence = NULL, last_revised = NULL"
                )
                conn.execute("DELETE FROM doubts")
                conn.execute("DELETE FROM feedback")
                conn.execute("DELETE FROM learned_weights")
        return build_state(conn)
