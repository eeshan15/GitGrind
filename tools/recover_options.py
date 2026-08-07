#!/usr/bin/env python3
"""Recover MCQ options that MinerU's formula pass left empty.

WHY THIS EXISTS

  The GO volumes render every formula as graphics, so the PDF text layer holds
  only the option letters ("A.", "B.", ...) and none of the bodies. MinerU
  recovers those bodies with its own formula model and gets roughly two thirds
  of them; the rest arrive blank. Re-running MinerU unchanged reproduces the
  same gaps, and pdftotext/pdfplumber cannot help because there is no text to
  read.

  What IS reliable is the geometry. The option letters always extract, with
  exact coordinates, and they sit in a clean two-column grid. So this locates
  each option from its letter, crops the strip to its right at high DPI, and
  hands that crop to a formula OCR model. The crop is deterministic - no layout
  model is involved - and the rendered input is pristine.

STAGES

  --crops   (default)  geometry + crops + manifest. Needs only PyMuPDF, which
                       is already in the venv. Look at the PNGs before going
                       further: if they are framed correctly the OCR step is
                       worth running, and if they are not, nothing has been
                       written to the bank.
  --ocr                run pix2tex over the manifest and write recovered LaTeX
                       back into it. Requires: pip install pix2tex
  --apply              merge recovered options into content/banks/<bank>/*.json

USAGE

  .venv\\Scripts\\python.exe tools\\recover_options.py --limit 20
  .venv\\Scripts\\python.exe tools\\recover_options.py --ocr
  .venv\\Scripts\\python.exe tools\\recover_options.py --apply
"""

import argparse
import glob
import warnings
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, "content", "banks")
PAPERS = os.path.join(ROOT, "papers")
WORK = os.path.join(ROOT, "content", "imports", "option-recovery")
MANIFEST = os.path.join(WORK, "manifest.json")

# The body of these PDFs is graphics; the only text is the question refs and
# the option letters. A ref line is bare ("1.3.11"), with no title after it.
HEADING = re.compile(r"^(\d+\.\d+\.\d+)\s*$")
LETTER = re.compile(r"^([A-H])\.$")

# A formula can be taller than its letter (fractions, radicals, subscripts), so
# the crop is padded vertically. Bounded by the neighbouring rows below.
PAD_TOP = 5.0
PAD_BOTTOM = 3.0
PAD_LEFT = 1.0
DPI = 400


def load_targets(bank_name, limit):
    """Questions whose option list is short or has a blank entry."""
    out = []
    for path in sorted(glob.glob(os.path.join(BANK, bank_name, "*.json"))):
        for q in json.load(open(path, encoding="utf-8")).get("questions", []):
            opts = q.get("options") or []
            if q.get("type") == "nat":
                continue
            # "Present" is not the same as "usable". An option list can be the
            # right length and still be junk - the Huffman question came through
            # as four identical ", , , , ," strings because the binary codes were
            # graphics that got dropped. Those need recovering just as much as a
            # blank one does, so target anything that is short, non-alphanumeric,
            # or not distinct.
            blank = any(not str(o).strip() for o in opts)
            junk = False
            if opts:
                stripped = [str(o).strip() for o in opts]
                if any(not any(c.isalnum() for c in o) for o in stripped):
                    junk = True
                real = [o for o in stripped if o]
                if len(real) > 1 and len(set(real)) < len(real):
                    junk = True
            if len(opts) >= 4 and not blank and not junk:
                continue
            origin = q.get("origin") or {}
            if not origin.get("ref") or not origin.get("source_file"):
                continue
            out.append(
                dict(
                    id=q["id"],
                    file=os.path.relpath(path, ROOT),
                    ref=origin["ref"],
                    pdf=origin["source_file"],
                    have=len(opts),
                    blank=blank,
                )
            )
            if limit and len(out) >= limit:
                return out
    return out


def index_headings(doc):
    """{ref: (page_no, y_top)} for every numbered question heading in the PDF."""
    index = {}
    for pno in range(doc.page_count):
        for block in doc[pno].get_text("dict")["blocks"]:
            if block.get("type"):
                continue
            for line in block["lines"]:
                text = "".join(s["text"] for s in line["spans"]).strip()
                m = HEADING.match(text)
                if m and m.group(1) not in index:
                    index[m.group(1)] = (pno, line["bbox"][1])
    return index


def letters_on_page(page):
    """[(letter, bbox)] for every standalone option letter, in reading order."""
    found = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type"):
            continue
        for line in block["lines"]:
            text = "".join(s["text"] for s in line["spans"]).strip()
            m = LETTER.match(text)
            if m:
                found.append((m.group(1), list(line["bbox"])))
    found.sort(key=lambda r: (r[1][1], r[1][0]))
    return found


def crop_rects(page, letters, page_width):
    """Turn each option letter into the rectangle holding its formula.

    The right edge is the start of the next column, or the page margin for the
    rightmost column - never a guess about where the formula happens to end,
    because a crop that is too wide only wastes pixels while one that is too
    narrow silently truncates the answer.
    """
    xs = sorted({round(bb[0]) for _l, bb in letters})
    cols = []
    for x in xs:
        if not cols or x - cols[-1] > 40:
            cols.append(x)
    right_margin = page_width - 25.0

    rects = []
    for i, (letter, bb) in enumerate(letters):
        nxt = [c for c in cols if c > bb[0] + 40]
        right = (min(nxt) - 6.0) if nxt else right_margin
        # Bound vertically by the neighbouring rows in ANY column, not just this
        # one. The padding exists because a fraction or a radical is taller than
        # its letter, but unbounded it reaches into the row above or below and
        # drags in a sliver of the wrong formula. Clamp to whatever row is
        # actually adjacent, and only pad into free space.
        # Split the inter-row gap down the middle rather than stopping at the
        # neighbouring LETTER. A formula is taller than the letter that labels
        # it - parentheses, fractions and radicals all overshoot - so clamping
        # to the next letter's edge still lets that row's ascenders into this
        # crop. Half the gap each is the only division where no crop can reach
        # another row's centre line.
        bottom = bb[3] + PAD_BOTTOM
        lower = [bb2[1] for _l2, bb2 in letters if bb2[1] > bb[1] + 4]
        if lower:
            bottom = min(bottom, (bb[3] + min(lower)) / 2.0)

        top = bb[1] - PAD_TOP
        # Compare TOPS to decide which row a letter belongs to, then take that
        # row's bottom. Rows here can sit only ~2.6pt apart, so the previous
        # row's bottom edge is often BELOW this letter's top - testing bottoms
        # made the clamp silently never fire and let the row above bleed in.
        upper = [bb2[3] for _l2, bb2 in letters if bb2[1] < bb[1] - 4]
        if upper:
            top = max(top, (max(upper) + bb[1]) / 2.0)

        rects.append((letter, [bb[2] + PAD_LEFT, top, right, bottom]))
    return rects


def write_worklist(args):
    """Emit the target list so the heavy stage can run somewhere else.

    The crop+OCR stage needs only the PDFs and this list - not the bank, not the
    app. Splitting it here means a GPU box never needs a copy of the repo, and
    only a few KB of JSON crosses the wire in each direction.
    """
    targets = load_targets(args.bank, args.limit)
    json.dump(targets, open(args.worklist, "w", encoding="utf-8"), indent=1)
    print("  %d question(s) -> %s" % (len(targets), args.worklist))
    print("  copy that plus the PDFs to the GPU box, then run --from-worklist.")
    return 0


LABEL_PREFIX = re.compile(r"^\(?[A-H]\)?\s*[.)]\s*")


def plain_text_in(page, rect):
    """The option's text if the PDF already holds it, else "".

    A crop can overrun into the next column when the layout only exposes one
    column of letters, so a leading "D." style label is stripped: that belongs
    to a different option and would otherwise be pasted into this one. Anything
    that still looks like stray punctuation is rejected rather than kept.
    """
    import fitz

    raw = page.get_text("text", clip=fitz.Rect(*rect)).strip()
    if not raw:
        return ""
    raw = " ".join(raw.split())
    raw = LABEL_PREFIX.sub("", raw).strip()
    if len(raw) < 2 or not any(c.isalnum() for c in raw):
        return ""
    return raw


def build_crops(args):
    try:
        import fitz
    except ImportError:
        sys.exit("PyMuPDF missing. Run:  .venv\\Scripts\\python.exe -m pip install pymupdf")

    if args.from_worklist:
        targets = json.load(open(args.from_worklist, encoding="utf-8"))
        if args.limit:
            targets = targets[: args.limit]
    else:
        targets = load_targets(args.bank, args.limit)
    if not targets:
        sys.exit("Nothing to recover - every question already has four options.")
    os.makedirs(WORK, exist_ok=True)

    by_pdf = {}
    for t in targets:
        by_pdf.setdefault(t["pdf"], []).append(t)

    manifest = []
    missing_pdf = []
    no_heading = 0
    from_text = [0]
    carried = [0]

    for pdf_name, items in sorted(by_pdf.items()):
        pdf_path = os.path.join(PAPERS, pdf_name)
        if not os.path.isfile(pdf_path):
            missing_pdf.append(pdf_name)
            continue
        doc = fitz.open(pdf_path)
        print("  %s: %d page(s), %d question(s) to recover" % (pdf_name, doc.page_count, len(items)))
        index = index_headings(doc)

        for t in items:
            hit = index.get(t["ref"])
            if not hit:
                no_heading += 1
                continue
            pno, ytop = hit
            page = doc[pno]
            # Options belong to this question only: below its heading, and above
            # whichever heading comes next on the same page.
            ynext = page.rect.height
            for ref2, (p2, y2) in index.items():
                if p2 == pno and y2 > ytop:
                    ynext = min(ynext, y2)
            letters = [
                (l, bb) for l, bb in letters_on_page(page) if ytop < bb[1] < ynext
            ]
            src_page = page

            # A question whose heading sits near the foot of a page has its
            # options printed overleaf. Nothing on the heading's own page marks
            # this, so when the heading is the last one there and no options
            # followed it, continue onto the next page and take whatever comes
            # before that page's first heading - those options are still ours.
            if not letters and ynext >= page.rect.height and pno + 1 < doc.page_count:
                nxt = doc[pno + 1]
                cut = nxt.rect.height
                for _ref2, (p2, y2) in index.items():
                    if p2 == pno + 1:
                        cut = min(cut, y2)
                spill = [(l, bb) for l, bb in letters_on_page(nxt) if bb[1] < cut]
                if spill:
                    letters, src_page, spilled = spill, nxt, True
                    carried[0] += 1

            if not letters:
                continue

            page = src_page
            for letter, rect in crop_rects(page, letters, page.rect.width):
                name = "%s_%s.png" % (t["id"], letter)
                out = os.path.join(WORK, name)
                page.get_pixmap(clip=fitz.Rect(*rect), dpi=DPI).save(out)
                row = dict(id=t["id"], file=t["file"], ref=t["ref"], letter=letter,
                           page=page.number, crop=name, latex=None)
                # Not every option is mathematics. "None of the above" and the
                # like are ordinary text and DO sit in the text layer, where
                # they can be read exactly. Sending those through a formula OCR
                # is how "None of the above" came back as
                # \mathrm{\boldmath{~\D.~Norle~of~t1pe~above}}. Take the text
                # whenever it exists and only OCR what is genuinely graphical.
                plain = plain_text_in(page, rect)
                if plain:
                    row["latex"] = plain
                    row["source"] = "textlayer"
                    from_text[0] += 1
                manifest.append(row)
        doc.close()

    json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"), indent=1)
    qs = len({m["id"] for m in manifest})
    print("\n  %d crop(s) for %d question(s) -> %s" % (len(manifest), qs, os.path.relpath(WORK, ROOT)))
    print("  %d read straight from the PDF text layer (no OCR needed)" % from_text[0])
    print("  %d question(s) had their options overleaf" % carried[0])
    if no_heading:
        print("  %d question(s) skipped: heading ref not found in the PDF" % no_heading)
    if missing_pdf:
        print("  missing from papers/: %s" % ", ".join(missing_pdf))
    print("\n  Open a few PNGs. If the formulas are framed cleanly, run --ocr.")
    return 0


def run_ocr(args):
    # Third-party deprecation chatter buries the lines that matter (progress,
    # and the per-crop failures). Real errors are still reported below.
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    try:
        from PIL import Image
        from pix2tex.cli import LatexOCR
    except ImportError:
        sys.exit(
            "pix2tex missing. Run:\n"
            "  .venv\\Scripts\\python.exe -m pip install pix2tex\n"
            "First run downloads the model weights (~100 MB)."
        )

    def is_blank(img):
        """True when the crop holds no ink at all.

        pix2tex normalises by (max - min), so a uniform image divides by zero
        and emits a RuntimeWarning before returning noise. These crops are the
        options whose body was never printed, so there is nothing to read -
        skip them instead of feeding the model something it cannot use.
        """
        g = img.convert("L")
        lo, hi = g.getextrema()
        return hi - lo < 8

    blank = 0
    model = LatexOCR()
    if args.device:
        # LatexOCR is two networks, not one: an image_resizer that picks the
        # input scale and the decoder itself. Moving only the decoder left the
        # resizer on the CPU, so every crop died on a device mismatch and the
        # run "finished" having recovered nothing but the text-layer reads.
        # Move both, and verify on a real tensor before trusting it.
        try:
            import torch

            dev = torch.device(args.device)
            model.model = model.model.to(dev)
            if getattr(model, "image_resizer", None) is not None:
                model.image_resizer = model.image_resizer.to(dev)
            model.args.device = str(dev)
            torch.zeros(1).to(dev)
            print("  device: %s (decoder + image_resizer)" % dev)
        except Exception as exc:
            print("  could not use %s (%s); falling back to CPU" % (args.device, exc))
            try:
                model.model = model.model.cpu()
                if getattr(model, "image_resizer", None) is not None:
                    model.image_resizer = model.image_resizer.cpu()
                model.args.device = "cpu"
            except Exception:
                pass
    done = 0
    for m in manifest:
        if m.get("latex"):
            continue
        path = os.path.join(WORK, m["crop"])
        if not os.path.isfile(path):
            continue
        try:
            img = Image.open(path)
            if is_blank(img):
                m["latex"] = None
                m["error"] = "blank crop: nothing printed for this option"
                blank += 1
            else:
                m["latex"] = model(img).strip() or None
        except Exception as exc:
            m["latex"] = None
            m["error"] = str(exc)[:120]
        done += 1
        if done % 25 == 0:
            print("  %d/%d" % (done, len(manifest)))
            json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"), indent=1)

    json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"), indent=1)
    got = sum(1 for m in manifest if m.get("latex"))
    print("\n  recovered %d of %d crop(s) (%d%%)" % (got, len(manifest),
                                                     round(100 * got / max(1, len(manifest)))))
    if blank:
        print("  %d crop(s) were blank - that option was never printed" % blank)

    # A run where the OCR never once succeeded is a setup fault, not a data
    # fault, and it looks deceptively like partial success because the
    # text-layer reads still land. Say so plainly rather than let --apply
    # proceed on a manifest that is almost entirely empty.
    ocr_rows = [m for m in manifest if m.get("source") != "textlayer"]
    ocr_ok = sum(1 for m in ocr_rows if m.get("latex"))
    if ocr_rows and ocr_ok == 0:
        first = next((m.get("error") for m in ocr_rows if m.get("error")), "unknown")
        print("\n  ! every OCR attempt failed - this is a setup problem, not the data.")
        print("    first error: %s" % first)
        print("    do NOT run --apply until this is fixed.")
        return 1
    if ocr_rows:
        print("  OCR itself: %d of %d (%d%%)" % (ocr_ok, len(ocr_rows),
                                                 round(100 * ocr_ok / len(ocr_rows))))
    print("  next: --apply")
    return 0


def apply_manifest(args):
    """Write recovered options back, but only where the whole set came through.

    A question is rewritten only when every one of its letters produced LaTeX.
    Filling three of four options would leave a list whose positions no longer
    line up with the printed answer key, which is a worse failure than the
    blank it replaced - so a partial recovery is left alone.
    """
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    by_q = {}
    for m in manifest:
        by_q.setdefault((m["file"], m["id"]), []).append(m)

    ready = {}
    for key, rows in by_q.items():
        rows.sort(key=lambda r: r["letter"])
        if len(rows) < 2 or any(not r.get("latex") for r in rows):
            continue
        letters = [r["letter"] for r in rows]
        if letters != [chr(ord("A") + i) for i in range(len(letters))]:
            continue
        # Only the OCR output is LaTeX. Text-layer values are already plain
        # prose and would render as a broken formula if wrapped in dollars.
        ready[key] = [
            r["latex"] if r.get("source") == "textlayer" else "$%s$" % r["latex"]
            for r in rows
        ]

    changed = 0
    for path in sorted({k[0] for k in ready}):
        full = os.path.join(ROOT, path)
        data = json.load(open(full, encoding="utf-8"))
        hit = 0
        for q in data.get("questions", []):
            opts = ready.get((path, q["id"]))
            if not opts:
                continue
            q["options"] = opts
            q["origin"] = dict(q.get("origin") or {}, options_recovered="pix2tex")
            # The answer key was parsed against these positions, so an answer
            # that now fits again makes the question servable.
            if q.get("answer_pending") and q.get("answer_from_source"):
                idx = sorted({ord(c) - 65 for c in re.findall(r"[A-H]", q["answer_from_source"])})
                if idx and max(idx) < len(opts):
                    q["answer"] = idx
                    q["type"] = "msq" if len(idx) > 1 else "mcq"
                    q.pop("answer_pending", None)
                    q.pop("answer_from_source", None)
                    q.pop("needs_fix", None)
                    q["explain"] = ""
            hit += 1
        if hit:
            json.dump(data, open(full, "w", encoding="utf-8"), indent=1)
            print("  %-46s %d question(s)" % (path, hit))
            changed += hit

    print("\n  %d question(s) updated. Run: python app.py --check" % changed)
    return 0


def main():
    ap = argparse.ArgumentParser(description="Recover MCQ options from the source PDFs.")
    ap.add_argument("--bank", default="mineru")
    ap.add_argument("--worklist", metavar="FILE",
                    help="write the target list and exit (run where the bank is)")
    ap.add_argument("--from-worklist", metavar="FILE",
                    help="take targets from a worklist instead of the bank")
    ap.add_argument("--pdf-dir", help="where the source PDFs live (default: papers/)")
    ap.add_argument("--work", help="where crops and manifest go")
    ap.add_argument("--device", default=None,
                    help="torch device for --ocr, e.g. cuda:0 (default: auto)")
    ap.add_argument("--batch", type=int, default=32, help="OCR batch size on GPU")
    ap.add_argument("--limit", type=int, default=0, help="stop after N questions (sampling)")
    ap.add_argument("--ocr", action="store_true", help="run pix2tex over the crops")
    ap.add_argument("--apply", action="store_true", help="merge recovered options into the bank")
    args = ap.parse_args()

    global PAPERS, WORK, MANIFEST
    if args.pdf_dir:
        PAPERS = os.path.abspath(args.pdf_dir)
    if args.work:
        WORK = os.path.abspath(args.work)
        MANIFEST = os.path.join(WORK, "manifest.json")

    if args.worklist:
        return write_worklist(args)
    if args.apply:
        return apply_manifest(args)
    if args.ocr:
        return run_ocr(args)
    return build_crops(args)


if __name__ == "__main__":
    sys.exit(main())