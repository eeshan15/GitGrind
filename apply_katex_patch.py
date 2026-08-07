#!/usr/bin/env python3
"""Apply the KaTeX math-rendering edits to GitGrind's UI files.

Windows has no `patch` and `git apply` rejects the diff over line-ending
strictness, so this does the same five edits directly. It is safe to run twice:
every edit is checked first and skipped if already present, so a half-applied
tree can be finished rather than corrupted.

Run from the GitGrind directory:

    .venv\\Scripts\\python.exe apply_katex_patch.py
"""

import io
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

MATH_HELPER = '''  /* ----------------------------- math text ------------------------------- */
  /* Extracted questions carry LaTeX inline as literal $...$ source (MinerU's
     extraction format, not markdown). el()'s text: attribute sets textContent,
     so that source used to show up as raw "$\\Theta ( n )$" on screen instead of
     a rendered symbol.

     This renders each $...$ span through KaTeX, which builds its own DOM nodes
     rather than being handed a string to parse as HTML - so a malformed or
     hostile LaTeX source degrades to plain text (via throwOnError: false) and
     never becomes a way to inject markup. trust: false (KaTeX's default) keeps
     \\href and similar commands from reaching out to arbitrary URLs. Everything
     outside a $...$ pair is still added as a plain text node, exactly as
     before - only the math spans get special handling. */
  function mathText(text) {
    const host = document.createElement('span');
    host.className = 'math-text';
    const str = text === null || text === undefined ? '' : String(text);
    if (!str) return host;
    if (!window.katex) {
      host.appendChild(document.createTextNode(str));
      return host;
    }
    str.split(/(\\$[^$\\n]+\\$)/g).forEach(part => {
      if (!part) return;
      if (part.length > 1 && part.charAt(0) === '$' && part.charAt(part.length - 1) === '$') {
        const expr = part.slice(1, -1).trim();
        const span = document.createElement('span');
        try {
          window.katex.render(expr, span, { throwOnError: false, trust: false, strict: 'ignore' });
        } catch (e) {
          span.appendChild(document.createTextNode(part));
        }
        host.appendChild(span);
      } else {
        host.appendChild(document.createTextNode(part));
      }
    });
    return host;
  }

'''

MATH_CSS = '''
/* ------------------------------------------------------------------------- */
/* Math text (KaTeX)                                                         */
/* Extracted questions carry $...$ LaTeX source; core.js renders it in place */
/* through KaTeX rather than as raw text. Keep it inline with the paragraph.  */
/* ------------------------------------------------------------------------- */
.math-text { display: inline; }
.math-text .katex { font-size: 1.05em; }
.math-text .katex-error { color: var(--bad, #b4232a); }
'''

# (path, description, marker-already-present, old, new)
EDITS = [
    (
        "static/index.html", "KaTeX stylesheet",
        '/vendor/katex/katex.min.css',
        '<link rel="stylesheet" href="/css/style.css">',
        '<link rel="stylesheet" href="/css/style.css">\n'
        '<link rel="stylesheet" href="/vendor/katex/katex.min.css">',
    ),
    (
        "static/index.html", "KaTeX script",
        '/vendor/katex/katex.min.js',
        '<script src="/js/core.js"></script>',
        '<script src="/vendor/katex/katex.min.js"></script>\n'
        '<script src="/js/core.js"></script>',
    ),
    (
        "static/js/core.js", "mathText() helper",
        'function mathText(',
        '  function figures(q) {',
        MATH_HELPER + '  function figures(q) {',
    ),
    (
        "static/js/core.js", "export mathText",
        'empty, figures, mathText,',
        'key, shortcutHelp, band, clamp, pct, empty, figures, splashDone,',
        'key, shortcutHelp, band, clamp, pct, empty, figures, mathText, splashDone,',
    ),
    (
        "static/js/practice.js", "import mathText",
        'growBars, figures, mathText }',
        '  const { $, $$, el, esc, ago, growBars, figures } = GG;',
        '  const { $, $$, el, esc, ago, growBars, figures, mathText } = GG;',
    ),
    (
        "static/js/practice.js", "question text",
        "class: 'q-text' }, [mathText(",
        "wrap.appendChild(el('div', { class: 'q-text', text: q.text }));",
        "wrap.appendChild(el('div', { class: 'q-text' }, [mathText(q.text)]));",
    ),
    (
        "static/js/practice.js", "quiz options",
        "class: 'opt-txt' }, [mathText(",
        "          el('span', { class: 'opt-txt', text: text }),",
        "          el('span', { class: 'opt-txt' }, [mathText(text)]),",
    ),
    (
        "static/js/practice.js", "explanation",
        "class: 'q-explain' }, [mathText(",
        "if (q.explain) box.appendChild(el('div', { class: 'q-explain', text: q.explain }));",
        "if (q.explain) box.appendChild(el('div', { class: 'q-explain' }, [mathText(q.explain)]));",
    ),
    (
        "static/js/bank.js", "review card text",
        "class: 'review-q' }, [GG.mathText(q.text || '(no text)')",
        "      card.appendChild(el('div', { class: 'review-q', text: q.text || '(no text)' }));",
        "      card.appendChild(el('div', { class: 'review-q' }, "
        "[GG.mathText(q.text || '(no text)')]));",
    ),
    (
        "static/js/bank.js", "review card options",
        "['ABCD'[i] || String(i + 1)]), GG.mathText(String(o)),\n        ])));\n        card.appendChild(opts);",
        "        q.options.forEach((o, i) => opts.appendChild(el('div', { class: 'review-opt' }, [\n"
        "          el('b', {}, ['ABCD'[i] || String(i + 1)]), String(o),\n"
        "        ])));\n"
        "        card.appendChild(opts);",
        "        q.options.forEach((o, i) => opts.appendChild(el('div', { class: 'review-opt' }, [\n"
        "          el('b', {}, ['ABCD'[i] || String(i + 1)]), GG.mathText(String(o)),\n"
        "        ])));\n"
        "        card.appendChild(opts);",
    ),
    (
        "static/js/bank.js", "pending detail text",
        "class: 'review-q' }, [GG.mathText(q.text || '(no text extracted)')",
        "wrap.appendChild(el('div', { class: 'review-q', text: q.text || '(no text extracted)' }));",
        "wrap.appendChild(el('div', { class: 'review-q' }, "
        "[GG.mathText(q.text || '(no text extracted)')]));",
    ),
    (
        "static/js/bank.js", "pending detail options",
        "['ABCD'[i] || String(i + 1)]), GG.mathText(String(o)),\n      ])));\n      wrap.appendChild(opts);",
        "      q.options.forEach((o, i) => opts.appendChild(el('div', { class: 'review-opt' }, [\n"
        "        el('b', {}, ['ABCD'[i] || String(i + 1)]), String(o),\n"
        "      ])));\n"
        "      wrap.appendChild(opts);",
        "      q.options.forEach((o, i) => opts.appendChild(el('div', { class: 'review-opt' }, [\n"
        "        el('b', {}, ['ABCD'[i] || String(i + 1)]), GG.mathText(String(o)),\n"
        "      ])));\n"
        "      wrap.appendChild(opts);",
    ),
]


def main():
    if not os.path.isdir(os.path.join(ROOT, "static", "js")):
        sys.exit("Run this from the GitGrind directory (no static/js found here).")

    katex = os.path.join(ROOT, "static", "vendor", "katex", "katex.min.js")
    if not os.path.isfile(katex):
        print("  ! static/vendor/katex/katex.min.js is missing.")
        print("    Unzip katex-vendor.zip into static\\ first, then re-run.")
        sys.exit(1)

    applied = skipped = 0
    cache = {}

    for path, label, marker, old, new in EDITS:
        full = os.path.join(ROOT, path)
        if full not in cache:
            with io.open(full, encoding="utf-8", newline="") as fh:
                raw = fh.read()
            cache[full] = [raw, "\r\n" if "\r\n" in raw else "\n"]
        text, nl = cache[full]

        if marker.replace("\n", nl) in text:
            print("  = %-22s %s (already applied)" % (path, label))
            skipped += 1
            continue

        target = old.replace("\n", nl)
        count = text.count(target)
        if count != 1:
            sys.exit(
                "  x %s %s: expected exactly one match, found %d.\n"
                "    The file differs from what this patch expects - is the first "
                "patch (gitgrind-mineru-figures) applied?" % (path, label, count)
            )
        cache[full][0] = text.replace(target, new.replace("\n", nl), 1)
        print("  + %-22s %s" % (path, label))
        applied += 1

    for full, (text, _nl) in cache.items():
        with io.open(full, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)

    # CSS is appended rather than replaced, so it gets its own idempotency check.
    css = os.path.join(ROOT, "static", "css", "style.css")
    with io.open(css, encoding="utf-8", newline="") as fh:
        body = fh.read()
    if ".math-text" in body:
        print("  = static/css/style.css    math CSS (already applied)")
        skipped += 1
    else:
        nl = "\r\n" if "\r\n" in body else "\n"
        with io.open(css, "a", encoding="utf-8", newline="") as fh:
            fh.write(MATH_CSS.replace("\n", nl))
        print("  + static/css/style.css    math CSS")
        applied += 1

    print("\n  %d edit(s) applied, %d already in place." % (applied, skipped))
    print("  next: .venv\\Scripts\\python.exe app.py --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())