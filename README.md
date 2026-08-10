<div align="center">

```
   ██████╗ ██╗████████╗ ██████╗ ██████╗ ██╗███╗   ██╗██████╗
  ██╔════╝ ██║╚══██╔══╝██╔════╝ ██╔══██╗██║████╗  ██║██╔══██╗
  ██║  ███╗██║   ██║   ██║  ███╗██████╔╝██║██╔██╗ ██║██║  ██║
  ██║   ██║██║   ██║   ██║   ██║██╔══██╗██║██║╚██╗██║██║  ██║
  ╚██████╔╝██║   ██║   ╚██████╔╝██║  ██║██║██║ ╚████║██████╔╝
   ╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
```

### `dev-v2.0` — the layout-aware extraction pipeline

**A local, file-based GATE preparation tracker.**
Quizzes, spaced revision, a readiness model, and a question bank you own as plain JSON on disk.
No account. No server. No external API.

<br>

| bank health | questions | figures | listings | broken |
|:---:|:---:|:---:|:---:|:---:|
| **17% → 85%** | **3667** | **310** | **273** | **0** |

<br>

[Quick start](#quick-start) · [The pipeline](#the-pipeline) · [How we got here](#how-we-got-here) · [Build artifacts](#build-artifacts-how-each-one-was-made) · [What is still wrong](#what-is-still-wrong)

</div>

---

> [!IMPORTANT]
> **This is a development branch.**
> Clone it and check out your own branch from it. Please do not commit directly to `dev-v2.0`.
>
> ```bash
> git clone -b dev-v2.0 https://github.com/eeshan15/GitGrind.git
> cd GitGrind
> git checkout -b your-name/whatever
> ```

---

## Table of contents

- [What changed and why](#what-changed-and-why)
- [Quick start](#quick-start)
- [The pipeline](#the-pipeline)
  - [Stage 1 — MinerU](#stage-1--mineru)
  - [Stage 2 — the converter](#stage-2--toolsimport_mineru_bankpy)
  - [Stage 3 — option recovery](#stage-3--toolsrecover_optionspy)
  - [Stage 4 — maths delimiting](#stage-4--toolstexwrappy)
- [How we got here](#how-we-got-here)
- [Rendering](#rendering)
- [Build artifacts: how each one was made](#build-artifacts-how-each-one-was-made)
- [Tool reference](#tool-reference)
- [Verifying a change](#verifying-a-change)
- [What is still wrong](#what-is-still-wrong)
- [Note for v1.0 users](#note-for-v10-users)

---

## What changed and why

v1.0 imported questions by running `pdftotext` over the
[GATE Overflow](https://github.com/GATEOverflow/GO-PDFs) volumes and parsing the
result. It produced a bank of 3597 questions at **17% usable**, and every
formula, diagram and program was missing.

That was not a parser bug. It is a property of the source.

We opened the PDFs and looked at what is actually inside a page:

```python
>>> import fitz
>>> page = fitz.open("filter1_volume2.pdf")[28]
>>> [l for l in page.get_text().split("\n") if l.strip()][:8]
['1.3.8', 'A.', 'B.', 'C.', 'D.', '1.3.9', '1.3.10', 'A.']
```

That is the **entire** text layer of the page: question reference numbers and
option letters. Nothing else. The GO volumes are generated from HTML, and every
formula, every diagram and every code listing is rendered as **graphics**. There
is no text to extract, so no amount of `pdftotext` tuning would ever have
worked.

Rendering that same region at 400 DPI shows what is really there:

```
A.  T(n) = O(n²)          B.  T(n) = O(n log n)
C.  T(n) = Ω(n²)          D.  T(n) = Θ(n log n)
```

Pristine. Two clean columns. Perfect input for a model — just not for a text
extractor.

**dev-v2.0 therefore treats the PDFs as images, not as text.** MinerU handles
layout and formula recognition; everything MinerU misses is recovered from page
geometry, because the option letters that *do* extract give exact coordinates
for the graphics sitting beside them.

---

## Quick start

```bash
# 1. sanity-check the bank as it ships
python app.py --check

# 2. run it
python app.py            # or: run.bat on Windows
```

Rebuilding the bank from source PDFs is a four-command sequence. Stages 1 and 3
want a GPU; stages 2 and 4 run anywhere.

```bash
# stage 1 — MinerU (GPU, once per PDF)
python mineru_run.py --input papers/ --output out/

# stage 2 — convert to bank JSON
python tools/import_mineru_bank.py out/ --dry-run
python tools/import_mineru_bank.py out/

# stage 3 — recover options that MinerU could not read
python tools/recover_options.py --worklist worklist.json
#   ...on the GPU box, then bring manifest.json back...
python tools/recover_options.py --apply

# verify
python app.py --check
python tools/selftest.py
```

> [!NOTE]
> Stage 2 **overwrites** the bank. Always follow it with
> `recover_options.py --apply`, or you will drop back from 85% to 58% and
> wonder why.

---

## The pipeline

```
                    GO volume PDFs  (papers/*.pdf)
                            │
                            │   ① mineru_run.py            GPU, one-off
                            ▼
        ┌───────────────────────────────────────────────────┐
        │  MinerU output                                    │
        │    merged/full.md          stitched markdown      │
        │    merged/images/          extracted graphics     │
        │    pNNNN_MMMM/.../*.json   bbox + page_idx        │
        └───────────────────────────────────────────────────┘
                            │
                            │   ② tools/import_mineru_bank.py
                            │        └── tools/texwrap.py   ④
                            ▼
        ┌───────────────────────────────────────────────────┐
        │  content/banks/mineru/<subject>.json              │
        │  content/assets/question-images/mineru/*.jpg      │
        │  content/review/mineru-unsorted.json              │
        └───────────────────────────────────────────────────┘
                            │
                            │   ③ tools/recover_options.py  GPU
                            │        crops ──► pix2tex ──► manifest.json
                            ▼
                      servable bank
```

### Stage 1 — MinerU

`mineru_run.py` chunks each PDF into page ranges, spreads them across the
available GPUs, strips QR codes, and merges the chunk outputs back into one
markdown file plus one image folder.

It writes three things worth knowing about:

| path | what it holds |
|---|---|
| `<vol>/merged/full.md` | every chunk stitched together, image refs intact |
| `<vol>/merged/images/cNNN_<sha>.jpg` | every extracted graphic, chunk-prefixed |
| `<vol>/pAAAA_BBBB/<stem>/hybrid_auto/*_content_list.json` | structured nodes with `bbox` and `page_idx` |

This is the only stage that needs a GPU, and it only runs once per PDF.

### Stage 2 — `tools/import_mineru_bank.py`

Converts MinerU output into bank JSON.

**`merged/full.md` is the structural spine.** It is the only place where three
things coexist: the book's own `1.44.2` numbering, the per-chapter answer-key
tables, and the image references. Using it means questions never have to be
counted into position — a missing marker cannot desynchronise the answer refs.

**`content_list.json` supplies provenance.** It is joined on image filename to
recover `page_idx` and `bbox`, so a bad figure can be found again in the source
PDF. The join needs one trick: merged images are prefixed `cNNN_`, where `NNN`
is the chunk index, and each chunk restarts `page_idx` at 0. Chunk-local page +
that chunk's first page = the absolute page. Verified: `c004_` ↔ `p0096_0119`,
`page_idx 1` → page 97.

What the converter guarantees:

- **Figures are sidecars.** Copied to `content/assets/question-images/` and
  referenced by path. **No image bytes ever enter a JSON file.**
- **Code listings get their own field.** MinerU emits them as fenced blocks *or*
  as `<div class="mineru-algorithm" style="white-space: pre-wrap">`. Both are
  lifted into `code_blocks`. Flattened into the prose, a twenty-line program
  became one unreadable sentence — that hit 275 questions.
- **Tables are parked behind a placeholder during option parsing.** A
  match-the-following table starts its rows with `(A)`, `(B)` — exactly what the
  option parser looks for — so flattening it inline turned a four-option
  question into an eight-option one.
- **Answer keys are read, never guessed.** `N/A`, `TBA` and `X` mean "no
  answer". Ranges (`10:10`, `147.1 : 148.1`) become a value plus a tolerance.
  Multi-selects (`B;D`) become an MSQ.
- **Topic resolution is delegated** to `import_questions.py`, so the two
  importers cannot drift into disagreeing about what a topic slug means.
- **Uncertainty is recorded, not resolved.** Anything doubtful is marked
  `answer_pending` with a human-readable `needs_fix` reason and stays out of
  quizzes.

```bash
python tools/import_mineru_bank.py out/ --dry-run     # report only
python tools/import_mineru_bank.py out/ --limit 40    # sample
python tools/import_mineru_bank.py out/               # the real thing
python tools/import_mineru_bank.py out/ --retire go-extracted
```

`--retire` moves a superseded bank into `content/backups/retired-banks/`. It is
reversible — move the folder back. Without it, the same questions load twice.

### Stage 3 — `tools/recover_options.py`

MinerU's formula model reads roughly two thirds of the option bodies. The rest
arrive blank, and **re-running MinerU reproduces the same gaps** — it is
deterministic.

But the geometry is reliable. The option letters always extract, with exact
coordinates, in a clean grid:

```
letter A  [55.9, 723.2, 66.9, 732.2]      letter B  [297.4, 723.2, 308.4, 732.2]
letter C  [55.5, 734.8, 66.9, 743.8]      letter D  [297.0, 734.8, 308.4, 743.8]
```

So: locate each option from its letter, crop the strip beside it at 400 DPI, run
a dedicated formula OCR over the crop. No layout model is involved and the
input is pristine.

Details that mattered:

- **Options printed overleaf are followed onto the next page.** A question whose
  heading sits near the foot of a page has its options on the next one. Missing
  this cost 96 questions and looked exactly like a source gap.
- **Plain-text options are read from the text layer, not OCR'd.** "None of the
  above" is prose. Sent through a formula model it came back as
  `\mathrm{\boldmath{~\D.~Norle~of~t1pe~above}}`. 623 options are read exactly
  instead of guessed.
- **Crop bounds split the inter-row gap down the middle.** Rows can sit 2.6pt
  apart; clamping to the neighbouring *letter* still let the row above bleed in,
  because a formula is taller than the letter labelling it.
- **Blank crops are detected and skipped.** pix2tex normalises by
  `(max - min)`, so a uniform image divides by zero and returns noise.
- **A question is only rewritten when every one of its options is recovered.**
  A partial fill leaves positions that no longer line up with the printed answer
  key — worse than the blank it replaced.

```bash
# where the bank is
python tools/recover_options.py --worklist worklist.json

# on the GPU box — needs only the PDFs and that worklist, not the repo
python recover_options.py --from-worklist worklist.json --pdf-dir . --work crops
python recover_options.py --work crops --ocr --device cuda:0

# back where the bank is
python tools/recover_options.py --apply
```

> [!WARNING]
> **`pix2tex` pins its own torch build. Install it in a separate venv.**
> Putting it in the MinerU environment downgrades torch and transformers and
> breaks MinerU.
>
> ```bash
> python -m venv ~/ocrenv && source ~/ocrenv/bin/activate
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
> pip install pix2tex pymupdf
> ```
>
> Match the CUDA wheel to the **driver**, not the newest available. A driver at
> 12.2 with a `cu128` torch silently falls back to CPU.

> [!TIP]
> `--device cuda:0` is correct even when you set `CUDA_VISIBLE_DEVICES=2`.
> That variable *remaps* GPU 2 to index 0, so `cuda:2` does not exist.

### Stage 4 — `tools/texwrap.py`

MinerU does not always delimit its maths, so stems arrive with raw LaTeX sitting
in the prose. This wraps it in `$...$` so KaTeX can render it.

It is a **separate module** for a reason. Two earlier regex-only attempts
shipped broken. Both opened a dollar *inside* an existing matched pair, after
which every later dollar paired with the wrong partner and whole English
sentences rendered as run-together italics:

```
before:  itisrequiredtopartitionthemintotwopartsandsuchthat, ∑ai − ∑ai...
```

The fix is structural, not a better pattern: split the text into in-math and
out-of-math segments **first**, then only ever touch the out-of-math ones.
Reaching inside an existing formula becomes impossible rather than something a
regex has to be careful about. A final balance check discards any result whose
dollar count did not stay even.

Measured against fixtures drawn from the real bank:

| check | result |
|---|---|
| 200 no-LaTeX stems, must be byte-identical | **199 / 200** |
| 60 target stems, should be wrapped | **56 / 60** |
| unbalanced output | **0** |
| bank-wide undelimited LaTeX | **304 → 6** |

---

## How we got here

The order things were discovered in, because the dead ends are worth as much as
the fixes.

<details>
<summary><b>1. The bank was reporting 65% usable, and it was a lie</b></summary>

<br>

At one point `app.py --check` read 65%. Inspecting what was actually being
served:

```json
{
  "id": "mineru-vol1-5-5-8",
  "options": ["is", "is", "is", "does not exist ..."],
  "answer_from_source": "C"
}
```

A quiz would show four options — *is*, *is*, *is*, *does not exist* — and mark
you correct only for the third "is". **237 questions were like this.**

Adding a distinctness check dropped health from 65% to 58%. That drop was the
metric becoming honest, not a regression. The number to watch is not the
percentage; it is whether what gets served is answerable.

</details>

<details>
<summary><b>2. 1138 answers were being thrown away by our own code</b></summary>

<br>

The source answer key had a perfectly good `C` for 1138 pending questions. The
converter was discarding it — when options failed a quality check, the question
was marked pending and the parsed answer was dropped along with it.

But it is usually the **options** that fail, not the answer. Preserving the key
in `answer_from_source` changed the value of the whole option-recovery effort:

| | before | after |
|---|---|---|
| recovery targets | 961 | 961 |
| ...whose answer is already known | **76** | **877** |

A three-hour OCR run that fixes 76 questions is not worth it. One that fixes 877
is.

</details>

<details>
<summary><b>3. pdftotext and pdfplumber were dead ends — and we proved it</b></summary>

<br>

Before committing to OCR we checked whether the text was recoverable more
cheaply:

```
PAGE 28 option lines:
    'A.'  'B.'  'C.'  'D.'  'A.'  'B.'  'C.'  'D.'  ...
```

Letters only. No bodies. The path was closed, and knowing that made the crop
pipeline the obvious answer rather than a guess.

</details>

<details>
<summary><b>4. Silent success is worse than loud failure</b></summary>

<br>

One OCR run reported **"recovered 623 of 3993 (16%)"** and exited cleanly. That
623 was exactly the count of text-layer reads — pix2tex had failed on every
single crop:

```
Input type (torch.cuda.FloatTensor) and weight type (torch.FloatTensor)
should be the same
```

`LatexOCR` is **two** networks. Only the decoder had been moved to the GPU; the
`image_resizer` stayed on CPU, so every crop died on a device mismatch. The
error was being swallowed into a per-row `error` field, and a partial number
looked like partial success.

Fixed both by moving both networks and by making a zero-success run exit
non-zero with the first error printed. After that: **3340 of 3370 (99%)**.

</details>

<details>
<summary><b>5. "Fix it all in one shot" failed three times</b></summary>

<br>

Three separate attempts to batch-fix rendering bugs shipped regressions that
were only caught by screenshots from the browser. The LaTeX one broke the same
way twice.

That is why stage 4 lives in its own module with a fixture set, and why the
workflow settled into: **one fix, then `--check`, then look at it.**

</details>

---

## Rendering

Figures, listings and maths all reach the UI under one rule:
**data goes in as data, never as markup.**

| feature | how it is kept safe |
|---|---|
| `figure_assets` | `src` validated against `content/assets/` server-side, then set through the DOM. A bank file is hand-editable, so an asset path is untrusted input. |
| `code_blocks` | inserted as a text node inside `<pre>`; nothing in a program can become markup. |
| `$...$` | rendered with KaTeX. Malformed LaTeX falls back to readable source, not red error markup. |

The asset route is deliberately narrow — a fixed extension allow-list, a
`realpath` containment check, and a 404 rather than the app shell on a miss, so
a broken figure shows as a broken image instead of silently rendering HTML.
Verified against `../..`, URL-encoded `%2e%2e%2f`, missing files and bare
directories: all 404.

KaTeX is **vendored** under `static/vendor/katex/` rather than loaded from a
CDN, so the app keeps working offline — which is the whole point of GitGrind.

---

## Build artifacts: how each one was made

Several files were shipped during this work that are not source code. Here is
exactly how each was produced, so they can be regenerated.

### Making a `.patch` file

A patch is just a unified diff between two trees. The important part is diffing
against a **known baseline**, not against a working copy that has drifted.

```bash
# 1. reconstruct the exact baseline the patch should apply to
mkdir baseline && unzip -q GitGrind.zip -d baseline

# 2. if the patch stacks on an earlier one, apply that first
cd baseline/GitGrind && patch -p1 -s < ../../gitgrind-mineru-figures.patch && cd -

# 3. diff only the files you touched, with a/ b/ labels so -p1 works
: > my-change.patch
for f in core/content.py static/js/core.js static/css/style.css; do
  diff -u "baseline/GitGrind/$f" "working/GitGrind/$f" \
       --label "a/$f" --label "b/$f" >> my-change.patch
done

# 4. ALWAYS verify it applies to a pristine copy before shipping
rm -rf verify && mkdir verify && unzip -q GitGrind.zip -d verify
cd verify/GitGrind && patch -p1 --dry-run < ../../my-change.patch
```

`diff -u` exits 1 when files differ, which is normal — that is why the loop uses
`>>` rather than relying on `set -e`.

### Why patches were abandoned on Windows

They did not work. Every attempt failed:

```
git apply  ..\gitgrind-katex-and-dedup.patch   → error: corrupt patch at line 165
git apply --3way ...                           → error: corrupt patch at line 165
patch -p1 < ...                                → PowerShell: '<' operator is reserved
patch -p1 -i ...                               → 'patch' is not recognized
```

Two independent problems: `git apply` is strict about CRLF line endings and
rejected diffs generated on Linux, and Windows has no `patch` binary at all.

The replacement is a **Python applier script** — `apply_katex_patch.py`,
`fix_math_render.py`, `apply_code_blocks.py`. Each holds explicit
`(file, label, marker, old, new)` tuples and:

- detects the file's own line ending and rewrites the edit to match, so CRLF
  files stay CRLF
- checks a `marker` first and skips edits already applied, so it is **idempotent**
- requires each `old` string to match **exactly once**, and exits **before
  writing anything** if not — never leaving a half-applied tree
- appends CSS separately, guarded by its own marker

```powershell
.venv\Scripts\python.exe apply_katex_patch.py
```
```
  + static/index.html      KaTeX stylesheet
  + static/js/core.js      mathText() helper
  ...
  13 edit(s) applied, 0 already in place.
```

Run it twice and everything reports `= (already applied)`.

### `katex-vendor.zip`

KaTeX is bundled locally so the app works with no network. The npm registry is
the source, and only the runtime files are kept — the tarball also carries
sources, docs and contrib modules that are not needed.

```bash
npm pack katex@0.16.9
tar xzf katex-0.16.9.tgz

mkdir -p static/vendor/katex/fonts
cp package/dist/katex.min.js   static/vendor/katex/
cp package/dist/katex.min.css  static/vendor/katex/
cp package/dist/fonts/*        static/vendor/katex/fonts/   # 60 font files

cd static && zip -qr ../katex-vendor.zip vendor/katex
```

3.0 MB of `dist/` becomes 1.5 MB on disk, 941 KB zipped. Wired in with two lines
in `static/index.html`:

```html
<link rel="stylesheet" href="/vendor/katex/katex.min.css">
<script src="/vendor/katex/katex.min.js"></script>
```

The existing static handler serves the fonts without changes —
`mimetypes.guess_type` already knows `.woff2`.

```powershell
Expand-Archive katex-vendor.zip -DestinationPath static -Force
```

### `mineru-bank-and-assets.zip`

The generated bank plus its figures, so the pipeline output can be used without
re-running MinerU (which needs a GPU and several hours).

```bash
cd GitGrind
zip -qr mineru-bank-and-assets.zip \
    content/banks/mineru \
    content/assets/question-images/mineru \
    content/review/mineru-unsorted.json
```

| contents | size |
|---|---|
| `content/banks/mineru/*.json` — 12 subject files | 4.7 MB |
| `content/assets/question-images/mineru/*.jpg` — 478 figures | 5.5 MB |
| `content/review/mineru-unsorted.json` — unresolved topics | small |
| **total, zipped** | **4.5 MB** |

Three deliberate choices:

1. **Only referenced images are included.** `merged/images/` holds 621 files per
   volume; only the ones actually cited by a question are copied.
2. **Filenames are rebuilt as `<volume-slug>-<hash>.jpg`.** MinerU's `cNNN_`
   prefix is a chunk index that shifts if the run is re-chunked; deriving the
   name from the volume and content hash means a re-import overwrites the same
   file instead of littering the folder with near-duplicates.
3. **`_unsorted` is not in the bank directory.** `bank_files()` loads every
   `*.json` under `content/banks/<bank>/`, so a topic-less file left there would
   be served with no topic — it showed up as 108 broken and 192 untagged before
   being moved to `content/review/`, which is outside the load path.

```powershell
Expand-Archive mineru-bank-and-assets.zip -DestinationPath . -Force
Remove-Item content\banks\go-extracted -Recurse    # superseded, same source
```

---

## Tool reference

| tool | purpose |
|---|---|
| [`tools/import_mineru_bank.py`](tools/import_mineru_bank.py) | MinerU output → bank JSON + figure assets |
| [`tools/recover_options.py`](tools/recover_options.py) | crop options from the PDFs, OCR them, merge back |
| [`tools/texwrap.py`](tools/texwrap.py) | delimit bare LaTeX, math-mode aware |
| [`tools/import_questions.py`](tools/import_questions.py) | v1.0 text importer; still the source of topic resolution |
| [`tools/answer_fill.py`](tools/answer_fill.py) | fill pending answers by hand, one at a time |
| [`tools/selftest.py`](tools/selftest.py) | 46 end-to-end checks across every engine |
| [`tools/repair_bank.py`](tools/repair_bank.py) | bulk fixes on bank JSON |

### Useful flags

```bash
# converter
--dry-run              report only, write nothing
--limit N              stop after N questions per volume
--skip-existing        drop questions already in the loaded bank
--retire BANK          park a superseded bank in content/backups/

# option recovery
--worklist FILE        emit the target list, then stop (run where the bank is)
--from-worklist FILE   take targets from a worklist (run where the PDFs are)
--pdf-dir DIR          where the source PDFs live
--work DIR             where crops and manifest go
--ocr                  run pix2tex over the crops
--device cuda:0        put both networks on the GPU
--apply                merge recovered options into the bank
```

---

## Verifying a change

```bash
python app.py --check        # schema, bank health, coverage, review queue
python tools/selftest.py     # 46 checks, temp database, no side effects
```

`--check` should always end with **0 broken, 0 untagged**. Health will move; the
other two should not.

For UI work, check the payload directly — it is faster than clicking around:

```bash
python app.py --no-browser --port 8420 &
curl -s "http://127.0.0.1:8420/api/questions?subject=digital-logic&limit=50" \
  | python -m json.tool
```

Unrevealed question payloads must contain **no** `answer*` fields. That is
covered in `selftest.py`, and it is worth re-checking by hand after touching
`public_question()`.

---

## What is still wrong

Stated plainly, because the numbers at the top make it easy to assume the bank
is clean.

- **~344 pending questions have no options in the source at all.** These are
  genuine descriptive GATE questions — *"Match the pairs"*, *"Show that L is not
  context free"*, *"State any undesirable characteristic"*. They can never
  become MCQs, and they currently sit in the review queue where they do not
  belong. The fix is to route them to `content/review/` like the unsorted ones;
  roughly 15 lines, not yet written.

- **Roughly 1 stem in 200 has its maths fragmented** across several `$...$`
  spans when a decimal point falls mid-expression:

  ```
  in :  (C 0 1 2. 2 5) _ {H} - (1 0 1 1 1 0 0 1 1 1 0. 1 0 1) _ {B} =
  out:  (C 0 1 2. $2 5) _ {H} - (1 0 1 1 1 0 0 1 1 1 0$. $1 0 1) _ {B} =$
  ```

  Output stays balanced and the sentence stays intact — the formula just renders
  in pieces.

- **Around 385 questions have no printed answer.** The source itself says `N/A`
  or `TBA`. Nothing to recover; they need a human with the paper.

- **~30 crops came back blank** — that option was never printed. Correctly
  skipped, correctly left pending.

- **The accuracy gate in [issue #5](../../issues/5) was never run.** The target
  was a 150-question hand-verified gold set at 95% field-level accuracy *before*
  any bulk run. The bulk run happened first. What exists instead is spot-checking
  on a few hundred stems and a fixture set for `texwrap.py`.
  **The 85% figure is a health metric, not an accuracy audit.** Read it as "how
  much is servable", not "how much is correct".

---

## Note for v1.0 users

> **There is no pre-processing "filter" script.**

The `filter1_volume*.txt` files under `papers/` are leftover `pdftotext` output
from the v1.0 flow, and `filter1` is simply part of the filename GateOverflow
ships. Nothing in this repo produced them from a "2-column fixer".

`tools/import_questions.py` still exists and still works — but only on text that
actually contains questions. Pointed at a raw GO volume it finds almost nothing,
because there is almost nothing in the text layer to find. A run over a raw
volume producing 75,000 lines and six garbage blocks with zero answer keys is
the expected result, not a bug.

`go_extract.py` is not coming back. `import_mineru_bank.py` is its replacement.

**For any GO volume — including the GATE DA ones — run MinerU first, then the
converter:**

```bash
python mineru_run.py --input papers/ --output out/
python tools/import_mineru_bank.py out/ --dry-run
python tools/import_mineru_bank.py out/
python tools/recover_options.py --worklist worklist.json
```

The converter is not CSE-specific. It keys off the book's own section numbering
and the GO tag vocabulary, both of which the DA volumes share. Topics that do
not map to `content/syllabus.json` land in `content/review/mineru-unsorted.json`
rather than being dropped — for a DA syllabus, expect that file to be large
until `content/syllabus.json` and `content/go_tag_map.json` are extended with DA
topics.

---

<div align="center">

**Sources** ·
[GATE Overflow PDFs](https://github.com/GATEOverflow/GO-PDFs) ·
[MinerU](https://github.com/opendatalab/MinerU) ·
[pix2tex](https://github.com/lukas-blecher/LaTeX-OCR) ·
[KaTeX](https://katex.org)

Question content belongs to GATE Overflow and is used from their public release
assets. Extraction is local; nothing is scraped from any paid platform.

</div>