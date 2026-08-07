"""Put $...$ around LaTeX that MinerU left undelimited.

WHY THIS IS ITS OWN MODULE

  Two earlier attempts at this lived inside the converter as a pair of regexes
  and both shipped broken - they inserted a dollar between an existing matched
  pair, after which every later dollar paired with the wrong partner and whole
  English sentences rendered as run-together italics. The failure was only
  visible in the browser, several steps downstream.

  So the logic is separated out here where it can be run against a fixture set
  directly (tools/test_texwrap.py), and the two properties that actually matter
  are asserted rather than eyeballed:

    1. text containing no LaTeX comes back byte-identical
    2. the dollar count stays even, and every pair that was already balanced
       is still balanced afterwards

HOW IT WORKS

  Split the text into alternating in-math and out-of-math segments by walking
  the dollars. Only out-of-math segments are considered at all, which makes
  "insert inside an existing formula" structurally impossible rather than
  something a pattern has to be careful about.

  Inside those segments, a run of maths-shaped tokens is wrapped only if it
  contains a backslash command or a braced sub/superscript. Prose has neither.
  Anything that fails that test is left exactly as it was: raw LaTeX on screen
  is ugly, a mangled sentence is worse.
"""

import re

# A braced group is a single token so \text {for} and {l l} stay inside a run
# instead of ending it at the first ordinary word they contain. \left( and
# \right. carry their delimiter, including the "." that means an invisible one.
TEX_TOKEN = (
    r"(?:\\(?:left|right|big|Big|bigg|Bigg)[lr]?[ \t]*(?:\\[{}|]|[.|\[\]()/])"
    r"|\{[^{}]*\}"
    r"|\\[A-Za-z]+\*?"
    r"|\\[\\{}|,;:!\[\]()]"
    r"|[\[\]()^_&|<>=+\-*/,;]"
    r"|\d+(?:\.\d+)?"
    r"|[A-Za-z](?![A-Za-z]))"
)
TEX_RUN = re.compile(r"(?<![\\$\w])(%s(?:[ \t]*%s)*)" % (TEX_TOKEN, TEX_TOKEN))
TEX_CMD = re.compile(r"\\[A-Za-z]+")
TEX_SCRIPT = re.compile(r"[\^_][ \t]*\{")


def split_math_mode(text):
    """[(is_math, segment), ...], splitting on balanced $...$ pairs.

    An unclosed dollar is not a delimiter - it is just a character - so the
    scan only opens a segment when it can also find the close.
    """
    out, buf, i, n = [], [], 0, len(text)
    while i < n:
        if text[i] == "$" and (i == 0 or text[i - 1] != "\\"):
            j = i + 1
            while j < n and not (text[j] == "$" and text[j - 1] != "\\"):
                j += 1
            if j < n:
                if buf:
                    out.append((False, "".join(buf)))
                    buf = []
                out.append((True, text[i:j + 1]))
                i = j + 1
                continue
        buf.append(text[i])
        i += 1
    if buf:
        out.append((False, "".join(buf)))
    return out


def _wrap_segment(seg):
    def fix(m):
        run = m.group(1).strip()
        if "$" in run or len(run) < 3:
            return m.group(0)
        if not (TEX_CMD.search(run) or TEX_SCRIPT.search(run)):
            return m.group(0)
        # Trailing punctuation belongs to the sentence, not the formula.
        trail = ""
        while run and run[-1] in ".,;":
            # ... unless it is the delimiter of \right. or a decimal point.
            if re.search(r"\\(?:left|right|big|Big|bigg|Bigg)[lr]?[ \t]*$", run[:-1]):
                break
            if run[-1] == "." and len(run) > 1 and run[-2].isdigit():
                break
            trail = run[-1] + trail
            run = run[:-1].rstrip()
        if len(run) < 3 or not (TEX_CMD.search(run) or TEX_SCRIPT.search(run)):
            return m.group(0)
        return "$%s$%s" % (run, trail)

    return TEX_RUN.sub(fix, seg)


def wrap_bare_math(text):
    if "\\" not in text and not TEX_SCRIPT.search(text):
        return text

    before = text.count("$")
    result = "".join(
        seg if is_math else _wrap_segment(seg)
        for is_math, seg in split_math_mode(text)
    )

    # Refuse anything that did not stay balanced. A half-open formula swallows
    # the rest of the sentence, which is strictly worse than the raw LaTeX it
    # was meant to replace.
    if result.count("$") % 2 or before % 2:
        return text
    return result