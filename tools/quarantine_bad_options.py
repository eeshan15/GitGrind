#!/usr/bin/env python3
"""Quarantine options that a formula-OCR pass destroyed.

WHY THIS EXISTS

  A previous run of tools/recover_options.py --apply overwrote roughly a thousand
  option lists with pix2tex output, and much of that output is not an option. It
  is either an empty LaTeX skeleton::

      $\\left\\lceil\\begin{array}{c}{{}}\\\\{{}}\\\\{{}}\\end{array}\\right\\rceil$

  or invalid LaTeX that KaTeX refuses and the UI then shows as raw source::

      $\\4{\\sqrt{\\left(Q^{2}+r^{2}\\right)}}$

  or the bare connective left behind when a formula never reached the text layer
  at all: four options all reading "and".

  The app's own validator passes all of these. Four options are present, the
  answer index is in range, so validate_question() sees nothing wrong and the
  selector serves them. The person then gets a question that cannot be answered.

  Questions without the options_recovered flag are, by contrast, mostly fine -
  the extraction was not the problem, the recovery was.

  This finds them by asking what a human would actually see once the LaTeX is
  stripped, marks them answer_pending, and leaves everything else alone.
  answer_pending is the flag the app already understands: such questions count
  towards coverage, are listed in the Bank tab for repair, and are never served.
  Nothing is deleted, and origin keeps the crop reference so a better OCR pass
  can still fix them properly.

USAGE

  python tools/quarantine_bad_options.py                 report
  python tools/quarantine_bad_options.py --show 15       look at examples first
  python tools/quarantine_bad_options.py --apply
  python tools/quarantine_bad_options.py --undo          lift the quarantine
"""

import argparse
import glob
import json
import os
import re
import shutil
import sys
from collections import Counter
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

BANKS = os.path.join(ROOT, "content", "banks")
QUESTIONS = os.path.join(ROOT, "content", "questions")
MARKER = "options_quarantined"

# Structural LaTeX: delimiters, environments, spacing, styling. None of it is
# content, so it comes out before deciding whether anything is left.
#
# Crucially this is a closed list, not "every backslash command". A greek letter
# or an operator IS content: stripping \Omega, \sigma and \Theta made the four
# options of an asymptotic-notation question look identical, and the question was
# perfectly answerable.
STRUCTURAL_COMMANDS = {
    "left", "right", "begin", "end", "atop", "over", "stackrel", "displaystyle",
    "textstyle", "scriptstyle", "boldsymbol", "mathbf", "mathrm", "mathit",
    "mathsf", "mathcal", "mathbb", "textbf", "textit", "text", "bf", "it", "rm",
    "cal", "quad", "qquad", "hspace", "vspace", "big", "Big", "bigg", "Bigg",
    "bigl", "bigr", "Bigl", "Bigr", "limits", "nolimits", "smash", "phantom",
    "hphantom", "vphantom", "kern", "mkern", "mspace", "thinspace", "negthinspace",
    "!", ",", ";", ":", " ", "\\",
}
COMMAND = re.compile(r"\\([a-zA-Z]+|.)")
BRACKETS = re.compile(r"[{}$&\[\]]|~")
# A LaTeX command that is not a command: a backslash followed by a digit.
BAD_COMMAND = re.compile(r"\\\d")
# Repeated empty groups - an array whose cells never got any content.
EMPTY_CELLS = re.compile(r"(\{\{\s*\}\}[\s\\&]*){2,}")
FILLER = re.compile(
    r"^(?:[\s,.:;()/\-]|and|or|only|both|neither|nor|is|are|the|of|in|to|then"
    r"|ns|s|ms|us|kb|mb|gb|bit|bits|byte|bytes|%)*$",
    re.I,
)


def visible(text):
    """Roughly what a reader would see once LaTeX markup is removed.

    Structural commands vanish; every other command is kept as its own name, so
    two options differing only by \\Omega versus \\Theta still differ here.
    """
    def sub(m):
        name = m.group(1)
        return "" if name in STRUCTURAL_COMMANDS else " %s " % name

    return " ".join(BRACKETS.sub(" ", COMMAND.sub(sub, str(text))).split())


# Large operators and decorations that need an operand to mean anything. An
# option that is nothing but these is OCR noise: a bare summation sign with
# nothing summed is not an answer to anything.
BARE_OPERATORS = {
    "sum", "prod", "coprod", "int", "iint", "oint", "bigcup", "bigcap", "bigvee",
    "bigwedge", "bigoplus", "bigotimes", "biguplus", "sqcup", "nabla", "partial",
    "otimes", "oplus", "ominus", "odot", "widehat",
    "widetilde", "hat", "tilde", "bar", "vec", "dot", "ddot", "backslash",
    "langle", "rangle", "lceil", "rceil", "lfloor", "rfloor", "vert", "Vert",
    "land", "lor", "neg", "forall", "exists", "emptyset", "cdot",
    "cdots", "ldots", "dots", "prime", "circ", "ast", "star", "dagger",
}
DELIM_LEFT = re.compile(r"\\\\left(?![a-zA-Z])")
DELIM_RIGHT = re.compile(r"\\\\right(?![a-zA-Z])")
WORD = re.compile(r"[A-Za-z]{2,}")
DIGIT = re.compile(r"\d")


def is_symbol_soup(vis):
    """True when a rendered option is only decoration, with nothing decorated."""
    tokens = [t for t in vis.split() if t]
    if not tokens:
        return True
    if DIGIT.search(vis):
        return False
    words = [t for t in tokens if WORD.fullmatch(t)]
    # Every multi-letter token is a bare operator name, and nothing else carries
    # meaning: no digits, and at most one stray letter.
    if words and all(w in BARE_OPERATORS for w in words):
        rest = [t for t in tokens if t not in words]
        return len([t for t in rest if t not in "_^,.()[]{}|"]) <= 1
    return False


def broken_indices(opts):
    """Which individual options are unreadable."""
    out = []
    for i, o in enumerate(str(x) for x in opts):
        v = visible(o)
        if (
            BAD_COMMAND.search(o)
            or EMPTY_CELLS.search(o)
            or o.count("{") != o.count("}")
            or ("\\left" in o and o.count("\\left") != o.count("\\right"))
            or not v
            or is_symbol_soup(v)
        ):
            out.append(i)
    return out


def answerable_anyway(q):
    """True when the damage is confined to distractors the answer does not need.

    A question with one unreadable distractor is degraded, not broken: the correct
    option is still there to be picked. Quarantining it would throw away a usable
    question, and there are enough of those already. It is still reported, so it
    can be repaired, but it keeps being served.
    """
    opts = q.get("options") or []
    if len(opts) < 4:
        return False
    bad = broken_indices(opts)
    if len(bad) != 1:
        return False
    answer = q.get("answer") or []
    if not answer or bad[0] in answer:
        return False
    # The set-level rules must still pass: four options that all read "and" are
    # useless even though no single one of them is malformed.
    readable = [visible(str(o)) for i, o in enumerate(opts) if i not in bad]
    if len({r for r in readable if r}) < len(readable):
        return False
    return all(not FILLER.match(r) for r in readable)


def diagnose(opts):
    """Return a reason string if this option list is not answerable, else ''."""
    opts = [str(o) for o in opts]
    if len(opts) < 2:
        return "fewer than two options"

    if any(BAD_COMMAND.search(o) for o in opts):
        return "invalid LaTeX command (renders as raw source)"
    if any(EMPTY_CELLS.search(o) for o in opts):
        return "empty LaTeX array - no content in the cells"

    # An unbalanced \left or brace means KaTeX throws and the UI falls back to
    # printing the source, which is what the screenshots show.
    for o in opts:
        if o.count("{") != o.count("}"):
            return "unbalanced braces (renders as raw source)"
        # \leftrightarrow and \leftarrow contain "\left" as a substring but are
        # complete commands, so a plain count flags perfectly good options.
        lefts = len(DELIM_LEFT.findall(o))
        rights = len(DELIM_RIGHT.findall(o))
        if lefts and lefts != rights:
            return "unbalanced \\left/\\right (renders as raw source)"

    vis = [visible(o) for o in opts]
    empty = sum(1 for v in vis if not v)
    if empty >= 2:
        return "%d option(s) render to nothing" % empty
    soup = sum(1 for v in vis if is_symbol_soup(v))
    if soup >= 2:
        return "%d option(s) are bare symbols with no operand" % soup
    informative = [v for v in vis if not FILLER.match(v)]
    if len(informative) < 2:
        return "options carry no distinguishing content"
    if len(set(vis)) < max(2, len(vis) - 1):
        return "options are indistinguishable once rendered"
    return ""


def bank_files():
    return sorted(glob.glob(os.path.join(BANKS, "*", "*.json"))) + sorted(
        glob.glob(os.path.join(QUESTIONS, "*.json"))
    )


def main():
    ap = argparse.ArgumentParser(description="Quarantine unanswerable option lists.")
    ap.add_argument("--show", type=int, default=0, help="print this many examples")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--undo", action="store_true", help="lift a previous quarantine")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="also quarantine questions whose only broken option is a distractor "
        "the answer does not need; by default those keep being served",
    )
    args = ap.parse_args()

    hits = []
    spared = []
    reasons = Counter()
    recovered_flag = Counter()
    total = 0
    quarantined_already = 0

    for path in bank_files():
        data = json.load(open(path, encoding="utf-8"))
        for q in data.get("questions", []):
            total += 1
            if q.get(MARKER):
                quarantined_already += 1
            if q.get("type") not in ("mcq", "msq"):
                continue
            if q.get("answer_pending") and not q.get(MARKER):
                continue
            why = diagnose(q.get("options") or [])
            if not why:
                continue
            if not args.strict and answerable_anyway(q):
                spared.append((path, q, why))
                continue
            hits.append((path, q, why))
            reasons[why] += 1
            recovered_flag[
                "options_recovered set" if (q.get("origin") or {}).get(
                    "options_recovered"
                ) else "no recovery flag"
            ] += 1

    if args.undo:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        lifted = 0
        for path in bank_files():
            data = json.load(open(path, encoding="utf-8"))
            touched = 0
            for q in data.get("questions", []):
                if q.pop(MARKER, None):
                    q.pop("answer_pending", None)
                    touched += 1
            if touched:
                shutil.copy2(path, "%s.%s.bak" % (path, stamp))
                tmp = path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=1)
                os.replace(tmp, path)
                lifted += touched
        print("\n  lifted quarantine on %d question(s)\n" % lifted)
        return 0

    print("\nbank: %d questions" % total)
    if quarantined_already:
        print("already quarantined: %d" % quarantined_already)
    print("unanswerable option lists: %d" % len(hits))
    if spared:
        print(
            "kept anyway: %d  (one broken distractor, correct option intact)" % len(spared)
        )
        print("             add --strict to quarantine those too")
    print()
    if not hits:
        print("  nothing to quarantine.\n")
        return 0

    print("  reason")
    print("  " + "-" * 62)
    for why, n in reasons.most_common():
        print("  %-52s %5d" % (why, n))

    print("\n  where they came from")
    print("  " + "-" * 62)
    for k, n in recovered_flag.most_common():
        print("  %-52s %5d" % (k, n))
    print(
        "\n  A high count against 'options_recovered set' means the OCR pass did\n"
        "  this, not the extraction - those options were probably fine before it."
    )

    # A bank file names its subject once at the top, not on every question.
    by_subject = Counter(
        q.get("subject") or os.path.splitext(os.path.basename(p))[0]
        for p, q, _w in hits
    )
    print("\n  by subject")
    print("  " + "-" * 62)
    for s, n in by_subject.most_common():
        print("  %-52s %5d" % (s, n))

    if args.show:
        print("\n  examples\n")
        for path, q, why in hits[: args.show]:
            print("  %s  [%s]" % (q["id"], why))
            print("     %s" % (q.get("text", "")[:96].replace("\n", " ")))
            for i, o in enumerate(q.get("options") or []):
                print("       %s: %r" % ("ABCD"[i] if i < 4 else i, str(o)[:88]))
            print()

    if not args.apply:
        print("\n  dry run: nothing written.")
        print("  look first:  --show 15")
        print("  then:        --apply\n")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    per_file = Counter()
    for path in bank_files():
        ids = {q["id"] for p, q, _w in hits if p == path}
        if not ids:
            continue
        data = json.load(open(path, encoding="utf-8"))
        for q in data.get("questions", []):
            if q["id"] in ids:
                q[MARKER] = True
                # answer_pending is what the selector already honours. The answer
                # itself is kept: it is the options that are gone, and the Bank
                # tab needs the answer to rebuild them against.
                q["answer_pending"] = True
                per_file[path] += 1
        shutil.copy2(path, "%s.%s.bak" % (path, stamp))
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, path)

    for path, n in sorted(per_file.items()):
        print("  %-52s %5d" % (os.path.relpath(path, ROOT), n))
    print("\n  quarantined %d question(s); .bak written beside each file" % sum(per_file.values()))
    print("  they stay in the bank and in coverage, but are no longer served")
    print("\n  next:")
    print("    python tools/build_mocks.py --apply     rebuild mocks without them")
    print('    "Reload from disk" in the Bank tab')
    print("    python tools/quarantine_bad_options.py --undo   to reverse this\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())