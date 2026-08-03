## Install

Download **GitGrind-Setup-1.0.exe**, run it, done. No Python, no dependencies,
no account. Windows 8.1 or newer, 64-bit.

Windows will say "Windows protected your PC" because the installer is not
code-signed. More info -> Run anyway. The source is right here if you would
rather build it yourself:

    python tools/build_installer.py

## What it is

A local, offline operating system for a GATE CSE attempt. Not a study-hours
tracker with charts. Every screen answers one question: what should I do in the
next hour, and why that one?

- **Spaced repetition** that treats confidently-wrong as the worst outcome,
  because that is the state you will never revise voluntarily
- **A readiness index that explains itself** - where each point came from, why it
  moved since last time, and which single topic is the cheapest to fix
- **21 interactive visualisers** for CPU scheduling, paging, cache mapping,
  pipelining, B+ trees, K-maps, automata, LL(1) parsing and more. Type your own
  numbers in; they double as a way to check your answer to a paper question
- **Two ways to log**: fill in a session afterwards, or start a stopwatch before
  you begin
- **Lives in the system tray.** Close the window, the streak keeps running

## Your data

One SQLite file next to the executable. Nothing leaves your machine, ever. Copy
`data/gitgrind.db` to back up your entire history.

## Honest limitations

- The bundled bank ships with a curated set. Build your own from PDFs you already
  have with `python tools/extract_go_bank.py`
- Cohort percentiles are a local simulation from a fixed seed, not real students.
  The app says so on the page itself
- Cutoffs in `content/targets.json` are unofficial. Verify them and edit the file
- The readiness index is a heuristic, never validated against real results. Treat
  it as "is this going up?", not as a score prediction

## Requirements

Windows 8.1+, 64-bit. That is the whole list.