#!/usr/bin/env python3
"""Apply the lion splash animation, fix the favicon wiring, and register the
Inno Setup path.

Three separate problems, one command, safe to run twice:

1. **Favicon left-over.** An earlier version of ``tools/make_icon.py`` replaced
   the favicon with a regex that stopped at the first ``>``. Because the old
   favicon was an inline SVG data URI, the rest of that SVG was stranded in
   ``<head>`` as loose markup. This removes it.

2. **The splash animation was never installed.** ``static/index.html`` needs the
   lion markup, ``style.css`` needs the phase-keyed rules, and ``core.js`` needs
   the four-phase table. Without all three the animation silently does nothing.

3. **Inno Setup installed per-user.** winget puts ISCC.exe under
   ``%LOCALAPPDATA%\\Programs``, which ``tools/build_installer.py`` did not look
   in, so it reported Inno Setup as missing.

Every file it edits is backed up beside itself as ``<name>.prelion.bak``.

    python patch_lion.py            apply
    python patch_lion.py --check    report only
"""

import argparse
import os
import re
import shutil
import sys

SPLASH_HTML = r"""<div class="splash" id="splash" data-phase="icon" role="status"
     aria-label="GitGrind is starting">
  <button class="splash-skip" id="splashSkip" type="button">Skip</button>

  <div class="splash-stage">
    <!-- the crest arrives first -->
    <div class="splash-icon"><img src="/icon.png" alt="" draggable="false"></div>

    <!-- shockwaves thrown by the roar -->
    <i class="roar-ring r1"></i><i class="roar-ring r2"></i><i class="roar-ring r3"></i>

    <!-- the lion, drawn as vector artwork so it holds up at any size -->
    <div class="lion">
    <svg class="lion-art-svg" viewBox="0 0 220 260" xmlns="http://www.w3.org/2000/svg">
     <defs>
      <linearGradient id="furG" x1="0" y1="0" x2="0" y2="1">
       <stop offset="0" stop-color="#f7dd8f"/><stop offset="46%" stop-color="#e0b94a"/>
       <stop offset="100%" stop-color="#9a6f16"/>
      </linearGradient>
      <linearGradient id="maneG" x1="0" y1="0" x2="1" y2="1">
       <stop offset="0" stop-color="#ffe9a8"/><stop offset="55%" stop-color="#d8ad3b"/>
       <stop offset="100%" stop-color="#8d6512"/>
      </linearGradient>
     </defs>
     <g class="lion-art" fill="url(#furG)" stroke="#5c400c" stroke-width="2.4"
        stroke-linejoin="round" stroke-linecap="round">
    
      <!-- tail, sweeping up and over with a tuft -->
      <path class="tail" d="M158 128 C186 116 200 82 182 62 C172 50 156 54 152 66
           C149 76 156 84 164 82 C158 92 166 100 172 96 C166 110 160 118 152 122 Z"/>
    
      <!-- hind leg, planted -->
      <path d="M136 132 C146 156 148 186 142 212 C140 222 132 228 124 226
           C118 224 116 216 120 208 C126 194 128 168 122 148 Z"/>
      <path class="paw" d="M124 226 C132 228 142 230 146 236 C148 241 142 244 134 243
           L120 240 C116 236 118 229 124 226 Z"/>
    
      <!-- body -->
      <path class="body" d="M84 96 C110 92 136 104 144 128 C150 150 148 178 140 200
           C132 216 116 224 100 220 C86 216 78 202 80 186 C84 160 80 126 84 96 Z"/>
    
      <!-- standing foreleg -->
      <path d="M96 140 C100 166 98 192 92 212 C90 220 82 224 76 220
           C70 216 70 208 74 200 C80 184 82 162 80 144 Z"/>
      <path class="paw" d="M76 220 C84 222 92 226 95 232 C97 237 90 240 82 238
           L70 234 C66 230 70 222 76 220 Z"/>
    
      <!-- raised foreleg, reaching forward -->
      <path class="arm" d="M86 108 C70 112 52 106 40 92 C32 82 34 70 44 68
           C52 66 58 74 66 80 C74 86 82 90 90 90 Z"/>
      <path class="claw" d="M44 68 C36 64 26 62 20 66 C15 69 17 76 24 78
           L38 82 C44 80 48 72 44 68 Z"/>
    
      <!-- chest -->
      <path d="M84 96 C76 112 74 134 80 152 C72 140 70 116 76 100 Z" fill="#f3cf71"
            stroke="none" opacity=".55"/>
    
      <!-- mane: eight locks radiating around the head -->
      <g class="mane" fill="url(#maneG)">
       <path d="M96 44 C104 22 92 6 74 8 C82 18 82 32 76 42 Z"/>
       <path d="M76 42 C56 30 38 38 36 56 C48 50 62 52 70 58 Z"/>
       <path d="M70 58 C48 62 38 78 46 94 C54 84 66 78 76 78 Z"/>
       <path d="M76 78 C62 96 66 114 84 118 C80 106 84 94 90 88 Z"/>
       <path d="M96 44 C112 26 132 28 138 44 C126 42 112 48 106 56 Z"/>
       <path d="M106 56 C128 54 142 68 138 86 C130 74 116 70 106 72 Z"/>
       <path d="M106 72 C124 82 126 102 112 112 C112 100 106 90 98 86 Z"/>
      </g>
    
      <!-- head -->
      <path class="head" d="M92 46 C112 46 124 60 122 78 C120 96 106 108 90 106
           C74 104 64 90 66 72 C68 56 78 46 92 46 Z"/>
    
      <!-- brows, eyes, nose -->
      <path class="brow" d="M76 68 C82 62 90 63 94 68" fill="none" stroke="#5c400c"
            stroke-width="3.4"/>
      <path class="brow" d="M114 68 C108 62 100 63 96 68" fill="none" stroke="#5c400c"
            stroke-width="3.4"/>
      <ellipse class="eye" cx="82" cy="75" rx="4.2" ry="4.8" fill="#3a1d07" stroke="none"/>
      <ellipse class="eye" cx="106" cy="75" rx="4.2" ry="4.8" fill="#3a1d07" stroke="none"/>
      <path class="snout" d="M94 84 L100 91 L88 91 Z" fill="#f7e3a0" stroke="none"/>
    
      <!-- jaw: the part that opens on the roar -->
      <g class="jaw">
       <path d="M78 94 C86 90 102 90 110 94 C112 106 104 116 94 116
            C84 116 76 106 78 94 Z" fill="#3a1d07" stroke="#5c400c" stroke-width="2"/>
       <path d="M83 96 L87 106 L79 100 Z" fill="#fff" stroke="none"/>
       <path d="M105 96 L109 100 L101 106 Z" fill="#fff" stroke="none"/>
       <path class="tongue" d="M90 106 C94 104 99 106 99 111 C99 116 94 118 90 115 Z"
             fill="#c0473f" stroke="none"/>
      </g>
     </g>
    </svg>
    </div>

    <!-- the wash that carries the gold outward into the app's own palette -->
    <i class="blend-bloom"></i>
  </div>

  <div class="splash-name">GitGrind</div>
  <div class="splash-tag">One session a day. Everything else follows.</div>
  <div class="splash-load">LOADING</div>
</div>"""

SPLASH_CSS = r"""/* ==========================================================================
   welcome splash - crest, roar, blend, open

   core.js flips data-phase on #splash and mirrors it onto <body>, so timing
   lives in exactly one place (the PHASES table) and CSS only describes what each
   phase looks like.

     icon   1.1s   the crest arrives and settles
     roar   1.7s   the lion climbs out of the crest and roars
     blend  1.2s   gold bleeds outward and washes toward the app's palette
     open   1.0s   lion and crest dissolve, the app rises behind them
                   -------
                   5.0s

   Skip button, plus Escape / Enter / Space. Reduced motion goes straight to the
   app with no theatre at all.
   ========================================================================== */
.splash{position:fixed;inset:0;z-index:300;display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  background:radial-gradient(circle at 50% 44%,rgba(30,38,54,1) 0%,
    rgba(11,15,22,1) 62%,rgba(7,10,16,1) 100%);
  opacity:1;transition:opacity 700ms var(--ease),transform 700ms var(--ease)}
.splash.gone{opacity:0;transform:scale(1.05);pointer-events:none}

.splash-skip{position:absolute;top:22px;right:22px;background:transparent;
  border:1px solid rgba(216,173,59,.35);color:rgba(230,237,243,.7);
  font:600 11px/1 var(--sans);letter-spacing:.14em;text-transform:uppercase;
  padding:8px 14px;border-radius:999px;cursor:pointer;
  transition:all var(--hover) var(--ease)}
.splash-skip:hover{border-color:var(--gold);color:var(--fg)}

.splash-stage{position:relative;width:300px;height:300px;display:flex;
  align-items:center;justify-content:center}

/* ---------------------------------------------------------------- crest --- */
.splash-icon{position:absolute;width:212px;height:212px;border-radius:34px;
  overflow:hidden;background:var(--bg);border:2px solid rgba(216,173,59,.9);
  box-shadow:0 0 40px rgba(216,173,59,.30),inset 0 0 22px rgba(255,255,255,.04);
  opacity:0;transform:scale(.62) rotate(-6deg);
  transition:opacity 760ms var(--ease),transform 760ms var(--ease),
             filter 700ms var(--ease)}
.splash-icon img{width:100%;height:100%;object-fit:cover;display:block}

.splash[data-phase=icon] .splash-icon{opacity:1;transform:none;
  animation:icon-settle 1100ms var(--ease) both}
/* during the roar the crest sits behind, dimmed, as the lion's origin */
.splash[data-phase=roar] .splash-icon{opacity:.55;transform:scale(.86);
  filter:saturate(.6) brightness(.8)}
.splash[data-phase=blend] .splash-icon{opacity:.9;transform:scale(1.02);
  filter:saturate(1.25) brightness(1.15)}
.splash[data-phase=open] .splash-icon{opacity:0;transform:scale(1.5);
  filter:blur(8px) brightness(1.4)}

/* ----------------------------------------------------------------- lion --- */
/* The lion starts hidden inside the crest, climbs out, roars, then dissolves
   into the blend. Scale and origin are what sell "it came out of the icon". */
.lion{position:absolute;width:250px;height:295px;
  transform-origin:50% 78%;
  opacity:0;transform:scale(.28) translateY(26px);
  transition:opacity 620ms var(--ease),transform 760ms var(--ease),
             filter 620ms var(--ease)}
.lion-art-svg{width:100%;height:100%;display:block;
  filter:drop-shadow(0 10px 26px rgba(0,0,0,.55))}

.splash[data-phase=roar] .lion{opacity:1;transform:none;
  animation:lion-emerge 760ms var(--ease) both,
            lion-shake 300ms var(--ease) 760ms 3 alternate}
.splash[data-phase=blend] .lion{opacity:1;transform:scale(1.06);
  filter:brightness(1.5) saturate(1.4)}
.splash[data-phase=open] .lion{opacity:0;transform:scale(1.35);
  filter:blur(10px) brightness(2)}

/* jaw, mane and tail only animate while roaring */
.splash[data-phase=roar] .lion-art .jaw{transform-origin:94px 92px;
  animation:jaw-roar 380ms var(--ease) 700ms 3 alternate}
.splash[data-phase=roar] .lion-art .mane{transform-origin:94px 76px;
  animation:mane-flare 420ms var(--ease) 700ms 3 alternate}
.splash[data-phase=roar] .lion-art .tail{transform-origin:152px 122px;
  animation:tail-flick 620ms var(--ease) 700ms 2 alternate}
.splash[data-phase=roar] .lion-art .tongue{
  animation:tongue-out 380ms var(--ease) 720ms 3 alternate}

/* ----------------------------------------------------------- shockwaves --- */
.roar-ring{position:absolute;width:150px;height:150px;border-radius:50%;
  border:2px solid rgba(216,173,59,.30);opacity:0}
.splash[data-phase=roar] .roar-ring{animation:roar-out 1000ms var(--ease) 700ms 2}
.splash[data-phase=roar] .roar-ring.r2{animation-delay:880ms}
.splash[data-phase=roar] .roar-ring.r3{animation-delay:1060ms}

/* ---------------------------------------------------------------- blend --- */
/* One bloom that grows from the lion's chest out past the edges of the screen,
   shifting gold into the app's own surface colour on the way. */
.blend-bloom{position:absolute;width:120px;height:120px;border-radius:50%;
  background:radial-gradient(circle,rgba(247,221,143,.95) 0%,
    rgba(216,173,59,.55) 38%,rgba(46,160,67,.22) 62%,rgba(13,17,23,0) 78%);
  opacity:0;transform:scale(.3);pointer-events:none}
.splash[data-phase=blend] .blend-bloom{animation:bloom-out 1200ms var(--ease) both}
.splash[data-phase=open] .blend-bloom{animation:bloom-fade 900ms var(--ease) both}

/* the splash background itself settles onto the app canvas colour */
.splash[data-phase=blend]{background:radial-gradient(circle at 50% 44%,
  rgba(46,80,60,1) 0%,rgba(13,17,23,1) 60%,rgba(7,10,16,1) 100%)}
.splash[data-phase=open]{background:radial-gradient(circle at 50% 44%,
  rgba(22,27,34,1) 0%,rgba(13,17,23,1) 55%,rgba(13,17,23,1) 100%)}

/* ----------------------------------------------------------------- text --- */
.splash-name{font-size:32px;font-weight:700;letter-spacing:-.03em;
  margin-top:var(--s5);opacity:0;transform:translateY(9px);
  transition:opacity 560ms var(--ease),transform 560ms var(--ease)}
.splash-tag{color:var(--dim);font-size:13px;margin-top:8px;opacity:0;
  transform:translateY(9px);
  transition:opacity 560ms var(--ease) 120ms,transform 560ms var(--ease) 120ms}
.splash[data-phase=icon] .splash-name,.splash[data-phase=icon] .splash-tag,
.splash[data-phase=blend] .splash-name,.splash[data-phase=blend] .splash-tag{
  opacity:1;transform:none}
.splash[data-phase=open] .splash-name,.splash[data-phase=open] .splash-tag{opacity:0}
.splash-load{position:absolute;bottom:46px;font:600 11px/1 var(--sans);
  letter-spacing:.35em;color:rgba(230,237,243,.65);
  animation:load-pulse 1200ms var(--ease) infinite}

/* --------------------------------------------------------------- frames --- */
@keyframes icon-settle{
  0%{opacity:0;transform:scale(.62) rotate(-6deg)}
  62%{opacity:1;transform:scale(1.05) rotate(2deg)}
  100%{opacity:1;transform:none}
}
@keyframes lion-emerge{
  0%{opacity:0;transform:scale(.30) translateY(30px)}
  45%{opacity:1;transform:scale(1.10) translateY(-8px)}
  75%{transform:scale(.97) translateY(2px)}
  100%{opacity:1;transform:none}
}
@keyframes lion-shake{
  0%{transform:rotate(-1.4deg) scale(1)}
  100%{transform:rotate(1.4deg) scale(1.035)}
}
@keyframes jaw-roar{0%{transform:scale(1,1)}100%{transform:scale(1.18,1.62)}}
@keyframes mane-flare{0%{transform:scale(1)}100%{transform:scale(1.13)}}
@keyframes tail-flick{0%{transform:rotate(-5deg)}100%{transform:rotate(7deg)}}
@keyframes tongue-out{0%{transform:translateY(0)}100%{transform:translateY(5px) scaleY(1.3)}}
@keyframes roar-out{
  0%{opacity:0;transform:scale(.35)}
  30%{opacity:.65}
  100%{opacity:0;transform:scale(2.7)}
}
@keyframes bloom-out{
  0%{opacity:0;transform:scale(.3)}
  25%{opacity:1}
  100%{opacity:.85;transform:scale(11)}
}
@keyframes bloom-fade{0%{opacity:.85;transform:scale(11)}100%{opacity:0;transform:scale(15)}}
@keyframes load-pulse{0%,100%{opacity:.35}50%{opacity:1}}

/* ------------------------------------------------------- handover to app --- */
/* The shell starts arriving during the blend, so the colour wash reveals a live
   app rather than cutting to it. */
body.booting .topbar,body.booting .shell{opacity:0;
  transition:opacity 900ms var(--ease)}
body[data-splash-phase=blend] .topbar,
body[data-splash-phase=blend] .shell{opacity:.35}
body[data-splash-phase=open] .topbar,
body[data-splash-phase=open] .shell{opacity:1}
body.booted .topbar,body.booted .shell{opacity:1;
  transition:opacity 460ms var(--ease) 60ms}

/* reduced motion: no theatre at all */
body.reduced-motion .splash{transition:none}
body.reduced-motion .splash *{animation:none !important;transition:none !important}
body.reduced-motion .lion,body.reduced-motion .roar-ring,
body.reduced-motion .blend-bloom{display:none}
body.reduced-motion .splash-icon{opacity:1;transform:none}
body.reduced-motion .splash-name,body.reduced-motion .splash-tag{opacity:1;transform:none}
body.reduced-motion.booting .topbar,body.reduced-motion.booting .shell{opacity:1}
body.reduced-motion.booted .topbar,body.reduced-motion.booted .shell{transition:none}

/* The topbar mark is the app icon itself, so the header, the browser tab,
   the taskbar and the splash can never drift apart. */
.brand-mark{width:26px;height:26px;border-radius:7px;display:block;flex:none;
  box-shadow:0 0 0 1px rgba(216,173,59,.35)}
"""

PHASES = r"""  const PHASES = [
    ['icon',  1100],   /* the crest arrives first and settles                */
    ['roar',  1700],   /* the lion climbs out of it and roars                */
    ['blend', 1200],   /* gold bleeds outward and washes toward the app       */
    ['open',  1000],   /* lion and crest dissolve, the app rises behind them  */
  ];"""

RUNPHASES = r"""  function runPhases() {
    const node = $('#splash');
    if (!node) return;
    /* Mirrored onto <body> as well, because the app shell is a sibling of the
       splash and needs to start fading in during the blend - a child selector
       cannot reach across. */
    const set = name => {
      if (node.parentNode) node.dataset.phase = name;
      document.body.dataset.splashPhase = name;
    };
    set(PHASES[0][0]);
    let elapsed = 0;
    PHASES.forEach(([name, ms], i) => {
      if (i === 0) return;                       /* the first phase is the initial state */
      elapsed += PHASES[i - 1][1];
      setTimeout(() => set(name), elapsed);
    });
  }"""

SKIP = r"""    /* Five seconds is a long time when you open the app twenty times a day, so
       always leave a way out: the button, Escape, Enter or Space. */
    const skip = $('#splashSkip');
    if (skip) skip.onclick = () => splashDone(true);
    const bail = e => {
      if (splashGone) { document.removeEventListener('keydown', bail); return; }
      if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        splashDone(true);
        document.removeEventListener('keydown', bail);
      }
    };
    document.addEventListener('keydown', bail);
"""

ISCC_LINE = (
    '    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs",\n'
    '                 "Inno Setup 6", "ISCC.exe"),\n'
)


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write(path, text, check):
    if check:
        return
    backup = path + ".prelion.bak"
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
def fix_favicon(check):
    path = os.path.join("static", "index.html")
    if not os.path.isfile(path):
        return "index.html   NOT FOUND"
    html = original = read(path)

    # strip any stranded SVG fragment sitting right after the favicon link
    html = re.sub(
        r'(<link rel="icon" href="/icon\.png">)'
        r'(?:<(?:rect|circle|path|svg|g|polygon)\b[^\n]*?">)',
        r"\1",
        html,
        count=1,
    )

    # if the favicon is still the old inline SVG, point it at the file
    tag = re.compile(r'<link\b(?:"[^"]*"|\'[^\']*\'|[^>"\'])*>')
    for m in list(tag.finditer(html)):
        if 'rel="icon"' in m.group(0) and "/icon.png" not in m.group(0):
            html = (
                html[: m.start()] + '<link rel="icon" href="/icon.png">' + html[m.end() :]
            )
            break

    if html == original:
        return "index.html   favicon already clean"
    write(path, html, check)
    return "index.html   favicon repaired"


def install_splash_html(check):
    path = os.path.join("static", "index.html")
    if not os.path.isfile(path):
        return "index.html   NOT FOUND"
    html = read(path)
    if "lion-art-svg" in html:
        return "index.html   splash already installed"

    # drop whatever splash block is there now
    html = re.sub(
        r'<div class="splash" id="splash".*?\n</div>\n+', "", html, count=1, flags=re.S
    )
    anchor = '<a class="skip-link" href="#content">Skip to main content</a>'
    if anchor not in html:
        return "index.html   could not find the skip-link anchor; add the splash by hand"
    html = html.replace(anchor, SPLASH_HTML + "\n\n" + anchor, 1)
    write(path, html, check)
    return "index.html   splash markup installed"


def install_splash_css(check):
    path = os.path.join("static", "css", "style.css")
    if not os.path.isfile(path):
        return "style.css    NOT FOUND"
    css = read(path)
    if "blend-bloom" in css:
        return "style.css    splash rules already installed"

    marker = "   welcome splash"
    idx = css.find(marker)
    if idx == -1:
        css = css.rstrip("\n") + "\n\n" + SPLASH_CSS
    else:
        head = css.rfind("/* =", 0, idx)
        if head == -1:
            head = css.rfind("/*", 0, idx)
        css = css[:head].rstrip("\n") + "\n\n" + SPLASH_CSS
    write(path, css, check)
    return "style.css    splash rules installed"


def install_phases(check):
    path = os.path.join("static", "js", "core.js")
    if not os.path.isfile(path):
        return "core.js      NOT FOUND"
    js = original = read(path)

    if "'blend'" not in js:
        js = re.sub(r"  const PHASES = \[.*?\n  \];", PHASES, js, count=1, flags=re.S)

    if "document.body.dataset.splashPhase" not in js:
        js = re.sub(
            r"  function runPhases\(\) \{.*?\n  \}", RUNPHASES, js, count=1, flags=re.S
        )

    # the mane is part of the SVG artwork now, so buildLion is dead weight
    if "function buildLion" in js:
        start = js.index("  function buildLion()")
        head = js.rfind("  /*", 0, start)
        if head != -1 and "mane" in js[head:start]:
            start = head
        i = js.index("{", js.index("function buildLion"))
        depth = 0
        while True:
            if js[i] == "{":
                depth += 1
            elif js[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        end = i + 1
        while end < len(js) and js[end] in "\n ":
            end += 1
        js = js[:start] + js[end:]
    js = js.replace("    buildLion();\n", "")

    if "#splashSkip" not in js:
        js = js.replace(
            "    setTimeout(() => splashDone(true), SPLASH_MAX_MS);\n",
            "    setTimeout(() => splashDone(true), SPLASH_MAX_MS);\n\n" + SKIP,
            1,
        )

    js = js.replace(
        "node.dataset.phase = 'show';     /* no theatre, just the icon */",
        "node.dataset.phase = 'open';     /* no theatre, just the app */\n"
        "      document.body.dataset.splashPhase = 'open';",
    )

    if js == original:
        return "core.js      already up to date"
    write(path, js, check)
    return "core.js      four-phase timeline installed"


def fix_iscc(check):
    path = os.path.join("tools", "build_installer.py")
    if not os.path.isfile(path):
        return "build_installer.py  NOT FOUND"
    py = read(path)
    if "LOCALAPPDATA" in py:
        return "build_installer.py  Inno Setup path already registered"
    py = py.replace("ISCC_CANDIDATES = (\n", "ISCC_CANDIDATES = (\n" + ISCC_LINE, 1)
    write(path, py, check)
    return "build_installer.py  per-user Inno Setup path added"


def main():
    ap = argparse.ArgumentParser(
        description="Install the lion splash and fix the wiring."
    )
    ap.add_argument("--check", action="store_true", help="report only")
    args = ap.parse_args()

    if not os.path.isdir("static") or not os.path.isfile("app.py"):
        print("Run this from the gitgrind folder (the one with app.py in it).")
        return 1

    print("\n  %s\n" % ("checking" if args.check else "patching"))
    for fn in (
        fix_favicon,
        install_splash_html,
        install_splash_css,
        install_phases,
        fix_iscc,
    ):
        print("  " + fn(args.check))

    print("\n  verify:")
    html = read(os.path.join("static", "index.html"))
    css = read(os.path.join("static", "css", "style.css"))
    js = read(os.path.join("static", "js", "core.js"))
    checks = [
        ("icon.png references (want 3)", str(html.count("/icon.png"))),
        (
            "favicon clean",
            (
                "yes"
                if 'href="/icon.png">' in html and "<rect" not in html.split("<title>")[0]
                else "NO"
            ),
        ),
        ("lion artwork", "yes" if "lion-art-svg" in html else "NO"),
        ("splash css", "yes" if "blend-bloom" in css else "NO"),
        ("four phases", "yes" if "'blend'" in js else "NO"),
        ("body phase mirror", "yes" if "splashPhase" in js else "NO"),
        ("skip handler", "yes" if "#splashSkip" in js else "NO"),
    ]
    for label, value in checks:
        print("    %-30s %s" % (label, value))
    print("\n  then:  python tools\\make_icon.py --from-image app_icon.png")
    print("         python tools\\build_installer.py\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
