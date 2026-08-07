#!/usr/bin/env python3
"""Convert MinerU extraction output into GitGrind bank JSON, figures included.

WHY THIS EXISTS

  tools/import_questions.py and tools/extract_go_bank.py read `pdftotext` output.
  That path loses every figure, so any question whose statement lives in a graph,
  a circuit or a table arrives as a sentence with a hole in it. MinerU keeps the
  figures: it writes real image files plus a structured `*_content_list.json`
  with a page index and a bounding box for each one.

  This script is the bridge. MinerU is the extraction layer, GitGrind is the
  serving and validation layer, and nothing here tries to do the other's job:
  images stay on disk as sidecar assets, the bank JSON only ever holds a path.

  Everything downstream of "what does a question look like" is reused rather
  than reimplemented -- topic resolution, the GO tag map, keyword scoring and
  the answer-shape rules all come from import_questions / extract_go_bank.

WHAT IT READS

  A MinerU run directory. Per volume, the layout this understands is:

    <vol>/merged/full.md                     stitched markdown, image refs intact
    <vol>/merged/images/cNNN_<sha>.jpg       every extracted image, chunk-prefixed
    <vol>/pAAAA_BBBB/<stem>/hybrid_auto/
        <stem>_content_list.json             structured nodes: bbox, page_idx, ...
        images/<sha>.jpg                     the same image, unprefixed

  merged/full.md is the structural spine because it is the only place where the
  book's own "1.44.2" numbering, the per-chapter answer-key tables and the image
  references all coexist. content_list.json is then joined on the image filename
  to recover page_idx and bbox, which is what makes a bad figure findable again
  in the source PDF. `cNNN_` maps to the NNN-th page chunk, so a chunk-local
  page_idx plus that chunk's first page gives the absolute page.

WHAT IT WRITES

    content/banks/<bank>/<subject>.json          one file per subject
    content/banks/<bank>/_unsorted.json          topic unresolved, not loaded
    content/assets/question-images/<bank>/*.jpg  the figures

  Each question that has a figure carries:

    "figure_assets": [{"src": "/content/assets/question-images/<bank>/<f>.jpg",
                       "alt": "...", "page_idx": 12, "bbox": [x1,y1,x2,y2]}]

USAGE

    # look first, write nothing
    python tools/import_mineru_bank.py /path/to/mineru/out --dry-run

    # one volume, small sample, to eyeball the shapes
    python tools/import_mineru_bank.py /path/to/mineru/out/vol1 --limit 40

    # the real thing
    python tools/import_mineru_bank.py /path/to/mineru/out

    # the MinerU bank supersedes the text-only one; park it so quizzes do not
    # serve every question twice
    python tools/import_mineru_bank.py /path/to/mineru/out --retire go-extracted

HONEST LIMITS

  MinerU recovers figures, not mathematics. A stem whose content was a rendered
  formula still arrives thin, and an option list rendered as LaTeX still arrives
  empty. Those questions are kept, marked answer_pending with a needs_fix note,
  and given their page number and bbox so they can be repaired by hand. Nothing
  is guessed: a question this script is unsure about is never served.
"""

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import extract_go_bank as ego
import texwrap
import import_questions as imp
import ingest
from core import content as registry

CONTENT = os.path.join(ROOT, "content")
BANKS_DIR = os.path.join(CONTENT, "banks")
REVIEW_DIR = os.path.join(CONTENT, "review")
ASSETS_ROOT = os.path.join(CONTENT, "assets", "question-images")

DEFAULT_BANK = "mineru"

# The URL prefix core/api.py serves content/assets from. Keep the two in step.
ASSET_URL_PREFIX = "/content/assets/question-images"

FIGURE_PLACEHOLDER = "Refer to the figure below."

PENDING_NOTE = (
    "Answer not printed in the source, or not recoverable from the extraction. "
    "Look it up, then run 'python tools/answer_fill.py --next' to record it. "
    "Until then this question stays out of quizzes so it cannot be graded "
    "against a missing answer."
)


# ===========================================================================
# MinerU markdown grammar
# ===========================================================================
# A GO volume rendered by MinerU looks like this (### depth varies, and the
# heading hashes are sometimes dropped entirely, so they are optional):
#
#   ## 1 Algorithms (358)                     <- chapter: subject + group
#   ## 1.44                                   <- section number, often alone...
#   ## Topological Sort (4)                   <- ...with its name on the next line
#   ## 1.44.2 Topological Sort: GATE CSE 2014 | Set 1 | Question: 13
#   Consider the directed graph below given.
#   ![](images/c004_<sha>.jpg)                <- the figure
#   <details><summary>flowchart</summary>```mermaid ...```</details>
#   Which one of the following is TRUE?
#   A. The graph does not have any topological ordering.
#   B. Both PQRS and SRQP are topological orderings.
#   gatecse-2014-set1 graph-algorithms easy topological-sort
#   ## Answer key                             <- per-question link, ends the block
#   ...
#   Answer Keys                               <- chapter end, the real values
#   <table><tr><td>1.44.2</td><td>C</td></tr>...
#
# The a.b.c heading is the anchor: unlike the pdftotext path, MinerU preserves
# the printed numbering, so blocks never have to be counted into position and a
# missing "Answer key" link cannot desynchronise the answer refs.
Q_HEAD = re.compile(r"^#{0,6}[ \t]*(\d+\.\d+\.\d+)[ \t]+(\S.*?)[ \t]*$")
SEC_FULL = re.compile(r"^#{0,6}[ \t]*(\d+\.\d+)[ \t]+(.{2,70}?)[ \t]*\((\d+)\)[ \t]*$")
SEC_NUM = re.compile(r"^#{1,6}[ \t]*(\d+\.\d+)[ \t]*$")
SEC_NAME = re.compile(r"^#{1,6}[ \t]*([A-Za-z][^()\n]{1,69}?)[ \t]*\((\d+)\)[ \t]*$")
CHAP_FULL = re.compile(r"^#{0,6}[ \t]*(\d+)[ \t]+([A-Za-z][^()\n]{2,90}?)[ \t]*\((\d+)\)[ \t]*$")

ANSWER_KEYS = re.compile(r"^#{0,6}[ \t]*answer[ \t]+keys[ \t]*$", re.I)
# The per-question link. MinerU keeps the little "goto" glyph, so allow trailing
# non-word junk, but do NOT allow a trailing 's' - that is the plural section.
ANSWER_MARK = re.compile(r"^#{0,6}[ \t]*answer[ \t]+key[^\w]*$", re.I)

IMG_REF = re.compile(r"!\[[^\]]*\]\(\s*(images/[^)\s]+?)\s*\)")
DETAILS = re.compile(r"<details\b.*?</details>", re.S | re.I)
TABLE = re.compile(r"<table\b.*?</table>", re.S | re.I)
KEY_CELL = re.compile(
    r"<td>\s*(\d+\.\d+\.\d+)\s*</td>\s*<td>\s*([^<]*?)\s*</td>", re.I
)

# "A. text", "(A) text", "A.text", and the bare "A." that a dropped formula
# leaves behind. A delimiter is mandatory, otherwise every sentence starting
# with "A " becomes an option.
OPT_LINE = re.compile(r"^\(?([A-H])\)?[ \t]*[.)][ \t]*(.*)$")
OPT_PAREN = re.compile(r"^\(([A-H])\)[ \t]*(.*)$")

MERMAID = re.compile(r"```mermaid\s*(.*?)```", re.S)
# MinerU wraps the C/SQL/pseudocode listings that many GATE questions are built
# around in fenced blocks. Flattening those into the prose destroyed them: the
# fence markers showed up literally and every line collapsed onto one, so a
# twenty-line program became an unreadable sentence. They are lifted out here
# and carried separately, the same way figures are.
CODE_FENCE = re.compile(r"```[ \t]*([A-Za-z0-9+#_-]*)[ \t]*\n?(.*?)```", re.S)
# MinerU does not always use a fence. Longer listings come back as a pre-wrap
# div instead, and because only its opening line begins with "<" the program
# inside was surviving the markup filter and getting flattened into the prose.
CODE_DIV = re.compile(
    r'<div[^>]*class="[^"]*mineru-algorithm[^"]*"[^>]*>(.*?)</div>', re.S | re.I)
HTML_TAG = re.compile(r"<[^>]+>")

# Boilerplate MinerU carries over from the book's running headers/footers.
NOISE = re.compile(
    r"^\s*(?:"
    r"answer\s+key\W*|"
    r"gate\s*overflow\b.*|"
    r"©.*|"
    r"page\s+\d+(\s+of\s+\d+)?|"
    r"\d{1,4}|"
    r"[\W_]+"
    r")\s*$",
    re.I,
)

SKIP_SECTION = re.compile(
    r"^#{0,6}\s*(topic-?wise key concepts|subject overview|quick formula reference|"
    r"important tips for gate|mark distribution|table of contents|contributors|"
    r"index|syllabus|definition|formulas?/theorems?|properties/identities|"
    r"pitfalls/tricks|techniques/shortcuts)\s*:?\s*$",
    re.I,
)

DIFFICULTY_TAG = {
    "easy": "easy",
    "normal": "medium",
    "medium": "medium",
    "difficult": "hard",
    "hard": "hard",
}

NO_ANSWER_TOKENS = {"", "N/A", "NA", "TBA", "TBD", "X", "-", "--", "?", "NONE"}

# MinerU does not always delimit its maths. Plenty of stems arrive with raw
# LaTeX sitting in the prose - "f(x) = \left\{ \begin{array}..." - which the UI
# then shows verbatim because nothing marks it as a formula. A backslash
# followed by letters is the giveaway: English prose does not contain it, so a
# run of maths-shaped tokens holding at least one such command can be wrapped
# safely. Anything without a command is left alone rather than guessed at.
TEX_TOKEN = re.compile(
    # \left( and \right. carry their delimiter, including the "." that means an
    # invisible one - leaving that dot outside broke the pair and made KaTeX
    # reject the whole formula. A braced group is one token too, so \text {for}
    # and {l l} stay inside the run instead of ending it on the first ordinary
    # word they contain.
    r"(?:\\(?:left|right|big|Big|bigg|Bigg)[lr]?[ \t]*(?:\\[{}|]|[.|\[\]()/])"
    r"|\{[^{}]*\}|\\[A-Za-z]+\*?|\\[\\{}|,;:!\[\]()]|[\[\]()^_&|<>=+\-*/,;]"
    r"|\d+(?:\.\d+)?|[A-Za-z](?![A-Za-z]))"
)
# A superscript or subscript group is as reliable a marker as a command: prose
# does not contain "x ^ {2}" or "P _ { 0 }". Accepting it lifts the stems whose
# maths is pure notation with no \command in it at all.
TEX_SCRIPT = re.compile(r"[\^_][ \t]*\{")
TEX_RUN = re.compile(
    r"(?<![\\$\w])((?:%s)(?:[ \t]*(?:%s))*)" % (TEX_TOKEN.pattern, TEX_TOKEN.pattern)
)
TEX_CMD = re.compile(r"\\[A-Za-z]+")

# The GO tag line sometimes ends up glued to the last sentence instead of on a
# line of its own, and then it reads as part of the question.
# Anchored on a gate#### token: once that appears, everything after it to the
# end of the stem is the tag run. Without the anchor an ordinary trailing word
# could be mistaken for a tag.
TRAIL_TAGS = re.compile(
    r"\s+gate(?:cse|it|da|me|ec|overflow)?-?\d{4}[a-z0-9-]*"
    r"(?:\s+[a-z][a-z0-9-]*)*\s*$"
)


def strip_trailing_tags(text, min_keep=20):
    """Drop a GO tag run that got glued onto the end of the stem.

    min_keep guards against eating the whole string. A stem needs a sentence
    left over, but an option can legitimately be as short as "A-R B-P C-Q D-S",
    so callers working on options pass a lower floor.
    """
    out = TRAIL_TAGS.sub("", text).strip()
    return out if len(out) >= min_keep else text


FIGURE_WORDS = (
    "figure",
    "fig.",
    "diagram",
    "graph below",
    "graph given",
    "shown below",
    "given below",
    "following graph",
    "following circuit",
    "following diagram",
    "below given",
    "as shown",
    "table below",
)


# ===========================================================================
# locating a MinerU run on disk
# ===========================================================================
CHUNK_DIR = re.compile(r"^p(\d+)_(\d+)$")


def discover_volumes(paths):
    """Every MinerU volume under the given paths, as (name, dir) pairs.

    A volume is any directory holding merged/full.md. Passing the run root picks
    up all of them; passing a single volume directory picks up just that one.
    """
    found = []
    seen = set()

    def consider(d):
        if not os.path.isdir(d):
            return
        if os.path.isfile(os.path.join(d, "merged", "full.md")):
            real = os.path.realpath(d)
            if real not in seen:
                seen.add(real)
                found.append((os.path.basename(d.rstrip(os.sep)), d))

    for path in paths:
        path = os.path.abspath(path)
        consider(path)
        if os.path.isdir(path):
            for name in sorted(os.listdir(path)):
                consider(os.path.join(path, name))
    return found


def chunk_offsets(vol_dir):
    """[(chunk_index, first_page)] so a chunk-local page_idx can be absolutised.

    MinerU splits a big PDF into page ranges and restarts page_idx at 0 in each
    one. The directory name carries the range, and merged/ prefixes that chunk's
    images with cNNN where NNN is the chunk's position in sorted order.
    """
    names = sorted(
        n for n in os.listdir(vol_dir) if CHUNK_DIR.match(n) and os.path.isdir(os.path.join(vol_dir, n))
    )
    return [(i, int(CHUNK_DIR.match(n).group(1)), n) for i, n in enumerate(names)]


def content_list_paths(vol_dir, chunk_name):
    """The content_list.json for one chunk.

    The flat v1 file is preferred: it carries page_idx on every node, which is
    exactly what provenance needs. MinerU's v2 file groups nodes by page instead
    and is only used as a fallback (see normalise_nodes).
    """
    base = os.path.join(vol_dir, chunk_name)
    v1, v2 = [], []
    for dirpath, _dirs, files in os.walk(base):
        for name in files:
            if name.endswith("_content_list_v2.json"):
                v2.append(os.path.join(dirpath, name))
            elif name.endswith("_content_list.json"):
                v1.append(os.path.join(dirpath, name))
    return sorted(v1) + sorted(v2)


def normalise_nodes(data):
    """Yield flat image-ish nodes from either content_list layout.

    v1: a flat list of nodes, each with ``img_path`` and ``page_idx``.
    v2: a list of pages, each a list of nodes whose image path is nested under
        ``content.image_source.path`` and whose page index is its position.
    """
    if not isinstance(data, list):
        return

    for i, entry in enumerate(data):
        if isinstance(entry, dict):
            if entry.get("img_path"):
                yield entry
                continue
            content = entry.get("content")
            if isinstance(content, dict) and content.get("image_source"):
                path = (content.get("image_source") or {}).get("path")
                if path:
                    yield dict(
                        img_path=path,
                        type=entry.get("type") or "image",
                        sub_type=entry.get("sub_type") or "",
                        bbox=entry.get("bbox"),
                        page_idx=entry.get("page_idx"),
                        image_caption=content.get("image_caption") or [],
                        content=content.get("content") or "",
                    )
        elif isinstance(entry, list):
            # v2 page bucket: the page index is the bucket's position.
            for node in normalise_nodes(entry):
                node.setdefault("page_idx", i)
                if node.get("page_idx") is None:
                    node["page_idx"] = i
                yield node


def build_image_index(vol_dir, source_file):
    """{merged_filename: metadata} for every image MinerU described structurally.

    Keyed on the merged/ filename (``cNNN_<sha>.jpg``) because that is what the
    markdown references. Anything MinerU did not describe still imports, just
    without a page number or bbox.
    """
    index = {}
    for chunk_idx, first_page, chunk_name in chunk_offsets(vol_dir):
        paths = content_list_paths(vol_dir, chunk_name)
        if not paths:
            continue
        try:
            with open(paths[0], "r", encoding="utf-8") as fh:
                raw = json.load(fh)
        except (ValueError, OSError):
            continue
        for node in normalise_nodes(raw):
            img = node.get("img_path") or ""
            if not img:
                continue
            base = os.path.basename(img)
            merged_name = "c%03d_%s" % (chunk_idx, base)
            page = node.get("page_idx")
            meta = dict(
                node_type=node.get("type") or "image",
                sub_type=node.get("sub_type") or "",
                page_idx=(first_page + page) if isinstance(page, int) else None,
                bbox=node.get("bbox") if isinstance(node.get("bbox"), list) else None,
                caption=" ".join(node.get("image_caption") or [])[:200],
                source_file=source_file,
                chunk=chunk_name,
            )
            content = node.get("content") or ""
            m = MERMAID.search(content)
            if m:
                meta["mermaid"] = m.group(1).strip()[:1200]
            index[merged_name] = meta
    return index


# ===========================================================================
# segmenting the markdown into question blocks
# ===========================================================================
def parse_markdown(md):
    """Split merged/full.md into question blocks and collect the answer tables.

    Returns (blocks, answers). A block keeps its raw lines; body parsing happens
    later so that the two concerns stay separable and testable.
    """
    lines = md.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    blocks = []
    answers = {}
    current = None
    chapter = None
    section = None
    section_ref = None
    pending_section_ref = None
    in_answer_keys = False
    seen_refs = set()

    def flush():
        nonlocal current
        if current and current["lines"]:
            blocks.append(current)
        current = None

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        # ---- answer-key tables ------------------------------------------
        # These are emitted as HTML tables, one <td> pair per question ref, and
        # they may run for dozens of lines. Harvest pairs wherever they appear:
        # a stray table outside a marked section is still a real answer key.
        pairs = KEY_CELL.findall(line)
        if pairs:
            for ref, value in pairs:
                answers.setdefault(ref, value.strip())
            if in_answer_keys:
                continue

        if ANSWER_KEYS.match(stripped):
            flush()
            in_answer_keys = True
            continue

        # ---- headings ----------------------------------------------------
        m = Q_HEAD.match(stripped)
        if m and not SEC_FULL.match(stripped):
            in_answer_keys = False
            flush()
            ref, title = m.group(1), m.group(2).strip()
            # Duplicate refs happen where MinerU's chunk boundaries overlap.
            # Suffix rather than drop, so no question is silently lost.
            uniq = ref
            n = 2
            while uniq in seen_refs:
                uniq = "%s+%d" % (ref, n)
                n += 1
            seen_refs.add(uniq)
            topic_hint, exam, paper_q = "", "", ""
            if ":" in title:
                head, tail = title.split(":", 1)
                if 2 < len(head) < 70:
                    topic_hint, exam = head.strip(), tail.strip()
            qm = re.search(r"Question:?\s*(\S+)\s*$", title)
            if qm:
                paper_q = qm.group(1)
            current = dict(
                ref=ref,
                uniq_ref=uniq,
                title=title,
                topic_hint=topic_hint,
                exam=exam,
                paper_q=paper_q,
                section=section,
                section_ref=section_ref,
                chapter=chapter,
                lines=[],
            )
            continue

        m = CHAP_FULL.match(stripped)
        if m and "." not in m.group(1):
            in_answer_keys = False
            flush()
            name = m.group(2).strip()
            subject_part, _, group_part = name.partition(":")
            chapter = dict(
                num=m.group(1),
                subject=(subject_part or name).strip(),
                group=(group_part or name).strip(),
                count=int(m.group(3)),
            )
            section = section_ref = None
            continue

        m = SEC_FULL.match(stripped)
        if m:
            in_answer_keys = False
            flush()
            section_ref, section = m.group(1), m.group(2).strip()
            pending_section_ref = None
            continue

        m = SEC_NUM.match(stripped)
        if m:
            in_answer_keys = False
            flush()
            pending_section_ref = m.group(1)
            continue

        if pending_section_ref:
            m = SEC_NAME.match(stripped)
            if m:
                section_ref, section = pending_section_ref, m.group(1).strip()
                pending_section_ref = None
                continue
            if stripped:
                pending_section_ref = None

        if ANSWER_MARK.match(stripped):
            # Ends the current question without opening a new one. The next real
            # question announces itself with its own numbered heading.
            flush()
            continue

        if in_answer_keys:
            continue

        if SKIP_SECTION.match(stripped):
            flush()
            continue

        if current is not None:
            current["lines"].append(line)

    flush()
    return blocks, answers


def html_table_to_text(html):
    """Flatten a MinerU HTML table into pipe-separated rows.

    A table inside a question stem is content, not decoration, so it has to
    survive - but raw markup must never reach the UI, which renders question
    text as a text node. Rows become 'a | b | c' lines instead.
    """
    rows = []
    for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", html, re.S | re.I):
        cells = [
            re.sub(r"<[^>]+>", " ", c)
            for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row, re.S | re.I)
        ]
        cells = [re.sub(r"\s+", " ", c).strip() for c in cells]
        if any(cells):
            # Lead with the pipe. A match-the-pairs table starts its rows with
            # "(A)", which is exactly the shape of an option label - without
            # this the four table rows were parsed as four more options and the
            # question ended up with eight.
            rows.append("| " + " | ".join(cells))
    return "\n".join(rows)


def parse_block_body(block, image_index):
    """Pull the stem, options, tags and figure references out of one block."""
    text_parts = []
    option_pairs = []          # [(letter, text)] - may arrive out of order
    tags = []
    images = []
    has_table = False
    current_letter = None
    current_buf = None

    def close_option():
        if current_letter is not None:
            option_pairs.append((current_letter, " ".join(current_buf).strip()))

    body = "\n".join(block["lines"])

    # Fenced diagram blocks are MinerU's textual rendering of a figure. They are
    # captured per-asset from content_list.json, so strip them here rather than
    # letting mermaid source leak into the question stem.
    body = DETAILS.sub(" ", body)

    code_blocks = []

    def take_code(m):
        lang = (m.group(1) or "").strip().lower()
        code = m.group(2).replace("\r\n", "\n").strip("\n")
        # A fence holding one short line is almost always an inline snippet the
        # sentence needs, not a listing; leave those in the prose.
        if code.strip() and ("\n" in code or len(code) > 40):
            code_blocks.append(dict(lang=lang, code=code[:4000]))
            return " "
        return " " + code.replace("\n", " ") + " "

    def take_div(m):
        code = HTML_TAG.sub("", m.group(1))
        code = (code.replace("&lt;", "<").replace("&gt;", ">")
                    .replace("&amp;", "&").replace("&quot;", '"'))
        code = code.replace("\r\n", "\n").strip("\n")
        if code.strip():
            code_blocks.append(dict(lang="", code=code[:4000]))
        return " "

    body = CODE_DIV.sub(take_div, body)
    body = CODE_FENCE.sub(take_code, body)

    # Table rows are parked behind a placeholder rather than dropped inline.
    # A match-the-following table starts its rows with "(A)", "(B)" - exactly
    # what the option parser looks for - so flattening it into the body made
    # every row register as an extra option, and a four-option question came
    # out with eight. The rows are put back after option parsing is done.
    tables = []

    def swap_table(m):
        nonlocal has_table
        has_table = True
        flat = html_table_to_text(m.group(0))
        if not flat:
            return " "
        tables.append(flat)
        return "\n\x00T%d\x00\n" % (len(tables) - 1)

    body = TABLE.sub(swap_table, body)

    for line in body.split("\n"):
        # Figures first: an image reference can share a line with prose.
        refs = IMG_REF.findall(line)
        if refs:
            for ref in refs:
                name = os.path.basename(ref)
                if name not in [i["name"] for i in images]:
                    images.append(dict(name=name, meta=image_index.get(name)))
            line = IMG_REF.sub(" ", line)

        stripped = line.strip()
        # A sub-heading inside a question body ("## Turn around time") is not a
        # question, section or chapter heading, so nothing above caught it and
        # the hashes travelled into the stem.
        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()
        if not stripped or NOISE.match(stripped):
            continue
        if stripped.startswith("<"):        # any residual markup, never content
            continue

        # A sub-heading inside a question body is content - "Turn around time"
        # is the thing being asked about - but its markdown hashes are not, and
        # they were being read out as part of the sentence.
        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()
            if not stripped:
                continue

        m = OPT_LINE.match(stripped) or OPT_PAREN.match(stripped)
        if m:
            close_option()
            current_letter = m.group(1).upper()
            current_buf = [m.group(2).strip()] if m.group(2).strip() else []
            continue

        if imp.looks_like_tag_line(stripped) and len(stripped) < 220:
            tags.extend(re.findall(r"\b[a-z][a-z0-9]*(?:[-&][a-z0-9]+)*\b", stripped))
            continue

        if current_buf is not None:
            current_buf.append(stripped)
        else:
            text_parts.append(stripped)

    close_option()

    options, option_problem = order_options(option_pairs)

    if tables:
        text_parts = [
            tables[int(t[2:-1])] if t.startswith("\x00T") else t
            for t in text_parts
        ]
    text = re.sub(r"[ \t]+", " ", " ".join(text_parts)).strip()
    text = re.sub(r"\s+([,.;:?])", r"\1", text)
    text = strip_trailing_tags(text)
    text = texwrap.wrap_bare_math(text)

    return dict(
        text=text,
        options=options,
        option_problem=option_problem,
        code_blocks=code_blocks,
        tags=[t for t in tags if t],
        images=images,
        has_table=has_table,
    )


ARRAY_BLOCK = re.compile(
    r"\\begin\{array\}\s*(?:\{[^{}]*\})?\s*(.*?)\s*\\end\{array\}", re.S
)


def strip_outer_braces(text):
    """Drop the wrapping {...} of an array cell without touching inner groups.

    A plain strip("{} ") would eat the closing braces of trailing subscripts too,
    turning "{ f _ { 1 } }" into "f _ { 1" and breaking the formula. So scan for
    the brace that actually matches the first one and only remove that pair.
    """
    text = (text or "").strip()
    while len(text) > 1 and text[0] == "{" and text[-1] == "}":
        depth = 0
        for i, ch in enumerate(text):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
        if i != len(text) - 1:      # first brace closes early: not a wrapper
            break
        text = text[1:-1].strip()
    return text


def split_stacked_options(ordered):
    """Un-merge options that MinerU collapsed into one LaTeX array.

    The GO books print options in two columns. When both cells of a column are
    mathematics, MinerU sometimes emits them as a single stacked array under the
    first option's letter and leaves the second letter empty:

        A. $\\begin{array}{r} {A(n) = \\Omega(W(n))} \\\\ {A(n) = O(W(n))} \\end{array}$
        B.

    The two rows are genuinely two separate options, so splitting them recovers
    real content rather than inventing it. This only fires when the list already
    has blank entries for the rows to fill, which is what makes it safe: a real
    matrix-valued option stands alone with no empty sibling, so it is left
    untouched. Returns (options, changed).
    """
    if not ordered or not any(not t for t in ordered):
        return ordered, False

    out = []
    changed = False
    for text in ordered:
        m = ARRAY_BLOCK.search(text or "")
        rows = re.split(r"\\\\", m.group(1)) if m else []
        rows = [strip_outer_braces(r) for r in rows]
        rows = [r for r in rows if r]
        if len(rows) < 2:
            out.append(text)
            continue
        # Keep the surrounding math delimiters so each row still renders.
        out.extend("$%s$" % r for r in rows)
        changed = True

    if not changed:
        return ordered, False

    # Drop exactly as many trailing blanks as rows we gained, so the option
    # count stays honest instead of growing past what the paper printed.
    gained = len(out) - len(ordered)
    while gained > 0 and "" in out:
        out.remove("")
        gained -= 1
    return out, True


def order_options(pairs):
    """Options print in two columns, so A and C often precede B and D.

    Sorting by letter fixes that. Anything the sort cannot make sense of is
    reported rather than straightened out into a plausible-looking lie, but the
    recovered text is always returned alongside the complaint so a human
    repairing the question can see what the extraction actually found.
    """
    if not pairs:
        return [], None

    letters = [p[0] for p in pairs]
    # The tag run follows the last option on the same line often enough that it
    # ends up glued to option D. Strip it there too, not just off the stem.
    ordered = [strip_trailing_tags(re.sub(r"\s+", " ", t).strip(), min_keep=3)
               for _l, t in sorted(pairs)]
    # MinerU collapses stacked option columns into a single LaTeX array. Undo
    # that first: judging the list before un-merging makes a recoverable
    # question look half-empty, and leaves a blank option on screen.
    ordered, _unstacked = split_stacked_options(ordered)

    if len(set(letters)) != len(letters):
        return ordered, "duplicate option letters"

    expected = [chr(ord("A") + i) for i in range(len(letters))]
    if sorted(letters) != expected:
        return (
            ordered,
            "option letters %s are not a run from A" % ",".join(sorted(letters)),
        )

    blank = sum(1 for t in ordered if not t)
    if blank:
        return ordered, "%d of %d options came through empty" % (blank, len(ordered))

    # Two options that print identically are never a real GATE question - it means
    # a rendered formula (e.g. a fraction or a Greek letter) dropped out during
    # extraction and left two options reading the same leftover word ("and").
    # Answer keys have already committed to one letter, so silently leaving this
    # servable would let a quiz grade against text the person never actually saw.
    non_empty = [t for t in ordered if t]
    dupes = {t for t in non_empty if non_empty.count(t) > 1}
    if dupes:
        return ordered, "options are not distinct: %r repeated" % sorted(dupes)[0]
    return ordered, None


# ===========================================================================
# answers
# ===========================================================================
RANGE_ANY = re.compile(
    r"^(-?\d+(?:\.\d+)?)\s*(?:to|:|-|\u2013)\s*(-?\d+(?:\.\d+)?)$", re.I
)
LETTER_SET = re.compile(r"^[A-H](?:\s*[,;/&]\s*[A-H])*$", re.I)
NUMBER_ONLY = re.compile(r"^-?\d+(?:\.\d+)?$")


def read_answer(raw):
    """Normalise one answer-key cell.

    Returns (kind, payload) where kind is 'letters', 'value', 'range' or
    'unreadable', or None when the source printed no answer at all. GO prints
    ranges as "10:10" and "147.1 : 148.1", multi-selects as "B;D", and no-answer
    as N/A, TBA or X.
    """
    if raw is None:
        return None
    raw = str(raw).strip()
    if raw.upper().replace(" ", "") in NO_ANSWER_TOKENS:
        return None

    m = RANGE_ANY.match(raw)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        if lo > hi:
            lo, hi = hi, lo
        return "range", (lo, hi)
    if NUMBER_ONLY.match(raw):
        return "value", float(raw)
    if LETTER_SET.match(raw):
        letters = sorted({c.upper() for c in re.findall(r"[A-Ha-h]", raw)})
        return "letters", letters
    return "unreadable", raw


def apply_answer(q, parsed_answer, options):
    """Settle type, answer and any needs_fix reason. Never guesses."""
    if parsed_answer is None:
        q["_pending"] = True
        q["_reason"] = "no answer printed in the source answer key"
        q["type"] = "mcq" if len(options) >= 2 else "nat"
        return

    kind, payload = parsed_answer
    if kind == "range":
        lo, hi = payload
        q["type"] = "nat"
        q["answer_value"] = round((lo + hi) / 2.0, 6)
        q["tolerance"] = round(abs(hi - lo) / 2.0, 6)
        return
    if kind == "value":
        q["type"] = "nat"
        q["answer_value"] = payload
        q["tolerance"] = 0.01 if isinstance(payload, float) and payload % 1 else 0
        return
    if kind == "letters":
        idx = [ord(c) - 65 for c in payload]
        q["type"] = "msq" if len(idx) > 1 else "mcq"
        if not options or max(idx) >= len(options):
            # The answer is known but there is nothing valid to attach it to.
            # Keep the letters verbatim so a human repair is a copy, not a hunt.
            q["_pending"] = True
            q["_reason"] = "answer %s but only %d option(s) recovered" % (
                ";".join(payload),
                len(options),
            )
            q["answer_from_source"] = ";".join(payload)
            return
        q["answer"] = idx
        return

    q["_pending"] = True
    q["_reason"] = "answer %r could not be read" % payload
    q["answer_from_source"] = str(payload)
    q["type"] = "mcq" if len(options) >= 2 else "nat"


# ===========================================================================
# assets
# ===========================================================================
def asset_filename(volume_slug, merged_name):
    """A stable, collision-free, app-owned filename.

    MinerU names images by content hash, which is already stable, but the merged
    prefix is a chunk index that shifts if the run is re-chunked. Rebuilding the
    name from the volume slug plus the hash means a re-import overwrites the same
    file instead of littering the assets folder with near-duplicates.
    """
    base, ext = os.path.splitext(merged_name)
    ext = (ext or ".jpg").lower()
    digest = base.split("_", 1)[-1] if "_" in base else base
    digest = re.sub(r"[^0-9a-z]", "", digest.lower())[:24] or "img"
    return "%s-%s%s" % (volume_slug, digest, ext)


class AssetCopier(object):
    """Copies referenced images once each, and reports what it did."""

    def __init__(self, dest_dir, dry_run=False):
        self.dest_dir = dest_dir
        self.dry_run = dry_run
        self.copied = 0
        self.reused = 0
        self.missing = []
        self._done = {}

    def add(self, src_path, volume_slug, merged_name):
        key = (volume_slug, merged_name)
        if key in self._done:
            self.reused += 1
            return self._done[key]
        name = asset_filename(volume_slug, merged_name)
        if not os.path.isfile(src_path):
            self.missing.append(merged_name)
            return None
        if not self.dry_run:
            os.makedirs(self.dest_dir, exist_ok=True)
            dest = os.path.join(self.dest_dir, name)
            if not os.path.exists(dest) or os.path.getsize(dest) != os.path.getsize(src_path):
                shutil.copy2(src_path, dest)
        self.copied += 1
        self._done[key] = name
        return name


def figure_asset(url_base, filename, meta, index):
    """The sidecar record that goes into the bank JSON. Paths only, never bytes."""
    asset = {"src": "%s/%s" % (url_base, filename)}
    caption = (meta or {}).get("caption") or ""
    sub_type = (meta or {}).get("sub_type") or ""
    if caption:
        asset["alt"] = caption[:200]
    elif sub_type:
        asset["alt"] = "Figure %d for this question (%s)" % (index + 1, sub_type)
    else:
        asset["alt"] = "Figure %d for this question" % (index + 1)
    if meta:
        if meta.get("page_idx") is not None:
            asset["page_idx"] = meta["page_idx"]
        if meta.get("bbox"):
            asset["bbox"] = meta["bbox"]
        if meta.get("sub_type"):
            asset["kind"] = meta["sub_type"]
        if meta.get("mermaid"):
            asset["mermaid"] = meta["mermaid"]
    return asset


# ===========================================================================
# building questions
# ===========================================================================
def volume_slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "vol"


def resolve_topic(block, parsed, maps, topics, matchers, min_score):
    """Section heading, then question title, then GO tags, then keywords.

    Delegates to import_questions so this converter and the text importer can
    never drift into disagreeing about what a topic slug means.
    """
    topic_map, subject_map, chapter_map, ignore = maps
    shim = dict(
        section=block.get("section"),
        topic_hint=block.get("topic_hint"),
        chapter=block.get("chapter"),
    )
    key, subject, source, unknown = imp.resolve_topic(
        shim, parsed, topic_map, subject_map, chapter_map, ignore, topics
    )
    score = None
    if key is None:
        key, _runner, score, _hits, problem = imp.classify(
            parsed["text"], parsed["options"], matchers, topics,
            subject, min_score,
        )
        source = "keyword" if key and not problem else None
        if problem:
            key = None
    return key, source, score, unknown


def build_question(block, parsed, answers, ctx):
    """One MinerU block -> one GitGrind question dict (plus private _ fields)."""
    tags = parsed["tags"]
    ref = block["uniq_ref"]

    marks = 2
    for tag in tags:
        if tag in imp.GO_MARK_TAG:
            marks = imp.GO_MARK_TAG[tag]
            break

    difficulty = "medium"
    for tag in tags:
        if tag in DIFFICULTY_TAG:
            difficulty = DIFFICULTY_TAG[tag]
            break

    year = None
    ym = imp.GO_YEAR.search(" ".join(tags) + " " + (block.get("exam") or ""))
    if ym:
        year = int(ym.group(1))

    # ---- figures -----------------------------------------------------------
    figures = []
    for i, img in enumerate(parsed["images"]):
        src = os.path.join(ctx["images_dir"], img["name"])
        filename = ctx["assets"].add(src, ctx["volume_slug"], img["name"])
        if not filename:
            continue
        figures.append(figure_asset(ctx["url_base"], filename, img["meta"], i))

    # ---- text --------------------------------------------------------------
    text = parsed["text"]
    if figures:
        low = text.lower()
        if not any(w in low for w in FIGURE_WORDS):
            # The stem clearly leans on a figure it never names. Say so rather
            # than converting the image to markdown and hoping the UI copes.
            text = (text + " " + FIGURE_PLACEHOLDER).strip() if text else FIGURE_PLACEHOLDER

    q = dict(
        id="mineru-%s-%s" % (ctx["volume_slug"], ref.replace(".", "-").replace("+", "d")),
        kind=ctx["kind"],
        difficulty=difficulty,
        marks=marks,
        text=text,
        options=parsed["options"],
        explain="",
    )
    if year:
        q["year"] = year
    if figures:
        q["figure_assets"] = figures
    if parsed["code_blocks"]:
        q["code_blocks"] = parsed["code_blocks"]

    # ---- type hints from GO's own tags ------------------------------------
    if "numerical-answers" in tags and not parsed["options"]:
        q["type"] = "nat"
    if "multiple-selects" in tags:
        q["type"] = "msq"

    apply_answer(q, read_answer(answers.get(block["ref"])), parsed["options"])

    # ---- reasons a human should look at this ------------------------------
    reasons = []
    if q.get("_reason"):
        reasons.append(q.pop("_reason"))
    if parsed["option_problem"]:
        reasons.append(parsed["option_problem"])
        q["_pending"] = True
    if figures and len(text) < 40:
        reasons.append("figure-dependent question with almost no stem text")
        q["_pending"] = True
    if not text:
        reasons.append("no question text recovered")
        q["_pending"] = True
    if parsed["has_table"]:
        reasons.append("stem contains a table; check it flattened readably")
    if q.get("type") != "nat" and not q.get("_pending") and len(parsed["options"]) < 2:
        reasons.append("fewer than two options")
        q["_pending"] = True

    q["_reasons"] = reasons
    q["_origin"] = dict(
        source_file=ctx["source_file"],
        volume=ctx["volume_name"],
        ref=block["ref"],
        exam=block.get("exam", ""),
        section=block.get("section") or "",
        paper_question=block.get("paper_q", ""),
        tags=tags[:8],
    )
    pages = [f["page_idx"] for f in figures if f.get("page_idx") is not None]
    if pages:
        q["_origin"]["page_idx"] = min(pages)
        boxes = [f["bbox"] for f in figures if f.get("bbox")]
        if boxes:
            q["_origin"]["bbox"] = boxes[0]
    return q


def finalise(q):
    """Strip private fields and settle the shape that lands in the bank file."""
    pending = bool(q.pop("_pending", False))
    reasons = q.pop("_reasons", [])
    origin = q.pop("_origin", {})

    out = {}
    for field in (
        "id", "topic", "kind", "type", "marks", "difficulty", "year",
        "text", "options", "answer", "answer_value", "tolerance",
        "answer_from_source", "figure_assets", "code_blocks", "explain",
    ):
        if field in q and q[field] not in (None, ""):
            out[field] = q[field]
    out.setdefault("type", "mcq")
    out.setdefault("marks", 2)
    out.setdefault("difficulty", "medium")
    out.setdefault("kind", "pyq")
    out.setdefault("options", [])
    if origin:
        out["origin"] = origin

    if pending:
        out["answer_pending"] = True
        # Keep the key even though the question is held back. It is usually the
        # OPTIONS that failed, not the answer - the source printed a perfectly
        # good "C" and the option list it indexes into is what did not survive.
        # Dropping the answer here threw that away and made the question look
        # unanswered, so a later option recovery had nothing to snap back into.
        if not out.get("answer_from_source"):
            if out.get("answer"):
                out["answer_from_source"] = ";".join(chr(65 + i) for i in out["answer"])
            elif out.get("answer_value") is not None:
                out["answer_from_source"] = str(out["answer_value"])
        out.pop("answer", None)
        out.pop("answer_value", None)
        out.pop("tolerance", None)
        out["explain"] = PENDING_NOTE
        if reasons:
            out["needs_fix"] = "; ".join(reasons)
    elif reasons:
        # Servable, but worth a look. needs_fix is advisory here, not blocking.
        out["needs_fix"] = "; ".join(reasons)
    return out


# ===========================================================================
# the run
# ===========================================================================
def convert(volumes, args):
    topics = imp.load_syllabus()
    matchers, _missing = imp.compile_lexicon(topics)
    maps = imp.load_tag_map()
    if not maps[0]:
        raise SystemExit("content/go_tag_map.json is missing or empty.")

    assets_dir = os.path.join(ASSETS_ROOT, args.bank)
    assets = AssetCopier(assets_dir, dry_run=args.dry_run)
    url_base = "%s/%s" % (ASSET_URL_PREFIX, args.bank)

    by_subject = defaultdict(list)
    unsorted = []
    stats = Counter()
    topic_sources = Counter()
    seen_hashes = {}
    seen_ids = set()

    existing = set()
    if args.skip_existing:
        for q in registry.question_bank(reload=True).values():
            existing.add(ingest.text_hash(q))

    for volume_name, vol_dir in volumes:
        slug = volume_slug(volume_name)
        merged = os.path.join(vol_dir, "merged")
        md_path = os.path.join(merged, "full.md")
        images_dir = os.path.join(merged, "images")

        with open(md_path, "r", encoding="utf-8", errors="replace") as fh:
            md = imp.repair_mojibake(fh.read())

        source_file = guess_source_file(vol_dir, volume_name)
        image_index = build_image_index(vol_dir, source_file)
        blocks, answers = parse_markdown(md)

        print("\n%s" % os.path.relpath(vol_dir, os.getcwd()))
        print(
            "  %d block(s), %d answer-key entr(ies), %d image(s) described structurally"
            % (len(blocks), len(answers), len(image_index))
        )

        ctx = dict(
            volume_name=volume_name,
            volume_slug=slug,
            source_file=source_file,
            images_dir=images_dir,
            assets=assets,
            url_base=url_base,
            kind=args.kind,
        )

        kept = 0
        for block in blocks:
            if args.limit and kept >= args.limit:
                break
            parsed = parse_block_body(block, image_index)

            # A block with neither usable text nor a figure is page furniture.
            if len(parsed["text"]) < 20 and not parsed["images"] and len(parsed["options"]) < 2:
                stats["skipped_not_a_question"] += 1
                continue

            key, source, score, _unknown = resolve_topic(
                block, parsed, maps, topics, matchers, args.min_score
            )
            topic_sources[source or "unresolved"] += 1

            q = build_question(block, parsed, answers, ctx)
            if key:
                q["subject"] = topics[key]["subject"]
                q["topic"] = topics[key]["topic"]
            if score is not None:
                q["_origin"]["topic_score"] = round(score, 1)
            q["_origin"]["topic_source"] = source or "none"

            fingerprint = ingest.text_hash(q)
            if fingerprint in seen_hashes:
                stats["duplicate_within_run"] += 1
                continue
            if fingerprint in existing:
                stats["already_in_bank"] += 1
                continue
            seen_hashes[fingerprint] = q["id"]
            if q["id"] in seen_ids:
                q["id"] = "%s-b" % q["id"]
            seen_ids.add(q["id"])

            had_figures = bool(q.get("figure_assets"))
            record = finalise(q)
            kept += 1

            stats["questions"] += 1
            if had_figures:
                stats["with_images"] += 1
            if record.get("answer_pending"):
                stats["pending"] += 1
            else:
                stats["answered"] += 1
            if record.get("needs_fix"):
                stats["flagged"] += 1

            subject = q.get("subject")
            if subject and q.get("topic"):
                by_subject[subject].append(record)
                stats["filed"] += 1
            else:
                record["_note"] = (
                    "Topic could not be resolved automatically. Set 'topic' to a "
                    "slug from content/syllabus.json and move this entry into that "
                    "subject's file. Ignored by the app until then."
                )
                unsorted.append(record)
                stats["unsorted"] += 1

    return by_subject, unsorted, stats, topic_sources, assets


def guess_source_file(vol_dir, volume_name):
    """The original PDF name, for provenance. Falls back to the volume name."""
    for _i, _p, chunk in chunk_offsets(vol_dir):
        inner = os.path.join(vol_dir, chunk)
        for name in sorted(os.listdir(inner)):
            if os.path.isdir(os.path.join(inner, name)) and name != "hybrid_auto":
                return "%s.pdf" % name
    return "%s.pdf" % volume_name


def write_bank(by_subject, unsorted, args):
    out_dir = os.path.join(BANKS_DIR, args.bank)
    os.makedirs(out_dir, exist_ok=True)
    written = {}
    source_meta = {
        "slug": args.source_slug,
        "name": "GATE Overflow volumes, MinerU extraction",
        "kind": "release",
        "url": "https://github.com/GATEOverflow/GO-PDFs/releases",
        "licence_note": "Public release assets, extracted locally with MinerU.",
    }
    note = (
        "Converted from MinerU output by tools/import_mineru_bank.py. Figures are "
        "sidecar files under content/assets/question-images/%s and referenced from "
        'each question\'s "figure_assets"; no image bytes live in this file. '
        'Entries with "answer_pending": true are kept out of quizzes until an '
        "answer is filled in." % args.bank
    )

    for subject, questions in sorted(by_subject.items()):
        path = os.path.join(out_dir, "%s.json" % subject)
        ingest.write_json_atomic(
            path,
            {"subject": subject, "source": source_meta, "note": note, "questions": questions},
        )
        written[subject] = (
            len(questions),
            sum(1 for q in questions if q.get("answer_pending")),
            sum(1 for q in questions if q.get("figure_assets")),
        )

    # Topic-less questions go to content/review/, NOT into the bank directory.
    # bank_files() loads every *.json under content/banks/<bank>/, so a file left
    # there would be served with no topic: it would count against bank health,
    # show up as untagged, and never be reachable from a topic drill. content/
    # review/ is outside the load path and already holds go-unsorted.json, so
    # this follows the convention the repo set rather than inventing one.
    review_path = ""
    if unsorted:
        os.makedirs(REVIEW_DIR, exist_ok=True)
        review_path = os.path.join(REVIEW_DIR, "%s-unsorted.json" % args.bank)
        ingest.write_json_atomic(
            review_path,
            {
                "subject": "",
                "note": (
                    "Extracted cleanly but the topic could not be matched to "
                    "content/syllabus.json. Give each one a 'topic' slug and a "
                    "'subject', then move it into content/banks/%s/<subject>.json. "
                    "Not loaded by the app until then." % args.bank
                ),
                "questions": unsorted,
            },
        )
    return out_dir, written, review_path


def retire_bank(name):
    """Move a superseded bank directory out of the load path, reversibly."""
    src = os.path.join(BANKS_DIR, name)
    if not os.path.isdir(src):
        print("  nothing to retire: %s does not exist" % src)
        return
    dest_root = os.path.join(CONTENT, "backups", "retired-banks")
    os.makedirs(dest_root, exist_ok=True)
    dest = os.path.join(dest_root, name)
    n = 2
    while os.path.exists(dest):
        dest = os.path.join(dest_root, "%s-%d" % (name, n))
        n += 1
    shutil.move(src, dest)
    print("  retired bank %r -> %s (move it back to undo)" % (name, os.path.relpath(dest, ROOT)))


def annotate_from_validator(out_dir, bank):
    """Second pass: let the app's own validator have the final word.

    The converter cannot fully predict servability, because the registry
    normalises and hydrates a question as it loads it. So write first, load
    through the real registry, and record its verdict back into the file. That
    way needs_fix can never claim something the app disagrees with.
    """
    registry.invalidate()
    verdicts = {}
    for qid, q in registry.question_bank(reload=True).items():
        if str(q.get("file", "")).startswith("%s/" % bank):
            verdicts[qid] = registry.validate_question(q)

    counts = Counter()
    for name in sorted(os.listdir(out_dir)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(out_dir, name)
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        changed = False
        for q in payload.get("questions", []):
            issues = verdicts.get(q.get("id"))
            if issues is None:
                counts["not_loaded"] += 1
                continue
            if q.get("answer_pending"):
                counts["pending"] += 1
                continue
            blocking = [i for i in issues if i != "no explanation"]
            if blocking:
                reason = "; ".join(blocking)
                if q.get("needs_fix") != reason:
                    q["needs_fix"] = reason
                    changed = True
                counts["needs_fix"] += 1
            else:
                counts["usable"] += 1
        if changed:
            ingest.write_json_atomic(path, payload)
    return counts


# ===========================================================================
# reporting
# ===========================================================================
def report(stats, topic_sources, assets, args):
    print("\n  dry run, nothing written" if args.dry_run else "\n  summary")
    print("  " + "-" * 46)
    rows = [
        ("questions found", stats["questions"]),
        ("with figures", stats["with_images"]),
        ("answers recovered", stats["answered"]),
        ("pending review", stats["pending"]),
        ("flagged needs_fix", stats["flagged"]),
        ("image assets copied", assets.copied),
        ("figure refs reused", assets.reused),
        ("filed under a topic", stats["filed"]),
        ("topic unresolved", stats["unsorted"]),
        ("duplicates within run", stats["duplicate_within_run"]),
        ("already in the bank", stats["already_in_bank"]),
        ("blocks skipped as noise", stats["skipped_not_a_question"]),
    ]
    for label, value in rows:
        if value or label in ("questions found", "with figures", "pending review"):
            print("  %-26s %d" % (label, value))
    if assets.missing:
        print("  %-26s %d (e.g. %s)" % ("image files not found", len(assets.missing), assets.missing[0]))
    print(
        "  topic source: %s"
        % ", ".join("%s %d" % (k, v) for k, v in topic_sources.most_common())
    )


def main():
    ap = argparse.ArgumentParser(
        description="Convert MinerU output into a GitGrind question bank, figures included."
    )
    ap.add_argument(
        "inputs",
        nargs="+",
        help="a MinerU run directory (or one volume directory inside it)",
    )
    ap.add_argument("--bank", default=DEFAULT_BANK, help="bank name under content/banks/")
    ap.add_argument("--source-slug", default="go-mineru", help="source slug for the bank header")
    ap.add_argument("--kind", default="pyq", choices=registry.SESSION_KINDS)
    ap.add_argument("--min-score", type=float, default=3.0, help="keyword-match threshold")
    ap.add_argument("--limit", type=int, default=0, help="stop after N questions per volume")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="report only: no JSON written, no images copied",
    )
    ap.add_argument(
        "--skip-existing",
        action="store_true",
        help="drop questions whose text already appears in the loaded bank",
    )
    ap.add_argument(
        "--retire",
        metavar="BANK",
        help="move a superseded bank (e.g. go-extracted) into content/backups/",
    )
    args = ap.parse_args()

    volumes = discover_volumes(args.inputs)
    if not volumes:
        raise SystemExit(
            "No MinerU volume found. Expected a directory containing merged/full.md."
        )
    print("MinerU import: %d volume(s)" % len(volumes))

    by_subject, unsorted, stats, topic_sources, assets = convert(volumes, args)
    report(stats, topic_sources, assets, args)

    if args.dry_run:
        print("\n  re-run without --dry-run to write.")
        return 0

    if args.retire:
        retire_bank(args.retire)

    out_dir, written, review_path = write_bank(by_subject, unsorted, args)
    print("\n  wrote %s" % os.path.relpath(out_dir, ROOT))
    for subject, (total, pending, figs) in sorted(written.items()):
        print("  %-26s %4d  (%d pending, %d with figures)" % (subject, total, pending, figs))
    if review_path:
        print(
            "  %-26s %4d  -> %s (not loaded)"
            % ("topic unresolved", len(unsorted), os.path.relpath(review_path, ROOT))
        )

    counts = annotate_from_validator(out_dir, args.bank)
    print(
        "\n  validator: %d usable, %d pending, %d need a fix"
        % (counts["usable"], counts["pending"], counts["needs_fix"])
    )
    print("  next: python app.py --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())