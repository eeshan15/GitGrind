#!/usr/bin/env python3
"""Name what the after-session set was narrowed to, and speak up when it wasn't.

/api/sessions now returns quiz_from - "bankers-algorithm", or "questions
mentioning 'tlb'" - and timer.js ignores it:

    if (out.quiz && out.quiz.questions && out.quiz.questions.length) {
      setTimeout(() => GG.practice.open(out.quiz, 'Quiz on what you just studied'), 340);
    }

"Quiz on what you just studied" is a claim the app cannot back up when it
guessed, and a waste of one it can when it did not. A note of "banker algo"
produced a set of exactly the Banker's algorithm questions; the title should
say so, because that is the confirmation that writing the note did anything.

The second half matters more. When the note resolves but every matching
question is inside its repeat cooldown or held by a mock, out.quiz_error
explains it and nothing reads that either, so the set simply does not appear.
Silence after a deliberate action reads as a bug - it is the same failure that
made a correct spaced-repetition repeat feel random until the reason was put on
the card.

Two edits in static/js/timer.js:

  1. title      use quiz_from when there is one
  2. no set     toast the reason instead of nothing, but only when the note
                actually resolved. A note like "read the chapter" resolves to
                nothing on purpose and should stay quiet.

Requires patch_session_note.py, patch_session_subject.py and
patch_session_topic.py, which are what put quiz_from in the response.

CRLF-safe and idempotent. Run from the repo root:  python patch_timer_title.py
"""
import io
import os
import sys

EDITS = [
    ('static/js/timer.js',
     "      if (out.quiz && out.quiz.questions && out.quiz.questions.length) {\n"
     "        setTimeout(() => GG.practice.open(out.quiz, 'Quiz on what you just studied'), 340);\n"
     "      }",

     "      /* quiz_from names what the note was resolved to. Saying it is the\n"
     "         only confirmation that writing the note changed anything, and\n"
     "         without it the title claims to know what was studied even when\n"
     "         the set came from a ticked chip instead. */\n"
     "      const from = out.quiz_from || '';\n"
     "      if (out.quiz && out.quiz.questions && out.quiz.questions.length) {\n"
     "        const title = from\n"
     "          ? 'Quiz on ' + from.replace(/-/g, ' ')\n"
     "          : 'Quiz on what you just studied';\n"
     "        setTimeout(() => GG.practice.open(out.quiz, title), 340);\n"
     "      } else if (from) {\n"
     "        /* The note resolved and still produced nothing - everything\n"
     "           matching is inside its repeat cooldown, or held by a mock.\n"
     "           Saying so beats the set silently not appearing. A note that\n"
     "           resolved to nothing sets no quiz_from and stays quiet. */\n"
     "        toast('No set for ' + from.replace(/-/g, ' '),\n"
     "          out.quiz_error || 'Nothing available outside its repeat cooldown.');\n"
     "      }",
     ),
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
            print("  skip    %-22s already applied" % path)
            skipped += 1
            continue
        if s.count(o) != 1:
            sys.exit("  ERROR   %s: anchor found %d times, expected 1"
                     % (path, s.count(o)))
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(o, n, 1))
        print("  patched %-22s ok" % path)
        changed += 1
    print("\n  %d edit(s) applied, %d already present" % (changed, skipped))
    if changed:
        print("  Hard-refresh the browser. A timed session noted \"banker algo\"")
        print("  should open a set titled \"Quiz on bankers algorithm\".")
    return 0


if __name__ == "__main__":
    sys.exit(main())