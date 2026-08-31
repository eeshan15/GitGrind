#!/usr/bin/env python3
"""Turn the triaged section_gaps report into an override sidecar to review.

Reads content/review/section_gaps.json after tools/section_triage.py has run,
and writes content/subtopic_overrides.json. Every entry lands with
"apply": false, so nothing takes effect until you have read it and flipped the
flag. Re-running preserves the apply flags and any values already edited by
hand - only the evidence fields are refreshed.

What each triage bucket becomes:

  clear-subtopic  subtopic "", topic untouched. The heading is wrong and the
                  topic is fine, so this drops a wrong label rather than
                  guessing a right one. These are the ones that were breaking
                  concept search, and they are safe to apply as generated.

  check-topic     subtopic "", plus a proposed topic from the block vote. The
                  proposal is corroborated by an independent measurement: every
                  destination the vote picked is a topic that bank_stats already
                  reported as thin or empty, which is what you would expect if
                  these blocks had been holding its questions. It is still a
                  proposal - read the questions before flipping apply.

  keep            not written. The heading is correct and the block was only
                  flagged because GATE Overflow splits one long section across
                  consecutive numbered blocks. Clearing these would discard a
                  good label.

  review          written with apply false and no values, as a record. Most are
                  a limitation of the detector rather than a defect: GATE
                  Overflow splits one long section across several numbered
                  blocks, and consecutive blocks sharing a heading is normal
                  there. Left in the file so nothing is silently forgotten.

  skip            not written. "No Classified Topic" is the source's own
                  placeholder and there is nothing to correct.

Run from the repo root:  python tools/propose_overrides.py
"""
import collections
import json
import os
import sys

ROOT = os.getcwd()
sys.path.insert(0, ROOT)

try:
    from core import content
except ImportError as exc:
    sys.exit("cannot import core.content - run this from the repo root (%s)" % exc)

REPORT = os.path.join("content", "review", "section_gaps.json")
SIDECAR = os.path.join("content", "subtopic_overrides.json")

README = [
    "Corrections for questions whose origin.section was captured wrong by the",
    "MinerU import. Keyed '<volume>|<chapter>.<block>' so an entry survives a",
    "re-import; question ids do not.",
    "",
    "Nothing here does anything until \"apply\" is true. core.content.overrides()",
    "skips every entry with apply false, so a generated file is inert.",
    "",
    "  subtopic  \"\" clears the wrong label. Empty is the honest value when the",
    "            right heading is unknown: it costs granularity, where a wrong",
    "            one misroutes every search that should have found the question.",
    "  topic     \"subject/topic\". Only set this where the wrong heading actually",
    "            produced the topic - go_tag_map.json is what decides that, and",
    "            the triage report records it per block. May move a question to",
    "            another subject.",
    "",
    "Regenerate with tools/propose_overrides.py; apply flags and hand-edited",
    "values are preserved. Restart the app after editing - content caches per",
    "process.",
]


def main():
    if not os.path.isfile(REPORT):
        sys.exit("%s not found - run section_gaps.py then section_triage.py" % REPORT)
    with open(REPORT, encoding="utf-8") as fh:
        report = json.load(fh)
    findings = report.get("findings") or []
    if not findings:
        sys.exit("no findings in the report")
    if not any(f.get("recommended_action") for f in findings):
        sys.exit("report is not triaged - run tools/section_triage.py first")

    topic_index = content.topic_index()
    valid = {"%s/%s" % k for k in topic_index}

    existing = {}
    if os.path.isfile(SIDECAR):
        with open(SIDECAR, encoding="utf-8") as fh:
            existing = (json.load(fh).get("overrides") or {})

    out = {}
    counts = collections.Counter()
    warnings = []

    for f in findings:
        action = f.get("recommended_action")
        # keep and skip are both "do nothing": keep means the heading is
        # correct and the flag was the detector's limitation, so writing an
        # entry would only invite someone to clear a good label later.
        if action in ("skip", "keep"):
            counts[action] += 1
            continue
        key = "%s|%s" % (f.get("volume", ""), f.get("block", ""))
        prior = existing.get(key) or {}
        vote = f.get("block_vote") or {}

        entry = collections.OrderedDict()
        entry["apply"] = bool(prior.get("apply"))

        if action == "review":
            entry["subtopic"] = prior.get("subtopic", "")
        else:
            entry["subtopic"] = prior.get("subtopic", "")

        proposed = ""
        if action == "check-topic":
            proposed = vote.get("modal") or ""
            if proposed and proposed not in valid:
                warnings.append((key, proposed))
                proposed = ""
        entry["topic"] = prior.get("topic", proposed)

        entry["_action"] = action
        entry["_current_section"] = f.get("current_section", "")
        entry["_current_topic"] = f.get("current_topic", "")
        entry["_topic_from_bad_heading"] = bool(f.get("topic_from_bad_heading"))
        entry["_question_count"] = f.get("question_count", 0)
        entry["_note"] = f.get("recommendation_note", "")
        if vote.get("modal"):
            entry["_block_vote"] = "%s (%s/%s scored)" % (
                vote["modal"], vote.get("votes"), vote.get("scored")
            )
        samples = [q.get("text", "") for q in (f.get("questions") or [])[:2]]
        if samples:
            entry["_sample"] = samples

        out[key] = entry
        counts[action] += 1
        if entry["apply"]:
            counts["already_on"] += 1

    payload = collections.OrderedDict()
    payload["_read_me"] = README
    payload["overrides"] = collections.OrderedDict(
        sorted(out.items(), key=lambda kv: (-kv[1]["_question_count"], kv[0]))
    )
    with open(SIDECAR, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    print("\n  wrote %s" % SIDECAR)
    for action in ("clear-subtopic", "check-topic", "review"):
        if counts[action]:
            print("    %-16s %2d entr(y/ies)" % (action, counts[action]))
    for action in ("keep", "skip"):
        if counts[action]:
            print("    %-16s %2d not written, nothing to correct" % (action, counts[action]))
    if counts["already_on"]:
        print("    %-16s %2d kept from the previous file"
              % ("apply already on", counts["already_on"]))

    if warnings:
        print("\n  proposed topics not in syllabus.json, left blank:")
        for key, topic in warnings:
            print("    %-28s %s" % (key, topic))
        print("  Either the syllabus needs the topic, or the vote is wrong.")

    print("\n  Every entry is apply:false. To turn on the safe ones:")
    print("    python tools/apply_overrides.py --enable clear-subtopic")
    print("  or edit the file by hand. Then restart the app.")
    return 0


if __name__ == "__main__":
    sys.exit(main())