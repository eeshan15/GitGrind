#!/usr/bin/env python3
"""Browser pass: seeds realistic data, walks every tab, captures console errors.

    python tools/browsercheck.py

Needs playwright. Writes screenshots to /tmp/gg-shots.
"""

import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PORT = 8733
BASE = "http://127.0.0.1:%d" % PORT
SHOTS = "/tmp/gg-shots"


def api(path, method="GET", body=None):
    req = urllib.request.Request(
        BASE + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def seed():
    """Six months of plausible activity so every panel has something to draw."""
    from core import content

    bank = content.question_bank()
    state = api("/api/state")
    subjects = state["subjects"]
    rng = random.Random(4242)
    kinds = ["concept", "concept", "revision", "pyq", "dpp", "mock", "notes"]

    api(
        "/api/profile",
        "POST",
        dict(
            display_name="Eeshan Bablani",
            handle="eeshan-gate",
            bio="GATE CSE 2027. Target: BARC OCES plus DGFS at IIT Bombay.",
            location="Jaipur, India",
            exam_name="GATE CSE",
            exam_date=(date.today() + timedelta(days=196)).isoformat(),
            daily_target_mins=240,
            primary_target="dgfs-iitb",
        ),
    )

    today = date.today()
    logged = 0
    for back in range(184, -1, -1):
        d = today - timedelta(days=back)
        # a couple of realistic gaps
        if 96 <= back <= 103 or 41 <= back <= 44:
            continue
        if rng.random() < 0.13:
            continue
        n = 1 if rng.random() < 0.62 else 2
        for _ in range(n):
            s = rng.choices(subjects, weights=[x["marks"] for x in subjects])[0]
            tids = [t["id"] for t in s["topics"]]
            pick = rng.sample(tids, min(len(tids), rng.randint(1, 2))) if tids else []
            api(
                "/api/sessions",
                "POST",
                dict(
                    subject_id=s["id"],
                    day=d.isoformat(),
                    minutes=rng.choice([45, 60, 75, 90, 120, 150, 180]),
                    kind=rng.choice(kinds),
                    hour=rng.choice([6, 7, 9, 11, 15, 18, 21, 22]),
                    note=rng.choice(
                        [
                            "",
                            "",
                            "worked through the standard problems",
                            "revisited the derivation",
                            "PYQ set from 2019-2023",
                        ]
                    ),
                    topic_ids=pick,
                    mark_topics_done=rng.random() < 0.55,
                    with_quiz=False,
                ),
            )
            logged += 1

    # practice sets with mixed accuracy
    for _ in range(26):
        s = rng.choice(subjects)
        try:
            quiz = api("/api/quiz", "POST", dict(subject_id=s["id"], count=5))
        except Exception:
            continue
        responses = []
        for q in quiz["questions"]:
            real = bank[q["id"]]
            good = rng.random() < 0.64
            if real["type"] == "nat":
                v = (
                    real.get("answer_value")
                    if good
                    else float(real.get("answer_value", 0)) + 7
                )
            else:
                key = real.get("answer", [0])
                if good:
                    v = key
                else:
                    others = [
                        i for i in range(len(real.get("options", [0, 1]))) if i not in key
                    ]
                    v = others[:1] or [0]
            responses.append(dict(question_id=q["id"], response=v))
        api(
            "/api/quiz/%d/submit" % quiz["id"],
            "POST",
            dict(responses=responses, duration_s=380),
        )

    return logged


def main():
    from playwright.sync_api import sync_playwright

    shutil.rmtree(SHOTS, ignore_errors=True)
    os.makedirs(SHOTS, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="gg-bc-")
    real_data = os.path.join(ROOT, "data")
    os.makedirs(real_data, exist_ok=True)
    backup = os.path.join(tmp, "bk")
    os.makedirs(backup)
    for f in os.listdir(real_data):
        if f.startswith("gitgrind.db"):
            shutil.move(os.path.join(real_data, f), os.path.join(backup, f))

    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=ROOT,
        env=dict(
            os.environ,
            GITGRIND_NO_BROWSER="1",
            GITGRIND_PORT=str(PORT),
            GITGRIND_VERBOSE="1",
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    problems = []
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(BASE + "/api/bank", timeout=2)
                break
            except Exception:
                time.sleep(0.4)

        print("seeding activity...")
        t0 = time.time()
        n = seed()
        print("  %d sessions + 26 quizzes in %.1fs" % (n, time.time() - t0))

        st = api("/api/state")
        m = st["metrics"]
        print("\n-- seeded profile --")
        print(
            "  active days   :",
            m["active_days"],
            "| streak",
            m["current_streak"],
            "| longest",
            m["longest_streak"],
        )
        print("  hours         :", m["total_hours"])
        print(
            "  topics closed :",
            m["topics_done"],
            "/",
            m["topics_total"],
            "| coverage",
            m["coverage_pct"],
            "%",
        )
        print(
            "  questions     :",
            m["questions_attempted"],
            "| accuracy",
            m["accuracy"],
            "%",
        )
        print(
            "  badges        :",
            sum(1 for a in st["achievements"] if a["unlocked"]),
            "/",
            len(st["achievements"]),
        )
        r = st["readiness"]
        print(
            "  readiness     : %.1f -> est score %.0f | percentile %.2f"
            % (r["index"], r["est_score"], r["position"]["percentile"])
        )
        for t in r["targets"]:
            if t["comparable"]:
                print(
                    "     %-28s cutoff %4d  you %4d  gap %6.1f"
                    % (t["name"], t["cutoff"], t["your_value"], t["gap"])
                )

        def go(url):
            """Navigate and wait the intro splash out - it covers the viewport
            for six seconds and swallows every click until it is gone."""
            go(url, wait_until="networkidle")
            try:
                page.wait_for_selector("#splash", state="detached", timeout=12000)
            except Exception:
                pass

        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.on(
                "console",
                lambda msg: (
                    problems.append(("console." + msg.type, msg.text))
                    if msg.type in ("error", "warning")
                    else None
                ),
            )
            page.on("pageerror", lambda e: problems.append(("pageerror", str(e))))

            go(BASE, wait_until="networkidle")
            try:
                page.wait_for_selector("#splash", state="detached", timeout=12000)
            except Exception:
                pass
            page.wait_for_timeout(1400)

            views = [
                "overview",
                "subjects",
                "practice",
                "readiness",
                "achievements",
                "doubts",
                "activity",
            ]
            for v in views:
                go(BASE + "/#/" + v, wait_until="networkidle")
                page.wait_for_timeout(1100)
                page.screenshot(path=os.path.join(SHOTS, "%s.png" % v), full_page=True)
                print("  shot: %s" % v)

            # expand a subject to expose the topic checkboxes
            go(BASE + "/#/subjects", wait_until="networkidle")
            page.wait_for_timeout(700)
            page.click(".subj-head")
            page.wait_for_timeout(600)
            page.screenshot(
                path=os.path.join(SHOTS, "subjects-topics.png"), full_page=True
            )
            print("  shot: subjects-topics")

            # subject detail
            first_id = st["subjects"][0]["id"]
            go(BASE + "/#/subject/%d" % first_id, wait_until="networkidle")
            page.wait_for_timeout(1100)
            page.screenshot(path=os.path.join(SHOTS, "detail.png"), full_page=True)
            print("  shot: detail")

            # session log modal with topic picker
            go(BASE + "/#/overview", wait_until="networkidle")
            page.wait_for_timeout(600)
            page.click("#btnLog")
            page.wait_for_timeout(600)
            picked = page.locator("#fTopics .tp").count()
            page.locator("#fTopics .tp").first.click()
            page.wait_for_timeout(250)
            page.screenshot(path=os.path.join(SHOTS, "modal-log.png"))
            print("  shot: modal-log  (%d topic chips)" % picked)
            if picked == 0:
                problems.append(("ui", "log modal rendered no topic chips"))

            # commit it and catch the auto quiz
            page.fill("#fMinutes", "95")
            page.click("#saveLog")
            page.wait_for_timeout(2200)
            quiz_open = page.locator("#modalQuiz").is_visible()
            print("  auto quiz opened after session:", quiz_open)
            if not quiz_open:
                problems.append(("ui", "session-end quiz did not open"))
            else:
                page.screenshot(path=os.path.join(SHOTS, "modal-quiz.png"))
                print("  shot: modal-quiz")
                # answer everything then submit
                count = page.locator(".qn").count()
                for i in range(count):
                    page.locator(".qn").nth(i).click()
                    page.wait_for_timeout(180)
                    if page.locator(".opt").count():
                        page.locator(".opt").first.click()
                    elif page.locator(".nat-input input").count():
                        page.fill(".nat-input input", "12")
                    page.wait_for_timeout(150)
                page.click("#quizFoot .btn-primary")
                page.wait_for_timeout(2200)
                page.screenshot(
                    path=os.path.join(SHOTS, "quiz-result.png"), full_page=True
                )
                print("  shot: quiz-result")
                has_peer = page.locator(".peer-box").count() > 0
                sim_label = (
                    page.locator(".peer-box .state-key").inner_text() if has_peer else ""
                )
                print("  peer curve shown:", has_peer, "| label:", sim_label)
                if not has_peer:
                    problems.append(("ui", "peer curve missing from results"))
                page.click("#quizFoot .btn-primary")
                page.wait_for_timeout(500)

            # doubt desk prompt build
            go(BASE + "/#/doubts", wait_until="networkidle")
            page.wait_for_timeout(800)
            page.fill(
                "#dBody", "Why does SRTF give a lower average waiting time than SJF?"
            )
            page.click("#dBuild")
            page.wait_for_timeout(1600)
            has_prompt = page.locator(".prompt-box").count() > 0
            links = page.locator("#dResult .prov").count()
            print("  doubt prompt built:", has_prompt, "| handoff links:", links)
            if not has_prompt or links < 5:
                problems.append(("ui", "doubt prompt or links missing"))
            page.screenshot(path=os.path.join(SHOTS, "doubts-prompt.png"), full_page=True)
            print("  shot: doubts-prompt")

            # mobile
            page.set_viewport_size({"width": 400, "height": 900})
            for v in ("overview", "readiness", "subjects"):
                go(BASE + "/#/" + v, wait_until="networkidle")
                page.wait_for_timeout(900)
                page.screenshot(
                    path=os.path.join(SHOTS, "mobile-%s.png" % v), full_page=True
                )
                print("  shot: mobile-%s" % v)

            browser.close()

        print("\n-- console --")
        if problems:
            for kind, text in problems[:25]:
                print("  [%s] %s" % (kind, text[:190]))
        else:
            print("  clean: no errors or warnings")
        print("\nscreenshots in %s" % SHOTS)
        return 1 if problems else 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        for f in list(os.listdir(real_data)):
            if f.startswith("gitgrind.db"):
                os.remove(os.path.join(real_data, f))
        for f in os.listdir(backup):
            shutil.move(os.path.join(backup, f), os.path.join(real_data, f))
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
