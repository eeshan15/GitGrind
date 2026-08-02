#!/usr/bin/env python3
"""Download the GATE Overflow PDF releases from GitHub.

GO-PDFs publishes its books as GitHub release assets, which are meant to be
downloaded - so this just uses the public releases API. Nothing is scraped.

    # what is available right now
    python tools/fetch_go_pdfs.py --list

    # everything attached to a release tag
    python tools/fetch_go_pdfs.py --tag gatecse-2027

    # just the volumes you want
    python tools/fetch_go_pdfs.py --tag gatecse-2027 --only vol1 vol2

    # download and immediately turn into .txt (needs pdftotext or pypdf)
    python tools/fetch_go_pdfs.py --tag gatecse-2027 --extract

Files land in papers/ by default. Partial downloads resume, so a dropped
connection is not a restart.

Notes:
  - Unauthenticated GitHub allows 60 API calls an hour, which is plenty here.
    Pass --token if you hit the limit (a read-only classic token is enough).
  - These books are large. Expect tens of megabytes and a thousand-plus pages
    per volume.
  - The books are GATE Overflow's compilation of exam questions together with
    answers written by their community. Downloading them for your own study is
    what they are published for. Do not redistribute what you generate from
    them.
"""

import argparse
import json
import hashlib
import os
import shutil
import subprocess
import sys
from datetime import datetime
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
MANIFEST = os.path.join(ROOT, "papers", "manifest.json")
DEFAULT_DIR = os.path.join(ROOT, "papers")

REPO = "GATEOverflow/GO-PDFs"
API = "https://api.github.com/repos/%s/releases" % REPO

# GitHub attaches these to every release automatically; they are not books.
SKIP_NAMES = {"Source code (zip)", "Source code (tar.gz)"}
SKIP_EXT = {".zip", ".tar.gz", ".tgz", ".asc", ".sig"}

KNOWN_TAGS = [
    ("gatecse-2027", "GATE CSE 2027, 3 volumes"),
    ("tifr", "TIFR CSE"),
    ("ugcnet", "UGC NET CSE"),
    ("isro", "ISRO CSE"),
    ("NIELIT", "NIELIT Scientist A/B/C/D CSE"),
    ("aptitude", "Aptitude Overflow"),
]


def api_get(url, token=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "gitgrind-fetch",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = "Bearer %s" % token
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            remaining = exc.headers.get("x-ratelimit-remaining")
            reset = exc.headers.get("x-ratelimit-reset")
            if remaining == "0":
                wait = ""
                if reset:
                    secs = max(0, int(reset) - int(time.time()))
                    wait = " Try again in about %d minute(s)." % (secs // 60 + 1)
                raise SystemExit(
                    "GitHub API rate limit reached for your IP.%s\n"
                    "  Or pass a token:  --token ghp_xxxx" % wait
                )
        raise SystemExit("GitHub API error %s: %s" % (exc.code, exc.reason))
    except urllib.error.URLError as exc:
        raise SystemExit("Could not reach GitHub: %s" % exc.reason)


def is_book(asset):
    name = asset.get("name", "")
    if name in SKIP_NAMES:
        return False
    lower = name.lower()
    return not any(lower.endswith(e) for e in SKIP_EXT)


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "%.1f %s" % (n, unit)
        n /= 1024.0


def list_releases(releases):
    print()
    for rel in releases:
        tag = rel.get("tag_name", "?")
        books = [a for a in (rel.get("assets") or []) if is_book(a)]
        print("  %-18s %s" % (tag, rel.get("name", "")))
        print(
            "  %-18s released %s, %d downloadable file(s)"
            % ("", (rel.get("published_at") or "")[:10], len(books))
        )
        if rel.get("prerelease"):
            print("  %-18s (pre-release)" % "")
        for a in books:
            print("      %-52s %9s" % (a["name"], human(a["size"])))
        if not books:
            print("      (no book assets on this release)")
        print()
    print("  Download with:  python tools/fetch_go_pdfs.py --tag <tag>")


# ---------------------------------------------------------------------------
# manifest and integrity
# ---------------------------------------------------------------------------
def load_manifest():
    """What has already been downloaded, so a rerun is cheap and idempotent."""
    if not os.path.isfile(MANIFEST):
        return {"repo": REPO, "assets": {}}
    try:
        with open(MANIFEST, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        data.setdefault("assets", {})
        return data
    except (ValueError, OSError):
        return {"repo": REPO, "assets": {}}


def save_manifest(data):
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    tmp = MANIFEST + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, MANIFEST)
    return MANIFEST


def sha256_of(path, chunk=1048576):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def expected_digest(asset):
    """GitHub exposes a digest on newer release assets. Use it when present."""
    raw = asset.get("digest") or ""
    if isinstance(raw, str) and raw.startswith("sha256:"):
        return raw.split(":", 1)[1].strip()
    return ""


def verify(path, asset, manifest, quiet=False):
    """Check size, then the published digest if there is one, then record ours."""
    name = asset["name"]
    entry = manifest["assets"].setdefault(name, {})
    size = os.path.getsize(path)
    entry.update(
        name=name,
        size=size,
        url=asset.get("browser_download_url", ""),
        tag=asset.get("_tag", ""),
        downloaded_at=datetime.now().isoformat(timespec="seconds"),
    )

    if asset.get("size") and size != asset["size"]:
        entry["status"] = "size-mismatch"
        return False, "size mismatch (%s on disk, %s published)" % (
            human(size),
            human(asset["size"]),
        )

    want = expected_digest(asset)
    got = entry.get("sha256")
    if want or not got:
        got = sha256_of(path)
        entry["sha256"] = got
    if want:
        entry["published_sha256"] = want
        if want.lower() != got.lower():
            entry["status"] = "digest-mismatch"
            return False, "sha256 does not match the published digest"
        entry["status"] = "verified"
        return True, "sha256 verified against the release digest"
    entry["status"] = "recorded"
    return True, "no published digest; sha256 recorded for next time"


def register_source_in_db(release_tag=""):
    """Record GO-PDFs as a question source, so imports can be traced to it."""
    try:
        from core import db as database
        import ingest
    except ImportError:
        return None
    conn = database.init()
    try:
        ingest.register_source(
            conn,
            "go-pdfs",
            "GATE Overflow PDFs (GitHub Releases)",
            kind="release",
            url="https://github.com/%s/releases" % REPO,
            licence_note="Public GitHub release assets. Downloaded directly, never "
            "scraped from web pages.",
            trust=0.85,
        )
        ingest.touch_source(conn, "go-pdfs", "last_fetch_at")
        return "go-pdfs"
    finally:
        conn.close()


def download(asset, out_dir, token=None):
    """Stream to disk with resume, so a dropped connection is not fatal."""
    name = asset["name"]
    url = asset["browser_download_url"]
    total = asset["size"]
    dest = os.path.join(out_dir, name)
    part = dest + ".part"

    if os.path.isfile(dest) and os.path.getsize(dest) == total:
        print("  %-46s already complete, skipping" % name)
        return dest

    have = os.path.getsize(part) if os.path.isfile(part) else 0
    if have > total:
        os.remove(part)
        have = 0

    headers = {"User-Agent": "gitgrind-fetch", "Accept": "application/octet-stream"}
    if token:
        headers["Authorization"] = "Bearer %s" % token
    if have:
        headers["Range"] = "bytes=%d-" % have
        print("  %-46s resuming at %s" % (name, human(have)))
    else:
        print("  %-46s %s" % (name, human(total)))

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            if have and resp.status == 200:
                # server ignored the range, start over
                have = 0
            mode = "ab" if have else "wb"
            done = have
            start = time.time()
            with open(part, mode) as fh:
                while True:
                    chunk = resp.read(262144)
                    if not chunk:
                        break
                    fh.write(chunk)
                    done += len(chunk)
                    if total:
                        pct = done / total * 100
                        rate = done - have
                        elapsed = max(time.time() - start, 0.001)
                        sys.stdout.write(
                            "\r      %5.1f%%  %9s / %-9s  %6.1f MB/s"
                            % (pct, human(done), human(total), rate / elapsed / 1048576)
                        )
                        sys.stdout.flush()
            sys.stdout.write("\n")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
        print("\n      failed: %s" % exc)
        print("      run the same command again to resume")
        return None

    actual = os.path.getsize(part)
    if total and actual != total:
        print(
            "      size mismatch (%s vs %s expected) - keeping .part, rerun to resume"
            % (human(actual), human(total))
        )
        return None
    os.replace(part, dest)
    return dest


def extract_text(pdf_path):
    txt_path = os.path.splitext(pdf_path)[0] + ".txt"
    if os.path.isfile(txt_path) and os.path.getsize(txt_path) > 1000:
        print("      text already extracted: %s" % os.path.basename(txt_path))
        return txt_path

    if shutil.which("pdftotext"):
        print("      extracting text with pdftotext...")
        out = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", pdf_path, txt_path],
            capture_output=True,
        )
        if out.returncode == 0 and os.path.isfile(txt_path):
            print(
                "      wrote %s (%s)"
                % (os.path.basename(txt_path), human(os.path.getsize(txt_path)))
            )
            return txt_path
        print("      pdftotext failed: %s" % out.stderr.decode("utf-8", "replace")[:200])

    try:
        import pypdf
    except ImportError:
        print("      no pdftotext and no pypdf - skipping extraction")
        print("      install one:  pip install pypdf")
        return None

    print("      extracting text with pypdf (slower on big books)...")
    reader = pypdf.PdfReader(pdf_path)
    n = len(reader.pages)
    with open(txt_path, "w", encoding="utf-8") as fh:
        for i, page in enumerate(reader.pages, 1):
            fh.write((page.extract_text() or "") + "\n")
            if i % 50 == 0 or i == n:
                sys.stdout.write("\r      page %d / %d" % (i, n))
                sys.stdout.flush()
    sys.stdout.write("\n")
    print(
        "      wrote %s (%s)"
        % (os.path.basename(txt_path), human(os.path.getsize(txt_path)))
    )
    return txt_path


def main():
    ap = argparse.ArgumentParser(description="Fetch GATE Overflow PDF releases.")
    ap.add_argument(
        "--list", action="store_true", help="show releases and assets, download nothing"
    )
    ap.add_argument("--tag", help="release tag to download (see --list)")
    ap.add_argument(
        "--only",
        nargs="+",
        metavar="TEXT",
        help="only assets whose filename contains one of these (e.g. vol1)",
    )
    ap.add_argument(
        "--dir", default=DEFAULT_DIR, help="download directory (default papers/)"
    )
    ap.add_argument(
        "--extract", action="store_true", help="also produce .txt next to each PDF"
    )
    ap.add_argument("--token", help="GitHub token, only needed if rate limited")
    ap.add_argument(
        "--index-only",
        action="store_true",
        help="record asset metadata in papers/manifest.json and exit, "
        "downloading nothing",
    )
    ap.add_argument(
        "--verify",
        action="store_true",
        help="re-check the sha256 of everything already downloaded",
    )
    ap.add_argument(
        "--manifest",
        action="store_true",
        help="print what has been downloaded so far and exit",
    )
    args = ap.parse_args()

    if args.manifest:
        data = load_manifest()
        if not data["assets"]:
            print("Nothing downloaded yet. papers/manifest.json is empty.")
            return 0
        print("\n  %-46s %10s %-16s %s" % ("file", "size", "status", "sha256 (first 16)"))
        for name, e in sorted(data["assets"].items()):
            print(
                "  %-46s %10s %-16s %s"
                % (
                    name[:46],
                    human(e.get("size", 0)),
                    e.get("status", "-"),
                    (e.get("sha256") or "")[:16],
                )
            )
        print("\n  manifest: %s\n" % os.path.relpath(MANIFEST, ROOT))
        return 0

    if args.verify:
        data = load_manifest()
        bad = 0
        for name, e in sorted(data["assets"].items()):
            path = os.path.join(args.dir, name)
            if not os.path.isfile(path):
                print("  %-46s missing on disk" % name[:46])
                continue
            got = sha256_of(path)
            want = e.get("sha256")
            if want and got.lower() != want.lower():
                print("  %-46s CHANGED since download" % name[:46])
                e["status"] = "changed"
                bad += 1
            else:
                e["sha256"] = got
                print("  %-46s ok" % name[:46])
        save_manifest(data)
        return 1 if bad else 0

    if not args.list and not args.tag:
        ap.print_help()
        print("\nKnown tags:")
        for tag, desc in KNOWN_TAGS:
            print("  %-18s %s" % (tag, desc))
        return 1

    print("Querying %s ..." % REPO)
    releases = api_get(API, args.token)
    if not isinstance(releases, list):
        raise SystemExit("Unexpected API response.")

    if args.list:
        list_releases(releases)
        return 0

    rel = next((r for r in releases if r.get("tag_name") == args.tag), None)
    if rel is None:
        print("No release tagged %r. Available:" % args.tag)
        for r in releases:
            print("  %s" % r.get("tag_name"))
        return 1

    assets = [a for a in (rel.get("assets") or []) if is_book(a)]
    for a in assets:
        a["_tag"] = args.tag
    if args.only:
        wanted = [s.lower() for s in args.only]
        assets = [a for a in assets if any(w in a["name"].lower() for w in wanted)]
    if not assets:
        print("Nothing to download for that tag and filter.")
        return 1

    manifest = load_manifest()

    if args.index_only:
        # Metadata only: useful for recording what a release contains without
        # pulling hundreds of megabytes, and for planning an import later.
        for a in assets:
            manifest["assets"].setdefault(a["name"], {}).update(
                name=a["name"],
                size=a["size"],
                tag=args.tag,
                url=a.get("browser_download_url", ""),
                published_sha256=expected_digest(a),
                status="indexed",
            )
        save_manifest(manifest)
        register_source_in_db(args.tag)
        print(
            "\n  Indexed %d asset(s) from %s into %s. Nothing downloaded."
            % (len(assets), args.tag, os.path.relpath(MANIFEST, ROOT))
        )
        print("  Download later with the same command minus --index-only.\n")
        return 0

    os.makedirs(args.dir, exist_ok=True)
    total = sum(a["size"] for a in assets)
    print(
        "\n%s: %d file(s), %s total, into %s\n"
        % (args.tag, len(assets), human(total), os.path.relpath(args.dir, ROOT))
    )

    got, failed = [], []
    for a in assets:
        path = download(a, args.dir, args.token)
        if not path:
            failed.append(a["name"])
            continue
        ok, note = verify(path, a, manifest)
        print("      %s" % note)
        if not ok:
            failed.append(a["name"])
            continue
        got.append(path)
        if args.extract and path.lower().endswith(".pdf"):
            txt = extract_text(path)
            if txt:
                manifest["assets"][a["name"]]["text"] = os.path.relpath(txt, ROOT)

    save_manifest(manifest)
    source = register_source_in_db(args.tag)

    print(
        "\n  %d of %d file(s) ready in %s"
        % (len(got), len(assets), os.path.relpath(args.dir, ROOT))
    )
    print("  manifest: %s" % os.path.relpath(MANIFEST, ROOT))
    if source:
        print(
            "  source registered as '%s' - pass --source %s when importing"
            % (source, source)
        )
    if failed:
        print("\n  %d file(s) need another run:" % len(failed))
        for name in failed:
            print("    %s" % name)
    if got:
        print("\n  Next, see what the structure looks like before importing:")
        target = os.path.relpath(
            os.path.splitext(got[0])[0] + (".txt" if args.extract else ".pdf"), ROOT
        )
        print("    python tools/import_questions.py --probe %s" % target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
