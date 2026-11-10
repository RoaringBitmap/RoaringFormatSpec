#!/usr/bin/env python3
"""Generate the SVG figures used in README.md.

Usage: python3 figures/generate.py   (writes the SVG files next to this script)

No third-party dependency is required.
"""
import os
import re
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace"
INK = "#1f2933"
MUTED = "#5f6b7a"
LINE = "#9aa5b1"

# fill, stroke for each part of the format
C = {
    "cookie": ("#dbeafe", "#2563eb"),
    "count": ("#dbeafe", "#2563eb"),
    "runflags": ("#ede9fe", "#7c3aed"),
    "desc": ("#ccfbf1", "#0d9488"),
    "offset": ("#fef3c7", "#d97706"),
    "array": ("#dcfce7", "#16a34a"),
    "bitset": ("#ffedd5", "#ea580c"),
    "run": ("#fce7f3", "#db2777"),
    "neutral": ("#f1f5f9", "#64748b"),
}


def subscripts(s, size):
    """Render 'a_0', 'a_{k-1}' with real subscripts (Unicode ones render poorly)."""
    out, sub = [], max(8, round(size * 0.72))
    for part in re.split(r"(_\{[^}]*\}|_\d)", s):
        if part.startswith("_") and len(part) > 1:
            body = part[2:-1] if part[1] == "{" else part[1:]
            out.append(f'<tspan dy="{size * 0.3:.1f}" font-size="{sub}">{escape(body)}</tspan>'
                       f'<tspan dy="{-size * 0.3:.1f}">\u200b</tspan>')
        else:
            out.append(escape(part))
    return "".join(out)


class SVG:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.items = []

    def rect(self, x, y, w, h, kind="neutral", dashed=False, rx=4, sw=1.5):
        fill, stroke = C[kind]
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        self.items.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>'
        )

    def text(self, x, y, s, size=13, anchor="middle", color=INK, weight="normal",
             mono=False, italic=False):
        fam = MONO if mono else FONT
        style = ' font-style="italic"' if italic else ""
        self.items.append(
            f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{color}" font-weight="{weight}"{style}>'
            f"{subscripts(s, size)}</text>"
        )

    def line(self, x1, y1, x2, y2, color=LINE, sw=1.2, dashed=False, arrow=False):
        dash = ' stroke-dasharray="4 3"' if dashed else ""
        mk = ' marker-end="url(#arrow)"' if arrow else ""
        self.items.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}"{dash}{mk}/>'
        )

    def path(self, d, color=LINE, sw=1.2, arrow=False):
        mk = ' marker-end="url(#arrow)"' if arrow else ""
        self.items.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{mk}/>'
        )

    def brace(self, x1, x2, y, label, kind="neutral", below=True, size=12):
        """A square bracket spanning [x1, x2] with a centered label."""
        stroke = C[kind][1]
        d = 6 if below else -6
        self.path(f"M{x1},{y} L{x1},{y + d} L{x2},{y + d} L{x2},{y}", color=stroke)
        ty = y + d + (15 if below else -6)
        self.text((x1 + x2) / 2, ty, label, size=size, color=MUTED)

    def save(self, name):
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" '
            f'height="{self.h}" viewBox="0 0 {self.w} {self.h}">\n'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker></defs>\n'
            f'<rect width="{self.w}" height="{self.h}" rx="10" fill="#ffffff"/>\n'
        )
        with open(os.path.join(HERE, name), "w") as f:
            f.write(head + "\n".join(self.items) + "\n</svg>\n")


def cells(svg, x, y, h, spec, size=12, mono=False):
    """Draw adjacent cells. spec = list of (width, label, kind, dashed)."""
    for w, label, kind, *rest in spec:
        dashed = rest[0] if rest else False
        svg.rect(x, y, w, h, kind, dashed=dashed, rx=3)
        if label:
            svg.text(x + w / 2, y + h / 2 + size * 0.36, label, size=size, mono=mono)
        x += w
    return x


# ---------------------------------------------------------------------------
# Figure 1: how a 32-bit value is split, and the three container types
# ---------------------------------------------------------------------------
def partition():
    s = SVG(860, 330)
    s.text(30, 34, "A 32-bit value is split into a 16-bit key and a 16-bit low part",
           size=15, anchor="start", weight="bold")

    # the value
    x0, y0 = 60, 62
    s.text(x0 - 10, y0 + 24, "x =", size=14, anchor="end")
    s.rect(x0, y0, 220, 36, "desc")
    s.text(x0 + 110, y0 + 23, "high 16 bits", size=13)
    s.rect(x0 + 220, y0, 220, 36, "neutral")
    s.text(x0 + 330, y0 + 23, "low 16 bits", size=13)
    s.text(x0 + 110, y0 + 54, "key = x >> 16", size=12, color=MUTED, mono=True)
    s.text(x0 + 330, y0 + 54, "x & 0xFFFF", size=12, color=MUTED, mono=True)
    s.text(x0 + 470, y0 + 16, "Values sharing a key go into the same",
           size=12, anchor="start", color=MUTED)
    s.text(x0 + 470, y0 + 33, "container, which stores only their low",
           size=12, anchor="start", color=MUTED)
    s.text(x0 + 470, y0 + 50, "16 bits. Containers are sorted by key.",
           size=12, anchor="start", color=MUTED)

    # three containers
    y1 = 165
    boxes = [
        ("array", "Array container", ["cardinality ≤ 4096", "sorted 16-bit values", "2 bytes per value"]),
        ("bitset", "Bitset container", ["cardinality > 4096", "65536 bits = 1024 words", "always 8192 bytes"]),
        ("run", "Run container", ["marked in the run flags", "sorted runs (start, length−1)", "4 bytes per run, plus 2"]),
    ]
    bw, gap = 240, 25
    for i, (kind, title, lines) in enumerate(boxes):
        bx = 30 + i * (bw + gap)
        s.rect(bx, y1, bw, 130, kind, rx=8)
        s.text(bx + bw / 2, y1 + 28, title, size=14, weight="bold")
        for j, ln in enumerate(lines):
            s.text(bx + bw / 2, y1 + 60 + j * 22, ln, size=12)
    s.path(f"M{x0 + 110},{y0 + 62} L{x0 + 110},{y1 - 12}", arrow=True)
    return s.save("partition.svg")


# ---------------------------------------------------------------------------
# Figure 2: overall layout of a serialized 32-bit Roaring bitmap
# ---------------------------------------------------------------------------
def layout():
    s = SVG(820, 560)
    H = 40
    s.text(30, 32, "Serialized 32-bit Roaring bitmap (n containers, little endian)",
           size=15, anchor="start", weight="bold")

    # (a) with run containers
    y = 80
    s.text(30, y - 16, "(a) cookie = SERIAL_COOKIE (12347): run containers allowed",
           size=13, anchor="start", weight="bold", color=MUTED)
    x = 30
    spec = [
        (90, "cookie", "cookie"),
        (86, "run flags", "runflags"),
        (60, "key_0", "desc"), (70, "card_0−1", "desc"), (36, "…", "desc"),
        (60, "off_0", "offset", True), (60, "off_1", "offset", True), (36, "…", "offset", True),
        (110, "container_0", "neutral"), (110, "container_1", "neutral"), (40, "…", "neutral"),
    ]
    ends = []
    xx = x
    for w, *_ in spec:
        xx += w
        ends.append(xx)
    cells(s, x, y, H, spec)
    b = y + H + 2
    s.brace(30, ends[0], b, "4 bytes", "cookie")
    s.text(30, b + 40, "cookie = 12347 | ((n − 1) << 16)", size=11, anchor="start", color=MUTED, mono=True)
    s.brace(ends[0], ends[1], b, "⌈n/8⌉ bytes", "runflags")
    s.brace(ends[1], ends[4], b, "4n bytes", "desc")
    s.brace(ends[4], ends[7], b, "4n bytes, only if n ≥ 4", "offset")
    s.brace(ends[7], ends[10], b, "variable", "neutral")

    # (b) without run containers
    y = 225
    s.text(30, y - 16, "(b) cookie = SERIAL_COOKIE_NO_RUNCONTAINER (12346): no run containers",
           size=13, anchor="start", weight="bold", color=MUTED)
    spec = [
        (90, "cookie", "cookie"),
        (86, "n", "count"),
        (60, "key_0", "desc"), (70, "card_0−1", "desc"), (36, "…", "desc"),
        (60, "off_0", "offset"), (60, "off_1", "offset"), (36, "…", "offset"),
        (110, "container_0", "neutral"), (110, "container_1", "neutral"), (40, "…", "neutral"),
    ]
    cells(s, 30, y, H, spec)
    b = y + H + 2
    s.brace(30, ends[0], b, "4 bytes", "cookie")
    s.brace(ends[0], ends[1], b, "4 bytes", "count")
    s.brace(ends[1], ends[4], b, "4n bytes", "desc")
    s.brace(ends[4], ends[7], b, "4n bytes, always", "offset")
    s.brace(ends[7], ends[10], b, "variable", "neutral")

    # legend for the headers
    y = 330
    legend = [
        ("cookie", "Cookie header: format and container count"),
        ("runflags", "Run flags: bit i set ⇔ container i is a run container"),
        ("desc", "Descriptive header: 16-bit key, 16-bit cardinality − 1"),
        ("offset", "Offset header: 32-bit byte offset of each container"),
    ]
    for i, (kind, label) in enumerate(legend):
        lx = 30 + (i % 2) * 430
        ly = y + (i // 2) * 26
        s.rect(lx, ly - 12, 16, 16, kind, rx=3)
        s.text(lx + 24, ly + 1, label, size=12, anchor="start")

    # container encodings
    y = 420
    s.text(30, y - 18, "Container encodings", size=13, anchor="start",
           weight="bold", color=MUTED)
    rows = [
        ("Array", "array", [(56, "v_0"), (56, "v_1"), (40, "…"), (56, "v_{k−1}")],
         "2k bytes for cardinality k ≤ 4096; sorted 16-bit values"),
        ("Bitset", "bitset", [(64, "w_0"), (64, "w_1"), (40, "…"), (64, "w_{1023}")],
         "8192 bytes: 1024 64-bit words; value j is bit j % 64 of word j / 64"),
        ("Run", "run", [(42, "r"), (60, "start_0"), (70, "len_0−1"), (40, "…")],
         "2 + 4r bytes for r runs; runs sorted, non-overlapping"),
    ]
    for i, (name, kind, sp, note) in enumerate(rows):
        ry = y + i * 46
        s.text(30, ry + 21, name, size=13, anchor="start", weight="bold")
        xe = cells(s, 100, ry, 30, [(w, l, kind) for w, l in sp], size=12)
        s.text(xe + 16, ry + 20, note, size=12, anchor="start", color=MUTED)
    return s.save("layout.svg")


# ---------------------------------------------------------------------------
# Figure 3: a worked example, byte by byte
# ---------------------------------------------------------------------------
EXAMPLE = [
    ("cookie", ["3b", "30", "01", "00"], ["cookie 12347", "n − 1 = 1"]),
    ("runflags", ["02"], ["run flags", "0b10"]),
    ("desc", ["00", "00", "02", "00"], ["key 0", "card − 1 = 2"]),
    ("desc", ["02", "00", "63", "00"], ["key 2", "card − 1 = 99"]),
    ("array", ["05", "00", "0a", "00", "e8", "03"], ["array container", "5, 10, 1000"]),
    ("run", ["01", "00", "00", "00", "63", "00"], ["run container: 1 run", "start 0, length − 1 = 99"]),
]


def example():
    cw, H = 31, 34
    n = sum(len(b) for _, b, _ in EXAMPLE)
    x0 = 30
    s = SVG(x0 * 2 + cw * n, 200)
    s.text(30, 30, "Example: {5, 10, 1000} ∪ [131072, 131172) in 25 bytes",
           size=15, anchor="start", weight="bold")
    y = 76
    x = x0
    for i in range(0, n, 4):
        s.text(x0 + i * cw + 2, y - 8, str(i), size=10, anchor="start", color=MUTED)
    for kind, bs, label in EXAMPLE:
        x1 = x
        for b in bs:
            s.rect(x, y, cw, H, kind, rx=2, sw=1)
            s.text(x + cw / 2, y + H / 2 + 5, b, size=13, mono=True)
            x += cw
        s.brace(x1 + 2, x - 2, y + H + 3, "", kind)
        ly = y + H + 26
        for j, ln in enumerate(label):
            s.text((x1 + x) / 2, ly + j * 15, ln, size=11, color=MUTED)
    s.text(30, 185, "No offset header: the cookie is SERIAL_COOKIE and n = 2 < NO_OFFSET_THRESHOLD = 4.",
           size=12, anchor="start", color=MUTED)
    return s.save("example.svg")


# ---------------------------------------------------------------------------
# Figure 4: the 64-bit extension
# ---------------------------------------------------------------------------
def layout64():
    s = SVG(870, 190)
    H = 40
    s.text(30, 32, "Portable 64-bit format (m buckets, little endian)",
           size=15, anchor="start", weight="bold")
    y = 62
    spec = [
        (130, "m", "count"),
        (110, "key_0", "desc"), (200, "32-bit Roaring bitmap_0", "neutral"),
        (110, "key_1", "desc"), (200, "32-bit Roaring bitmap_1", "neutral"),
        (60, "…", "neutral"),
    ]
    ends, xx = [], 30
    for w, *_ in spec:
        xx += w
        ends.append(xx)
    cells(s, 30, y, H, spec, size=12)
    b = y + H + 2
    s.brace(30, ends[0], b, "8 bytes (uint64)", "count")
    s.brace(ends[0], ends[1], b, "4 bytes", "desc")
    s.brace(ends[1], ends[2], b, "variable", "neutral")
    s.brace(ends[2], ends[3], b, "4 bytes", "desc")
    s.brace(ends[3], ends[4], b, "variable", "neutral")
    s.text(30, 150, "Each bucket holds the elements sharing the same high 32 bits (the key);",
           size=12, anchor="start", color=MUTED)
    s.text(30, 168, "buckets are written by increasing key, each followed by a standard 32-bit Roaring bitmap of the low 32 bits.",
           size=12, anchor="start", color=MUTED)
    return s.save("layout64.svg")


if __name__ == "__main__":
    partition()
    layout()
    example()
    layout64()
