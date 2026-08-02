"""SQLite connection handling, schema and versioned migrations.

This module owns every table in GitGrind. Two things live here:

* ``SCHEMA``  - the base tables that existed in v2. Still created with
  ``IF NOT EXISTS`` so a fresh install works in one shot.
* ``MIGRATIONS`` - an ordered list of upgrade steps. Each step has a version
  number and a list of statements. The applied version is recorded in the
  ``schema_meta`` table, so an old ``data/gitgrind.db`` upgrades in place
  without losing a single logged minute.

Adding a table or a column means appending a new migration. Never edit an old
one: someone's database has already run it.
"""

import os
import sqlite3
import sys
import threading

# --------------------------------------------------------------------------
# Where things live.
#
# Running from source these are all the same folder. Inside a PyInstaller or
# Nuitka build they are not, and getting this wrong is fatal: the bundle is
# unpacked into a temporary directory that is deleted on exit, so anything
# written there (your database, any answer you looked up) would vanish every
# time you closed the app.
#
#   ASSET_DIR  read-only, inside the bundle: static/ and the shipped content/
#   APP_DIR    writable, next to the executable: data/ and your edited content/
# --------------------------------------------------------------------------
FROZEN = bool(getattr(sys, "frozen", False))
ASSET_DIR = getattr(sys, "_MEIPASS", None) or os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


def _writable(path):
    """Can we actually create files here? Program Files says no."""
    try:
        os.makedirs(path, exist_ok=True)
        probe = os.path.join(path, ".gitgrind-write-test")
        with open(probe, "w") as fh:
            fh.write("ok")
        os.remove(probe)
        return True
    except OSError:
        return False


def _pick_app_dir():
    """Where the database and the editable content/ should live.

    Normally this is the folder holding the executable, which keeps the app and
    its data together and makes backing up a matter of copying one folder. But a
    packaged app is often dropped somewhere unwritable - Program Files, a
    read-only share, a locked-down work machine - and silently failing to save a
    session is the worst possible outcome. So probe first, and fall back to the
    per-user application data folder when the exe's own folder is not writable.
    """
    if not FROZEN:
        return ASSET_DIR

    beside_exe = os.path.dirname(os.path.abspath(sys.executable))
    if _writable(beside_exe):
        return beside_exe

    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        root = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        root = os.environ.get("XDG_DATA_HOME") or os.path.join(
            os.path.expanduser("~"), ".local", "share"
        )

    fallback = os.path.join(root, "GitGrind")
    if _writable(fallback):
        return fallback

    # Last resort: the home directory. If even this fails the app will report the
    # error on startup rather than pretending to work.
    return os.path.join(os.path.expanduser("~"), "GitGrind")


APP_DIR = _pick_app_dir()

# BASE_DIR stays the name every other module already uses, and always points at
# the writable root.
BASE_DIR = APP_DIR
DATA_DIR = os.path.join(BASE_DIR, "data")
# GITGRIND_DB lets tools and tests point at a different file without touching
# the real one. Unset, it is the normal location next to the app.
DB_PATH = os.environ.get("GITGRIND_DB") or os.path.join(DATA_DIR, "gitgrind.db")

# One writer at a time. SQLite handles the rest.
LOCK = threading.RLock()

SCHEMA_VERSION = 8

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subjects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slug        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    grp         TEXT NOT NULL DEFAULT 'core',
    marks       INTEGER NOT NULL DEFAULT 5,
    target_mins INTEGER NOT NULL DEFAULT 3000,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    archived    INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS topics (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    slug       TEXT NOT NULL,
    name       TEXT NOT NULL,
    weight     INTEGER NOT NULL DEFAULT 1,
    status     TEXT NOT NULL DEFAULT 'pending',
    sort_order INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT,
    UNIQUE (subject_id, slug)
);
CREATE INDEX IF NOT EXISTS idx_topics_subject ON topics(subject_id);

CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    day        TEXT NOT NULL,
    minutes    INTEGER NOT NULL DEFAULT 0,
    kind       TEXT NOT NULL DEFAULT 'concept',
    note       TEXT NOT NULL DEFAULT '',
    hour       INTEGER NOT NULL DEFAULT 12,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_day ON sessions(day);
CREATE INDEX IF NOT EXISTS idx_sessions_subject ON sessions(subject_id);

CREATE TABLE IF NOT EXISTS session_topics (
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    topic_id   INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    PRIMARY KEY (session_id, topic_id)
);

CREATE TABLE IF NOT EXISTS quizzes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source        TEXT NOT NULL DEFAULT 'session',
    subject_id    INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    session_id    INTEGER REFERENCES sessions(id) ON DELETE SET NULL,
    day           TEXT NOT NULL,
    topic_slugs   TEXT NOT NULL DEFAULT '',
    total_marks   INTEGER NOT NULL DEFAULT 0,
    scored_marks  REAL NOT NULL DEFAULT 0,
    question_count INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    duration_s    INTEGER NOT NULL DEFAULT 0,
    finished_at   TEXT,
    created_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_quizzes_day ON quizzes(day);

CREATE TABLE IF NOT EXISTS attempts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id     INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL,
    subject_slug TEXT NOT NULL DEFAULT '',
    topic_slug  TEXT NOT NULL DEFAULT '',
    source      TEXT NOT NULL DEFAULT 'quiz',
    response    TEXT NOT NULL DEFAULT '',
    correct     INTEGER NOT NULL DEFAULT 0,
    marks_total REAL NOT NULL DEFAULT 0,
    marks_got   REAL NOT NULL DEFAULT 0,
    day         TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attempts_day ON attempts(day);
CREATE INDEX IF NOT EXISTS idx_attempts_topic ON attempts(topic_slug);

CREATE TABLE IF NOT EXISTS daily_question (
    day         TEXT PRIMARY KEY,
    question_id TEXT NOT NULL,
    reason      TEXT NOT NULL DEFAULT '',
    served_at   TEXT NOT NULL,
    answered_at TEXT,
    response    TEXT,
    correct     INTEGER
);

CREATE TABLE IF NOT EXISTS readiness_log (
    day         TEXT PRIMARY KEY,
    index_value REAL NOT NULL,
    est_score   REAL NOT NULL,
    percentile  REAL NOT NULL,
    behind_you  INTEGER NOT NULL DEFAULT 0,
    ahead_of_you INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS unlocked (
    code        TEXT PRIMARY KEY,
    unlocked_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS doubts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_slug TEXT NOT NULL DEFAULT '',
    topic_slug  TEXT NOT NULL DEFAULT '',
    question_id TEXT NOT NULL DEFAULT '',
    body        TEXT NOT NULL,
    prompt      TEXT NOT NULL DEFAULT '',
    provider    TEXT NOT NULL DEFAULT '',
    answer      TEXT NOT NULL DEFAULT '',
    resolved    INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


# ---------------------------------------------------------------------------
# migrations
# ---------------------------------------------------------------------------
# Version 3 - the question bank becomes a first-class citizen.
M3 = [
    """CREATE TABLE IF NOT EXISTS question_sources (
        slug         TEXT PRIMARY KEY,
        name         TEXT NOT NULL,
        kind         TEXT NOT NULL DEFAULT 'manual',
        url          TEXT NOT NULL DEFAULT '',
        licence_note TEXT NOT NULL DEFAULT '',
        trust        REAL NOT NULL DEFAULT 0.7,
        questions    INTEGER NOT NULL DEFAULT 0,
        last_fetch_at TEXT,
        last_import_at TEXT,
        created_at   TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS question_tags (
        question_id TEXT NOT NULL,
        tag         TEXT NOT NULL,
        origin      TEXT NOT NULL DEFAULT 'import',
        PRIMARY KEY (question_id, tag)
    )""",
    "CREATE INDEX IF NOT EXISTS idx_qtags_tag ON question_tags(tag)",
    """CREATE TABLE IF NOT EXISTS question_imports (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        source_slug  TEXT NOT NULL DEFAULT '',
        input_path   TEXT NOT NULL DEFAULT '',
        manifest     TEXT NOT NULL DEFAULT '',
        dry_run      INTEGER NOT NULL DEFAULT 1,
        found        INTEGER NOT NULL DEFAULT 0,
        matched      INTEGER NOT NULL DEFAULT 0,
        needs_review INTEGER NOT NULL DEFAULT 0,
        rejected     INTEGER NOT NULL DEFAULT 0,
        duplicates   INTEGER NOT NULL DEFAULT 0,
        promoted     INTEGER NOT NULL DEFAULT 0,
        status       TEXT NOT NULL DEFAULT 'done',
        log          TEXT NOT NULL DEFAULT '',
        started_at   TEXT NOT NULL,
        finished_at  TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS question_review (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        import_id   INTEGER,
        source_slug TEXT NOT NULL DEFAULT '',
        question_id TEXT NOT NULL DEFAULT '',
        payload     TEXT NOT NULL,
        confidence  REAL NOT NULL DEFAULT 0,
        issues      TEXT NOT NULL DEFAULT '',
        status      TEXT NOT NULL DEFAULT 'pending',
        notes       TEXT NOT NULL DEFAULT '',
        created_at  TEXT NOT NULL,
        decided_at  TEXT
    )""",
    "CREATE INDEX IF NOT EXISTS idx_qreview_status ON question_review(status)",
    """CREATE TABLE IF NOT EXISTS topic_alias (
        alias        TEXT NOT NULL,
        subject_slug TEXT NOT NULL DEFAULT '',
        topic_slug   TEXT NOT NULL DEFAULT '',
        source_slug  TEXT NOT NULL DEFAULT '',
        PRIMARY KEY (alias, subject_slug)
    )""",
    """CREATE TABLE IF NOT EXISTS question_stats (
        question_id     TEXT PRIMARY KEY,
        subject_slug    TEXT NOT NULL DEFAULT '',
        topic_slug      TEXT NOT NULL DEFAULT '',
        usage_count     INTEGER NOT NULL DEFAULT 0,
        correct_count   INTEGER NOT NULL DEFAULT 0,
        reattempts      INTEGER NOT NULL DEFAULT 0,
        last_attempt_day TEXT,
        last_correct_day TEXT,
        last_wrong_day  TEXT,
        avg_seconds     REAL NOT NULL DEFAULT 0,
        avg_confidence  REAL NOT NULL DEFAULT 0,
        mistake_kind    TEXT NOT NULL DEFAULT '',
        saved           INTEGER NOT NULL DEFAULT 0,
        updated_at      TEXT
    )""",
    "CREATE INDEX IF NOT EXISTS idx_qstats_topic ON question_stats(topic_slug)",
    "CREATE INDEX IF NOT EXISTS idx_qstats_last ON question_stats(last_attempt_day)",
]

# Version 4 - retention: spaced repetition queue and topic prerequisites.
M4 = [
    """CREATE TABLE IF NOT EXISTS revision_queue (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        item_type     TEXT NOT NULL DEFAULT 'topic',
        item_key      TEXT NOT NULL,
        subject_slug  TEXT NOT NULL DEFAULT '',
        topic_slug    TEXT NOT NULL DEFAULT '',
        label         TEXT NOT NULL DEFAULT '',
        due_day       TEXT NOT NULL,
        interval_days REAL NOT NULL DEFAULT 1,
        ease          REAL NOT NULL DEFAULT 2.5,
        reps          INTEGER NOT NULL DEFAULT 0,
        lapses        INTEGER NOT NULL DEFAULT 0,
        last_review_day TEXT,
        last_result   TEXT NOT NULL DEFAULT '',
        strength      REAL NOT NULL DEFAULT 0.5,
        active        INTEGER NOT NULL DEFAULT 1,
        created_at    TEXT NOT NULL,
        updated_at    TEXT NOT NULL,
        UNIQUE (item_type, item_key)
    )""",
    "CREATE INDEX IF NOT EXISTS idx_revq_due ON revision_queue(due_day, active)",
    """CREATE TABLE IF NOT EXISTS topic_prerequisites (
        topic_slug   TEXT NOT NULL,
        prereq_slug  TEXT NOT NULL,
        strength     REAL NOT NULL DEFAULT 1.0,
        PRIMARY KEY (topic_slug, prereq_slug)
    )""",
]

# Version 5 - planning: goals, daily plans, DPP sets.
M5 = [
    """CREATE TABLE IF NOT EXISTS user_goals (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        slug        TEXT NOT NULL,
        kind        TEXT NOT NULL DEFAULT 'metric',
        label       TEXT NOT NULL DEFAULT '',
        target_value REAL NOT NULL DEFAULT 0,
        horizon_day TEXT,
        note        TEXT NOT NULL DEFAULT '',
        active      INTEGER NOT NULL DEFAULT 1,
        achieved_at TEXT,
        created_at  TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS daily_plans (
        day            TEXT PRIMARY KEY,
        generated_at   TEXT NOT NULL,
        target_mins    INTEGER NOT NULL DEFAULT 240,
        horizon_days   INTEGER,
        blocks         TEXT NOT NULL DEFAULT '[]',
        reason         TEXT NOT NULL DEFAULT '',
        status         TEXT NOT NULL DEFAULT 'open',
        done_blocks    TEXT NOT NULL DEFAULT '[]',
        rating         INTEGER,
        notes          TEXT NOT NULL DEFAULT '',
        updated_at     TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS dpp_sets (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_day     TEXT NOT NULL DEFAULT '',
        block_key    TEXT NOT NULL DEFAULT '',
        mode         TEXT NOT NULL DEFAULT 'dpp',
        label        TEXT NOT NULL DEFAULT '',
        reason       TEXT NOT NULL DEFAULT '',
        fixing       TEXT NOT NULL DEFAULT '',
        aim          TEXT NOT NULL DEFAULT '',
        target_topic TEXT NOT NULL DEFAULT '',
        question_ids TEXT NOT NULL DEFAULT '[]',
        quiz_id      INTEGER,
        total        INTEGER NOT NULL DEFAULT 0,
        correct      INTEGER NOT NULL DEFAULT 0,
        generated_at TEXT NOT NULL,
        started_at   TEXT,
        finished_at  TEXT
    )""",
    "CREATE INDEX IF NOT EXISTS idx_dpp_day ON dpp_sets(plan_day)",
]

# Version 6 - the feedback loop and recommendation ledger.
M6 = [
    """CREATE TABLE IF NOT EXISTS recommendations (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        day         TEXT NOT NULL,
        slug        TEXT NOT NULL,
        kind        TEXT NOT NULL DEFAULT 'study',
        title       TEXT NOT NULL DEFAULT '',
        detail      TEXT NOT NULL DEFAULT '',
        reason      TEXT NOT NULL DEFAULT '',
        expected    TEXT NOT NULL DEFAULT '',
        subject_slug TEXT NOT NULL DEFAULT '',
        topic_slug  TEXT NOT NULL DEFAULT '',
        urgency     REAL NOT NULL DEFAULT 0,
        score       REAL NOT NULL DEFAULT 0,
        payload     TEXT NOT NULL DEFAULT '{}',
        shown_at    TEXT NOT NULL,
        acted_at    TEXT,
        dismissed_at TEXT,
        outcome     TEXT NOT NULL DEFAULT ''
    )""",
    "CREATE INDEX IF NOT EXISTS idx_recs_day ON recommendations(day)",
    "CREATE INDEX IF NOT EXISTS idx_recs_slug ON recommendations(slug)",
    """CREATE TABLE IF NOT EXISTS feedback (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        target_type   TEXT NOT NULL DEFAULT 'recommendation',
        target_id     TEXT NOT NULL DEFAULT '',
        target_slug   TEXT NOT NULL DEFAULT '',
        subject_slug  TEXT NOT NULL DEFAULT '',
        topic_slug    TEXT NOT NULL DEFAULT '',
        rating        INTEGER,
        answer        TEXT NOT NULL DEFAULT '',
        reason        TEXT NOT NULL DEFAULT '',
        difficulty    TEXT NOT NULL DEFAULT '',
        length        TEXT NOT NULL DEFAULT '',
        followed      INTEGER,
        completed     INTEGER,
        time_spent_s  INTEGER NOT NULL DEFAULT 0,
        correction    TEXT NOT NULL DEFAULT '',
        day           TEXT NOT NULL,
        payload       TEXT NOT NULL DEFAULT '{}',
        created_at    TEXT NOT NULL
    )""",
    "CREATE INDEX IF NOT EXISTS idx_feedback_target ON feedback(target_type, target_slug)",
    "CREATE INDEX IF NOT EXISTS idx_feedback_day ON feedback(day)",
    """CREATE TABLE IF NOT EXISTS learned_weights (
        scope      TEXT NOT NULL,
        key        TEXT NOT NULL,
        weight     REAL NOT NULL DEFAULT 1.0,
        samples    INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT,
        PRIMARY KEY (scope, key)
    )""",
]

# Version 7 - richer attempt telemetry, quiz modes, mission log.
M7 = [
    ("column", "attempts", "seconds", "INTEGER NOT NULL DEFAULT 0"),
    ("column", "attempts", "confidence", "INTEGER"),
    ("column", "attempts", "mistake_kind", "TEXT NOT NULL DEFAULT ''"),
    ("column", "attempts", "reattempt", "INTEGER NOT NULL DEFAULT 0"),
    ("column", "attempts", "dpp_set_id", "INTEGER"),
    ("column", "attempts", "plan_day", "TEXT NOT NULL DEFAULT ''"),
    ("column", "quizzes", "mode", "TEXT NOT NULL DEFAULT 'practice'"),
    ("column", "quizzes", "plan_day", "TEXT NOT NULL DEFAULT ''"),
    ("column", "quizzes", "dpp_set_id", "INTEGER"),
    ("column", "quizzes", "reason", "TEXT NOT NULL DEFAULT ''"),
    ("column", "doubts", "helped", "INTEGER"),
    ("column", "doubts", "retried_at", "TEXT"),
    ("column", "doubts", "resolved_at", "TEXT"),
    ("column", "topics", "confidence", "INTEGER"),
    ("column", "topics", "last_revised", "TEXT"),
    "CREATE INDEX IF NOT EXISTS idx_attempts_question ON attempts(question_id)",
    "CREATE INDEX IF NOT EXISTS idx_attempts_subject ON attempts(subject_slug)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_kind ON sessions(kind)",
]

# Version 8 - readiness snapshots keep their component breakdown, so
# "why did the score move" can be answered from history instead of guessed.
M8 = [
    ("column", "readiness_log", "coverage", "REAL"),
    ("column", "readiness_log", "accuracy", "REAL"),
    ("column", "readiness_log", "volume", "REAL"),
    ("column", "readiness_log", "consistency", "REAL"),
    ("column", "readiness_log", "confidence", "REAL"),
    ("column", "readiness_log", "mastery", "REAL"),
]

MIGRATIONS = [
    (3, M3),
    (4, M4),
    (5, M5),
    (6, M6),
    (7, M7),
    (8, M8),
]


# ---------------------------------------------------------------------------
# connection
# ---------------------------------------------------------------------------
def connect():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _table_exists(conn, table):
    return (
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (table,)
        ).fetchone()
        is not None
    )


def _columns(conn, table):
    if not _table_exists(conn, table):
        return set()
    return {r["name"] for r in conn.execute("PRAGMA table_info(%s)" % table)}


def _ensure_column(conn, table, column, decl):
    """ALTER TABLE ADD COLUMN, but only when the column is genuinely missing."""
    if not _table_exists(conn, table):
        return False
    if column in _columns(conn, table):
        return False
    conn.execute("ALTER TABLE %s ADD COLUMN %s %s" % (table, column, decl))
    return True


def current_version(conn):
    if not _table_exists(conn, "schema_meta"):
        return 0
    row = conn.execute(
        "SELECT value FROM schema_meta WHERE key = 'schema_version'"
    ).fetchone()
    if row is None:
        return 2 if _table_exists(conn, "sessions") else 0
    try:
        return int(row["value"])
    except (TypeError, ValueError):
        return 0


def _set_version(conn, version):
    conn.execute(
        "INSERT INTO schema_meta (key, value) VALUES ('schema_version', ?)"
        " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (str(version),),
    )


def migrate(conn, verbose=False):
    """Bring the database up to SCHEMA_VERSION. Returns the list of steps run."""
    from datetime import datetime

    applied = []
    version = current_version(conn)
    with conn:
        for target, steps in MIGRATIONS:
            if version >= target:
                continue
            for step in steps:
                if isinstance(step, tuple) and step and step[0] == "column":
                    _, table, column, decl = step
                    _ensure_column(conn, table, column, decl)
                else:
                    conn.execute(step)
            version = target
            applied.append(target)
            if verbose:
                print("  migrated schema to v%d" % target)
        _set_version(conn, max(version, SCHEMA_VERSION))
        conn.execute(
            "INSERT INTO schema_meta (key, value) VALUES ('migrated_at', ?)"
            " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (datetime.now().isoformat(timespec="seconds"),),
        )
    return applied


def init(verbose=False):
    """Open the database, create the base schema, then run migrations."""
    conn = connect()
    with conn:
        conn.executescript(SCHEMA)
    migrate(conn, verbose=verbose)
    return conn


def health(conn):
    """A small report used by the startup banner and /api/health."""
    tables = {
        r["name"]
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    size = os.path.getsize(DB_PATH) if os.path.isfile(DB_PATH) else 0
    return dict(
        path=DB_PATH,
        size_bytes=size,
        size_h=(
            "%.1f MB" % (size / 1048576.0) if size > 1048576 else "%d KB" % (size // 1024)
        ),
        schema_version=current_version(conn),
        expected_version=SCHEMA_VERSION,
        up_to_date=current_version(conn) >= SCHEMA_VERSION,
        tables=sorted(tables),
        table_count=len(tables),
    )


# ---------------------------------------------------------------------------
# settings helpers
# ---------------------------------------------------------------------------
def get_settings(conn):
    return {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM settings")}


def put_setting(conn, key, value):
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )


def setting_int(settings, key, default):
    try:
        return int(float(settings.get(key, default)))
    except (TypeError, ValueError):
        return default


def setting_float(settings, key, default):
    try:
        return float(settings.get(key, default))
    except (TypeError, ValueError):
        return default


def setting_bool(settings, key, default=False):
    raw = str(settings.get(key, default)).strip().lower()
    return raw in ("1", "true", "yes", "on")
