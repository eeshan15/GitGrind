#!/usr/bin/env python3
"""Flip apply flags in the override sidecar, and show what changed.

Editing content/subtopic_overrides.json by hand is fine and stays supported.
This exists for the bulk case - the clear-subtopic entries are safe as
generated and there is no value in flipping eight flags one at a time - and
because turning an override on with no way to see its effect is how a
correction gets applied to the wrong block without anyone noticing.

    python tools/apply_overrides.py                             show state
    python tools/apply_overrides.py --enable clear-subtopic      turn a bucket on
    python tools/apply_overrides.py --enable check-topic --dry   preview only
    python tools/apply_overrides.py --disable review             turn a bucket off
    python tools/apply_overrides.py --enable KEY                 one block

Before/after counts come from the real bank with the sidecar loaded, so what
prints is the effect on what the app will actually serve, not what the file
says. check-topic is never enabled implicitly: it carries a proposed topic and
those want reading first.
"""
import argparse
import collections
import json
import os
import re
import sys

ROOT = os.getcwd()
sys.path.insert(0, ROOT)

try:
    from core import content
except ImportError as exc:
    sys.exit("cannot import core.content - run this from the repo root (%s)" % exc)

SIDECAR = os.path.join("content", "subtopic_overrides.json")
ACTIONS = ("clear-subtopic", "check-topic", "review")


def snapshot():
    """Per-block view of what the bank currently says, for the diff."""
    content.invalidate()
    bank = content.question_bank(reload=True)
    out = collections.defaultdict(collections.Counter)
    for q in bank.values():
        key = content._block_key(q.get("origin"))
        if key:
            out[key][(q.get("subject", ""), q.get("topic", ""), q.get("subtopic", ""))] += 1
    return out


def describe(counter):
    return ", ".join(
        "%s/%s [%s] x%d" % (s, t, st or "-", n)
        for (s, t, st), n in counter.most_common(3)
    )


def project(before, spec, want):
    """What a block's questions become once this entry is on (or off).

    Computed here rather than read back from the file, because --dry must not
    write and content.overrides() only ever reads what is on disk. Mirrors the
    item.update(fix) in content._hydrate, so a mismatch against the real reload
    below means the two have drifted apart.
    """
    if not want:
        return None  # turning off restores whatever the bank file says
    fix = {}
    if "subtopic" in spec:
        subtopic = (spec.get("subtopic") or "").strip().lower()
        fix["subtopic"] = re.sub(r"[^a-z0-9]+", "-", subtopic).strip("-")
    topic = (spec.get("topic") or "").strip()
    if "/" in topic:
        fix["subject"], fix["topic"] = topic.split("/", 1)
    out = collections.Counter()
    for (subject, tslug, subtopic), n in before.items():
        out[(fix.get("subject", subject), fix.get("topic", tslug),
             fix.get("subtopic", subtopic))] += n
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enable", metavar="ACTION_OR_KEY")
    ap.add_argument("--disable", metavar="ACTION_OR_KEY")
    ap.add_argument("--dry", action="store_true", help="report without writing")
    args = ap.parse_args()

    if not os.path.isfile(SIDECAR):
        sys.exit("%s not found - run tools/propose_overrides.py first" % SIDECAR)
    with open(SIDECAR, encoding="utf-8") as fh:
        payload = json.load(fh)
    entries = payload.get("overrides") or {}
    if not entries:
        sys.exit("no entries in %s" % SIDECAR)

    # ---- state only -----------------------------------------------------
    if not args.enable and not args.disable:
        by_action = collections.Counter()
        on = collections.Counter()
        for key, spec in entries.items():
            action = spec.get("_action", "?")
            by_action[action] += 1
            if spec.get("apply"):
                on[action] += 1
        print("")
        for action in ACTIONS:
            if by_action[action]:
                print("  %-16s %2d entr(y/ies), %d on"
                      % (action, by_action[action], on[action]))
        print("\n  Enable a bucket with --enable <action>, or a single block")
        print("  with --enable '<volume>|<chapter>.<block>'.")
        return 0

    target = args.enable or args.disable
    want = bool(args.enable)
    if target in ACTIONS:
        hits = [k for k, v in entries.items() if v.get("_action") == target]
        label = "action %s" % target
    else:
        hits = [k for k in entries if k == target]
        label = "block %s" % target
    if not hits:
        sys.exit("nothing matches %s" % label)

    changing = [k for k in hits if bool(entries[k].get("apply")) != want]
    if not changing:
        print("\n  %s: all %d entr(y/ies) already %s"
              % (label, len(hits), "on" if want else "off"))
        return 0

    before = snapshot()
    projected = {
        key: project(before.get(key, collections.Counter()), entries[key], want)
        for key in changing
    }

    if args.dry:
        print("\n  DRY RUN - %s not written" % SIDECAR)
        after = None
    else:
        for key in changing:
            entries[key]["apply"] = want
        with open(SIDECAR, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        after = snapshot()

    print("\n  %s -> %s for %d entr(y/ies)\n"
          % (label, "on" if want else "off", len(changing)))
    moved = 0
    drift = []
    for key in sorted(changing, key=lambda k: -entries[k].get("_question_count", 0)):
        b = before.get(key, collections.Counter())
        want_state = projected[key] if want else b
        n = entries[key].get("_question_count", 0)
        if after is not None:
            real = after.get(key, collections.Counter())
            if want and real != want_state:
                drift.append(key)
            shown = real
        else:
            shown = want_state
        if shown == b:
            print("  %-28s %3dq  no change" % (key, n))
            print("        %s" % (entries[key].get("_note") or ""))
            continue
        moved += sum(shown.values())
        print("  %-28s %3dq" % (key, n))
        print("        before  %s" % describe(b))
        print("        after   %s" % describe(shown))

    if drift:
        print("\n  WARNING: the reload did not match the prediction for:")
        for key in drift:
            print("    %s" % key)
        print("  apply_overrides.project and content._hydrate have drifted.")

    print("\n  %d question(s) affected." % moved)
    if args.dry:
        print("  Nothing was written. Drop --dry to apply.")
    else:
        print("  Restart the app - content caches per process.")
    return 0


if __name__ == "__main__":
    sys.exit(main())