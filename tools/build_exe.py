#!/usr/bin/env python3
"""Build a single-file GitGrind executable.

Why this exists: `python app.py` is fine for development, but the daily-use
target is a file you double-click. PyInstaller is the default here because it is
the least fussy about bundling the static/ and content/ trees; Nuitka produces a
noticeably faster binary and is supported with --nuitka if you have a C compiler.

    python tools/build_exe.py                 one-file build with PyInstaller
    python tools/build_exe.py --onedir        faster startup, a folder not a file
    python tools/build_exe.py --nuitka        compile instead of bundling
    python tools/build_exe.py --clean         wipe build/ and dist/ first

What ends up inside:
  * app.py and the core/ package
  * static/  - the entire UI, so no CDN and no network at runtime
  * content/ - syllabus, targets, keyword lexicons and the question bank

What stays outside, deliberately:
  * data/gitgrind.db - your database must live next to the exe, not inside it,
    or every rebuild would wipe your history.
  * papers/ - source PDFs are large and only needed when importing.

The database is resolved relative to the executable when frozen, so the exe and
its data/ folder travel together. Copy both to back up.
"""

import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "GitGrind"

DATA_TREES = ["static", "content"]
ICON_ICO = os.path.join("static", "icon.ico")
ICON_PNG = os.path.join("static", "icon.png")


def icon_path():
    """The icon for this platform, or "" when it has not been generated yet."""
    want = ICON_ICO if os.name == "nt" else ICON_PNG
    full = os.path.join(ROOT, want)
    if os.path.isfile(full):
        return full
    other = os.path.join(ROOT, ICON_PNG if os.name == "nt" else ICON_ICO)
    return other if os.path.isfile(other) else ""


def have(module):
    try:
        __import__(module)
        return True
    except ImportError:
        return False


def sep():
    """PyInstaller wants ';' on Windows and ':' elsewhere for --add-data."""
    return ";" if os.name == "nt" else ":"


def pyinstaller(args):
    if not have("PyInstaller"):
        print("PyInstaller is not installed. Install it with:")
        print("    pip install pyinstaller")
        return 1

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--name",
        NAME,
        "--onedir" if args.onedir else "--onefile",
        "--windowed" if not args.console else "--console",
        "--distpath",
        os.path.join(ROOT, "dist"),
        "--workpath",
        os.path.join(ROOT, "build"),
        "--specpath",
        os.path.join(ROOT, "build"),
    ]

    for tree in DATA_TREES:
        src = os.path.join(ROOT, tree)
        if os.path.isdir(src):
            cmd += ["--add-data", "%s%s%s" % (src, sep(), tree)]

    # The core package is imported normally, but demo_data is only reached
    # through a CLI flag so the analyser can miss it.
    ico = icon_path()
    if ico:
        cmd += ["--icon", ico]
        print("using icon: %s" % os.path.relpath(ico, ROOT))
    else:
        print("no icon found. Generate one first:")
        print("    pip install pillow")
        print("    python tools/make_icon.py")
    for mod in (
        "demo_data",
        "pystray",
        "pystray._win32",
        "PIL",
        "PIL.Image",
        "PIL.ImageDraw",
    ):
        cmd += ["--hidden-import", mod]
    cmd += [os.path.join(ROOT, "app.py")]

    print("Running:\n  %s\n" % " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


def nuitka(args):
    if not have("nuitka"):
        print("Nuitka is not installed. Install it with:")
        print("    pip install nuitka")
        print("You will also need a C compiler (MSVC on Windows, gcc elsewhere).")
        return 1

    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--assume-yes-for-downloads",
        "--output-filename=" + NAME,
        "--output-dir=" + os.path.join(ROOT, "dist"),
        "--include-package=core",
    ]
    ico = icon_path()
    if ico and os.name == "nt":
        cmd.append("--windows-icon-from-ico=" + ico)
    elif ico:
        cmd.append("--linux-icon=" + ico)
    if args.onefile:
        cmd.append("--onefile")
    for tree in DATA_TREES:
        src = os.path.join(ROOT, tree)
        if os.path.isdir(src):
            cmd.append("--include-data-dir=%s=%s" % (src, tree))
    cmd.append(os.path.join(ROOT, "app.py"))

    print("Running:\n  %s\n" % " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


def main():
    ap = argparse.ArgumentParser(description="Package GitGrind as an executable.")
    ap.add_argument(
        "--onedir",
        action="store_true",
        help="PyInstaller: produce a folder instead of one file "
        "(starts noticeably faster)",
    )
    ap.add_argument(
        "--nuitka",
        action="store_true",
        help="compile with Nuitka instead of bundling with PyInstaller",
    )
    ap.add_argument(
        "--onefile", action="store_true", help="with --nuitka: also produce a single file"
    )
    ap.add_argument(
        "--console",
        action="store_true",
        help="keep the terminal window (useful while debugging a build)",
    )
    ap.add_argument("--clean", action="store_true", help="remove build/ and dist/ first")
    ap.add_argument(
        "--stage",
        action="store_true",
        help="after building, copy your existing data/gitgrind.db next to "
        "the executable so it starts with your real history",
    )
    ap.add_argument(
        "--stage-only",
        action="store_true",
        help="skip the build, just do the staging copy",
    )
    args = ap.parse_args()

    if args.stage_only:
        return stage()

    if args.clean:
        for d in ("build", "dist"):
            path = os.path.join(ROOT, d)
            if os.path.isdir(path):
                shutil.rmtree(path)
                print("removed %s/" % d)

    rc = nuitka(args) if args.nuitka else pyinstaller(args)
    if rc:
        print("\nBuild failed with exit code %d." % rc)
        return rc

    print("\nBuild finished. Look in dist/.")
    if args.stage:
        stage()
    else:
        print("\nNothing else is required: on first run the executable creates data/ and")
        print("unpacks content/ beside itself automatically.")
        print("To start from your existing history instead, run:")
        print("    python tools/build_exe.py --stage-only")
    print("\nThen double-click it. It starts the local server and opens your browser.")
    return 0


def stage():
    """Put an existing database next to the built executable.

    The executable does not need this: it will create an empty database and unpack
    content/ on its own. This is only for carrying your existing history over.
    """
    dist = os.path.join(ROOT, "dist")
    if not os.path.isdir(dist):
        print("There is no dist/ folder yet. Build first:")
        print("    python tools/build_exe.py")
        return 1

    # --onedir puts everything under dist/<NAME>/; --onefile puts the exe in dist/.
    inner = os.path.join(dist, NAME)
    target = inner if os.path.isdir(inner) else dist

    src_db = os.path.join(ROOT, "data", "gitgrind.db")
    if not os.path.isfile(src_db):
        print("No data/gitgrind.db to copy. The executable will create a fresh one.")
        return 0

    dest_dir = os.path.join(target, "data")
    os.makedirs(dest_dir, exist_ok=True)
    dest_db = os.path.join(dest_dir, "gitgrind.db")
    if os.path.isfile(dest_db):
        backup = dest_db + ".replaced"
        shutil.copy2(dest_db, backup)
        print("existing database moved aside to %s" % os.path.relpath(backup, ROOT))
    shutil.copy2(src_db, dest_db)
    print("copied your database to %s" % os.path.relpath(dest_db, ROOT))

    print("\nfinal layout:")
    print("    %s/" % os.path.relpath(target, ROOT))
    print("      %s%s" % (NAME, ".exe" if os.name == "nt" else ""))
    print("      data/gitgrind.db          <- your history")
    print("      content/                  <- created on first run, holds your bank")
    return 0


if __name__ == "__main__":
    sys.exit(main())
