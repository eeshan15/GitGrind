#!/usr/bin/env python3
"""Second round of math-rendering fixes for GitGrind.

Fixes two things visible after the first KaTeX patch:

1. RED LATEX. Options whose LaTeX did not survive extraction (a half
   \\begin{array}, unbalanced braces) were rendered by KaTeX as red error
   markup, which is harder to read than the raw source it replaced. Errors now
   fall back to the plain source text instead.

2. BLANK OPTION BOXES. .review-opt is display:flex, so the math span became a
   flex item and could shrink to nothing, leaving an option box that looked
   empty even though it had content. It is now given flex sizing and allowed to
   scroll rather than collapse. Options that really are empty say so instead of
   rendering as a bare box.

Safe to run twice. Run from the GitGrind directory:

    .venv\\Scripts\\python.exe fix_math_render.py
"""

import io
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

OLD_RENDER = """          window.katex.render(expr, span, { throwOnError: false, trust: false, strict: 'ignore' });
        } catch (e) {
          span.appendChild(document.createTextNode(part));
        }
        host.appendChild(span);"""

NEW_RENDER = """          /* throwOnError so a broken source raises here instead of rendering
             itself back out in red. Extraction leaves plenty of malformed
             LaTeX, and a wall of red error markup is harder to read than the
             raw text it was trying to replace. The node stays detached until
             the render succeeds, so a partial failure never reaches the page. */
          window.katex.render(expr, span, { throwOnError: true, trust: false, strict: 'ignore' });
          host.appendChild(span);
        } catch (e) {
          const raw = document.createElement('span');
          raw.className = 'math-raw';
          raw.title = 'This formula did not survive extraction from the PDF.';
          raw.appendChild(document.createTextNode(part));
          host.appendChild(raw);
        }"""

# Empty options should say why they are empty rather than render as a bare box.
OLD_OPT_A = """        q.options.forEach((o, i) => opts.appendChild(el('div', { class: 'review-opt' }, [
          el('b', {}, ['ABCD'[i] || String(i + 1)]), GG.mathText(String(o)),
        ])));"""
NEW_OPT_A = """        q.options.forEach((o, i) => opts.appendChild(el('div', { class: 'review-opt' }, [
          el('b', {}, ['ABCD'[i] || String(i + 1)]),
          String(o).trim() ? GG.mathText(String(o))
            : el('i', { class: 'opt-missing', text: 'not extracted' }),
        ])));"""

OLD_OPT_B = """      q.options.forEach((o, i) => opts.appendChild(el('div', { class: 'review-opt' }, [
        el('b', {}, ['ABCD'[i] || String(i + 1)]), GG.mathText(String(o)),
      ])));"""
NEW_OPT_B = """      q.options.forEach((o, i) => opts.appendChild(el('div', { class: 'review-opt' }, [
        el('b', {}, ['ABCD'[i] || String(i + 1)]),
        String(o).trim() ? GG.mathText(String(o))
          : el('i', { class: 'opt-missing', text: 'not extracted' }),
      ])));"""

EXTRA_CSS = """
/* .review-opt is display:flex, so the math span becomes a flex item and would
   otherwise shrink past its content and read as an empty option box. Give it
   room, let it scroll instead of collapsing, and mark the two states where the
   source did not survive extraction. */
.review-opt .math-text { flex: 1 1 auto; min-width: 0; overflow-x: auto; }
.q-text .math-text, .review-q .math-text { overflow-wrap: anywhere; }
.math-raw { font-family: var(--mono); font-size: .92em; color: var(--weak, #d29922); }
.opt-missing { color: var(--weak, #d29922); font-size: .92em; }
"""


def main():
    if not os.path.isdir(os.path.join(ROOT, "static", "js")):
        sys.exit("Run this from the GitGrind directory (no static/js found here).")

    edits = [
        ("static/js/core.js", "LaTeX error fallback", "math-raw", OLD_RENDER, NEW_RENDER),
        ("static/js/bank.js", "review card options", "opt-missing", OLD_OPT_A, NEW_OPT_A),
        ("static/js/bank.js", "pending detail options", None, OLD_OPT_B, NEW_OPT_B),
    ]

    applied = skipped = 0
    cache = {}

    for path, label, marker, old, new in edits:
        full = os.path.join(ROOT, path)
        if full not in cache:
            with io.open(full, encoding="utf-8", newline="") as fh:
                raw = fh.read()
            cache[full] = [raw, "\r\n" if "\r\n" in raw else "\n"]
        text, nl = cache[full]

        if text.count(new.replace("\n", nl)) >= 1:
            print("  = %-18s %s (already applied)" % (path, label))
            skipped += 1
            continue

        target = old.replace("\n", nl)
        count = text.count(target)
        if count != 1:
            sys.exit(
                "  x %s %s: expected one match, found %d.\n"
                "    Is apply_katex_patch.py applied first?" % (path, label, count)
            )
        cache[full][0] = text.replace(target, new.replace("\n", nl), 1)
        print("  + %-18s %s" % (path, label))
        applied += 1

    for full, (text, _nl) in cache.items():
        with io.open(full, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)

    css = os.path.join(ROOT, "static", "css", "style.css")
    with io.open(css, encoding="utf-8", newline="") as fh:
        body = fh.read()
    if ".opt-missing" in body:
        print("  = static/css/style.css  layout CSS (already applied)")
        skipped += 1
    else:
        nl = "\r\n" if "\r\n" in body else "\n"
        with io.open(css, "a", encoding="utf-8", newline="") as fh:
            fh.write(EXTRA_CSS.replace("\n", nl))
        print("  + static/css/style.css  layout CSS")
        applied += 1

    print("\n  %d edit(s) applied, %d already in place." % (applied, skipped))
    print("  Restart the app, then hard-refresh the browser (Ctrl+F5).")
    return 0


if __name__ == "__main__":
    sys.exit(main())