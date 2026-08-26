"""Crash-safe checkpointing of whatever is in flight.

Two questions this module answers on every launch:

    "was something running when we stopped?"      -> live_state
    "did we stop on purpose, or were we killed?"  -> run_log

Nothing here decides anything. The UI writes a checkpoint whenever it changes
something and at least every ten seconds while a clock is running; this stores
the last one; on boot ``resume_offer`` reports what is worth offering back.

Why the checkpoint is periodic rather than written on the way out: no exit hook
is reliable. Windows does not deliver SIGTERM when the machine shuts down, and
``atexit`` does not run when a process is killed. So the exit hooks in app.py
only *label* a run - the periodic write is what actually saves the work.
"""

import json
import os
from datetime import datetime

from . import db  # noqa: F401  (imported for symmetry with the other services)

# Older than this and it is not a resume, it is archaeology. An overnight
# shutdown should still offer yesterday evening's session back; last week's
# should not.
MAX_AGE_HOURS = 18

# The id of the run_log row for this process. Module-level because there is
# exactly one process per database - the single-instance bind in app.py is what
# guarantees that.
_RUN_ID = None


def stamp():
    return datetime.now().isoformat(timespec="seconds")


def _age_hours(iso):
    try:
        return (datetime.now() - datetime.fromisoformat(iso)).total_seconds() / 3600.0
    except (TypeError, ValueError):
        return float(10**6)


# ---------------------------------------------------------------------------
# the checkpoint
# ---------------------------------------------------------------------------
def save(conn, kind, payload):
    """Overwrite the checkpoint. Called often, so it stays a single statement."""
    now = stamp()
    with conn:
        conn.execute(
            "INSERT INTO live_state (id, kind, payload, revision, beat_at, updated_at)"
            " VALUES (1, ?, ?, 1, ?, ?)"
            " ON CONFLICT(id) DO UPDATE SET"
            "   kind = excluded.kind,"
            "   payload = excluded.payload,"
            "   revision = live_state.revision + 1,"
            "   beat_at = excluded.beat_at,"
            "   updated_at = excluded.updated_at",
            (kind, json.dumps(payload, default=str), now, now),
        )
    return dict(kind=kind, at=now)


def clear(conn):
    with conn:
        conn.execute("DELETE FROM live_state WHERE id = 1")


def load(conn):
    """The stored checkpoint, or None. A torn write reads as None, not a crash."""
    row = conn.execute("SELECT * FROM live_state WHERE id = 1").fetchone()
    if not row or not row["kind"]:
        return None
    try:
        payload = json.loads(row["payload"])
    except ValueError:
        return None
    if not isinstance(payload, dict) or not payload:
        return None
    return dict(
        kind=row["kind"],
        payload=payload,
        revision=row["revision"],
        beat_at=row["beat_at"],
        updated_at=row["updated_at"],
    )


# ---------------------------------------------------------------------------
# run bookkeeping
# ---------------------------------------------------------------------------
def start_run(conn, version=""):
    """Record that this process is now the running copy."""
    global _RUN_ID
    now = stamp()
    with conn:
        cur = conn.execute(
            "INSERT INTO run_log (pid, version, started_at, beat_at) VALUES (?,?,?,?)",
            (os.getpid(), version, now, now),
        )
        _RUN_ID = cur.lastrowid
    return _RUN_ID


def beat(conn):
    """Still alive. One UPDATE, called from a timer thread."""
    if not _RUN_ID:
        return
    with conn:
        conn.execute("UPDATE run_log SET beat_at = ? WHERE id = ?", (stamp(), _RUN_ID))


def end_run(conn, kind="clean"):
    """We are exiting on purpose. Idempotent: several hooks may all fire."""
    if not _RUN_ID:
        return
    with conn:
        conn.execute(
            "UPDATE run_log SET stopped_at = ?, exit_kind = ?"
            " WHERE id = ? AND stopped_at IS NULL",
            (stamp(), kind, _RUN_ID),
        )


def last_unclean(conn):
    """The run immediately before this one, if it never recorded an exit.

    Deliberately the *previous* run and no further back. Asking for "any earlier
    run with no stopped_at" looks equivalent and is not: a killed run keeps its
    NULL for ever, so one crash would make every launch after it claim to be
    recovering from a crash. Only the run we actually followed can tell us how
    the last session ended.
    """
    row = conn.execute(
        "SELECT * FROM run_log WHERE id < ? ORDER BY id DESC LIMIT 1",
        (_RUN_ID if _RUN_ID else 10**9,),
    ).fetchone()
    if not row or row["stopped_at"]:
        return None
    return dict(row)


def prune_runs(conn, keep=200):
    """Keep run_log from growing without bound. Called once at startup."""
    with conn:
        conn.execute(
            "DELETE FROM run_log WHERE id NOT IN"
            " (SELECT id FROM run_log ORDER BY id DESC LIMIT ?)",
            (keep,),
        )


# ---------------------------------------------------------------------------
# what to offer on boot
# ---------------------------------------------------------------------------
def resume_offer(conn):
    """What the UI should offer to bring back. Safe on every /api/state call."""
    unclean = last_unclean(conn)
    out = dict(resumable=False, unclean_exit=bool(unclean))
    if unclean:
        out["crashed_at"] = unclean.get("beat_at") or unclean.get("started_at")

    saved = load(conn)
    if not saved:
        return out

    age = _age_hours(saved["beat_at"] or saved["updated_at"])
    if age > MAX_AGE_HOURS:
        clear(conn)
        out["expired"] = True
        return out

    # A set that has already been submitted is not resumable, however fresh the
    # checkpoint is. Drop that half and keep whatever else was in flight.
    quiz_part = saved["payload"].get("quiz") or {}
    quiz_id = quiz_part.get("quiz_id")
    if quiz_id:
        row = conn.execute(
            "SELECT finished_at FROM quizzes WHERE id = ?", (quiz_id,)
        ).fetchone()
        if not row or row["finished_at"]:
            saved["payload"].pop("quiz", None)

    if not saved["payload"]:
        clear(conn)
        return out

    out.update(resumable=True, age_hours=round(age, 2), saved=saved)
    return out
