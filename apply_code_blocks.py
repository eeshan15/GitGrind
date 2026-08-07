#!/usr/bin/env python3
"""Render code listings in GitGrind instead of mangling them into the prose.

275 questions in the MinerU bank are built around a C / SQL / Pascal listing.
Those arrived as fenced markdown inside the question text, so the fence markers
showed up literally and every line of the program collapsed onto one - which is
what made them look like a figure that had failed to load. The converter now
lifts each listing into its own `code_blocks` field; this teaches the app to
serve and render them.

Safe to run twice. Run from the GitGrind directory, AFTER apply_katex_patch.py
and fix_math_render.py:

    .venv\\Scripts\\python.exe apply_code_blocks.py
"""

import io
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

PUBLIC_CODE = '''def public_code(q):
    """Code listings as the UI should see them.

    A listing is data, not markup: it is handed over as a plain string and the
    UI puts it in a text node, so nothing inside a program can become markup.
    """
    out = []
    blocks = q.get("code_blocks")
    if not isinstance(blocks, list):
        return out
    for b in blocks:
        if not isinstance(b, dict):
            continue
        code = str(b.get("code") or "")
        if not code.strip():
            continue
        out.append(dict(code=code[:4000], lang=str(b.get("lang") or "")[:20]))
    return out


'''

CODE_HELPER = '''  /* --------------------------- code listings ----------------------------- */
  /* Many GATE questions are built around a C or SQL listing. Those arrive as
     q.code_blocks: [{code, lang}] and must keep their line breaks - a program
     squashed onto one line is unreadable. The code goes in as a text node, so a
     listing can never be interpreted as markup no matter what it contains. */
  function codeBlocks(q) {
    const list = Array.isArray(q && q.code_blocks) ? q.code_blocks : [];
    if (!list.length) return null;
    const box = el('div', { class: 'q-code' });
    list.forEach(b => {
      if (!b || !b.code) return;
      const pre = el('pre', { class: 'q-code-pre' });
      pre.appendChild(document.createTextNode(String(b.code)));
      if (b.lang) pre.setAttribute('data-lang', String(b.lang));
      box.appendChild(pre);
    });
    return box.children.length ? box : null;
  }

'''

CSS = """
/* ------------------------------------------------------------------------- */
/* Code listings                                                             */
/* A program must keep its line breaks and its column alignment, so this is   */
/* the one place in a question where whitespace is significant.               */
/* ------------------------------------------------------------------------- */
.q-code { margin: 12px 0 4px; }

.q-code-pre {
  margin: 0 0 8px;
  padding: 10px 12px;
  overflow-x: auto;
  white-space: pre;
  tab-size: 4;
  font-family: var(--mono);
  font-size: .88rem;
  line-height: 1.45;
  background: var(--bg2, #0d1117);
  border: 1px solid var(--line, #30363d);
  border-left: 3px solid var(--accent, #2f81f7);
  border-radius: 5px;
}

.q-code-pre[data-lang]::before {
  content: attr(data-lang);
  display: block;
  margin-bottom: 6px;
  font-size: .72rem;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--dim, #8b949e);
}
"""

EDITS = [
    ("core/content.py", "public_code() helper", "def public_code(",
     'def validate_question(q):\n    """Return a list of problems. Empty list means the question is servable.',
     PUBLIC_CODE +
     'def validate_question(q):\n    """Return a list of problems. Empty list means the question is servable.'),

    ("core/content.py", "code in public payload", 'out["code_blocks"] = code',
     '    figures = public_figures(q)\n'
     '    if figures:\n'
     '        out["figure_assets"] = figures',
     '    figures = public_figures(q)\n'
     '    if figures:\n'
     '        out["figure_assets"] = figures\n'
     '    code = public_code(q)\n'
     '    if code:\n'
     '        out["code_blocks"] = code'),

    ("core/content.py", "code in pending payload", "code_blocks=public_code(q),",
     "                figure_assets=public_figures(q),",
     "                figure_assets=public_figures(q),\n"
     "                code_blocks=public_code(q),"),

    ("core/content.py", "hydrate default", 'item.setdefault("code_blocks", [])',
     '    item.setdefault("figure_assets", [])',
     '    item.setdefault("figure_assets", [])\n'
     '    item.setdefault("code_blocks", [])'),

    ("static/js/core.js", "codeBlocks() helper", "function codeBlocks(",
     "  function figures(q) {",
     CODE_HELPER + "  function figures(q) {"),

    ("static/js/core.js", "export codeBlocks", "mathText, codeBlocks,",
     "empty, figures, mathText, splashDone,",
     "empty, figures, mathText, codeBlocks, splashDone,"),

    ("static/js/practice.js", "import codeBlocks", "mathText, codeBlocks }",
     "growBars, figures, mathText } = GG;",
     "growBars, figures, mathText, codeBlocks } = GG;"),

    ("static/js/practice.js", "quiz listing", "const code = codeBlocks(q);",
     "    const figs = figures(q);\n    if (figs) wrap.appendChild(figs);",
     "    /* Listing first, then figure: that is the printed order, and the code is\n"
     "       usually what the question is asking about. */\n"
     "    const code = codeBlocks(q);\n"
     "    if (code) wrap.appendChild(code);\n"
     "    const figs = figures(q);\n    if (figs) wrap.appendChild(figs);"),

    ("static/js/bank.js", "review card listing", "const rCode = GG.codeBlocks(q);",
     "      const rFigs = GG.figures(q);\n      if (rFigs) card.appendChild(rFigs);",
     "      const rCode = GG.codeBlocks(q);\n      if (rCode) card.appendChild(rCode);\n"
     "      const rFigs = GG.figures(q);\n      if (rFigs) card.appendChild(rFigs);"),

    ("static/js/bank.js", "pending detail listing", "const pCode = GG.codeBlocks(q);",
     "    const pFigs = GG.figures(q);\n    if (pFigs) wrap.appendChild(pFigs);",
     "    const pCode = GG.codeBlocks(q);\n    if (pCode) wrap.appendChild(pCode);\n"
     "    const pFigs = GG.figures(q);\n    if (pFigs) wrap.appendChild(pFigs);"),
]


def main():
    if not os.path.isdir(os.path.join(ROOT, "static", "js")):
        sys.exit("Run this from the GitGrind directory.")

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
                "  x %s %s: expected one match, found %d.\n"
                "    Are apply_katex_patch.py and fix_math_render.py applied first?"
                % (path, label, count)
            )
        cache[full][0] = text.replace(target, new.replace("\n", nl), 1)
        print("  + %-22s %s" % (path, label))
        applied += 1

    for full, (text, _nl) in cache.items():
        with io.open(full, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)

    css = os.path.join(ROOT, "static", "css", "style.css")
    with io.open(css, encoding="utf-8", newline="") as fh:
        body = fh.read()
    if ".q-code-pre" in body:
        print("  = static/css/style.css   listing CSS (already applied)")
        skipped += 1
    else:
        nl = "\r\n" if "\r\n" in body else "\n"
        with io.open(css, "a", encoding="utf-8", newline="") as fh:
            fh.write(CSS.replace("\n", nl))
        print("  + static/css/style.css   listing CSS")
        applied += 1

    print("\n  %d edit(s) applied, %d already in place." % (applied, skipped))
    print("  next: re-run the converter, then app.py --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())