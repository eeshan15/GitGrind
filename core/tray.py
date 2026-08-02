"""System tray presence, so the app can keep running with no window open.

The shape of this is the same as a game launcher: the tray icon owns the process,
the window is disposable. Closing the window does not stop the server, so opening
it again is instant and a timer that was running is still running.

pystray wants the main thread on Windows, and so does pywebview - they cannot both
have it. That is why the window here is a detached browser process in app mode
rather than an embedded web view: a subprocess needs no thread at all, can be
closed and reopened as often as you like, and leaves the main thread free for the
tray.

pystray is optional. Without it the app falls back to holding the terminal open,
exactly as it did before.
"""

import os
import sys
import threading
import webbrowser

from core import db


def available():
    """Can a tray icon actually be created?"""
    try:
        import pystray  # noqa: F401
        from PIL import Image  # noqa: F401

        return True
    except Exception:
        return False


def _load_image():
    """The tray image. Falls back to a drawn square if the icon is missing."""
    from PIL import Image, ImageDraw

    for name in ("icon.png", "icon.ico"):
        path = os.path.join(db.ASSET_DIR, "static", name)
        if os.path.isfile(path):
            try:
                img = Image.open(path).convert("RGBA")
                # 64px is what Windows asks for; larger just gets downscaled badly
                return img.resize((64, 64), Image.LANCZOS)
            except Exception:
                pass

    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((2, 2, 61, 61), radius=14, fill=(13, 17, 23, 255))
    d.rounded_rectangle((14, 14, 30, 30), radius=4, fill=(232, 180, 62, 255))
    d.rounded_rectangle((34, 14, 50, 30), radius=4, fill=(0, 109, 50, 255))
    d.rounded_rectangle((14, 34, 30, 50), radius=4, fill=(25, 108, 46, 255))
    d.rounded_rectangle((34, 34, 50, 50), radius=4, fill=(232, 180, 62, 255))
    return img


def run(url, open_window, log, on_quit=None):
    """Show the tray icon and block until the user quits.

    ``open_window`` is called to (re)open the UI; ``log`` writes a line wherever
    logging goes in this build. Returns False if a tray could not be created, so
    the caller can fall back to serving in the foreground.
    """
    if not available():
        return False

    import pystray
    from pystray import MenuItem as Item

    stopping = threading.Event()

    def do_open(icon=None, item=None):
        try:
            open_window()
        except Exception as exc:
            log("  could not open the window: %s" % exc)

    def do_browser(icon=None, item=None):
        webbrowser.open(url)

    def do_folder(icon=None, item=None):
        folder = db.BASE_DIR
        try:
            if os.name == "nt":
                os.startfile(folder)
            elif sys.platform == "darwin":
                import subprocess

                subprocess.Popen(["open", folder])
            else:
                import subprocess

                subprocess.Popen(["xdg-open", folder])
        except Exception as exc:
            log("  could not open %s: %s" % (folder, exc))

    def do_quit(icon=None, item=None):
        log("  quitting from the tray")
        stopping.set()
        if on_quit:
            try:
                on_quit()
            except Exception:
                pass
        icon.stop()

    menu = pystray.Menu(
        Item("Open GitGrind", do_open, default=True),
        Item("Open in browser", do_browser),
        pystray.Menu.SEPARATOR,
        Item("Show my data folder", do_folder),
        pystray.Menu.SEPARATOR,
        Item("Quit", do_quit),
    )

    icon = pystray.Icon("GitGrind", _load_image(), "GitGrind - running", menu)
    log("  tray       icon active; closing the window leaves it running")
    icon.run()
    return True
