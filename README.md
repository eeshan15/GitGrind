# GitGrind
[![Latest release](https://img.shields.io/github/v/release/eeshan15/GitGrind)](https://github.com/eeshan15/GitGrind/releases/latest)
A local, offline operating system for a GATE CSE attempt.

It is not a study-hours tracker with charts. Every screen exists to answer one
question: **what should I do in the next hour, and why that one?** Logging is the
cheap part. The value is in what the app does with the log.

Everything runs on your machine. No account, no cloud, no telemetry, no
subscription. The entire state of your preparation is one SQLite file you can
copy to a USB stick.

```
python app.py
```

Python 3.8+, standard library only. Nothing to `pip install` to run it.

---

## Contents

1. [What it does](#1-what-it-does)
2. [How it is built](#2-how-it-is-built)
3. [What it contains](#3-what-it-contains)
4. [Running it](#4-running-it)
5. [The question bank](#5-the-question-bank)
6. [Your data and backups](#6-your-data-and-backups)
7. [Packaging into an executable](#7-packaging-into-an-executable)
8. [Diagnosing problems](#8-diagnosing-problems)
9. [Accessibility](#9-accessibility)
10. [Where to change things](#10-where-to-change-things)
11. [Future prospects](#11-future-prospects)
12. [Honest limitations](#12-honest-limitations)

---

## 1. What it does

### Prescriptive analytics, not descriptive

The Today page opens with a single **next action** card: one thing to do, the
reason it was chosen, what it is expected to be worth, and *why it beat the
runner-up*. The ranking is auditable — you can always see what came second and
why it lost.

Behind that card sit the numbers that chose it: coverage weighted by exam marks,
accuracy, volume, consistency, focus, retention debt, velocity trend, guess rate,
correction rate, confidence drift, and a per-topic risk score.

The rule the whole UI follows: **if a number cannot be turned into an action, it
does not get a card.**

### Real spaced repetition

`core/revision.py` runs an SM-2 variant over two kinds of card — topics you have
marked done, and individual questions you got wrong.

| Outcome | What happens |
|---|---|
| Answered well | Interval stretches: 1 day, 3 days, then × an ease factor that grows with success |
| Answered badly | Resets to tomorrow, ease knocked down |
| **Confidently wrong** | Treated as the worst possible outcome (quality 0) |

That last row is the important one. Confidently wrong is the most expensive state
in exam preparation, because it is the one thing you will never revise
voluntarily. The engine punishes it hardest.

Constants: ease clamped `1.3 – 2.9`, starting ease `2.5`, first interval 1 day,
second 3 days, maximum 180 days, failure below quality 2.

The queue produces a **revision debt** and a **pressure score** (0–100), and
overdue items outrank almost everything else in the planner. An old database gets
a schedule backfilled from its existing history, so this works from day one
rather than needing months of data first.

### A daily plan that explains itself

`core/planner.py` builds today's plan from live signals — overdue revision, your
weakest covered topic, the highest-mark pending topic, a mixed PYQ set, a speed
drill when you are slow or the exam is close, and one boss question.

Every block carries three fields: `reason` (why this block exists), `fixing`
(which weakness it targets), `aim` (what counts as success). Blocks are trimmed
to the time you actually have, in priority order, and block size scales with what
you have told the app about plan length.

### An explainable readiness index

The index is a weighted sum of four measured terms and two heuristic ones. Every
term is labelled `measured` or `heuristic`, so you always know which numbers are
your data and which are the app's guess.

The Readiness page decomposes it four ways:

- **Where the score comes from** — earned points and remaining headroom per term.
  The widest hatched bar is where the next hour buys the most.
- **Why it moved** — the change since the last reading, broken down term by term.
  A drop is never a mystery.
- **Biggest risk / cheapest points** — one topic each way, with the reasoning
  spelled out.
- **If you finish today's plan** — what the plan is arithmetically worth. Labelled
  arithmetic rather than forecast, because that is what it is.

There is also an **estimate confidence** band: with 12 attempts logged, the app
says so instead of pretending it knows your score.

### Purpose-driven practice

Six selection purposes, each with a different job:

| Purpose | What it serves |
|---|---|
| `review` | Only what the spacing schedule says is due — the highest-value practice there is |
| `weak` | Topics where accuracy is lowest relative to exam weight |
| `mixed` | Previous-year questions across subjects, the way the real paper mixes them |
| `speed` | One-mark questions on a tight clock, to fix time-per-question |
| `boss` | One hard two-mark question on covered ground |
| `fresh` | Only questions never served before |

Every question arrives with a `why` string saying why *that* question. A repeat
cooldown (default 9 days) stops the same question coming back too soon, unless it
is genuinely due for revision.

Per answer, the app records the response, seconds taken, self-rated confidence
(1–5), and — on a wrong answer — a mistake category: concept, silly, misread,
time, guess, or formula. "Silly" mistakes need a completely different fix from
"concept" mistakes, and the app will not pretend otherwise.

### A feedback loop, honestly described

Under every suggestion there are rating buttons. Rating one nudges a weight;
weights re-rank future advice, adjust question difficulty, and change how much
the planner hands you.

This is **preference learning. It is not RLHF and it is not a language model.**
Specifically:

- Weights are clamped between `0.35` and `1.90`.
- Learning rate `0.08`, and step size shrinks as sample count grows — one bad
  afternoon cannot permanently break your recommendations.
- With zero ratings every weight is exactly `1.0` and you get the plain rules
  engine. **The app is fully useful before it has learnt anything.**

The Readiness page shows every learned weight and how many ratings produced it,
so the loop is inspectable rather than magic.

### Gamification that rewards the right behaviour

45 stickers across five tracks: consistency (8), discipline (8), strength (11),
retention (8), mastery (10). Nothing is handed out — each sticker is a rule over
your own logs and unlocks the moment the rule is met. The tracks deliberately
reward showing up, revising on schedule, and finishing hard problems, because
those are what actually move a score.

Missions are live daily and weekly goals computed on the fly, stored nowhere.

### Cohort numbers are a simulation, and say so

Percentiles and cohort positions are generated locally from a fixed seed. They
are consistent, so you can pace against them — but there is no server and there
are no other users. Passing simulated people is not the same as passing real
ones. Cutoffs in `content/targets.json` are unofficial figures; verify them and
edit the file. **The app states this on the page itself, not just in this README.**

### Optional LLM, tightly fenced

The Doubt desk can call a model to *explain* a concept or rephrase a question. It
is never allowed to decide what you study, mark a topic done, or set a priority —
those come from your logs. You can also press **Build prompt** and paste it into
whatever chat window you already have open, with no key configured at all.

Doubts get a two-stage resolution signal: an immediate helped / still-stuck
button, and a delayed one the engine sets by itself when you later answer that
topic correctly.

---

## 2. How it is built

### Design constraints, chosen deliberately

| Constraint | Why |
|---|---|
| Python standard library only | Runs on any machine with Python. No dependency rot in three years. |
| Vanilla JavaScript, no framework | No build step, no `node_modules`, no bundler to break. View source and read it. |
| SQLite, single file | Your whole history is one file you can copy, email, or back up. |
| No cloud, no network at runtime | Nothing to go down, nothing to leak, nothing to pay for. |
| Every number carries a reason | Prevents the app from becoming a dashboard you stop looking at. |

Optional extras (`pillow` for icon generation, `pyinstaller` for packaging,
`pywebview` for a native window, `playwright` for the browser check) are needed
only by specific tools, never by the app itself.

### Architecture

```
                      ┌──────────────────────────┐
   browser  ◄────────►│  core/api.py             │  54 HTTP routes
   (vanilla JS)       │  ThreadingHTTPServer     │  one big /api/state payload
                      └────────────┬─────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
      ┌───────────────┐   ┌────────────────┐   ┌────────────────┐
      │ core/stats.py │   │ core/planner   │   │ core/recommend │
      │ ONE analytics │──►│ builds today's │──►│ ranked, with   │
      │ pass          │   │ plan           │   │ reasons        │
      └───────┬───────┘   └────────────────┘   └───────┬────────┘
              │                                        │
              ▼                                        ▼
      ┌───────────────┐                       ┌────────────────┐
      │ core/revision │                       │ core/feedback  │
      │ SM-2 schedule │                       │ learned weights│
      └───────┬───────┘                       └───────┬────────┘
              │                                        │
              ▼                                        ▼
      ┌───────────────┐   ┌────────────────┐   ┌────────────────┐
      │ core/quiz.py  │   │ core/readiness │   │ core/achieve.  │
      │ selection +   │   │ index + why it │   │ badges +       │
      │ GATE marking  │   │ moved          │   │ missions       │
      └───────┬───────┘   └────────────────┘   └────────────────┘
              │
              ▼
      ┌──────────────────────────────────────────────────────────┐
      │ core/content.py   content registry: banks, topics,        │
      │                   aliases, review promotion, answers      │
      ├──────────────────────────────────────────────────────────┤
      │ core/db.py        schema v8, versioned migrations, health │
      └──────────────────────────────────────────────────────────┘
                    │                            │
              data/gitgrind.db            content/*.json
```

### Key design decisions

**One analytics pass.** `stats.gather(conn)` walks the data once and returns a
bundle every other engine reads. Nothing recomputes metrics independently, so two
screens can never disagree about your accuracy.

**Versioned migrations, never a rebuild.** `core/db.py` holds a base `SCHEMA` for
fresh installs and an ordered `MIGRATIONS` list applied by version number, with
column additions handled idempotently. Your database is upgraded in place; a
logged minute is never lost to a schema change.

**Slugs at the edges, ids inside.** The UI speaks in slugs (`operating-systems`,
`deadlock`), the engines speak in integer ids. `core/api.py` translates at the
boundary so neither side needs to know about the other.

**Bank writes are always safe.** Every write to a question file is backed up to
`content/backups/` first and then written to a temp file and renamed. A crash
mid-write cannot truncate your bank; a bad import can be undone by restoring one
file.

**Read-only assets versus writable data.** `core/db.py` exposes `ASSET_DIR`
(inside the bundle when packaged: `static/` and shipped `content/`) and `APP_DIR`
(next to the executable: `data/` and your edited `content/`). Getting this wrong
would be fatal in a packaged build, because PyInstaller unpacks into a temporary
directory that is deleted on exit.

**The frontend is IIFE modules on a `GG` namespace.** Each file attaches one
object — `GG.render`, `GG.plan`, `GG.practice`, `GG.readiness`, `GG.bank`,
`GG.doubts`, `GG.app` — with shared helpers in `GG` itself. No imports, no build,
load order set by the `<script>` tags in `index.html`.

**ASCII-only glyphs.** No emoji anywhere. State is shown with `!` `~` `+` `#`, so
the UI renders identically in every terminal, browser, and font.

---

## 3. What it contains

### Current numbers

| Thing | Count |
|---|---|
| Python + JS + CSS | ~15,500 lines |
| Database tables | 27, schema v8 |
| HTTP routes | 54 |
| Engines in `core/` | 12 modules |
| Questions in the bank | 3,597 across 24 files |
| — gradable right now | 628 |
| — waiting on an answer | 2,948 (1,768 also missing options) |
| — unusable | 21 |
| Syllabus topic coverage | 99% (100 of 101 topics) |
| Stickers | 45 across 5 tracks |
| Selection purposes | 6 |
| Demo profiles | 4 |
| Self-test checks | 46 |

### Layout

```
app.py                    381   bootstrap, CLI, window launching
demo_data.py              529   four synthetic profiles
gitgrind.spec              68   PyInstaller spec for hand-tuned builds
run.bat / run.sh                development launchers only
README.md                       this file

core/                    5,884  the engines
  db.py                   580   schema, migrations, path resolution, health
  content.py              936   content registry: banks, topics, aliases,
                                review promotion, pending answers
  stats.py                683   the single analytics pass
  revision.py             370   spaced repetition (SM-2 variant)
  quiz.py                 908   purpose-driven selection, grading, GATE marking
  planner.py              487   daily plan / DPP builder
  recommend.py            468   ranked, explained recommendations
  readiness.py            600   index, decomposition, projections
  feedback.py             307   preference logging and weight updates
  achievements.py         345   45 badges across 5 tracks, live missions
  doubts.py               376   doubt log, prompt building, fenced LLM call
  api.py                  807   54 HTTP routes, the /api/state payload

static/                  4,616  the UI
  index.html              617   the shell and every modal
  css/style.css          1,148  design tokens, components, motion, a11y, splash
  js/core.js              457   helpers, prefs, shortcuts, focus trap, splash
  js/render.js            467   sidebar, subjects, calendar, feed, subject detail
  js/plan.js              595   command centre: next action, missions, plan,
                                revision queue, mastery map, recommendations
  js/practice.js          639   quiz runner, adaptive modes, confidence,
                                mistake tagging, saved questions
  js/readiness.js         352   index breakdown, movement, projection, weights
  js/bank.js              470   bank health, sources, imports, review queue,
                                pending answers, search
  js/doubts.js            366   doubt desk
  js/app.js               472   boot, routing, session logging, settings
  icon.ico / icon.png           generated app icon, matches the favicon

tools/                   4,312  the workshop
  ingest.py               521   ingestion backbone: sources, dedupe, manifests,
                                confidence scoring, DB review queue
  import_questions.py   1,508   paper and book parser
  extract_go_bank.py      589   bulk extraction from the GO volumes
  answer_fill.py          307   fill pending answers from the terminal
  fetch_go_pdfs.py        477   GitHub release downloader, sha256 verified
  selftest.py             313   46 end-to-end engine checks
  browsercheck.py         281   drives a real browser over every page
  build_exe.py            220   packaging
  make_icon.py             96   generate icon.ico from the favicon design

content/
  syllabus.json                 12 subjects, 101 topics, exam weights
  targets.json                  unofficial cutoffs — verify and edit
  topic_keywords.json           lexicon used to tag imported questions
  go_tag_map.json               GO section names → syllabus slugs
  questions/                    12 curated bank files
  banks/go-extracted/           12 files, 3,487 questions from the GO volumes
  banks/reviewed/               approved review items land here
  review/go-unsorted.json       206 questions whose topic did not match
  imports/                      one manifest per import run
  backups/                      pre-write .bak copies, 20 most recent

data/gitgrind.db                your entire history
papers/                         source PDFs and extracted text
```

### The database

27 tables. The ones you would actually look at:

| Table | Holds |
|---|---|
| `sessions` | Every study session: subject, minutes, kind, day, note |
| `attempts` | Every answer: correct, seconds, confidence, mistake kind, reattempt |
| `quizzes`, `quiz_questions` | Built sets and their contents, with the purpose and reason |
| `topics` | Status, confidence, last revised — the coverage source of truth |
| `revision_queue` | The spacing schedule: ease, interval, due date, reps, lapses |
| `readiness_log` | A snapshot per reading, with every component, for "why it moved" |
| `feedback`, `learned_weights` | Your ratings and the weights they produced |
| `daily_plans`, `dpp_sets` | Generated plans and the question sets behind blocks |
| `recommendations` | What was suggested, and what came of it |
| `question_sources`, `question_imports`, `question_review` | Bank provenance |
| `question_stats` | Per-question rollups used by the selector |
| `topic_alias`, `topic_prerequisites` | Topic normalisation and the topic graph |
| `doubts` | The doubt log, including whether it actually helped |
| `schema_meta`, `settings` | Schema version and your tunable preferences |

---

## 4. Running it

### Three stages

| Stage | Command | Use it when |
|---|---|---|
| Development | `python app.py` | You are editing code. Opens a browser tab. |
| Testing | `run.bat` / `./run.sh` | You want a double-click that still runs from source |
| Daily use | `dist/GitGrind.exe` | Every day. Opens its own window. |

### Flags

```
python app.py --check              health report, then exit
python app.py --window             open in a plain app window, not a browser tab
python app.py --no-browser         start the server, open nothing
python app.py --port 9000          different port
python app.py --host 0.0.0.0       bind wider (be careful, there is no auth)
python app.py --demo disciplined   load a demo profile to see a populated UI
python app.py --demo patchy        gaps and inconsistency
python app.py --demo comeback      a long break then a return
python app.py --demo sprint        exam close, high intensity
python app.py --reset activity     wipe sessions and attempts, keep the syllabus
python app.py --reset all          wipe everything
python app.py --version
```

### Keyboard

Press `?` for the full list — it is generated from the registered shortcuts, so
it cannot go stale. The ones worth memorising:

| Key | Action |
|---|---|
| `l` | Log a session |
| `n` | Do the next action |
| `v` | Start the revision set that is due |
| `g` | Rebuild today's plan |
| `t` `s` `p` `r` `b` `a` `d` | Jump to Today, Subjects, Practice, Readiness, Bank, Activity, Doubts |
| `m` | Toggle reduced motion |

Shortcuts are inert while you are typing in a field.

---

## 5. The question bank

### Where questions come from

Layered, in order of preference:

1. **Official GATE papers** you supply as PDF or text.
2. **GATE Overflow PDFs**, from the project's GitHub *Releases*.
   `tools/fetch_go_pdfs.py` pulls release assets through the API. It does not
   scrape web pages and it will not.
3. **Your own curated questions** in the JSON schema below.
4. **Generated practice sets (DPPs)** assembled from the above.

### Three-stage ingestion

```
    fetch                parse and normalise              review
  ----------           ---------------------          --------------
  release assets  ->   text extraction, topic    ->   a human approves
  or your own PDF      tagging, answer-key             each low-confidence
                       matching, confidence            item in the Bank tab
                       scoring, dedupe
```

**Stage 1 — fetch**

```
python tools/fetch_go_pdfs.py --list
python tools/fetch_go_pdfs.py --tag <tag> --only vol1 --extract
python tools/fetch_go_pdfs.py --index-only --tag <tag>   # metadata, no download
python tools/fetch_go_pdfs.py --verify                   # re-check every sha256
python tools/fetch_go_pdfs.py --manifest                 # what is on disk
```

Downloads resume, sizes are checked, and a sha256 lands in
`papers/manifest.json`, verified against GitHub's published digest when there is
one. `--verify` later tells you whether a file changed under you.

**Stage 2 — parse and normalise**

```
# always look first
python tools/import_questions.py papers/gate2024-cs.pdf --year 2024 --dry-run

# see what the extracted text even looks like
python tools/import_questions.py --probe papers/gate2024-cs.pdf

# the real thing
python tools/import_questions.py papers/gate2024-cs.pdf \
    --answers papers/gate2024-cs-key.pdf --year 2024 \
    --source gate-official --source-kind official --to-db-review
```

The `--dry-run` report gives you: how many were found, matched, held for review,
rejected as duplicates, flagged as near-duplicates, the confidence spread, the
lowest-confidence items *and why each scored low*, and which syllabus topics are
still underrepresented afterwards.

Every run writes a manifest to `content/imports/` and a row to the import log in
the Bank tab, so months later you can still answer "what did that import do?"

**Stage 3 — review**

Low-confidence questions land in the Bank tab's review queue. Approving copies
the question into `content/banks/reviewed/<subject>.json` and it goes live.
Rejecting leaves it out. Either way the raw imported file is never edited.

From the terminal:

```
python tools/ingest.py --review
python tools/ingest.py --approve 12
python tools/ingest.py --reject 12 --note "bad OCR, figure missing"
```

### Bulk extraction from the GO volumes

`tools/extract_go_bank.py` takes the opposite position from the importer on
purpose: **keep everything.** A question with no printed answer is still worth
having, because you can look the answer up once and then it is yours forever.

```
python tools/extract_go_bank.py --dry-run     report only
python tools/extract_go_bank.py               write content/banks/go-extracted/
```

Questions with no answer are written with:

```json
"answer_pending": true,
"answer": null,
"answer_note": "Answer not printed in the source. Look it up online, then log it from the Bank tab."
```

A `answer_pending` question is **present but not gradable**: it counts towards
coverage, it is listed in the Bank tab so you can fill it in, and the quiz
selector will never serve it. Verified: all six selection purposes leak zero
pending questions.

### Filling in pending answers

Bank tab → **Answers to look up**. Each row has a one-click search that opens the
question text in a web search. Find the answer, type `B` (or `B,D`, or a numeric
value for NAT), press Save. It is written straight into the bank file, backed up
first, and the question becomes gradable permanently. No re-import needed.

Questions marked `needs_options` also lost their option list to text extraction —
paste the options in as well, one per line.

From the terminal instead:

```
python tools/answer_fill.py
```

### Bank maintenance

```
python tools/ingest.py --sources     registered sources and question counts
python tools/ingest.py --imports     the import log
python tools/ingest.py --dedupe      duplicates already in the bank
python tools/ingest.py --gaps        underrepresented topics, by exam weight
python tools/ingest.py --register <slug> "<Name>" --kind official --url ...
```

### Adding questions by hand

One file per subject under `content/questions/`, or a folder under
`content/banks/<name>/`:

```json
{
  "subject": "operating-systems",
  "source": { "slug": "my-notes", "name": "My own notes", "kind": "manual" },
  "questions": [
    {
      "id": "os-deadlock-01",
      "topic": "deadlock",
      "kind": "dpp",
      "type": "mcq",
      "marks": 2,
      "difficulty": "medium",
      "year": 2023,
      "text": "A system has 3 processes and 4 instances of a resource...",
      "options": ["1", "2", "3", "4"],
      "answer": "B",
      "explain": "Apply the deadlock-free condition n*(k-1) < m ..."
    }
  ]
}
```

- `type` is `mcq`, `msq` or `nat`. For `nat`, drop `options`/`answer` and give
  `answer_value` (plus optional `answer_low`/`answer_high` for a range).
- `topic` must be a slug from `content/syllabus.json`. Unrecognised topics are
  reported, never silently guessed.
- Restart, or press **Reload from disk** in the Bank tab.

Validate before trusting it:

```
python tools/import_questions.py --validate content/questions/my-file.json
```

---

## 6. Your data and backups

Everything is in **one file**: `data/gitgrind.db`.

| What | Where |
|---|---|
| Sessions, attempts, quizzes, topics, revision schedule, feedback, plans | `data/gitgrind.db` |
| Syllabus, targets, lexicons | `content/*.json` |
| Question bank | `content/questions/`, `content/banks/` |
| Import manifests, pre-write backups | `content/imports/`, `content/backups/` |
| Source PDFs | `papers/` |

### Backups, in order of how much to trust them

1. **Copy the file.** Close the app, copy `data/gitgrind.db` elsewhere. Complete,
   byte-for-byte exact. Do this weekly; it takes two seconds.
2. **Export from the app.** Activity → *Export backup* writes a JSON dump of 25
   tables. Any API key is stripped on the way out.
3. **Import.** Activity → *Import backup* reads that JSON back.

### What is stored about you

Your name, handle, bio, location, exam date and daily target — whatever you typed
into the profile dialog. Your sessions, answers, timings, self-rated confidence,
mistake tags, doubts, and your ratings of the app's suggestions.

None of it leaves the machine. The only outbound network calls the app can make
are ones you explicitly trigger: `tools/fetch_go_pdfs.py`, and the Doubt desk if
you configure a provider.

---

## 7. Packaging into an executable

### Build

```
pip install pillow                        once, for the icon
python tools/make_icon.py --preview       generates static/icon.ico + .png

pip install pyinstaller                   once
python tools/build_exe.py --clean --stage
```

| Flag | Effect |
|---|---|
| `--clean` | Wipe `build/` and `dist/` first. Use it whenever you changed the UI. |
| `--stage` | Copy your existing `data/gitgrind.db` next to the built executable |
| `--onedir` | A folder instead of one file — starts noticeably faster |
| `--nuitka` | Compile rather than bundle (needs a C compiler); fastest binary |
| `--stage-only` | Skip the build, just do the staging copy |

The build log should say `using icon: static/icon.ico`. If it does not, the icon
was never generated.

### Result

```
dist/
  GitGrind.exe          the app
  data/gitgrind.db      your history (--stage copied it)
  content/              created automatically on first run
```

`static/` and `content/` are bundled inside the executable, so it needs no
network and no CDN. `data/` is deliberately **not** bundled, and on first run the
app copies `content/` out beside the executable so bank files stay writable —
otherwise logging an answer would vanish every time you closed the app.

### Window mode

A packaged build opens **its own window**, not a browser tab. `launch_ui()` in
`app.py` tries three routes in order:

1. **pywebview** if installed (`pip install pywebview`) — a genuinely native
   window using the system web view, with a taskbar icon.
2. **Chromium app mode** (`--app=`) using Edge or Chrome, which every Windows
   machine already has. No address bar, no tab strip. A private profile directory
   under `data/uiprofile` keeps it out of your normal browsing session.
3. **The normal browser**, which is what running from source does.

Test it from source with `python app.py --window`.

### Important

**The UI and Python code are baked into the executable at build time.** Editing
files on disk changes only the source tree. Any change to `static/` or `*.py`
needs a rebuild with `--clean`. `content/` is the exception — it lives beside the
executable and is editable.

Develop with `python app.py --window`. Build the executable only when the work is
finished.

---

## 8. Diagnosing problems

### Start here, always

```
python app.py --check
```

Reports the schema version, whether migrations are pending, table count, database
size, bank health, topic coverage, and how many questions are waiting for review.
Nine out of ten problems are visible in this output.

```
python tools/selftest.py
```

46 checks against a temporary database — schema, migrations, content registry,
session logging, quiz building and grading, all six selection purposes, spaced
repetition, analytics, planner, recommendations, readiness, feedback clamping,
badges, doubts, and the full `/api/state` payload. Add `--verbose` for
tracebacks, `--keep` to keep the temp database for poking at.

```
python tools/browsercheck.py
```

Drives a real browser over every page and reports JavaScript errors and console
warnings. This is the only check that catches frontend bugs; the Python tests
cannot see them. Needs `pip install playwright && playwright install chromium`.

### Symptom table

| Symptom | Cause | Fix |
|---|---|---|
| **Panels blank but no error** (missions, plan, hero empty) | A render function was never called, or threw before reaching them | Open the browser console. Then in the console run `GG.plan.paint(GG.S.state)` — if that works, the router is not calling it; check the `paint()` dispatch in `static/js/app.js`. |
| **A panel shows "--" or nothing where a number should be** | Field-name mismatch between engine and UI | In the console, `GG.S.state.readiness` (or the relevant key) and compare the keys with what the JS reads. This is the single most common frontend bug. |
| **Everything blank, console shows `Cannot read properties of undefined`** | JS threw mid-render, so everything after it is skipped | The stack trace names the file and line. Guard the field with `Number(x \|\| 0)` or `(x \|\| {})`. |
| **Changes to the UI have no effect** | Browser cache, or you are running a stale executable | `Ctrl+Shift+R`. If it is the exe, rebuild with `--clean` and delete `dist/data/uiprofile`. |
| **`Could not bind ...: address already in use`** | Another copy is running, or the port is taken | `python app.py --port 9000` |
| **Bank health suddenly low** | An import added questions with no answer or no options | Bank tab, or `python tools/ingest.py --gaps`. `pending` is normal and expected; `broken` is the number that matters. |
| **Quiz says "no questions available"** | The purpose filter found nothing — usually a topic with only pending questions | Check the Mastery map for that topic's bank count. Fill in answers, or widen the selection. |
| **Revision queue empty on an old database** | The schedule was never backfilled | It backfills automatically on init. Force it: `python -c "from core import db,revision; c=db.init(); print(revision.sync_from_activity(c))"` |
| **A migration failed** | Usually a hand-edited database | Restore your backup, then `python app.py --check` to see the version it stopped at. Migrations are ordered and idempotent; they can be re-run safely. |
| **Import wrecked a bank file** | A bad parse got written | Copy the matching `.bak` from `content/backups/` over the original, then **Reload from disk**. |
| **Executable loses its data every run** | `core/db.py` path resolution is wrong — `BASE_DIR` is pointing inside the bundle | `core/db.py` must define `ASSET_DIR` and `APP_DIR` separately. Verify: `python -c "from core import db; print(db.ASSET_DIR, db.APP_DIR)"` |
| **Exe icon did not change** | Windows icon cache | `ie4uinit.exe -show` |
| **Splash never goes away** | JS threw before the first paint | It self-dismisses after 7 seconds regardless. If the app is still hidden, `document.body.className` will show `booting` — the console will have the real error. |
| **Readiness index looks wrong** | Small sample | Check `estimate_confidence` on the Readiness page. With few attempts the index deliberately pulls toward neutral and says so. |

### Useful console probes

Open the browser console on any page:

```javascript
GG.S.state                      // the entire payload the server sent
Object.keys(GG.S.state)         // every top-level key
GG.S.state.plan.blocks          // today's plan blocks
GG.S.state.debt                 // revision pressure
GG.S.state.feedback.learned     // what the app has learnt from you
GG.plan.paint(GG.S.state)       // re-render the command centre by hand
GG.app.reload()                 // refetch state and repaint
```

### Useful Python probes

```python
from core import db, content, stats, planner, recommend, readiness
conn = db.init(); content.seed(conn)

db.health(conn)                       # schema version, tables, size
content.bank_stats(reload=True)       # usable / broken / pending / coverage
content.pending_counts()              # how many answers are waiting
bundle = stats.gather(conn)           # the one analytics pass
bundle["metrics"]                     # every metric the UI shows
planner.plan_for(conn, bundle, regenerate=True)
recommend.build(conn, bundle, None)   # ranked advice with reasons
readiness.compute(conn, bundle["metrics"], bundle=bundle)
```

Point any tool at a throwaway database with the `GITGRIND_DB` environment
variable, so experiments never touch your real history.

### Reading the logs

The app prints to its console. In a packaged build the console stays attached on
purpose — it is where the URL, the `content unpacked` message, and any bank
warnings appear. If the window closes instantly, run the executable from a
terminal to see why.

---

## 9. Accessibility

- Every state indicator carries a glyph as well as a colour — `!` critical,
  `~` weak, `+` ok, `#` strong — so nothing is communicated by hue alone. The
  mastery map prints the glyph inside each cell.
- Full keyboard operation. `?` lists every shortcut, generated from the registry.
- Dialogs trap Tab and return focus where it came from on close.
- Route changes move focus into the new view rather than leaving it on the nav.
- Toasts are announced through an `aria-live` region.
- `prefers-reduced-motion` is honoured, plus an in-app **Reduced motion** setting
  for when the OS setting is not what you want here. Either one strips every
  transition, the staggered entrance, and the splash animation.
- Visible focus rings everywhere, with a skip link to the main content.

---

## 10. Where to change things

The most common edits, and the one place to make each:

| You want to | Edit |
|---|---|
| Change the syllabus, topics, or exam weights | `content/syllabus.json` |
| Fix a cutoff or add a target | `content/targets.json` |
| Improve automatic topic tagging on import | `content/topic_keywords.json` |
| Change how the readiness index is weighted | the component weights in `core/readiness.py` |
| Change spacing intervals or ease bounds | the constants at the top of `core/revision.py` |
| Add a selection purpose | `PURPOSE_LABELS` and `select()` in `core/quiz.py` |
| Add a plan block type | the generators and `PACE` in `core/planner.py` |
| Add a recommendation | write a `_generator` in `core/recommend.py` and register it |
| Add a badge or track | the track tables in `core/achievements.py` |
| Add a mission | `missions()` in `core/achievements.py` |
| Change mistake categories | `MISTAKE_KINDS` in `core/quiz.py` |
| Tune how fast feedback learns | `LR` and the clamps in `core/feedback.py` |
| Add an API route | `core/api.py`, and add the key to `build_state()` if the UI needs it |
| Change colours, spacing, or motion | the `:root` tokens at the top of `static/css/style.css` |
| Change the splash timing | `SPLASH_MIN_MS` in `static/js/core.js` |
| Change the app icon | edit the palette in `tools/make_icon.py`, re-run it, rebuild |
| Add a keyboard shortcut | `registerShortcuts()` in `static/js/app.js` — the help dialog updates itself |
| Add a user-tunable setting | `TUNABLE` in `core/api.py`, defaults in `core/content.py`, copy in `SETTING_COPY` in `static/js/app.js` |
| Add a database table or column | append to `MIGRATIONS` in `core/db.py` and bump `SCHEMA_VERSION` — never edit the base `SCHEMA` alone, or existing databases will not get it |

### House rules if you extend it

1. **Every number needs a reason string.** If you cannot write the sentence
   explaining what to do about a metric, do not put it on screen.
2. **New engine data goes through `stats.gather()`**, not a second query pass.
3. **Schema changes go in `MIGRATIONS`.** Editing `SCHEMA` alone breaks every
   existing database.
4. **Bank writes back up first, then write atomically.** Copy the pattern in
   `content.set_answer()`.
5. **Never let a rating failure block a study action.** Feedback calls are wrapped
   in try/except for a reason.
6. **ASCII glyphs only.** No emoji.
7. **Run `selftest.py` and `browsercheck.py` before you trust a change.** The
   Python tests cannot see frontend bugs, and the browser check cannot see engine
   bugs. You need both.

---

## 11. Future prospects

Ordered by value-for-effort, honestly assessed.

### High value, low effort

- **Finish the pending answers.** 2,948 questions are one lookup each from being
  gradable. This is by far the highest-value thing left, and it needs no code.
  Filling 20 a day makes the bank properly usable in five months; filling the
  1,180 that already have options is faster still.
- **Match answer keys automatically.** The GO volumes print answers in a separate
  section for some volumes. A better key matcher in `import_questions.py` could
  clear a large fraction of the 2,948 without human lookup.
- **Fix the 21 broken questions.** `python tools/selftest.py --verbose` lists
  them. A morning's work.
- **Fill the last empty topic.** `computer-organization/secondary-storage` has no
  questions. Write five by hand.
- **Per-topic time budgeting.** The planner already knows exam weights and your
  accuracy. It could tell you how many hours a topic *deserves* rather than only
  what to do next.

### Medium effort, real payoff

- **Mock test mode.** A full 65-question, 180-minute paper with GATE marking,
  section timing, and a post-mortem that feeds the same analytics. The marking
  rules already exist in `core/quiz.py`; what is missing is the timed shell and
  the report.
- **Figure support.** 429 questions reference a diagram that text extraction
  dropped. Rendering the source PDF page region beside the question would
  recover them. `pypdf` plus a page-crop cache.
- **Prerequisite-aware planning.** `topic_prerequisites` is populated but barely
  used. The planner could refuse to schedule a topic whose prerequisites are weak,
  which is how a human tutor would sequence things.
- **Formula and note cards.** A revision surface for definitions and formulas,
  scheduled by the same SM-2 engine. Cheap, because the engine is generic.
- **Error-log review.** A dedicated screen for every question you ever got wrong,
  grouped by mistake category, with the pattern spelled out.
- **Mobile layout.** The CSS is responsive but was designed for a desktop HUD.
  A phone-first review mode — just the revision queue and the daily plan — would
  make dead time useful.
- **Multi-exam support.** The schema is not GATE-specific. Adding a second exam
  profile (BARC, ISRO, NET) mostly means another syllabus file and target file.

### Larger projects

- **Proper spaced repetition for subjective material.** Long-answer and
  derivation practice with self-grading rubrics, which the current binary
  correct/wrong model cannot represent.
- **A real cohort.** Replace the simulation with opt-in, anonymised, aggregate
  comparison. This is the one feature that would need a server, and it would need
  a serious privacy design before it deserved to exist.
- **Adaptive difficulty from item response theory.** The current difficulty dial
  is a heuristic. A two-parameter IRT model over your attempt history would
  estimate question difficulty and your ability jointly, and pick questions at the
  edge of your competence.
- **Handwriting and workings capture.** Photograph your rough work, attach it to
  the attempt. Would make the mistake taxonomy far more useful when reviewing.
- **Native window without a browser dependency.** `pywebview` is already
  supported; making it the default would need bundling the runtime.

### Deliberately not planned

- **Cloud sync.** The one-file-on-your-disk property is the reason you can trust
  this app. Sync would mean accounts, a server, and a privacy policy.
- **A recommendation LLM.** The rules engine is inspectable and cannot
  hallucinate a study plan. The LLM stays fenced to explaining concepts.
- **Streak pressure and notifications.** Guilt mechanics are how study apps get
  uninstalled in March.

---

## 12. Honest limitations

Read this before trusting any number.

- **Only 628 of 3,597 questions are gradable right now.** 2,948 are waiting on
  answers you must look up, and 1,768 of those also lost their options to text
  extraction. Topic coverage says 99%, but *gradable* coverage is much lower.
- **Cohort numbers are simulated.** Percentiles come from a fixed-seed local
  model, not from real students.
- **Cutoffs are unofficial.** `content/targets.json` needs verifying against the
  actual notification for your year.
- **The readiness index is a heuristic, not a predictor.** It has never been
  validated against real GATE results, because it cannot be. Treat it as a
  consistency measure — is it going up? — not as a score forecast.
- **The feedback loop is preference learning, not RLHF.** It re-ranks advice. It
  does not learn what makes you learn.
- **429 questions reference figures** that are not in the extracted text.
- **206 questions** could not be matched to a syllabus topic and sit unused in
  `content/review/go-unsorted.json`.
- **There is no authentication.** Do not run it on `--host 0.0.0.0` on a shared
  network.
- **The frontend has no automated unit tests.** `browsercheck.py` catches thrown
  errors and blank pages; it does not verify that a number is correct.

---

## Health check summary

```
python app.py --check          schema, bank health, coverage, pending review
python tools/selftest.py       46 engine checks against a temp database
python tools/browsercheck.py   real browser over every page
python tools/ingest.py --gaps  which topics still need questions
```

If something looks wrong, run the first one. It usually tells you.