"""Doubt desk - getting a doubt answered without paying for an API.

Three routes, in order of how little they cost you:

  1. HANDOFF (default, zero setup, zero cost)
     Builds a properly structured prompt with your syllabus context and hands it
     to a free web chat or search you already have access to. Nothing is sent
     from this machine - the link opens in your browser and you stay logged in
     with your own free account.

  2. OLLAMA (zero cost, one-time install, works offline)
     If Ollama is running locally, the tracker talks to it directly and shows the
     answer inline. Detection is automatic. Suggested small models that run on a
     modest laptop are listed in SUGGESTED_MODELS.

  3. HOSTED KEY (optional)
     If you ever get a free-tier key from Groq, Google AI Studio or OpenRouter,
     paste it in settings and answers appear inline. The key is stored in your
     local database and used only for these calls.

Route 1 needs nothing but a browser. Routes 2 and 3 are conveniences.

A doubt is also a signal. Once an answer has been read, the desk asks whether it
helped, and later notices whether the same concept was attempted again and got
right. Both land in the feedback table and feed recommendation ranking: a topic
you keep asking about is a topic the planner should be pushing at you, and a
"did not help" answer should not raise your confidence in that topic.

If a local or hosted model is used it only rephrases and explains. It never
decides what you should study - that stays with recommend.py, which is rules
over your own logs.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

from . import content, db, feedback

TIMEOUT = 60

SUGGESTED_MODELS = [
    dict(name="qwen2.5:3b", size="~2 GB", note="Fastest useful option on 8 GB RAM"),
    dict(name="llama3.2:3b", size="~2 GB", note="Good general explanations"),
    dict(
        name="qwen2.5:7b", size="~4.7 GB", note="Noticeably better at maths, needs 16 GB"
    ),
    dict(name="deepseek-r1:7b", size="~4.7 GB", note="Shows reasoning steps, slower"),
]

HANDOFF_TARGETS = [
    dict(
        slug="chatgpt",
        name="ChatGPT",
        url="https://chatgpt.com/?q={q}",
        note="Free tier. Prompt is pre-filled in the URL.",
        prefill=True,
    ),
    dict(
        slug="claude",
        name="Claude",
        url="https://claude.ai/new?q={q}",
        note="Free tier. Prompt is pre-filled in the URL.",
        prefill=True,
    ),
    dict(
        slug="perplexity",
        name="Perplexity",
        url="https://www.perplexity.ai/search?q={q}",
        note="Free, cites sources. Good for checking a formula.",
        prefill=True,
    ),
    dict(
        slug="duckduckgo",
        name="DuckDuckGo AI Chat",
        url="https://duckduckgo.com/?q={q}&ia=chat",
        note="No account needed at all.",
        prefill=True,
    ),
    dict(
        slug="gateoverflow",
        name="GATE Overflow",
        url="https://gateoverflow.in/search?q={q}",
        note="Human answers from GATE aspirants. Search the question text itself.",
        prefill=True,
        short_query=True,
    ),
    dict(
        slug="gemini",
        name="Google Gemini",
        url="https://gemini.google.com/app",
        note="Free tier, but does not accept a pre-filled prompt. Copy the prompt first.",
        prefill=False,
    ),
]

PROMPT_TEMPLATE = """You are helping a GATE CSE aspirant. Be precise and brief.

Subject: {subject}
Topic: {topic}
Their target: {target}
{question_block}
Their doubt:
{body}

Answer in this structure:
1. Direct answer in two sentences.
2. The reasoning, step by step, showing every formula used.
3. The single mistake most students make here.
4. One GATE-style follow-up question to test whether the idea landed, with the answer hidden at the very end.

Use plain text. No markdown tables. Keep it under 400 words."""


def build_prompt(conn, body, subject_slug="", topic_slug="", question_id=""):
    subject_name = subject_slug or "not specified"
    topic_name = topic_slug or "not specified"

    if subject_slug:
        row = conn.execute(
            "SELECT name FROM subjects WHERE slug = ?", (subject_slug,)
        ).fetchone()
        if row:
            subject_name = row["name"]
    if topic_slug:
        row = conn.execute(
            "SELECT name FROM topics WHERE slug = ? LIMIT 1", (topic_slug,)
        ).fetchone()
        if row:
            topic_name = row["name"]

    settings = db.get_settings(conn)
    targets = {t["slug"]: t for t in content.targets().get("targets", [])}
    primary = targets.get(settings.get("primary_target", ""), {})
    target_line = primary.get("name", settings.get("exam_name", "GATE CSE"))

    question_block = ""
    if question_id:
        q = content.question_bank().get(question_id)
        if q:
            lines = ["", "The question they are stuck on:", q.get("text", "")]
            for i, opt in enumerate(q.get("options", [])):
                lines.append("  (%s) %s" % (chr(65 + i), opt))
            lines.append("")
            question_block = "\n".join(lines)

    return PROMPT_TEMPLATE.format(
        subject=subject_name,
        topic=topic_name,
        target=target_line,
        question_block=question_block,
        body=body.strip() or "(no detail given)",
    )


def handoff_links(prompt, question_text=""):
    out = []
    for t in HANDOFF_TARGETS:
        if not t.get("prefill"):
            out.append(dict(t, ready_url=t["url"]))
            continue
        payload = question_text if t.get("short_query") and question_text else prompt
        encoded = urllib.parse.quote(payload[:1800])
        out.append(dict(t, ready_url=t["url"].format(q=encoded)))
    return out


# ---------------------------------------------------------------------------
# local Ollama
# ---------------------------------------------------------------------------
def _get_json(url, timeout=4):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def probe_ollama(base_url):
    base = (base_url or "http://127.0.0.1:11434").rstrip("/")
    try:
        data = _get_json(base + "/api/tags")
    except (urllib.error.URLError, OSError, ValueError, TimeoutError) as exc:
        return dict(
            available=False,
            base_url=base,
            reason=str(exc),
            install_hint="Install from ollama.com, then run: ollama pull qwen2.5:3b",
            suggested=SUGGESTED_MODELS,
        )
    models = [m.get("name", "") for m in (data.get("models") or [])]
    return dict(
        available=True,
        base_url=base,
        models=models,
        suggested=SUGGESTED_MODELS,
        note=(
            "Running locally. No data leaves this machine and there is no cost."
            if models
            else "Ollama is running but has no models. Run: ollama pull qwen2.5:3b"
        ),
    )


def ask_ollama(base_url, model, prompt):
    base = (base_url or "http://127.0.0.1:11434").rstrip("/")
    payload = json.dumps(dict(model=model, prompt=prompt, stream=False)).encode("utf-8")
    req = urllib.request.Request(
        base + "/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT * 3) as resp:
        data = json.load(resp)
    return (data.get("response") or "").strip()


# ---------------------------------------------------------------------------
# optional hosted providers (free tiers)
# ---------------------------------------------------------------------------
HOSTED = {
    "groq": dict(
        label="Groq",
        signup="https://console.groq.com/keys",
        default_model="llama-3.3-70b-versatile",
        note="Generous free tier, very fast.",
    ),
    "gemini": dict(
        label="Google AI Studio",
        signup="https://aistudio.google.com/apikey",
        default_model="gemini-2.0-flash",
        note="Free tier with a daily request cap.",
    ),
    "openrouter": dict(
        label="OpenRouter",
        signup="https://openrouter.ai/keys",
        default_model="meta-llama/llama-3.3-70b-instruct:free",
        note="Aggregator. Models ending in :free cost nothing.",
    ),
}


def _post_json(url, payload, headers, timeout=TIMEOUT):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=dict({"Content-Type": "application/json"}, **headers),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def ask_hosted(provider, key, model, prompt):
    if provider not in HOSTED:
        raise ValueError("Unknown provider: %s" % provider)
    if not key:
        raise ValueError("No API key saved for %s." % HOSTED[provider]["label"])
    model = model or HOSTED[provider]["default_model"]

    if provider == "gemini":
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "%s:generateContent?key=%s" % (model, urllib.parse.quote(key))
        )
        data = _post_json(url, dict(contents=[dict(parts=[dict(text=prompt)])]), {})
        cands = data.get("candidates") or []
        if not cands:
            raise ValueError("The model returned no candidates.")
        parts = (cands[0].get("content") or {}).get("parts") or []
        return "".join(p.get("text", "") for p in parts).strip()

    url = {
        "groq": "https://api.groq.com/openai/v1/chat/completions",
        "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    }[provider]
    data = _post_json(
        url,
        dict(model=model, messages=[dict(role="user", content=prompt)], max_tokens=1200),
        {"Authorization": "Bearer %s" % key},
    )
    choices = data.get("choices") or []
    if not choices:
        raise ValueError("The model returned no choices.")
    return (choices[0].get("message") or {}).get("content", "").strip()


# ---------------------------------------------------------------------------
# orchestration
# ---------------------------------------------------------------------------
def status(conn):
    settings = db.get_settings(conn)
    provider = settings.get("ai_provider", "none")
    ollama = probe_ollama(settings.get("ollama_url"))
    return dict(
        provider=provider,
        model=settings.get("ai_model", ""),
        has_key=bool(settings.get("ai_key")),
        ollama=ollama,
        hosted={
            k: dict(v, configured=(provider == k and bool(settings.get("ai_key"))))
            for k, v in HOSTED.items()
        },
        inline_available=ollama.get("available")
        or (provider in HOSTED and bool(settings.get("ai_key"))),
    )


def answer_inline(conn, prompt):
    """Try whatever is configured. Returns (answer, provider_used)."""
    settings = db.get_settings(conn)
    provider = settings.get("ai_provider", "none")

    if provider in HOSTED and settings.get("ai_key"):
        return (
            ask_hosted(provider, settings["ai_key"], settings.get("ai_model"), prompt),
            provider,
        )

    if provider in ("ollama", "none", "", None):
        probe = probe_ollama(settings.get("ollama_url"))
        if probe.get("available") and probe.get("models"):
            model = settings.get("ai_model") or probe["models"][0]
            return ask_ollama(settings.get("ollama_url"), model, prompt), "ollama"
        if provider == "ollama":
            raise ValueError(
                "Ollama is not reachable at %s. Start it, or use the handoff links below "
                "which need no setup." % probe.get("base_url")
            )

    raise ValueError(
        "No inline answer source is configured. Use the handoff links below - they are "
        "free and need no key - or install Ollama for inline answers."
    )


def save(
    conn, body, subject_slug, topic_slug, question_id, prompt, provider="", answer=""
):
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        cur = conn.execute(
            "INSERT INTO doubts (subject_slug, topic_slug, question_id, body, prompt,"
            " provider, answer, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (
                subject_slug or "",
                topic_slug or "",
                question_id or "",
                body,
                prompt,
                provider,
                answer,
                now,
            ),
        )
        return cur.lastrowid


def rate(conn, doubt_id, helped, note=""):
    """Record whether the answer actually helped, and feed it to the ranker."""
    row = conn.execute("SELECT * FROM doubts WHERE id = ?", (int(doubt_id),)).fetchone()
    if not row:
        raise LookupError("That doubt is not in the log.")
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute(
            "UPDATE doubts SET helped = ?, resolved = ?, resolved_at = ? WHERE id = ?",
            (
                1 if helped else 0,
                1 if helped else 0,
                now if helped else None,
                int(doubt_id),
            ),
        )
    feedback.record(
        conn,
        "doubt",
        "helped" if helped else "did_not_help",
        target_id=str(doubt_id),
        target_slug="doubt",
        subject_slug=row["subject_slug"],
        topic_slug=row["topic_slug"],
        reason=note[:280],
    )
    return dict(id=int(doubt_id), helped=bool(helped))


def check_retries(conn):
    """Mark a doubt as revisited once the topic has been attempted again.

    This is the delayed half of the signal: "did the explanation stick" is a
    better measure than "did it feel good at the time".
    """
    now = datetime.now().isoformat(timespec="seconds")
    rows = conn.execute(
        "SELECT id, topic_slug, created_at FROM doubts"
        " WHERE retried_at IS NULL AND topic_slug != ''"
    ).fetchall()
    touched = 0
    with conn:
        for r in rows:
            hit = conn.execute(
                "SELECT 1 FROM attempts WHERE topic_slug = ? AND created_at > ?"
                " AND correct = 1 LIMIT 1",
                (r["topic_slug"], r["created_at"]),
            ).fetchone()
            if hit:
                conn.execute(
                    "UPDATE doubts SET retried_at = ? WHERE id = ?", (now, r["id"])
                )
                touched += 1
    return touched


def topic_pressure(conn, days=60):
    """Topics you keep asking about. A useful weak-topic signal on its own."""
    from datetime import timedelta

    since = (datetime.now() - timedelta(days=days)).isoformat(timespec="seconds")
    rows = conn.execute(
        "SELECT subject_slug, topic_slug, COUNT(*) n,"
        " SUM(COALESCE(helped, 0)) helped, SUM(retried_at IS NOT NULL) retried"
        " FROM doubts WHERE created_at >= ? AND topic_slug != ''"
        " GROUP BY subject_slug, topic_slug HAVING n >= 2 ORDER BY n DESC LIMIT 8",
        (since,),
    ).fetchall()
    return [
        dict(
            subject=r["subject_slug"],
            topic=r["topic_slug"],
            asked=r["n"],
            helped=r["helped"],
            retried=r["retried"],
            unresolved=r["n"] - r["helped"],
        )
        for r in rows
    ]


def history(conn, limit=30):
    rows = conn.execute(
        "SELECT * FROM doubts ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["helped"] = None if r["helped"] is None else bool(r["helped"])
        item["retried"] = bool(r["retried_at"])
        out.append(item)
    return out
