#!/usr/bin/env python3
"""Exercise core/topicmatch against the real bank and report what it cannot do.

The resolver was developed against an operating-systems-only slice, so the
numbers that matter - behaviour over all twelve subjects and roughly 330
subtopic slugs - can only be measured here.

Every battery query carries the slug it should produce. That matters more than
it sounds: an earlier version of this script only checked that the questions it
selected agreed with whatever slug came back, so "thrashing" resolving to
hashing and "subneting" resolving to counting both passed. A harness that
cannot fail is worse than no harness, because it turns a wrong answer into
evidence of correctness.

Where the expected answer is None the query is expected to find nothing, and
finding something is the failure - that is the guard on the fuzzy cutoff.

Four sections:

  vocabulary   how many topics and subtopics are reachable at all
  round trip   every slug must resolve to itself, or it is unreachable even by
               exact typing, which would mean the normaliser is mangling it
  battery      each query resolved, checked against its expected slug, then run
               through quiz.select so a match that selects nothing is a failure
  gaps         queries that correctly found nothing. This is the real output:
               it is what the alias file has to cover, and no amount of
               edit-distance tuning will shorten it

Add ad-hoc queries as arguments; those are reported but not graded:

    python tools/topicmatch_check.py "banker algo" "thrashing"

Read-only apart from opening the database. Run from the repo root.
"""
import collections
import os
import sys
import time

ROOT = os.getcwd()
sys.path.insert(0, ROOT)

try:
    from core import db, quiz, topicmatch as tm
except ImportError as exc:
    sys.exit("cannot import core - run this from the repo root (%s)" % exc)

# (query, expected slug or None for "should find nothing")
BATTERY = [
    ("plain", [
        ("deadlock", "deadlock"),
        ("virtual memory", "virtual-memory"),
        # binary-search-tree is a subtopic in its own right (43 questions);
        # the bst topic is the wider label and not what this text says.
        ("binary search tree", "binary-search-tree"),
        ("normalization", "normalization"),
        ("finite automata", "finite-automata"),
        ("pipelining", "pipelining"),
        ("karnaugh map", "karnaugh-map"),
    ]),
    ("shorthand", [
        ("banker algo", "bankers-algorithm"),
        ("booth algo", "booths-algorithm"),
        ("disk sched", "disk-scheduling"),
    ]),
    ("partial", [
        ("bankers", "bankers-algorithm"),
        ("karnaugh", "karnaugh-map"),
        ("dijkstra", "dijkstra-algorithm"),
        ("huffman", "huffman-code"),
        ("subnetting", "subnetting"),
    ]),
    ("typo", [
        ("bankar algo", "bankers-algorithm"),
        ("virtaul memory", "virtual-memory"),
        ("page replacment", "page-replacement"),
        ("subneting", "subnetting"),
        ("disk sheduling", "disk-scheduling"),
        ("normalisation", "normalization"),
        ("pipelinning", "pipelining"),
        ("hasing", "hashing"),
    ]),
    # These share too few characters with their target for edit distance to
    # reach. Each one that resolves does so through the alias file or not at
    # all - which is what this section exists to measure.
    ("abbreviation", [
        # kmap is itself a topic slug with far more behind it than the
        # karnaugh-map subtopic, so exact beats any alias here.
        ("kmap", "kmap"),
        # dfs reaches graph-traversal through the "BFS DFS and applications"
        # topic name. An alias pointing at depth-first-search would be
        # sharper, but graph-traversal is not wrong.
        ("dfs", "graph-traversal"),
        ("tlb", "translation-lookaside-buffer"),
        ("sop form", "min-sum-of-products-form"),
        ("pos form", "min-products-of-sum-form"),
        ("2pl", "two-phase-locking-protocol"),
        ("rag", "resource-allocation"),
        ("crc", "crc-polynomial"),
        ("cfg", "cfg"),
        ("pda", "pda"),
    ]),
    ("synonym", [
        ("thrashing", "page-replacement"),
        ("safe state", "bankers-algorithm"),
        ("need matrix", "bankers-algorithm"),
        ("wait for graph", "resource-allocation"),
        ("armstrong axioms", "armstrong-axioms"),
        ("eigen values", "eigen-values"),
    ]),
    # Guards the token-sort tier: these five words in either order are two
    # different slugs meaning opposite things, so neither may match the other.
    ("ambiguous", [
        ("min sum of products form", "min-sum-of-products-form"),
        ("min products of sum form", "min-products-of-sum-form"),
    ]),
    ("reordered", [
        ("memory virtual", "virtual-memory"),
        ("scheduling disk", "disk-scheduling"),
    ]),
    # Nothing should come back for these. A match here means the fuzzy cutoff
    # has drifted loose again.
    ("nonsense", [("xyzzy", None), ("qqqq", None), ("asdf", None)]),
]


def main():
    extra = sys.argv[1:]
    vocab = tm.vocabulary(reload=True)
    if not vocab:
        sys.exit("vocabulary is empty - is the bank loaded?")

    kinds = collections.Counter(e["kind"] for e in vocab.values())
    both = [s for s, e in vocab.items() if e.get("also")]
    print("\n=== vocabulary ===")
    print("  %d reachable label(s): %d topic, %d subtopic"
          % (len(vocab), kinds["topic"], kinds["subtopic"]))
    print("  %d slug(s) are both a topic and a subtopic" % len(both))
    for slug in sorted(both, key=lambda s: -vocab[s]["count"])[:5]:
        e = vocab[slug]
        print("    %-30s picks %s (%d), not %s (%d)"
              % (slug, e["kind"], e["count"], e["also"]["kind"], e["also"]["count"]))

    n_alias = len(tm.aliases(reload=True))
    print("  %d curated alias(es)%s" % (
        n_alias, "" if n_alias else
        "  <- content/subtopic_aliases.json absent, so the abbreviation"
        " and synonym sections will show as gaps"))
    print("  fuzzy cutoff %.2f" % tm.FUZZY_CUTOFF)

    print("\n=== round trip ===")
    broken = []
    for slug, entry in vocab.items():
        m, _ = tm.resolve(slug.replace("-", " "))
        want = entry.get("canonical") or slug
        if not m or m["slug"] != want:
            broken.append((slug, m["slug"] if m else None))
    if broken:
        print("  %d slug(s) do not resolve to themselves:" % len(broken))
        for slug, got in broken[:15]:
            print("    %-34s -> %s" % (slug, got))
        if len(broken) > 15:
            print("    ... and %d more" % (len(broken) - 15))
    else:
        print("  all %d slug(s) resolve to themselves" % len(vocab))

    conn = db.connect()
    gaps, failures, absent = [], [], []
    try:
        print("\n=== battery ===")
        total_ms, n = 0.0, 0
        groups = BATTERY + ([("yours", [(q, "?") for q in extra])] if extra else [])
        for label, queries in groups:
            print("  -- %s" % label)
            for query, want in queries:
                t0 = time.perf_counter()
                m, sug = tm.resolve(query)
                total_ms += (time.perf_counter() - t0) * 1000
                n += 1

                # A target that is not in this bank cannot be graded. Say so
                # rather than counting it against the resolver.
                if want not in (None, "?") and want not in vocab:
                    absent.append((query, want))
                    print("     n/a  %-22s expected %s, not a label in this bank"
                          % (query, want))
                    continue

                if not m:
                    hint = ", ".join(s["slug"] for s in sug[:3]) or "nothing close"
                    if want in (None, "?"):
                        print("     OK   %-22s no match  (%s)" % (query, hint))
                    else:
                        gaps.append((label, query, want, [s["slug"] for s in sug[:3]]))
                        print("     GAP  %-22s wanted %-26s (closest: %s)"
                              % (query, want, hint))
                    continue

                if want is None:
                    failures.append((query, "no match", m["slug"],
                                     "matched when it should not have"))
                    print("     FAIL %-22s matched %s - cutoff too loose"
                          % (query, m["slug"]))
                    continue

                right = want == "?" or m["slug"] == want
                picked = quiz.select(conn, purpose="mixed", count=5,
                                     **tm.filter_args(m))
                got = [x for x, _ in picked]
                field = "subtopic" if m["kind"] == "subtopic" else "topic"
                stray = sorted({x.get(field, "") for x in got} - {m["slug"]})
                selects = bool(got) and not stray
                if not right:
                    failures.append((query, want, m["slug"], "wrong slug"))
                elif not selects:
                    failures.append((query, want, m["slug"],
                                     "selected nothing" if not got
                                     else "stray %s" % stray))
                via = m["matched"] if m["matched"] != m["slug"] else ""
                print("     %s %-22s %-28s %-12s n=%-4d picked %d%s%s"
                      % ("OK  " if (right and selects) else "FAIL",
                         query, m["slug"], m["how"], m["count"], len(got),
                         "  via " + via if via else "",
                         "  wanted " + str(want) if not right else ""))
        print("\n  %.2fms per query over %d queries" % (total_ms / n, n))
    finally:
        conn.close()

    if absent:
        print("\n=== not a label in this bank ===")
        for query, want in absent:
            print("  %-24s expects %s" % (query, want))
        print("  Ungraded: either that slug is spelt differently here, or no")
        print("  question carries it yet.")

    print("\n=== gaps: what the alias file has to cover ===")
    if not gaps:
        print("  none")
    else:
        for label in sorted({g[0] for g in gaps}):
            print("  %s:" % label)
            for _, query, want, sug in [g for g in gaps if g[0] == label]:
                print("    %-22s -> %-30s closest: %s"
                      % (query, want, ", ".join(sug) or "-"))
        print("\n  %d quer(y/ies). Lowering the cutoff is not the answer here -"
              % len(gaps))
        print("  at 0.62 the resolver answered thrashing with hashing. These")
        print("  need entries in content/subtopic_aliases.json.")

    if failures:
        print("\n=== failures ===")
        for query, want, got, why in failures:
            print("  %-22s wanted %-28s got %-28s %s" % (query, want, got, why))
        print("\n  %d failure(s). These are bugs, not missing aliases."
              % len(failures))
        return 1
    print("\n  no failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())