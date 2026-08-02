#!/usr/bin/env python3
"""Generate static/icon.ico (and .png) from the app's own favicon design.

The favicon in static/index.html is a rounded dark tile holding four squares in
GitHub-contribution greens. This redraws exactly that at every size Windows asks
for, so the taskbar icon, the Alt-Tab icon and the browser favicon are the same
mark rather than three near-misses.

    python tools/make_icon.py            write static/icon.ico + static/icon.png
    python tools/make_icon.py --preview  also write a large flat PNG to eyeball

Pillow is only needed to run this script, not to run the app. The generated .ico
is committed, so a normal build never needs Pillow at all.
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The same palette as the CSS custom properties and the favicon.
BG = (13, 17, 23, 255)  # #0d1117  GitHub dark canvas
CELLS = (
    (0x39, 0xD3, 0x53, 255),  # #39d353  brightest green, top-left
    (0x00, 0x6D, 0x32, 255),  # #006d32  mid green,       top-right
    (0x19, 0x6C, 0x2E, 255),  # #196c2e  dark green,      bottom-left
    (0x39, 0xD3, 0x53, 255),  # #39d353  brightest green, bottom-right
)

SIZES = (16, 24, 32, 48, 64, 128, 256)


def draw(size):
    """Render the mark at one size, supersampled 4x so edges stay clean."""
    from PIL import Image, ImageDraw

    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Rounded tile. The favicon uses a 7/32 radius on a 32-unit box.
    radius = int(s * 7 / 32)
    d.rounded_rectangle((0, 0, s - 1, s - 1), radius=radius, fill=BG)

    # Four squares on a 32-unit grid: 6,6 / 19,6 / 6,19 / 19,19, each 7 wide.
    unit = s / 32.0
    box = 7 * unit
    corner = max(1, int(2 * unit))
    spots = ((6, 6), (19, 6), (6, 19), (19, 19))
    for (gx, gy), colour in zip(spots, CELLS):
        x0, y0 = gx * unit, gy * unit
        d.rounded_rectangle((x0, y0, x0 + box, y0 + box), radius=corner, fill=colour)

    return img.resize((size, size), Image.LANCZOS)


def from_image(path, size, rounded=True):
    """Turn any square-ish PNG into one icon frame.

    This is the escape hatch for artwork made somewhere else - Inkscape, Canva,
    an AI generator, a scan of something you drew. It centre-crops to a square,
    resizes with a good filter, and optionally applies the same rounded-tile mask
    the drawn icon uses so a hand-made and a generated icon sit together without
    looking mismatched.
    """
    from PIL import Image, ImageDraw

    src = Image.open(path).convert("RGBA")

    # Centre-crop to square. Anything not square would otherwise be squashed.
    w, h = src.size
    if w != h:
        side = min(w, h)
        src = src.crop(
            (
                (w - side) // 2,
                (h - side) // 2,
                (w - side) // 2 + side,
                (h - side) // 2 + side,
            )
        )

    # Work 4x large so the rounded corners stay clean after the final resize.
    big = size * 4
    src = src.resize((big, big), Image.LANCZOS)

    if rounded:
        mask = Image.new("L", (big, big), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, big - 1, big - 1), radius=int(big * 7 / 32), fill=255
        )
        out = Image.new("RGBA", (big, big), (0, 0, 0, 0))
        out.paste(src, (0, 0), mask)
        src = out

    return src.resize((size, size), Image.LANCZOS)


def wire_into_app():
    """Point the favicon and the topbar mark at the generated icon.

    Without this the .ico would be picked up by the executable and the installer
    while the browser tab and the header still showed the old inline SVG - the
    kind of half-applied change that is easy to miss and annoying to debug.
    """
    changed = []

    html_path = os.path.join(ROOT, "static", "index.html")
    if os.path.isfile(html_path):
        with open(html_path, "r", encoding="utf-8") as fh:
            html = original = fh.read()
        # A <link> whose href is a data: URI contains '>' characters inside the
        # quoted value, so [^>]* stops in the middle and leaves the rest of the
        # SVG stranded in <head>. Consume quoted runs explicitly instead.
        tag = re.compile(r'<link\b(?:"[^"]*"|\'[^\']*\'|[^>"\'])*>')
        for m in list(tag.finditer(html)):
            if 'rel="icon"' in m.group(0):
                html = (
                    html[: m.start()]
                    + '<link rel="icon" href="/icon.png">'
                    + html[m.end() :]
                )
                break
        html = re.sub(
            r'<span class="brand-grid"[^>]*>.*?</span>',
            '<img class="brand-mark" src="/icon.png" alt="" aria-hidden="true">',
            html,
            count=1,
            flags=re.S,
        )
        if html != original:
            with open(html_path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(html)
            changed.append("static/index.html")

    css_path = os.path.join(ROOT, "static", "css", "style.css")
    if os.path.isfile(css_path):
        with open(css_path, "r", encoding="utf-8") as fh:
            css = fh.read()
        if ".brand-mark" not in css:
            css = css.rstrip("\n") + (
                "\n\n/* The topbar mark is the app icon itself, so the header, the "
                "browser tab,\n   the taskbar and the splash can never drift apart. */\n"
                ".brand-mark{width:26px;height:26px;border-radius:7px;display:block;"
                "flex:none;\n  box-shadow:0 0 0 1px rgba(216,173,59,.35)}\n"
            )
            with open(css_path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(css)
            changed.append("static/css/style.css")

    return changed


def main():
    ap = argparse.ArgumentParser(description="Generate the GitGrind app icon.")
    ap.add_argument("--out", default=os.path.join("static", "icon.ico"))
    ap.add_argument(
        "--preview", action="store_true", help="also write a 512px PNG for eyeballing"
    )
    ap.add_argument(
        "--from-image",
        metavar="PNG",
        help="build the icon from an existing image instead of "
        "drawing it (centre-cropped to square)",
    )
    ap.add_argument(
        "--no-round",
        action="store_true",
        help="with --from-image: keep square corners, do not apply "
        "the rounded-tile mask",
    )
    ap.add_argument(
        "--no-wire",
        action="store_true",
        help="only write the icon files; leave the HTML and CSS alone",
    )
    args = ap.parse_args()

    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("This script needs Pillow:")
        print("    pip install pillow")
        return 1

    if args.from_image:
        source = args.from_image
        if not os.path.isfile(source):
            source_alt = os.path.join(ROOT, args.from_image)
            if not os.path.isfile(source_alt):
                print("No such image: %s" % args.from_image)
                return 1
            source = source_alt
        print("building from %s" % source)
        frames = [from_image(source, n, rounded=not args.no_round) for n in SIZES]
        render = lambda n: from_image(source, n, rounded=not args.no_round)
    else:
        render = draw
        frames = [render(n) for n in SIZES]

    ico_path = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(ico_path), exist_ok=True)

    # Pillow writes every supplied size into the one .ico container.
    frames[-1].save(ico_path, format="ICO", sizes=[(n, n) for n in SIZES])
    print(
        "wrote %s (%s)"
        % (os.path.relpath(ico_path, ROOT), ", ".join("%dx%d" % (n, n) for n in SIZES))
    )

    # A PNG for macOS/Linux builds and for the README.
    png_path = os.path.splitext(ico_path)[0] + ".png"
    render(256).save(png_path, format="PNG")
    print("wrote %s (256x256)" % os.path.relpath(png_path, ROOT))

    if args.preview:
        prev = os.path.join(ROOT, "static", "icon-preview.png")
        render(512).save(prev, format="PNG")
        print("wrote %s (512x512)" % os.path.relpath(prev, ROOT))

    if not args.no_wire:
        for name in wire_into_app():
            print("updated %s" % name)

    print("")
    print("In use by: browser tab, topbar mark, splash animation, executable,")
    print("installer and shortcuts. Rebuild to put it inside the exe:")
    print("    python tools/build_installer.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
