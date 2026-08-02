#!/usr/bin/env python3
"""GitGrind - a local, GitHub-styled operating system for GATE CSE preparation.

Standard library only. Start it with:

    python app.py

then open the address it prints. Data lives in data/gitgrind.db.
Content (syllabus, question bank, cutoff targets) lives under content/ and is
plain JSON you can edit.

Bootstrap order, every launch:

    1. init the database and run any pending schema migrations
    2. seed the syllabus from content/syllabus.json
    3. load the content registry and mirror question sources into the DB
    4. validate the question bank and report its health
    5. launch the local server

Options:

    --demo [profile]   load sample activity before starting
    --reset [scope]    clear activity (or everything) before starting
    --check            run the bootstrap, print the report, and exit
    --no-browser       do not open a browser tab
    --port N           bind a different port
    --packaged         packaged-executable mode: quieter output, no dev hints
"""

import argparse
import os
import sys
import threading
import webbrowser
import shutil
import subprocess
from http.server import ThreadingHTTPServer
from core import tray, content, db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, getattr(sys, "_MEIPASS", BASE_DIR))
sys.path.insert(0, BASE_DIR)

from core import api

VERSION = "3.0"
HOST = os.environ.get("GITGRIND_HOST", "127.0.0.1")
PORT = int(os.environ.get("GITGRIND_PORT", "8420"))

# Set by PyInstaller / Nuitka builds; also forced by --packaged.
FROZEN = getattr(sys, "frozen", False)

# A --noconsole build has no stdout at all, so an unguarded print() raises
# AttributeError on None and takes the whole app down before it starts. Give it
# somewhere to write, and keep a copy on disk either way: when there is no
# terminal, that log file is the only way to find out what happened.
LOG_LINES = []


def _log_path():
    try:
        from core import db as _db

        folder = _db.BASE_DIR
    except Exception:
        folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, "gitgrind.log")


def log(*parts):
    """print(), but safe when stdout does not exist, and tee'd to a file."""
    line = " ".join(str(p) for p in parts)
    LOG_LINES.append(line)
    try:
        if sys.stdout is not None:
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
    except Exception:
        pass


def flush_log():
    """Write everything logged so far next to the database."""
    if not LOG_LINES:
        return
    try:
        path = _log_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        from datetime import datetime

        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n==== %s ====\n" % datetime.now().isoformat(timespec="seconds"))
            fh.write("\n".join(LOG_LINES) + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# bootstrap
# ---------------------------------------------------------------------------
def bootstrap(verbose=True):
    """Bring the install up to date and report on it. Safe to run repeatedly."""
    report = {}
    # In a packaged build this is the first run's one-time copy of content/ out of
    # the bundle and next to the executable, so it can be written to.
    unpacked = content.materialise(verbose=verbose)
    if unpacked:
        report["content_unpacked"] = unpacked
    conn = db.connect()
    try:
        with conn:
            conn.executescript(db.SCHEMA)
        applied = db.migrate(conn, verbose=False)
        report["migrations"] = applied
        report["db"] = db.health(conn)

        content.invalidate()
        content.seed(conn)
        report["bank"] = content.bank_stats(reload=True)
        report["sources"] = content.source_summary(conn)
        report["review"] = content.review_counts(conn)
        report["subjects"] = conn.execute(
            "SELECT COUNT(*) n FROM subjects WHERE archived = 0"
        ).fetchone()["n"]
        report["topics"] = conn.execute("SELECT COUNT(*) n FROM topics").fetchone()["n"]
        report["sessions"] = conn.execute("SELECT COUNT(*) n FROM sessions").fetchone()[
            "n"
        ]
    finally:
        conn.close()
    return report


def bank_warnings(bank):
    """Human-readable problems worth printing at startup."""
    out = []
    if not bank["total"]:
        out.append(
            "The question bank is empty. Drop JSON files into "
            "content/questions/ or run tools/import_questions.py."
        )
        return out
    if bank["broken"]:
        out.append(
            "%d question%s cannot be served (bad answer key, missing options "
            "or an unusable type). Run tools/selftest.py for the list."
            % (bank["broken"], "s" if bank["broken"] != 1 else "")
        )
    if bank["untagged"]:
        out.append(
            "%d question%s are tagged to a topic that is not in the syllabus, so "
            "they will never appear in a topic drill."
            % (bank["untagged"], "s" if bank["untagged"] != 1 else "")
        )
    if bank["topics_empty"]:
        out.append(
            "%d of %d syllabus topics have no questions at all. The heatmap will "
            "show them as untested rather than strong."
            % (bank["topics_empty"], bank["topics_total"])
        )
    if bank["missing_explanation"] > bank["total"] * 0.4:
        out.append(
            "%d questions have no explanation. Reviewing a wrong answer is much "
            "less useful without one." % bank["missing_explanation"]
        )
    return out


def banner(url, report, packaged=False):
    bank = report["bank"]
    dbh = report["db"]
    review = report["review"]

    lines = [
        "GitGrind %s - personal GATE OS" % VERSION,
        "",
        "Open        %s" % url,
        "Database    data/gitgrind.db  (schema v%d, %s)"
        % (dbh["schema_version"], dbh["size_h"]),
        "Content     content/  (syllabus, questions, targets)",
        "Bank        %d questions, %d%% health, %d%% topic coverage"
        % (bank["total"], bank["health_pct"], bank["coverage_pct"]),
        "Syllabus    %d subjects / %d topics" % (report["subjects"], report["topics"]),
        "Activity    %d logged sessions" % report["sessions"],
    ]
    if review["pending"]:
        lines.append(
            "Review      %d imported questions waiting for approval" % review["pending"]
        )
    if report["migrations"]:
        lines.append(
            "Migrated    schema v%s applied"
            % ", v".join(str(m) for m in report["migrations"])
        )
    lines += ["", "Stop        Ctrl + C"]

    width = max(len(x) for x in lines) + 4
    print()
    print("  +" + "-" * width + "+")
    for line in lines:
        print("  |  " + line.ljust(width - 4) + "  |")
    print("  +" + "-" * width + "+")
    print()

    warnings = bank_warnings(bank)
    if warnings:
        print("  Bank notes")
        for w in warnings:
            print("    - %s" % w)
        print()
    if not packaged and not report["sessions"]:
        print("  No activity logged yet. To see every panel populated first:")
        print("      python demo_data.py --profile disciplined")
        print()


# ---------------------------------------------------------------------------
# side commands
# ---------------------------------------------------------------------------
def run_demo(profile):
    try:
        import demo_data
    except ImportError:
        print("  demo_data.py is not next to app.py, skipping --demo.")
        return
    demo_data.load(profile=profile, confirm=False)


def run_reset(scope):
    conn = db.init()
    try:
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
                for t in ("doubts", "feedback", "learned_weights"):
                    conn.execute("DELETE FROM %s" % t)
        print("  Reset complete (scope: %s)." % scope)
    finally:
        conn.close()


def print_check(report):
    bank = report["bank"]
    print()
    print("  bootstrap check")
    print("  ---------------")
    print(
        "  schema        v%d (expected v%d) %s"
        % (
            report["db"]["schema_version"],
            report["db"]["expected_version"],
            "ok" if report["db"]["up_to_date"] else "OUT OF DATE",
        )
    )
    print("  tables        %d" % report["db"]["table_count"])
    print("  subjects      %d" % report["subjects"])
    print("  topics        %d" % report["topics"])
    print("  sessions      %d" % report["sessions"])
    print(
        "  bank          %d questions across %d files, %d source(s)"
        % (bank["total"], len(bank["files"]), len(bank["sources"]))
    )
    print(
        "  bank health   %d%% usable, %d broken, %d untagged"
        % (bank["health_pct"], bank["broken"], bank["untagged"])
    )
    print(
        "  topic cover   %d%% (%d of %d topics have questions)"
        % (
            bank["coverage_pct"],
            bank["topics_total"] - bank["topics_empty"],
            bank["topics_total"],
        )
    )
    print("  review queue  %d pending" % report["review"]["pending"])
    for w in bank_warnings(bank):
        print("  ! %s" % w)
    print()
    return 0 if report["db"]["up_to_date"] else 1


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def parse_args(argv):
    ap = argparse.ArgumentParser(
        prog="app.py", add_help=True, description="GitGrind %s" % VERSION
    )
    ap.add_argument(
        "--demo",
        nargs="?",
        const="disciplined",
        metavar="PROFILE",
        help="load demo activity first " "(disciplined | patchy | comeback | sprint)",
    )
    ap.add_argument(
        "--reset",
        nargs="?",
        const="activity",
        metavar="SCOPE",
        choices=["activity", "all"],
        help="clear activity ('activity') or everything ('all')",
    )
    ap.add_argument(
        "--check", action="store_true", help="run bootstrap, print a report, exit"
    )
    ap.add_argument("--no-browser", action="store_true", help="do not open a browser")
    ap.add_argument("--port", type=int, default=PORT, help="port to bind")
    ap.add_argument("--host", default=HOST, help="host to bind")
    ap.add_argument(
        "--packaged",
        action="store_true",
        help="packaged-executable mode: quieter, no dev hints",
    )
    ap.add_argument("--version", action="version", version="GitGrind %s" % VERSION)
    ap.add_argument(
        "--tray",
        action="store_true",
        help="keep running in the system tray with no terminal "
        "(the default for a packaged build)",
    )
    ap.add_argument(
        "--no-tray",
        action="store_true",
        help="do not use the tray even in a packaged build",
    )
    ap.add_argument(
        "--window",
        action="store_true",
        help="open in a plain app window instead of a browser tab "
        "(the default for a packaged build)",
    )
    return ap.parse_args(argv)


# ---------------------------------------------------------------------------
# opening the UI
# ---------------------------------------------------------------------------
CHROMIUM_NAMES = (
    # Windows
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    # macOS
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    # Linux / on PATH
    "msedge",
    "microsoft-edge",
    "google-chrome",
    "chromium",
    "chromium-browser",
)


def find_chromium():
    """A Chromium-family browser we can drive in app mode, or None."""
    local = os.environ.get("LOCALAPPDATA")
    candidates = list(CHROMIUM_NAMES)
    if local:
        candidates.insert(
            0, os.path.join(local, "Microsoft", "Edge", "Application", "msedge.exe")
        )
        candidates.insert(
            1, os.path.join(local, "Google", "Chrome", "Application", "chrome.exe")
        )
    for path in candidates:
        if os.path.isabs(path):
            if os.path.isfile(path):
                return path
        else:
            found = shutil.which(path)
            if found:
                return found
    return None


def have_webview():
    """Is pywebview importable? It is optional, never required."""
    try:
        import webview  # noqa: F401

        return True
    except Exception:
        return False


def open_native_window(url):
    """A real desktop window, not a browser. Blocks until the window closes.

    This must run on the main thread. On Windows pywebview uses the Edge WebView2
    runtime, which ships with Windows 10 and 11, so there is nothing to install -
    but it is the *runtime*, not the browser: no address bar, no tabs, its own
    taskbar entry and its own icon.
    """
    import webview

    # The WinForms backend builds a System.Drawing.Icon, which accepts .ico only.
    # Handing it a .png raises ArgumentException on a .NET thread, which Python
    # cannot catch - it takes the whole window down. Everywhere else a PNG is
    # correct, so pick per platform and skip the icon if the file is missing.
    name = "icon.ico" if os.name == "nt" else "icon.png"
    icon = os.path.join(db.ASSET_DIR, "static", name)

    webview.create_window(
        "GitGrind",
        url,
        width=1460,
        height=950,
        min_size=(1024, 700),
        background_color="#0d1117",
    )

    if os.path.isfile(icon):
        try:
            webview.start(icon=icon)
            return
        except TypeError:
            pass  # older pywebview has no icon= parameter
    webview.start()


def open_app_window(url):
    """Open the UI as a chromeless browser window, detached from this process.

    Deliberately a subprocess: it can be closed and reopened any number of times,
    it does not need the main thread, and when the user closes it the server here
    keeps running. That is what makes close-to-tray work.
    """
    browser = find_chromium()
    if not browser:
        webbrowser.open(url)
        return "browser"

    profile = os.path.join(db.DATA_DIR, "uiprofile")
    os.makedirs(profile, exist_ok=True)
    cmd = [
        browser,
        "--app=%s" % url,
        "--user-data-dir=%s" % profile,
        "--window-size=1460,950",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-features=Translate,AutofillServerCommunication",
    ]
    kwargs = {}
    if os.name == "nt":
        kwargs["creationflags"] = 0x00000008  # DETACHED_PROCESS
    subprocess.Popen(cmd, **kwargs)
    return "app-window"


class SingleInstanceServer(ThreadingHTTPServer):
    """HTTPServer, minus the address reuse that lets two copies bind one port.

    HTTPServer sets allow_reuse_address = 1, and on Windows that flag means
    "let another process bind this port too" rather than the Unix meaning of
    "reuse a socket in TIME_WAIT". So a second launch bound the same port
    happily, started its own server and added a second tray icon. Turning it off
    on Windows makes the bind itself the lock.
    """

    allow_reuse_address = os.name != "nt"
    daemon_threads = True


def another_instance(url, timeout=1.5):
    """Is a GitGrind already answering on this address?"""
    import json as _json
    import urllib.request

    try:
        with urllib.request.urlopen(url + "/api/health", timeout=timeout) as r:
            return _json.loads(r.read()).get("app") == "gitgrind"
    except Exception:
        return False


def wake_instance(url, timeout=3.0):
    """Ask the running copy to bring its window forward."""
    import urllib.request

    req = urllib.request.Request(
        url + "/api/show",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=timeout).read()
        return True
    except Exception:
        return False


def run_windowed_tray(url, server, open_browser):
    """A pywebview window on the main thread with the tray in a daemon thread.

    This is the arrangement that fixes the taskbar icon. Driving Edge with
    --app= gives a window owned by the Edge process, so Windows shows the Edge
    icon; a pywebview window belongs to this process and therefore carries this
    executable's icon.

    Closing the window hides it instead of destroying it, because pywebview
    cannot be started twice in one process. Hiding keeps close-to-tray working
    and makes reopening instant.
    """
    import webview

    if os.name == "nt":
        # Windows groups taskbar buttons by AppUserModelID and takes the icon
        # from whatever it thinks owns the window. Claim our own so it uses ours.
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "GitGrind.Desktop.3"
            )
        except Exception:
            pass

    threading.Thread(target=server.serve_forever, daemon=True).start()
    log("  server     running in the background")

    win = webview.create_window(
        "GitGrind",
        url,
        width=1460,
        height=950,
        min_size=(1024, 700),
        background_color="#0d1117",
        hidden=not open_browser,
    )
    state = {"quitting": False}

    def on_closing():
        if state["quitting"]:
            return True  # let the real close through
        win.hide()
        log("  window     hidden; still running in the tray")
        return False  # cancel this close

    try:
        win.events.closing += on_closing
    except Exception:  # pragma: no cover
        log("  window     this pywebview build cannot intercept close")

    def show():
        try:
            win.show()
        except Exception as exc:
            log("  could not show the window: %s" % exc)

    def quit_all():
        state["quitting"] = True
        try:
            server.shutdown()
        except Exception:
            pass
        try:
            win.destroy()
        except Exception:
            pass

    api.SHOW_WINDOW = show
    if tray.available():
        threading.Thread(
            target=lambda: tray.run(url, show, log, on_quit=quit_all), daemon=True
        ).start()
    else:
        log("  tray       pystray is not installed, so closing the window quits.")
        log("                 pip install pystray pillow")

    # The WinForms backend builds a System.Drawing.Icon, which accepts .ico only.
    name = "icon.ico" if os.name == "nt" else "icon.png"
    icon = os.path.join(db.ASSET_DIR, "static", name)
    try:
        if os.path.isfile(icon):
            webview.start(icon=icon)
        else:
            webview.start()
    except TypeError:
        webview.start()  # older pywebview
    finally:
        try:
            server.server_close()
        except Exception:
            pass
        flush_log()
    return 0


def launch_ui(url, window=True):
    """Open the app. In window mode there is no address bar and no tab strip.

    Three routes, tried in order:

    1. **pywebview**, if it happens to be installed. A genuinely native window
       using the system web view. Not a dependency: the app never requires it.
    2. **Chromium app mode** (``--app=``). Uses Edge or Chrome, which is already
       on every Windows machine, but renders a plain window with no browser
       furniture, so it reads as a desktop app. A private profile directory keeps
       it out of your normal browsing session and stops the window folding into
       an already-running browser.
    3. **The normal browser**, which is what running from source has always done.

    Failure is never fatal: the server is already up, so the worst case is that
    you open the printed URL yourself.
    """
    if not window:
        webbrowser.open(url)
        return "browser"

    try:
        import webview  # type: ignore

        webview.create_window(
            "GitGrind", url, width=1440, height=940, min_size=(1024, 700)
        )
        icon = os.path.join(db.ASSET_DIR, "static", "icon.png")
        webview.start(icon=icon if os.path.isfile(icon) else None)
        return "pywebview"
    except ImportError:
        pass
    except Exception as exc:  # pragma: no cover
        print("  window mode failed (%s), falling back" % exc)

    browser = find_chromium()
    if browser:
        profile = os.path.join(db.DATA_DIR, "uiprofile")
        os.makedirs(profile, exist_ok=True)
        cmd = [
            browser,
            "--app=%s" % url,
            "--user-data-dir=%s" % profile,
            "--window-size=1440,940",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-features=Translate,AutofillServerCommunication",
        ]
        try:
            kwargs = {}
            if os.name == "nt":
                # Do not let the browser keep a console window attached.
                kwargs["creationflags"] = 0x00000008  # DETACHED_PROCESS
            subprocess.Popen(cmd, **kwargs)
            return "app-window"
        except OSError as exc:
            print("  could not start %s (%s)" % (os.path.basename(browser), exc))

    webbrowser.open(url)
    return "browser"


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    packaged = args.packaged or FROZEN

    if args.reset:
        run_reset(args.reset)
    if args.demo:
        run_demo(args.demo)

    try:
        report = bootstrap()
    except Exception as exc:
        print("  Could not start: %s: %s" % (type(exc).__name__, exc))
        print("  If data/gitgrind.db is from a much older version, move it aside and")
        print("  restore from a backup export instead.")
        return 1

    if args.check:
        return print_check(report)

    url = "http://%s:%d" % (args.host, args.port)
    if another_instance(url):
        woke = wake_instance(url)
        log("")
        log("  GitGrind is already running at %s." % url)
        log(
            "  "
            + (
                "Brought its window to the front."
                if woke
                else "Open it from the tray icon."
            )
        )
        log("")
        flush_log()
        return 0
    banner(url, report, packaged)

    try:
        server = SingleInstanceServer((args.host, args.port), api.Handler)
    except OSError as exc:
        print("  Could not bind %s: %s" % (url, exc))
        print("  Another program may be using the port. Try:")
        print("      python app.py --port 9000")
        return 1

    open_browser = not args.no_browser and os.environ.get("GITGRIND_NO_BROWSER") != "1"
    want_window = args.window or FROZEN or args.packaged

    # A native window needs the main thread: pywebview runs a GUI event loop, and
    # starting it from a timer thread is why it silently failed and fell back to
    # Edge. So when a real window is wanted, the HTTP server moves to a daemon
    # thread and the window owns the main thread instead.
    # Tray mode: the icon owns the main thread and the process, the window is
    # disposable. Closing the window leaves the server up, so reopening is instant
    # and anything running - a session timer, for instance - is untouched.
    want_tray = (args.tray or FROZEN or args.packaged) and not args.no_tray
    if want_tray and have_webview():
        return run_windowed_tray(url, server, open_browser)
    if want_tray and tray.available():
        threading.Thread(target=server.serve_forever, daemon=True).start()
        log("  server     running in the background")
        api.SHOW_WINDOW = lambda: open_app_window(url)
        if open_browser:
            threading.Timer(0.6, lambda: open_app_window(url)).start()
        try:
            tray.run(
                url, lambda: open_app_window(url), log, on_quit=lambda: server.shutdown()
            )
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
            flush_log()
        return 0

    if want_tray and not tray.available():
        log("  tray       pystray is not installed, so the app will hold this")
        log("             terminal instead. To get a tray icon:")
        log("                 pip install pystray pillow")
    if open_browser and want_window and have_webview():
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            open_native_window(url)
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        print("\n  Stopped. Streak is safe.\n")
        return 0

    if open_browser:
        threading.Timer(0.8, lambda: launch_ui(url, window=want_window)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped. Streak is safe.\n")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
