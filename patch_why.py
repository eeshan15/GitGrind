#!/usr/bin/env python3
"""Show why each question was chosen. The reason is already in the payload.

quiz.select attaches a reason to every question it picks - "you got this wrong
before and it is due again", "high-risk topic (72/100 risk)", "not served
before" - and build_quiz carries it through as pub["why"]. practice.js never
reads it. That is the third thing in this codebase computed, stored, sent and
then dropped on the floor, after the subtopic field and the session-end
breakdown.

It matters here because of what the repeat investigation turned up. Five
mechanisms were ruled out by measurement and the build path does not repeat;
tracing an actual repeated question showed it had been answered twice, wrong
both times, and was one day overdue in the revision queue. Serving it again is
correct - it is the entire point of the schedule - but the app says nothing, so
a deliberate review is indistinguishable from a random repeat. The complaint
was about the silence, not the selection.

A question that says "you got this wrong on 27 Aug and it is due again" is not
a repeat. It is the app keeping its promise, out loud.

One edit, in questionBlock, which is enough for both places: the result card
builds each row by calling questionBlock too, so the reason appears while
answering and again on the result card, where "it is due again" is the answer
to "why did I just see this again". It uses the .why class the plan and
readiness screens already use for exactly this purpose.

Nothing changes server-side; the data has been there all along.

CRLF-safe and idempotent. Run from the repo root:  python patch_why.py
"""
import io
import os
import sys

EDITS = [
    ('static/js/practice.js',
     "      bookmark(q),\n"
     "    ]));\n"
     "    wrap.appendChild(el('div', { class: 'q-text' }, [mathText(q.text)]));",

     "      bookmark(q),\n"
     "    ]));\n"
     "    /* The selector's own reason, which has been in the payload as \"why\"\n"
     "       since build_quiz started recording it and has never been shown. A\n"
     "       question that explains itself - \"you got this wrong before and it\n"
     "       is due again\" - reads as a decision rather than a coincidence.\n"
     "       No locked check: the result card renders through this same\n"
     "       function, and that is where the question gets asked. */\n"
     "    if (q.why) {\n"
     "      wrap.appendChild(el('p', { class: 'why', style: 'margin-bottom:12px' },\n"
     "        [el('b', {}, ['Why this one: ']), q.why]));\n"
     "    }\n"
     "    wrap.appendChild(el('div', { class: 'q-text' }, [mathText(q.text)]));"),
]


def main():
    changed = skipped = 0
    for path, old, new in EDITS:
        if not os.path.isfile(path):
            sys.exit("missing %s - run this from the repo root" % path)
        s = io.open(path, encoding="utf-8", newline="").read()
        crlf = "\r\n" in s
        o = old.replace("\n", "\r\n") if crlf else old
        n = new.replace("\n", "\r\n") if crlf else new
        if n in s:
            print("  skip    %-24s already applied" % path)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d times, expected 1"
                     % (path, s.count(o)))
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-24s ok" % path)
        changed += 1
    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    if changed:
        print("  Hard-refresh the browser. Build a set and the first line under")
        print("  the chips should say why that question is there.")
    return 0


if __name__ == "__main__":
    sys.exit(main())