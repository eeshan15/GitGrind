"""Turn what somebody types into a label the bank can actually be filtered on.

The point of the whole exercise: a person finishes studying and types "banker
algo". The bank stores that as subtopic "bankers-algorithm" under
operating-systems/deadlock. Nothing in between knew how to get from one to the
other.

Five tiers, cheapest first, and each one exists because a real class of input
needs it:

  exact          "b tree" normalises straight onto b-tree
  alias          "kmap", "dfs", "tlb" - abbreviations share no characters with
                 what they stand for, so no amount of edit-distance reaches
                 karnaugh-map from kmap. Only a lookup table does. This is the
                 one tier that needs curated data; see subtopic_aliases.json
  token sort     the same words in another order
  token subset   "bankers" and "karnaugh" and "dijkstra" - a person types part
                 of the name and expects the whole thing. Edit distance is bad
                 at this because it penalises the length difference hard
  fuzzy          "bankar algo", "virtaul memory", "subneting", "sheduling" -
                 ordinary typos, which is what difflib is genuinely good at

Measured on a 291-slug vocabulary with twenty realistic queries this resolves
nineteen, at about 1.5ms each. rapidfuzz would add partial_ratio and
token_set_ratio, which handle the twentieth ("algorithm banker" - a misspelled
token *and* reordered), but it is a C extension: a platform wheel to bundle, an
entry in gitgrind.spec hiddenimports, and a bigger build. Not worth it for one
query shape out of twenty, so this module is stdlib only.

Below the fuzzy threshold nothing is returned. That is deliberate. An earlier
version had a sixth tier that fuzzy-matched individual tokens, and it answered
"algorithm banker" with dijkstra-algorithm - a confident wrong answer, which is
worse than no answer, because the person gets a set of questions about the
wrong thing and no hint that anything went astray. Now the caller gets None
plus suggestions and can ask.

FUZZY_CUTOFF is 0.90, which is high, and it is set from measurement rather than
taste. Over the queries in tools/topicmatch_check.py the worst correct fuzzy
match scores 0.909 ("bankar algo" onto bankers-algorithm) and the best incorrect
one scores 0.875 ("thrashing" onto hashing - four shared letters and nothing
else, since thrashing is a page-replacement idea). The gap between those is the
only honest place to draw the line. A looser cutoff does not find more right
answers, it just stops reporting the wrong ones as failures: at 0.62 this module
resolved "subneting" to counting and "dijkstra algo" to greedy.
"""
import difflib
import os
import re

from . import content

# Word-level rewrites applied before anything else. Deliberately small: these
# are shortenings a person types, not spelling corrections, which the fuzzy
# tier handles better than a table ever would.
SHORTHAND = {
    "algo": "algorithm",
    "algos": "algorithm",
    "sched": "scheduling",
    "repr": "representation",
    "rep": "representation",
    "func": "function",
    "prob": "probability",
    "n": "and",
}

# Tokens that carry no signal on their own. Stripped only as a second attempt,
# never on the first pass: dropping them unconditionally breaks exact matching
# for every slug that contains one, and this bank has plenty -
# min-sum-of-products-form, number-of-swap, degree-of-graph,
# system-of-equations. Worse than breaking them, it makes near-identical pairs
# collide: with "of" gone, "min products of sum form" stopped matching itself
# exactly and fuzzy handed back min-sum-of-products-form instead, which is a
# different slug and a different set of questions.
NOISE = {"the", "of", "in", "for", "a", "on", "questions", "question", "topic"}

FUZZY_CUTOFF = 0.90
SUGGEST_CUTOFF = 0.45
MAX_SUGGESTIONS = 5

_cache = {}


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").strip().lower()).strip("-")


def normalise(query, strip_noise=False):
    """Lowercase, expand shorthand, hyphen-join. Noise words kept by default."""
    words = re.sub(r"[^a-z0-9]+", " ", str(query or "").lower()).split()
    words = [SHORTHAND.get(w, w) for w in words]
    if strip_noise:
        words = [w for w in words if w not in NOISE] or words
    return "-".join(words)


def variants(query):
    """The forms to try, in order: as typed first, then with noise dropped."""
    full = normalise(query)
    lean = normalise(query, strip_noise=True)
    return [full] if lean == full else [full, lean]


def aliases(reload=False):
    """Curated alias -> slug, from content/subtopic_aliases.json.

    Absent file is normal and not an error: every other tier works without it.
    It only carries what edit distance cannot reach - abbreviations and
    synonyms that share no characters with the slug.
    """
    if reload or "aliases" not in _cache:
        path = os.path.join(content.CONTENT_DIR, "subtopic_aliases.json")
        raw = content._read_json(path, {}) or {}
        out = {}
        for slug, spec in (raw.get("subtopics") or {}).items():
            target = _slug(slug)
            terms = spec if isinstance(spec, list) else (spec or {}).get("aliases") or []
            for term in terms:
                key = normalise(term)
                if key and key not in out:
                    out[key] = target
        _cache["aliases"] = out
    return _cache["aliases"]


def vocabulary(reload=False):
    """slug -> what filtering on it would actually select.

    Built from the bank rather than the syllabus, so a slug only appears if
    questions carry it. Topics and subtopics share one lookup because a person
    typing "deadlock" (a topic) and "banker algo" (a subtopic) has no idea
    which is which and should not need to.

    They are counted separately though. Some slugs are both - virtual-memory is
    a topic with 82 questions and a subtopic with 46 - and adding those gives a
    number that matches neither filter. Where a slug is both, the one that
    selects more questions wins: the person typed the whole name, so the wider
    reading is the safer guess, and the count then matches what they will get.

    Rebuilt when content hands back a different bank object, which is what
    happens after content.invalidate() - so an override change is picked up
    without this module having to be told.
    """
    bank = content.question_bank()
    if not reload and _cache.get("vocab_for") is id(bank) and "vocab" in _cache:
        return _cache["vocab"]

    idx = content.topic_index()
    # (kind, slug) -> entry, so a slug that is both stays two separate things
    # until the moment one has to be picked.
    raw = {}

    def touch(kind, slug, label, key, canonical=None):
        if not slug:
            return
        entry = raw.setdefault(
            (kind, slug),
            dict(slug=slug, kind=kind, label=label, count=0, targets={}),
        )
        if canonical:
            entry["canonical"] = canonical
        entry["count"] += 1
        entry["targets"][key] = entry["targets"].get(key, 0) + 1

    for q in bank.values():
        key = (q.get("subject", ""), q.get("topic", ""))
        meta = idx.get(key) or {}
        if key[1]:
            touch("topic", key[1], meta.get("name") or key[1], key)
            name_slug = _slug(meta.get("name"))
            if name_slug and name_slug != key[1]:
                touch("topic", name_slug, meta.get("name"), key, canonical=key[1])
        if q.get("subtopic"):
            touch("subtopic", q["subtopic"], q["subtopic"].replace("-", " "), key)

    vocab = {}
    for (kind, slug), entry in raw.items():
        rival = vocab.get(slug)
        if rival is None or entry["count"] > rival["count"]:
            vocab[slug] = entry
        if rival is not None:
            # Record the road not taken so a caller can offer the narrower or
            # wider reading instead of silently losing it.
            keep = vocab[slug]
            other = entry if keep is rival else rival
            keep["also"] = dict(kind=other["kind"], count=other["count"])

    _cache["vocab"] = vocab
    _cache["vocab_for"] = id(bank)
    _cache["tokens"] = {}
    by_tokens = {}
    for slug in vocab:
        toks = frozenset(slug.split("-"))
        _cache["tokens"][slug] = toks
        by_tokens.setdefault("-".join(sorted(toks)), []).append(slug)
    # A sorted-token key shared by two slugs cannot identify either of them.
    # min-sum-of-products-form and min-products-of-sum-form are the same five
    # words in a different order and mean opposite things, so reordering is not
    # evidence here - drop the key and let exact or fuzzy decide.
    _cache["by_tokens"] = {
        key: slugs[0] for key, slugs in by_tokens.items() if len(slugs) == 1
    }
    _cache["ambiguous_tokens"] = {
        key: slugs for key, slugs in by_tokens.items() if len(slugs) > 1
    }
    return vocab


def _hit(entry, how, confidence, query, normalised):
    targets = sorted(
        (dict(subject=s, topic=t, count=n) for (s, t), n in entry["targets"].items()),
        key=lambda d: -d["count"],
    )
    return dict(
        query=query,
        normalised=normalised,
        slug=entry.get("canonical") or entry["slug"],
        # The key that actually matched. Differs from slug when a topic's
        # display name was what matched, and a report that only shows slug
        # cannot tell a good match from a lucky one.
        matched=entry["slug"],
        kind=entry["kind"],
        label=entry["label"],
        how=how,
        confidence=round(confidence, 3),
        count=entry["count"],
        targets=targets,
        also=entry.get("also"),
    )


def suggest(query, limit=MAX_SUGGESTIONS):
    """Ranked near misses, for a "did you mean" prompt."""
    vocab = vocabulary()
    n = normalise(query)
    if not n:
        return []
    names = difflib.get_close_matches(n, list(vocab), n=limit, cutoff=SUGGEST_CUTOFF)
    return [
        dict(slug=s, kind=vocab[s]["kind"], count=vocab[s]["count"],
             label=vocab[s]["label"])
        for s in names
    ]


def resolve(query):
    """(match, suggestions). match is None when nothing clears the threshold."""
    vocab = vocabulary()
    forms = [f for f in variants(query) if f]
    if not forms:
        return None, []

    # Every tier is tried on the query as typed before any tier is tried on the
    # noise-stripped form. An exact hit on the full form beats a fuzzy hit on a
    # shortened one, and the reverse order is what let "min products of sum
    # form" land on the wrong slug.
    for tier in ("exact", "alias", "token-sort", "token-subset", "fuzzy"):
        for n in forms:
            hit = _try(tier, n, query, vocab)
            if hit:
                return hit, []

    return None, suggest(query)


def _try(tier, n, query, vocab):
    if tier == "exact":
        if n in vocab:
            return _hit(vocab[n], "exact", 1.0, query, n)
        return None

    if tier == "alias":
        target = aliases().get(n)
        if target and target in vocab:
            return _hit(vocab[target], "alias", 1.0, query, n)
        return None

    if tier == "token-sort":
        slug = _cache["by_tokens"].get("-".join(sorted(n.split("-"))))
        if slug:
            return _hit(vocab[slug], "token-sort", 0.95, query, n)
        return None

    if tier == "token-subset":
        # Everything typed appears in the slug. Prefer the fewest extra words,
        # then the larger question count - "bankers" should land on
        # bankers-algorithm, not on a one-question near-namesake.
        qt = frozenset(n.split("-"))
        subs = [
            (len(_cache["tokens"][s] - qt), -vocab[s]["count"], s)
            for s in vocab
            if qt <= _cache["tokens"][s]
        ]
        if subs:
            subs.sort()
            extra, _neg, best = subs[0]
            return _hit(vocab[best], "token-subset", max(0.7, 1.0 - 0.1 * extra),
                        query, n)
        return None

    close = difflib.get_close_matches(n, list(vocab), n=1, cutoff=FUZZY_CUTOFF)
    if close:
        ratio = difflib.SequenceMatcher(None, n, close[0]).ratio()
        return _hit(vocab[close[0]], "fuzzy", ratio, query, n)
    return None


def filter_args(match):
    """Turn a match into keyword arguments for quiz.select.

    A subtopic filters on subtopic and leaves topic open, because a subtopic can
    sit under more than one topic and narrowing to one would silently drop
    questions the person asked for.
    """
    if not match:
        return {}
    if match["kind"] == "subtopic":
        return dict(subtopic_slugs=[match["slug"]])
    return dict(topic_slugs=[match["slug"]])


def build_args(planned, prefer=None):
    """Keyword arguments for quiz.build_quiz, honouring the plan's advice.

    prefer overrides it - "label" or "mentions" - which is what a caller passes
    after the person has been shown both counts and chosen. Mentions become
    question_ids rather than a filter, because there is no text filter in
    quiz.select and inventing one would duplicate what this already knows.
    """
    route = prefer or planned["advice"]
    if route == "mentions" and planned["mention_ids"]:
        return dict(question_ids=planned["mention_ids"])
    if planned["label"]:
        return filter_args(planned["label"])
    if planned["mention_ids"]:
        return dict(question_ids=planned["mention_ids"])
    return {}

def mentions(query, limit=400):
    """Question ids whose own text or options contain the query.

    Deliberately not content.search: that searches topic, subtopic and subject
    alongside the text, so for "page replacement" it would return the whole
    subtopic and the number would say nothing new. This counts only questions
    that actually say the words, which is the one measurement a label cannot
    give.

    It matters because the two numbers disagree in both directions. The slug
    translation-lookaside-buffer carries 2 questions while 14 mention TLB, so a
    label alone under-delivers. Conversely 30 questions sit under
    page-replacement while only 2 mention thrashing, so pointing "thrashing" at
    that label over-delivers by fifteen to one.
    """
    needle = " ".join(re.sub(r"[^a-z0-9]+", " ", str(query or "").lower()).split())
    if len(needle) < 3:
        return []
    out = []
    for qid, flat in _text_index().items():
        if needle in flat:
            out.append(qid)
            if len(out) >= limit:
                break
    return out


def _text_index():
    """id -> flattened lowercase text, built once per bank.

    Normalising 3,862 stems on every keystroke is the difference between this
    being usable and not; the strings do not change until content.invalidate()
    hands back a different bank, which is the same signal vocabulary() uses.
    """
    bank = content.question_bank()
    if _cache.get("text_for") is id(bank) and "text" in _cache:
        return _cache["text"]
    idx = {}
    for qid, q in bank.items():
        parts = [q.get("text") or ""]
        parts += [str(o) for o in (q.get("options") or [])]
        idx[qid] = " ".join(
            re.sub(r"[^a-z0-9]+", " ", " ".join(parts).lower()).split()
        )
    _cache["text"] = idx
    _cache["text_for"] = id(bank)
    return idx


def plan(query):
    """Both readings of a query, with the counts, and no opinion hidden.

    Returns label (a resolved slug or None), mentions (ids of questions that
    say the words), and an advice string naming which to offer. The caller gets
    both numbers because only the person typing knows which they meant, and a
    resolver that silently picks one is how "thrashing" turns into thirty
    page-replacement questions.

    advice values:
      label     a slug matched and nothing much else mentions the words
      mentions  the words are in more questions than the slug holds, or no
                slug matched at all
      both      each finds a useful and different set - offer the choice
      none      neither found anything; suggestions carry the near misses
    """
    match, suggestions = resolve(query)
    ids = mentions(query)
    label_n = match["count"] if match else 0
    text_n = len(ids)

    # How the label was reached decides this, not which count is bigger.
    # "deadlock" matches a topic exactly and is mentioned by 50 questions
    # across other topics too; going with the bigger number there would trade a
    # curated label for incidental word matches. A named label is a statement
    # of intent, a fuzzy one is a guess, and only a guess should lose to the
    # text.
    named = bool(match) and match["how"] in ("exact", "alias", "token-sort")

    if not match and not ids:
        advice = "none"
    elif not match:
        advice = "mentions"
    elif named or not ids:
        advice = "label"
    elif text_n > label_n:
        # A guessed label that holds fewer questions than say the words: the
        # guess is probably too narrow or simply wrong.
        advice = "mentions"
    elif label_n > text_n * 3:
        # A guessed label far wider than the words justify. Do not pretend it
        # is precise - show both counts and let the person pick.
        advice = "both"
    else:
        advice = "label"

    return dict(
        query=query,
        label=match,
        label_count=label_n,
        mention_ids=ids,
        mention_count=text_n,
        advice=advice,
        suggestions=suggestions,
    )