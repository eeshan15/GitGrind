#!/usr/bin/env python3
"""Move subtopic_slugs to the end of quiz.select's signature.

patch_subtopic.py added the parameter between topic_slugs and kinds, which
reads well and is wrong. build_quiz calls select positionally in four places:

    picked = select(
        conn, purpose, count, subject_slug, topic_slugs, kinds,
        metrics=metrics, topic_health=topic_health,
    )

so the sixth positional argument, kinds, has been binding to subtopic_slugs
ever since. When kinds is None - ordinary practice - subtopic_slugs is None too
and nothing looks wrong, which is why this went unnoticed. When a kind is
actually set, as it is whenever a set is built with the "previous year" or
"DPP" filter, subtopic_slugs becomes ["pyq"] or ["dpp"], no question carries a
subtopic with that name, and the set comes back empty. Meanwhile kinds stays
None, so the filter the person asked for is not applied either.

The fix puts subtopic_slugs last, after seed, rather than merely after kinds.
Anywhere earlier and the same mistake is one future positional argument away;
at the end there is no positional slot in front of it to shift.

tools/subtopic_verify.py did not catch this because it only ever called select
with keyword arguments. That gap is closed by tools/arity_check.py, which reads
the call sites instead of the signature.

Two edits in core/quiz.py: remove the parameter from its current position, add
it at the end. Nothing else moves and no call site changes.

CRLF-safe and idempotent. Run from the repo root:  python patch_argorder.py
"""
import io
import os
import sys

EDITS = [
    # ---- 1. take it out of the positional run --------------------------
    ('core/quiz.py',
     '    subject_slug=None,\n'
     '    topic_slugs=None,\n'
     '    subtopic_slugs=None,\n'
     '    kinds=None,',

     '    subject_slug=None,\n'
     '    topic_slugs=None,\n'
     '    kinds=None,'),

    # ---- 2. put it after the last parameter ----------------------------
    ('core/quiz.py',
     '    cooldown_days=None,\n'
     '    seed=None,\n'
     '):',

     '    cooldown_days=None,\n'
     '    seed=None,\n'
     '    # Last on purpose. build_quiz calls this function positionally, so a\n'
     '    # parameter inserted anywhere earlier silently captures the argument\n'
     '    # meant for the one after it - which is exactly what happened when\n'
     '    # this sat between topic_slugs and kinds. Keyword-only in practice.\n'
     '    subtopic_slugs=None,\n'
     '):'),
]


def check(path):
    """Report which parameter each positional call site's last argument hits."""
    import re

    src = io.open(path, encoding="utf-8", newline="").read()
    sig = re.search(r"def select\(\s*\r?\n(.*?)\r?\n\):", src, re.S)
    if not sig:
        return None
    params = ["conn"] + [
        p.strip().split("=")[0].strip().rstrip(",")
        for p in sig.group(1).strip().splitlines()
        if p.strip() and not p.strip().startswith("#")
        and p.strip().split("=")[0].strip().rstrip(",") != "conn"
    ]
    worst = 0
    for m in re.finditer(r"select\(\s*\r?\n((?:[^\n]*\r?\n)*?)\s*\)", src):
        args = [a.strip().rstrip(",") for a in m.group(1).strip().splitlines()
                if a.strip()]
        pos = [a for a in args if "=" not in a and not a.startswith("#")]
        worst = max(worst, len(pos))
    return params, worst


def main():
    path = "core/quiz.py"
    if not os.path.isfile(path):
        sys.exit("missing %s - run this from the repo root" % path)

    before = check(path)
    if before:
        params, worst = before
        if worst:
            print("  before: %d positional arg(s) at the widest call site,"
                  " landing on %r" % (worst, params[worst - 1]))

    changed = skipped = 0
    for target, old, new in EDITS:
        s = io.open(target, encoding="utf-8", newline="").read()
        crlf = "\r\n" in s
        o = old.replace("\n", "\r\n") if crlf else old
        n = new.replace("\n", "\r\n") if crlf else new
        if n in s:
            print("  skip    %-20s already applied" % target)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d times, expected 1."
                     " Run patch_subtopic.py first." % (target, s.count(o)))
        io.open(target, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-20s ok" % target)
        changed += 1

    after = check(path)
    if after:
        params, worst = after
        print("\n  after:  %d positional arg(s) at the widest call site,"
              " landing on %r" % (worst, params[worst - 1]))
        idx = params.index("subtopic_slugs") if "subtopic_slugs" in params else -1
        if idx >= 0:
            print("  subtopic_slugs is parameter %d; nothing passes more than %d"
                  " positionally" % (idx, worst - 1))
            if idx < worst:
                sys.exit("  ERROR   still in the positional run")

    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    if changed:
        print("  Restart the app. Then build a set with the previous-year or")
        print("  DPP filter on - it should return questions again.")
    return 0


if __name__ == "__main__":
    sys.exit(main())