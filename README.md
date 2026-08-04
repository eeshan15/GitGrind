<div align="center">

# GitGrind

**A local, offline operating system for a GATE CSE attempt.**

[![Latest release](https://img.shields.io/github/v/release/eeshan15/GitGrind?style=for-the-badge&color=e8b43e&labelColor=0d1117)](https://github.com/eeshan15/GitGrind/releases/latest)
[![Download](https://img.shields.io/badge/download-Windows%20installer-2ea043?style=for-the-badge&labelColor=0d1117)](https://github.com/eeshan15/GitGrind/releases/latest)
[![Licence](https://img.shields.io/github/license/eeshan15/GitGrind?style=for-the-badge&color=79c0ff&labelColor=0d1117)](LICENSE.txt)

[![Python](https://img.shields.io/badge/python-3.8%2B-3776ab?style=flat-square&labelColor=0d1117)](https://www.python.org/)
[![Runtime dependencies](https://img.shields.io/badge/runtime%20dependencies-none-2ea043?style=flat-square&labelColor=0d1117)](#design-constraints-chosen-deliberately)
[![Network](https://img.shields.io/badge/network-never-2ea043?style=flat-square&labelColor=0d1117)](#7-your-data-and-backups)
[![Selftest](https://img.shields.io/badge/selftest-46%2F46-2ea043?style=flat-square&labelColor=0d1117)](#9-diagnosing-problems)
[![Bandit](https://img.shields.io/badge/bandit-0%20issues-2ea043?style=flat-square&labelColor=0d1117)](pyproject.toml)
[![Code style](https://img.shields.io/badge/code%20style-black-000000?style=flat-square&labelColor=0d1117)](https://github.com/psf/black)
[![Visualisers](https://img.shields.io/badge/concept%20visualisers-21-e8b43e?style=flat-square&labelColor=0d1117)](#2-the-21-concept-visualisers)

</div>

---

## Download

<div align="center">

### [Download GitGrind for Windows](https://github.com/eeshan15/GitGrind/releases/latest)

</div> 

Grab the installer from the
**[latest release](https://github.com/eeshan15/GitGrind/releases/latest)**, run
it, and you are done.

- No Python needed
- No dependencies to install
- No account, no sign-up, no subscription
- Windows 8.1 or newer, 64-bit

Windows will show *"Windows protected your PC"* because the installer is not
code-signed. Click **More info**, then **Run anyway**. The entire source is in
this repository if you would rather build it yourself; see
[section 8](#8-packaging-into-an-executable).

The installer puts GitGrind in your own user folder, so it never asks for
administrator rights. It creates a Start Menu entry, an optional desktop
shortcut, and an entry in Add/Remove Programs. Uninstalling deliberately leaves
your study history behind.

**Running from source instead:**

```
git clone https://github.com/eeshan15/GitGrind.git
cd GitGrind
python app.py
```

That is the whole setup. Python 3.8 or newer, standard library only, nothing to
`pip install`.

---

## The pitch

This is not a study-hours tracker with charts bolted on.

Every screen exists to answer one question: **what should I do in the next hour,
and why that one?** Logging is the cheap part. The value is in what the app does
with the log once it has it.

Open it and the first thing you see is a single card naming one action, the
reason it was chosen, what it is expected to be worth, and which suggestion it
beat. Not a dashboard. A decision.

Everything runs on your machine. No account, no cloud, no telemetry. The entire
state of your preparation is one SQLite file you can copy to a USB stick.

---

## At a glance

| | |
|---|---|
| **Lines of code** | ~27,000 (Python, vanilla JS, CSS) |
| **Runtime dependencies** | Zero |
| **Engines** | 12 modules in `core/` |
| **HTTP routes** | 55 |
| **Database tables** | 27, schema v8, migrated in place |
| **Concept visualisers** | 21, interactive, driven by your own numbers |
| **Question bank** | 3,597 across 24 files, 99% topic coverage |
| **Achievement stickers** | 45 across 5 tracks |
| **Selection purposes** | 6 |
| **Self-test checks** | 46, all passing |
| **Security issues (bandit)** | 0 |

---

## Contents

1. [What it does](#1-what-it-does)
2. [The 21 concept visualisers](#2-the-21-concept-visualisers)
3. [Logging: two ways](#3-logging-two-ways)
4. [How it is built](#4-how-it-is-built)
5. [What it contains](#5-what-it-contains)
6. [Running it](#6-running-it)
7. [Your data and backups](#7-your-data-and-backups)
8. [Packaging into an executable](#8-packaging-into-an-executable)
9. [Diagnosing problems](#9-diagnosing-problems)
10. [The question bank](#10-the-question-bank)
11. [Accessibility and motion](#11-accessibility-and-motion)
12. [Where to change things](#12-where-to-change-things)
13. [Roadmap](#13-roadmap)
14. [Honest limitations](#14-honest-limitations)
15. [Licence and credits](#15-licence-and-credits)

---

## 1. What it does

### Prescriptive analytics, not descriptive

The Today page opens with a single **next action** card: one thing to do, the
reason it was chosen, what it is expected to be worth, and *why it beat the
runner-up*. The ranking is auditable; you can always see what came second and
why it lost.

Behind that card sit the numbers that chose it:

| Signal | What it measures |
|---|---|
| Coverage | Syllabus closed, weighted by marks in the paper |
| Accuracy | Correct rate, with a confidence band by sample size |
| Volume | Questions attempted, and the rate they are arriving |
| Consistency | How evenly effort is spread, not just the total |
| Focus | Whether sessions are concentrated or scattered |
| Retention debt | How much of the revision schedule is overdue |
| Velocity trend | 7-day against 28-day: rising, falling or flat |
| Guess rate | Answers given with confidence 1 or 2 |
| Correction rate | Wrong answers later got right |
| Confidence drift | Whether your self-assessment tracks reality |
| Per-topic risk | Accuracy against exam weight, topic by topic |

The rule the whole UI follows: **if a number cannot be turned into an action, it
does not get a card.**

### Real spaced repetition

`core/revision.py` runs an SM-2 variant over two kinds of card: topics you have
marked done, and individual questions you got wrong.

| Outcome | What happens |
|---|---|
| Answered well | Interval stretches: 1 day, 3 days, then multiplied by an ease factor that grows with success |
| Answered badly | Resets to tomorrow, ease knocked down |
| **Confidently wrong** | Treated as the worst possible outcome, quality 0 |

That last row is the important one. Confidently wrong is the most expensive state
in exam preparation, because it is the one thing you will never revise
voluntarily. The engine punishes it hardest, on purpose.

Constants: ease clamped `1.3 - 2.9`, starting ease `2.5`, first interval 1 day,
second 3 days, maximum 180 days, failure below quality 2.

The queue produces a **revision debt** and a **pressure score** from 0 to 100,
and overdue items outrank almost everything else in the planner. An existing
database gets a schedule backfilled from its own history, so this works from the
first launch rather than needing months of data first.

### A daily plan that explains itself

`core/planner.py` builds today's plan from live signals: overdue revision, your
weakest covered topic, the highest-mark pending topic, a mixed previous-year set,
a speed drill when you are slow or the exam is close, and one boss question.

Every block carries three fields:

- `reason` -- why this block exists at all
- `fixing` -- which specific weakness it targets
- `aim` -- what counts as having succeeded

Blocks are trimmed to the time you actually have, in priority order, and block
size scales with what you have told the app about how much you can take.

Pressing **Start** on a block materialises the questions lazily, records the
purpose and the reason on the quiz itself, and files the attempts back against
that plan day. Rating the finished plan as too long or too short tunes tomorrow.

### An explainable readiness index

The index is a weighted sum of four measured terms and two heuristic ones. Every
term is labelled `measured` or `heuristic`, so you always know which numbers are
your data and which are the app's guess.

The Readiness page decomposes it four ways.

**Where the score comes from.** Earned points and remaining headroom per term.
The widest hatched bar is where the next hour buys the most.

**Why it moved.** The change since the last reading, broken down term by term. A
drop is never a mystery; you can see exactly which component fell and by how
much.

**Biggest risk and cheapest points.** One topic each way, with the reasoning
spelled out. The risk topic is where you are most exposed; the recovery topic is
where the least effort buys the most index.

**If you finish today's plan.** What completing the plan is arithmetically worth,
in index points and estimated score. Labelled arithmetic rather than forecast,
because that is exactly what it is.

There is also an **estimate confidence** band. With a dozen attempts logged the
app says the sample is thin rather than pretending it knows your score.

### Purpose-driven practice

Six selection purposes, each with a different job:

| Purpose | What it serves |
|---|---|
| `review` | Only what the spacing schedule says is due, the highest-value practice there is |
| `weak` | Topics where accuracy is lowest relative to exam weight |
| `mixed` | Previous-year questions across subjects, the way the real paper mixes them |
| `speed` | One-mark questions on a tight clock, to fix time per question |
| `boss` | One hard two-mark question on ground you have already covered |
| `fresh` | Only questions never served before |

Every question arrives with a `why` string saying why *that* question was picked.
A repeat cooldown, nine days by default, stops the same question coming back too
soon, unless it is genuinely due for revision, in which case the cooldown is
bypassed deliberately.

Per answer, the app records:

- the response and whether it was correct
- seconds taken
- self-rated confidence, 1 to 5
- on a wrong answer, a mistake category: concept, silly, misread, time, guess,
  or formula

"Silly" mistakes need a completely different fix from "concept" mistakes, and
the app will not pretend otherwise. The Practice tab shows the split and names
the pattern that dominates.

### GATE-accurate marking

One-mark and two-mark questions, negative marking at one third and two thirds,
MSQ with no negative marking, NAT with a tolerance range. The rules live in one
place in `core/quiz.py`, and the score breakdown is computed from the same pass
that produced the total, so the two can never disagree.

### A feedback loop, honestly described

Under every suggestion there are rating buttons. Rating one nudges a weight;
weights re-rank future advice, adjust question difficulty, and change how much
the planner hands you tomorrow.

This is **preference learning. It is not RLHF and it is not a language model.**
Specifically:

- Weights are clamped between `0.35` and `1.90`. Nothing can run away.
- Learning rate `0.08`, and the step size shrinks as the sample count grows. One
  bad afternoon cannot permanently break your recommendations.
- With zero ratings every weight is exactly `1.0` and you get the plain rules
  engine. **The app is fully useful before it has learnt anything.**

The Readiness page shows every learned weight and how many ratings produced it,
so the loop is inspectable rather than magic.

### Gamification that rewards the right behaviour

45 stickers across five tracks, bronze through diamond:

| Track | Count | Rewards |
|---|---|---|
| Consistency | 8 | Showing up, streaks, active days |
| Discipline | 8 | Hitting daily targets, weekly hours |
| Strength | 11 | Accuracy, boss questions, hard topics |
| Retention | 8 | Revising on schedule, clearing debt, comebacks |
| Mastery | 10 | Topics closed, weak topics cleared, corrections |

Nothing is handed out. Each sticker is a rule evaluated over your own logs and
unlocks the moment the rule is met. The tracks deliberately reward the behaviour
that actually moves a score: showing up, revising on schedule, and finishing hard
problems.

**Missions** are live daily and weekly goals computed on the fly and stored
nowhere: hit the daily target, attempt ten questions, clear the revision queue,
finish today's plan, practise five days this week.

### The mastery map

Every syllabus topic as one square, grouped by subject, coloured *and* glyphed by
health. Click any square to drill straight into that topic. The map answers "what
does my syllabus actually look like right now" in one glance, which no list of
percentages does.

### Cohort numbers are a simulation, and say so

Percentiles and cohort positions are generated locally from a fixed seed. They
are consistent, so you can pace against them, but there is no server and there
are no other users. Passing simulated people is not the same as passing real
ones. Cutoffs in `content/targets.json` are unofficial figures; verify them and
edit the file.

**The app states this on the page itself, not just in this README.**

### Optional LLM, tightly fenced

The Doubt desk can call a model to *explain* a concept or rephrase a question. It
is never allowed to decide what you study, mark a topic done, or set a priority.
Those decisions come from your logs.

You can also press **Build prompt** and paste it into whatever chat window you
already have open, with no key configured at all.

Doubts get a two-stage resolution signal: an immediate helped / still-stuck
button, and a delayed one the engine sets by itself when you later answer that
topic correctly. Asking about the same topic twice is a stronger weak-topic
signal than one wrong answer, and the planner treats it that way.

### Lives in the system tray

A packaged build runs like a desktop application, not a script:

- Its own window, its own taskbar icon, no terminal
- A tray icon that owns the process
- Closing the window hides it; the server keeps running
- Reopening from the tray is instant, and a running session timer is untouched
- Launching a second time raises the existing window instead of starting a
  second copy

The tray menu offers Open GitGrind, Open in browser, Show my data folder, and
Quit.

---

## 2. The 21 concept visualisers

Watching a canned animation is low-yield. Feeding your own numbers into a
simulation is not: it teaches the concept *and* checks your answer to the paper
question in front of you.

Every visualiser takes editable input, steps one frame at a time, and prints a
sentence explaining **why** each step happened. Play, pause, step, scrub, change
the speed. When you are done, one button takes you straight into a drill on that
topic.

| Subject | Visualiser | What you change | What you see |
|---|---|---|---|
| OS | CPU scheduling | Processes, arrival, burst, priority, quantum | Gantt chart building tick by tick; turnaround and waiting read off the same simulation. FCFS, SJF, SRTF, Round Robin, Priority |
| OS | Page replacement | Reference string, frame count | Which page is evicted and why. FIFO, LRU, Optimal, Clock. Change the frame count to find Belady's anomaly |
| OS | Disk scheduling | Queue, head position, direction | Total head movement as the head walks. FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK |
| OS | Banker's algorithm | Allocation, Maximum, Available | A safe sequence, or a proof that none exists with the stuck processes named |
| COA | Cache mapping | Cache size, block size, associativity, addresses | The address split into tag, index and offset in binary, then the block landing in its set |
| COA | Pipelining | Your own instruction sequence, forwarding on or off | Five stages, every stall with the register and producing instruction named |
| CN | Sliding window | Window size, frame count, which frames are lost | Go-Back-N against Selective Repeat under identical losses |
| CN | Subnetting and CIDR | Address, prefix, bits to borrow | The 32 bits cut at the prefix, then mask, network, broadcast, range and a subnet table |
| CN | TCP congestion control | Initial ssthresh, round trips, loss events | The cwnd sawtooth. Timeout against three duplicate ACKs, Tahoe against Reno |
| DBMS | B+ tree insertion | Keys, max keys per node | Leaf splits copy the separator up, internal splits push it up; each frame says which |
| DBMS | Conflict serializability | The schedule | Precedence graph built edge by edge, then cycle detection |
| DBMS | Normalisation | Relation and dependencies | Attribute closure step by step, candidate keys, then the highest normal form with the offending dependency named |
| DS | AVL rotations | Keys to insert | Every rebalance names the case (LL, RR, LR, RL) with balance factors on each node |
| DS | Hash tables | Table size, keys, method | Probe count and clustering. Chaining, linear, quadratic, double hashing |
| Algorithms | Sorting | Your own array | Comparisons and moves counted live. Bubble, selection, insertion, merge, quick |
| Algorithms | Dijkstra, Prim, Kruskal | The graph | Three greedy algorithms on the same graph, and why each choice is safe |
| TOC | Automaton simulation | Transition table, input string | DFA and NFA with a live state set: subset construction happening in front of you |
| CD | FIRST and FOLLOW | The grammar | Both sets as fixed points, one rule application per frame |
| CD | LL(1) parsing | Grammar and input | Parse table from FIRST/FOLLOW, then a stack trace. Conflicting cells are named, not just flagged |
| DL | Karnaugh map | Variables, minterms, don't-cares | Quine-McCluskey with an exhaustive minimal cover, essential prime implicants called out |
| Maths | Gaussian elimination | The matrix | Row reduction one operation at a time, then rank, nullity and determinant |

### Verified, not just written

Every one of these was checked against a textbook example before it shipped:

```
scheduling   Galvin SRTF example               -> WT 9, 1, 0, 2
paging       Galvin 20-reference string        -> FIFO 15, LRU 12, Optimal 9 faults
             Belady on 1 2 3 4 1 2 5 1 2 3 4 5 -> 9 faults at 3 frames, 10 at 4
disk         head 53, 200 cylinders, upward    -> FCFS 640, SSTF 236, SCAN 331,
                                                  C-SCAN 382, LOOK 299, C-LOOK 322
banker       Galvin 5-process example          -> safe, P1 P3 P0 P2 P4
cache        128 B / 16 B blocks / 2-way       -> tag 10, index 2, offset 4, 4 sets
pipeline     load-use with forwarding          -> exactly 1 stall; ALU-to-ALU 0;
                                                  forwarding off 2
window       one loss, window 4                -> GBN retransmits more than SR
subnet       192.168.10.130/24                 -> .0 / .255 / 254 usable
K-map        S(0,1,2,5,6,7,8,9,10,14)          -> A'BD + B'C' + CD'
             S(1,3,7,11,15) + d(0,2,5)         -> A'B' + CD
B+ tree      1..10 with max 3 keys             -> root [7], height 3, five leaves
serializable R1(A) W2(A) R2(B) W1(B)           -> cycle T1 -> T2 -> T1
AVL          all four insertion orders         -> root 20, height 2
hashing      50 700 76 85 92 73 101, m=7       -> [700,50,85,92,73,101,76], 13 probes
FIRST/FOLLOW expression grammar                -> FIRST(E)={( id}, FOLLOW(T)={+ ) $}
LL(1)        "id + id * id" accepted           -> S -> a S | a reports 1 conflict
normalise    R(ABCD), AB -> C, C -> D          -> key AB, highest form 2NF
graph        the sample weighted graph         -> MST 13 by both Prim and Kruskal
matrix       the 3x4 system                    -> rank 3, solution 2, 3, -1
```

### Adding your own

One file, one `register()` call:

```javascript
GG.viz.register('my-topic', {
  title: 'My topic',
  subtitle: 'One sentence on what this shows.',
  topic: 'syllabus-slug',              // wires up the "practise this" button
  inputs: [ /* fields the user can change */ ],
  build(values) { return frames; },    // each frame carries a caption
  draw(host, frame, values, i) { },    // paint one frame
});
```

The player shell handles the dialog, transport controls, the scrubber, keyboard
shortcuts, reduced motion, and the hand-off into practice. You write the
simulation and the drawing, nothing else.

---

## 3. Logging: two ways

Both exist because they solve different problems.

### Manual entry

The right tool for a session you have already finished. Subject, minutes, session
type, hour started, topics covered, whether to mark them done, and a note.
Optionally finishes with a short quiz on exactly the topics you ticked.

### The stopwatch

Press start before you begin. Pick a subject, tick topics off as you get through
them, and press **Stop and log** when you are done.

- The clock lives in memory, not in the dialog. Closing the dialog does not stop
  it.
- A pill in the topbar keeps the running time visible from anywhere in the app.
- The subject locks once the clock is running, so half an hour of algebra cannot
  be filed under operating systems by accident.
- Pause and resume freely.
- Under a minute is not logged.
- Closing the tab with a timer running asks for confirmation.

---

## 4. How it is built

### Design constraints, chosen deliberately

| Constraint | Why |
|---|---|
| Python standard library only | Runs on any machine with Python. No dependency rot in three years. |
| Vanilla JavaScript, no framework | No build step, no `node_modules`, no bundler to break. View source and read it. |
| SQLite, single file | Your whole history is one file you can copy, email, or back up. |
| No cloud, no network at runtime | Nothing to go down, nothing to leak, nothing to pay for. |
| Every number carries a reason | Prevents the app from becoming a dashboard you stop looking at. |
| ASCII glyphs only | The UI renders identically in every terminal, browser and font. |

Optional extras are needed only by specific tools, never by the app itself:

| Package | Needed for |
|---|---|
| `pillow` | `tools/make_icon.py`, generating the app icon |
| `pyinstaller` | `tools/build_exe.py`, building the executable |
| `pywebview` | A native window rather than a browser tab |
| `pystray` | The system tray icon |
| `playwright` | `tools/browsercheck.py`, the real-browser test |

### Architecture

```
                      +--------------------------+
   browser  <-------->|  core/api.py             |  55 HTTP routes
   (vanilla JS)       |  ThreadingHTTPServer     |  one /api/state payload
                      +------------+-------------+
                                   |
              +--------------------+--------------------+
              v                    v                    v
      +---------------+   +----------------+   +----------------+
      | core/stats.py |   | core/planner   |   | core/recommend |
      | ONE analytics |-->| builds today's |-->| ranked, with   |
      | pass          |   | plan           |   | reasons        |
      +-------+-------+   +----------------+   +-------+--------+
              |                                        |
              v                                        v
      +---------------+                       +----------------+
      | core/revision |                       | core/feedback  |
      | SM-2 schedule |                       | learned weights|
      +-------+-------+                       +-------+--------+
              |                                        |
              v                                        v
      +---------------+   +----------------+   +----------------+
      | core/quiz.py  |   | core/readiness |   | core/achieve.  |
      | selection +   |   | index + why it |   | badges +       |
      | GATE marking  |   | moved          |   | missions       |
      +-------+-------+   +----------------+   +----------------+
              |
              v
      +----------------------------------------------------------+
      | core/content.py   content registry: banks, topics,        |
      |                   aliases, review promotion, answers      |
      +----------------------------------------------------------+
      | core/db.py        schema v8, versioned migrations, health |
      +----------------------------------------------------------+
                    |                            |
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

**Slugs at the edges, ids inside.** The UI speaks in slugs like
`operating-systems` and `deadlock`; the engines speak in integer ids.
`core/api.py` translates at the boundary so neither side needs to know about the
other.

**Bank writes are always safe.** Every write to a question file is backed up to
`content/backups/` first, then written to a temp file and renamed. A crash
mid-write cannot truncate your bank; a bad import can be undone by restoring one
file.

**Read-only assets versus writable data.** `core/db.py` exposes `ASSET_DIR` (in
the bundle when packaged: `static/` and the shipped `content/`) and `APP_DIR`
(next to the executable: `data/` and your edited `content/`). Getting this wrong
is fatal in a packaged build, because PyInstaller unpacks into a temporary
directory that is deleted on exit, so the database would vanish every time you
closed the app. If the executable's own folder is not writable, the app falls
back to the per-user application data folder rather than failing silently.

**Single instance by design.** `HTTPServer` sets `allow_reuse_address = 1`, and
on Windows that flag means "let another process bind this port too" rather than
the Unix meaning of reusing a socket in `TIME_WAIT`. Turning it off makes the
bind itself the lock; a second launch detects the running copy over HTTP and asks
it to raise its window instead of starting a second server and a second tray
icon.

**No console, but never silent.** A windowed build has no `stdout`, so an
unguarded `print()` would raise on `None` before the app even started. Everything
goes through a `log()` helper that tees to `gitgrind.log` next to the database.

**The frontend is IIFE modules on a `GG` namespace.** Each file attaches one
object (`GG.render`, `GG.plan`, `GG.practice`, `GG.readiness`, `GG.bank`,
`GG.doubts`, `GG.timer`, `GG.viz`, `GG.app`) with shared helpers on `GG` itself.
No imports, no build, load order set by the `<script>` tags in `index.html`.

**Timing lives in exactly one place.** The intro animation is driven by a
`PHASES` table in `static/js/core.js`; CSS only describes what each phase looks
like, keyed off a `data-phase` attribute mirrored onto `<body>`. Changing the
intro length is one number.

---

## 5. What it contains

### Layout

```
app.py                    bootstrap, CLI, window launching, single-instance guard
demo_data.py              four synthetic profiles for demos and screenshots
gitgrind.spec             PyInstaller spec for hand-tuned builds
pyproject.toml            black, ruff and bandit configuration
run.bat / run.sh          development launchers only
README.md                 this file

core/                     the engines
  db.py                   schema, migrations, path resolution, health
  content.py              content registry: banks, topics, aliases, review
                          promotion, pending answers
  stats.py                the single analytics pass
  revision.py             spaced repetition, SM-2 variant
  quiz.py                 purpose-driven selection, grading, GATE marking
  planner.py              daily plan and practice-set builder
  recommend.py            ranked, explained recommendations
  readiness.py            index, decomposition, projections
  feedback.py             preference logging and weight updates
  achievements.py         45 badges across 5 tracks, live missions
  doubts.py               doubt log, prompt building, fenced LLM call
  api.py                  55 HTTP routes, the /api/state payload
  tray.py                 system tray presence

static/                   the UI
  index.html              the shell and every dialog
  css/style.css           design tokens, components, motion, accessibility
  js/core.js              helpers, prefs, shortcuts, focus trap, intro
  js/render.js            sidebar, subjects, calendar, feed, subject detail
  js/plan.js              command centre: next action, missions, plan,
                          revision queue, mastery map, recommendations
  js/practice.js          quiz runner, adaptive modes, confidence, mistakes
  js/readiness.js         index breakdown, movement, projection, weights
  js/bank.js              bank health, sources, imports, review, pending answers
  js/doubts.js            doubt desk
  js/timer.js             stopwatch logging
  js/app.js               boot, routing, session logging, settings
  js/viz/_player.js       the visualiser shell
  js/viz/*.js             21 topic simulators
  icon.ico / icon.png     generated app icon, matches the favicon

tools/                    the workshop
  ingest.py               ingestion backbone: sources, dedupe, manifests,
                          confidence scoring, review queue
  import_questions.py     paper and book parser
  extract_go_bank.py      bulk extraction, keeps unanswered questions
  answer_fill.py          fill pending answers from the terminal
  repair_bank.py          repair questions that bled into each other
  fetch_go_pdfs.py        release-asset downloader, sha256 verified
  selftest.py             46 end-to-end engine checks
  browsercheck.py         drives a real browser over every page
  build_exe.py            packaging
  build_installer.py      one command from source to installer
  make_icon.py            generate icon.ico from any square image

installer/
  gitgrind.iss            Inno Setup script
  after-install.txt       what the user sees when setup finishes

content/
  syllabus.json           12 subjects, 101 topics, exam weights
  targets.json            unofficial cutoffs; verify and edit
  topic_keywords.json     lexicon used to tag imported questions
  go_tag_map.json         source section names to syllabus slugs
  questions/              curated bank files
  banks/<name>/           imported banks, one folder per source
  banks/reviewed/         approved review items land here
  imports/                one manifest per import run
  backups/                pre-write .bak copies, 20 most recent

data/gitgrind.db          your entire history
papers/                   source PDFs and extracted text
```

### The database

27 tables. The ones you would actually look at:

| Table | Holds |
|---|---|
| `sessions` | Every study session: subject, minutes, kind, day, note |
| `attempts` | Every answer: correct, seconds, confidence, mistake kind, reattempt |
| `quizzes`, `quiz_questions` | Built sets and their contents, with purpose and reason |
| `topics` | Status, confidence, last revised: the coverage source of truth |
| `revision_queue` | The spacing schedule: ease, interval, due date, reps, lapses |
| `readiness_log` | A snapshot per reading, every component, for "why it moved" |
| `feedback`, `learned_weights` | Your ratings and the weights they produced |
| `daily_plans`, `dpp_sets` | Generated plans and the question sets behind blocks |
| `recommendations` | What was suggested, and what came of it |
| `question_sources`, `question_imports`, `question_review` | Bank provenance |
| `question_stats` | Per-question rollups used by the selector |
| `topic_alias`, `topic_prerequisites` | Topic normalisation and the topic graph |
| `doubts` | The doubt log, including whether it actually helped |
| `schema_meta`, `settings` | Schema version and your tunable preferences |

---

## 6. Running it

### Three stages

| Stage | Command | Use it when |
|---|---|---|
| Development | `python app.py` | You are editing code. Opens a browser tab. |
| Testing | `python app.py --window` | You want the real window without rebuilding |
| Daily use | The installed app | Every day. Own window, tray icon, no terminal. |

### Flags

```
python app.py --check              health report, then exit
python app.py --window             open in a plain app window, not a browser tab
python app.py --tray               keep running in the tray with no terminal
python app.py --no-tray            do not use the tray even in a packaged build
python app.py --no-browser         start the server, open nothing
python app.py --port 9000          different port
python app.py --host 0.0.0.0       bind wider (careful, there is no auth)
python app.py --demo disciplined   load a demo profile to see a populated UI
python app.py --demo patchy        gaps and inconsistency
python app.py --demo comeback      a long break then a return
python app.py --demo sprint        exam close, high intensity
python app.py --reset activity     wipe sessions and attempts, keep the syllabus
python app.py --reset all          wipe everything
python app.py --version
```

### Keyboard

Press `?` for the full list. It is generated from the registered shortcuts, so it
cannot go stale.

| Key | Action |
|---|---|
| `l` | Log a session |
| `s` | Start or open the session timer |
| `n` | Do the next action |
| `v` | Start the revision set that is due |
| `g` | Rebuild today's plan |
| `t` `s` `p` `r` `b` `a` `d` | Jump to Today, Subjects, Practice, Readiness, Bank, Activity, Doubts |
| `m` | Toggle reduced motion |
| `?` | Show the shortcut list |

Inside a visualiser: space plays and pauses, arrow keys step one frame.

Shortcuts are inert while you are typing in a field.

---

## 7. Your data and backups

Everything is in **one file**: `data/gitgrind.db`.

| What | Where |
|---|---|
| Sessions, attempts, quizzes, topics, revision schedule, feedback, plans | `data/gitgrind.db` |
| Syllabus, targets, lexicons | `content/*.json` |
| Question bank | `content/questions/`, `content/banks/` |
| Import manifests, pre-write backups | `content/imports/`, `content/backups/` |
| Source PDFs | `papers/` |
| Startup log, when there is no console | `gitgrind.log` |

### Backups, in order of how much to trust them

1. **Copy the file.** Close the app, copy `data/gitgrind.db` elsewhere. Complete
   and byte-for-byte exact. Do this weekly; it takes two seconds.
2. **Export from the app.** Activity -> *Export backup* writes a JSON dump of 25
   tables. Any API key is stripped on the way out.
3. **Import.** Activity -> *Import backup* reads that JSON back.

### What is stored about you

Your name, handle, bio, location, exam date and daily target: whatever you typed
into the profile dialog. Your sessions, answers, timings, self-rated confidence,
mistake tags, doubts, and your ratings of the app's suggestions.

None of it leaves the machine. The only outbound network calls the app can make
are ones you explicitly trigger: `tools/fetch_go_pdfs.py`, and the Doubt desk if
you configure a provider.

There is no analytics, no crash reporting, no update check, and no phone-home of
any kind.

---

## 8. Packaging into an executable

### One command

```
pip install pillow pyinstaller pywebview pystray
python tools/build_installer.py
```

That generates the icon, builds the application as a folder, and wraps it in an
Inno Setup installer. Output lands in `installer/Output/`.

### Or step by step

```
python tools/make_icon.py --from-image app_icon.png    icon from any square image
python tools/build_exe.py --clean --onedir             the application
iscc installer/gitgrind.iss                            the installer
```

| Flag | Effect |
|---|---|
| `--clean` | Wipe `build/` and `dist/` first. Use it whenever you changed the UI. |
| `--onedir` | A folder instead of one file; starts noticeably faster |
| `--console` | Keep the terminal window, useful while debugging a build |
| `--stage` | Copy your existing database next to the built executable |
| `--nuitka` | Compile rather than bundle; needs a C compiler, fastest binary |

### Result

```
dist/GitGrind/
  GitGrind.exe          the app
  _internal/            bundled runtime, static/ and content/
  data/gitgrind.db      created on first run
  content/              unpacked beside the executable on first run
```

`static/` and `content/` are bundled inside, so the packaged app needs no network
and no CDN. `data/` is deliberately **not** bundled, and on first run the app
copies `content/` out beside the executable so bank files stay writable.
Otherwise logging an answer would vanish every time you closed the app.

### Important

**The UI and Python code are baked into the executable at build time.** Editing
files on disk changes only the source tree. Any change to `static/` or `*.py`
needs a rebuild with `--clean`. `content/` is the exception: it lives beside the
executable and is editable.

Develop with `python app.py --window`. Build only when the work is finished.

---

## 9. Diagnosing problems

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

46 checks against a temporary database: schema, migrations, content registry,
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
| **Panels blank but no error** | A render function was never called, or threw before reaching them | Open the browser console and run `GG.plan.paint(GG.S.state)`. If that works, the router is not calling it: check the `paint()` dispatch in `static/js/app.js`. |
| **A panel shows "--" where a number should be** | Field-name mismatch between engine and UI | In the console, inspect `GG.S.state.readiness` or the relevant key and compare with what the JS reads. The single most common frontend bug. |
| **Everything blank, console shows `Cannot read properties of undefined`** | JS threw mid-render, so everything after it is skipped | The stack trace names the file and line. Guard with `Number(x \|\| 0)` or `(x \|\| {})`. |
| **Changes to the UI have no effect** | Browser cache, or a stale executable | `Ctrl+Shift+R`. If it is the exe, rebuild with `--clean` and delete `dist/data/uiprofile`. |
| **`Could not bind ...: address already in use`** | Another copy is running, or the port is taken | `python app.py --port 9000` |
| **Two tray icons** | Two servers bound the same port | Fixed by disabling address reuse on Windows. If it returns, check `SingleInstanceServer` in `app.py`. |
| **Bank health suddenly low** | An import added questions with no answer or no options | Bank tab, or `python tools/ingest.py --gaps`. `pending` is normal and expected; `broken` is the number that matters. |
| **Quiz says "no questions available"** | The purpose filter found nothing, usually a topic with only pending questions | Check the mastery map for that topic's bank count. Fill in answers, or widen the selection. |
| **Revision queue empty on an old database** | The schedule was never backfilled | It backfills on init. Force it: `python -c "from core import db,revision; c=db.init(); print(revision.sync_from_activity(c))"` |
| **A migration failed** | Usually a hand-edited database | Restore your backup, then `python app.py --check` to see the version it stopped at. Migrations are ordered and idempotent; they can be re-run safely. |
| **Import wrecked a bank file** | A bad parse got written | Copy the matching `.bak` from `content/backups/` over the original, then **Reload from disk**. |
| **Executable loses its data every run** | `core/db.py` path resolution is wrong | It must define `ASSET_DIR` and `APP_DIR` separately. Verify with `python -c "from core import db; print(db.ASSET_DIR, db.APP_DIR)"` |
| **Taskbar shows the browser icon** | The window is owned by the browser process | Install `pywebview` so the window belongs to GitGrind instead. |
| **Exe icon did not change** | Windows icon cache | `ie4uinit.exe -show` |
| **Intro never goes away** | JS threw before the first paint | It self-dismisses on a timer regardless. If the app is still hidden, `document.body.className` shows `booting` and the console has the real error. |
| **Nothing on screen and no terminal** | A windowed build has no console | Read `gitgrind.log` next to the database. |
| **Readiness index looks wrong** | Small sample | Check `estimate_confidence` on the Readiness page. With few attempts the index deliberately pulls toward neutral and says so. |

### Useful console probes

```javascript
GG.S.state                      // the entire payload the server sent
Object.keys(GG.S.state)         // every top-level key
GG.S.state.plan.blocks          // today's plan blocks
GG.S.state.debt                 // revision pressure
GG.S.state.feedback.learned     // what the app has learnt from you
GG.viz.list()                   // every registered visualiser
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

---

## 10. The question bank

### Where questions come from

Layered, in order of preference:

1. **Official GATE papers** you supply as PDF or text.
2. **Public question compilations** distributed as release assets.
   `tools/fetch_go_pdfs.py` pulls them through the API. It does not scrape web
   pages and it will not.
3. **Your own curated questions** in the JSON schema below.
4. **Generated practice sets** assembled from the above.

### Three-stage ingestion

Nothing enters practice without passing all three stages.

```
    fetch                parse and normalise              review
  ----------           ---------------------          --------------
  release assets  ->   text extraction, topic    ->   a human approves
  or your own PDF      tagging, answer-key             each low-confidence
                       matching, confidence            item in the Bank tab
                       scoring, dedupe
```

**Stage 1: fetch**

```
python tools/fetch_go_pdfs.py --list
python tools/fetch_go_pdfs.py --tag <tag> --only vol1 --extract
python tools/fetch_go_pdfs.py --index-only --tag <tag>   # metadata, no download
python tools/fetch_go_pdfs.py --verify                   # re-check every sha256
python tools/fetch_go_pdfs.py --manifest                 # what is on disk
```

Downloads resume, sizes are checked, and a sha256 lands in
`papers/manifest.json`, verified against the published digest when there is one.
`--verify` later tells you whether a file changed under you.

**Stage 2: parse and normalise**

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

Safety, because a bad import must never cost you a working bank:

- Target files are backed up to `content/backups/` before being touched
- Writes go to a temp file and are then renamed, so a crash cannot truncate JSON
- Exact duplicates are dropped; near-duplicates above 0.86 token-shingle
  similarity are kept but flagged
- Anything below the confidence floor goes to review even if it classified

**Stage 3: review**

Low-confidence questions land in the Bank tab's review queue. Approving copies
the question into `content/banks/reviewed/<subject>.json` and it goes live.
Rejecting leaves it out. Either way the raw imported file is never edited.

From the terminal:

```
python tools/ingest.py --review
python tools/ingest.py --approve 12
python tools/ingest.py --reject 12 --note "bad OCR, figure missing"
```

### Bulk extraction

`tools/extract_go_bank.py` takes the opposite position from the importer on
purpose: **keep everything.** A question with no printed answer is still worth
having, because you can look the answer up once and then it is yours forever.

```
python tools/extract_go_bank.py --dry-run     report only
python tools/extract_go_bank.py               write the bank
```

Questions with no answer are written with:

```json
"answer_pending": true,
"answer": null,
"answer_note": "Answer not printed in the source. Look it up online, then log it from the Bank tab."
```

An `answer_pending` question is **present but not gradable**: it counts towards
coverage, it is listed in the Bank tab so you can fill it in, and the quiz
selector will never serve it. Verified: all six selection purposes leak zero
pending questions.

### Repairing a bad extraction

`tools/repair_bank.py` fixes questions that bled into each other. The classic
symptom is option D containing an entire second question.

```
python tools/repair_bank.py --dry-run
python tools/repair_bank.py
```

Section numbering is treated as a hard question boundary, merged option blocks
are discarded, and anything left unservable is demoted to `answer_pending` rather
than silently shipped as a broken question.

### Filling in pending answers

Bank tab -> **Answers to look up**. Each row has a one-click search that opens the
question text in a web search. Find the answer, type `B`, or `B,D`, or a numeric
value for NAT, and press Save. It is written straight into the bank file, backed
up first, and the question becomes gradable permanently. No re-import needed.

Questions marked `needs_options` also lost their option list to text extraction;
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

- `type` is `mcq`, `msq` or `nat`. For `nat`, drop `options` and `answer` and
  give `answer_value`, plus optional `answer_low` and `answer_high` for a range.
- `topic` must be a slug from `content/syllabus.json`. Unrecognised topics are
  reported, never silently guessed.
- Restart, or press **Reload from disk** in the Bank tab.

Validate before trusting it:

```
python tools/import_questions.py --validate content/questions/my-file.json
```

---

## 11. Accessibility and motion

- Every state indicator carries a glyph as well as a colour (`!` critical,
  `~` weak, `+` ok, `#` strong) so nothing is communicated by hue alone. The
  mastery map prints the glyph inside each cell.
- Full keyboard operation. `?` lists every shortcut, generated from the registry,
  so it cannot drift out of date.
- Dialogs trap Tab and return focus where it came from on close.
- Route changes move focus into the new view rather than leaving it on the nav.
- Toasts are announced through an `aria-live` region.
- `prefers-reduced-motion` is honoured, plus an in-app **Reduced motion** setting
  for when the operating system setting is not what you want here. Either one
  strips every transition, the staggered entrance, and the intro animation.
- Visible focus rings everywhere, with a skip link to the main content.
- The intro can always be skipped: a button, or Escape, Enter or Space.

---

## 12. Where to change things

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
| Add a concept visualiser | one file in `static/js/viz/`, plus a `<script>` tag |
| Change colours, spacing, or motion | the `:root` tokens at the top of `static/css/style.css` |
| Change the intro timing | the `PHASES` table in `static/js/core.js` |
| Change the app icon | `python tools/make_icon.py --from-image your.png` |
| Add a keyboard shortcut | `registerShortcuts()` in `static/js/app.js`; the help dialog updates itself |
| Add a user-tunable setting | `TUNABLE` in `core/api.py`, defaults in `core/content.py`, copy in `SETTING_COPY` in `static/js/app.js` |
| Add a database table or column | append to `MIGRATIONS` in `core/db.py` and bump `SCHEMA_VERSION`; never edit the base `SCHEMA` alone, or existing databases will not get it |

### House rules if you extend it

1. **Every number needs a reason string.** If you cannot write the sentence
   explaining what to do about a metric, do not put it on screen.
2. **New engine data goes through `stats.gather()`**, not a second query pass.
3. **Schema changes go in `MIGRATIONS`.** Editing `SCHEMA` alone breaks every
   existing database.
4. **Bank writes back up first, then write atomically.** Copy the pattern in
   `content.set_answer()`.
5. **Never let a rating failure block a study action.** Feedback calls are
   wrapped in try/except for a reason, and each one carries a comment saying why.
6. **ASCII glyphs only.** No emoji.
7. **Run `selftest.py` and `browsercheck.py` before you trust a change.** The
   Python tests cannot see frontend bugs, and the browser check cannot see engine
   bugs. You need both.

### Code quality

```
ruff check .
black .
bandit -r . -c pyproject.toml
python tools/selftest.py
```

Configuration lives in `pyproject.toml`, with a comment against every suppressed
rule explaining why it is suppressed. Current state: bandit reports zero issues,
selftest passes 46 of 46.

---

## 13. Roadmap

Ordered by value for effort, honestly assessed.

### High value, low effort

- **Finish the pending answers.** 2,991 questions are one lookup each from being
  gradable. By far the highest-value thing left, and it needs no code at all.
  Twenty a day makes the bank properly usable in five months.
- **Match answer keys automatically.** Official keys exist for every GATE year.
  A better key matcher could clear a large fraction without human lookup.
- **Fill the last empty topic.** `computer-organization/secondary-storage` has no
  questions. Five written by hand would close it.
- **Per-topic time budgeting.** The planner already knows exam weights and your
  accuracy. It could say how many hours a topic *deserves*, not only what to do
  next.

### Medium effort, real payoff

- **Mock test mode.** A full 65-question, 180-minute paper with GATE marking,
  section timing, and a post-mortem feeding the same analytics. The marking rules
  already exist; what is missing is the timed shell and the report.
- **Figure support.** Several hundred questions reference a diagram that text
  extraction dropped. Cropping the page region and storing it as an image would
  recover them properly. A caption is not a substitute for a circuit.
- **Prerequisite-aware planning.** `topic_prerequisites` is populated but barely
  used. The planner could refuse to schedule a topic whose prerequisites are
  weak, which is how a human tutor sequences things.
- **Formula and note cards.** A revision surface for definitions and formulas on
  the same SM-2 engine. Cheap, because the engine is generic.
- **Error-log review.** A dedicated screen for every question you ever got wrong,
  grouped by mistake category, with the pattern spelled out.
- **Mobile layout.** The CSS is responsive but designed for a desktop HUD. A
  phone-first review mode, just the revision queue and today's plan, would make
  dead time useful.
- **Multi-exam support.** The schema is not GATE-specific. A second exam profile
  mostly means another syllabus file and target file.

### Larger projects

- **Layout-aware extraction with a vision model.** Crop figures and tables as
  images rather than mangling them into text, then have a model transcribe only
  what it can read reliably, with a refusal option and a confidence tier written
  into the schema.
- **Spaced repetition for subjective material.** Long-answer and derivation
  practice with self-grading rubrics, which a binary correct/wrong model cannot
  represent.
- **Adaptive difficulty from item response theory.** The current difficulty dial
  is a heuristic. A two-parameter IRT model over your attempt history would
  estimate question difficulty and your ability jointly.
- **Handwriting capture.** Photograph your rough work and attach it to the
  attempt, making the mistake taxonomy far more useful on review.

### Deliberately not planned

- **Cloud sync.** The one-file-on-your-disk property is the reason you can trust
  this app. Sync means accounts, a server, and a privacy policy.
- **A recommendation LLM.** The rules engine is inspectable and cannot
  hallucinate a study plan. The LLM stays fenced to explaining concepts.
- **Streak pressure and notifications.** Guilt mechanics are how study apps get
  uninstalled in March.

---

## 14. Honest limitations

Read this before trusting any number.

- **Only 606 of 3,597 questions are gradable right now.** 2,991 are waiting on
  answers you must look up, and 1,894 of those also lost their options to text
  extraction. Topic coverage reads 99%, but *gradable* coverage is much lower.
  Filling those in is the single biggest thing left to do.
- **Cohort numbers are simulated.** Percentiles come from a fixed-seed local
  model, not from real students.
- **Cutoffs are unofficial.** `content/targets.json` needs verifying against the
  actual notification for your year.
- **The readiness index is a heuristic, not a predictor.** It has never been
  validated against real GATE results, because it cannot be. Treat it as a
  consistency measure, "is this going up?", not as a score forecast.
- **The feedback loop is preference learning, not RLHF.** It re-ranks advice. It
  does not learn what makes you learn.
- **Several hundred questions reference figures** that are not in the extracted
  text. They are flagged, not hidden.
- **There is no authentication.** Do not run it on `--host 0.0.0.0` on a shared
  network.
- **The frontend has no automated unit tests.** `browsercheck.py` catches thrown
  errors and blank pages; it does not verify that a number is correct.
- **The installer is not code-signed.** SmartScreen will warn on first run.

This section exists because an app that reports a number it cannot justify is
worse than one that reports nothing. If any of the above stops being true, the
list gets shorter, not quieter.

---

## 15. Licence and credits

The code in this repository is MIT licensed. See [LICENSE.txt](LICENSE.txt).

**The licence covers the source code only.** It does not cover exam questions,
answer keys or explanations placed in `content/` by you or by anyone else.
Previous-year GATE questions remain the property of their respective copyright
holders, and material compiled by third parties remains subject to whatever terms
those projects set. If you redistribute this software, ship it with your own
content, or with content you have the right to share.

Built with Python's standard library, SQLite, and no JavaScript framework at all.

---

<div align="center">

**[Download the latest release](https://github.com/eeshan15/GitGrind/releases/latest)**

`python app.py --check` -- if something looks wrong, that is the first thing to run.

</div>
