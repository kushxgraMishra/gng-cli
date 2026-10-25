"""GNG terminal identity: wordmark, palette, banner and output helpers."""

import os
import random
import shutil
import sys
import textwrap

VERSION = "0.1.0"

TAGLINES = [
    "hii lol"
]

# --- Wordmarks ---------------------------------------------------------------
# Full: three 9x5 glyphs, 2-column gaps, 31 columns total.
G = [
    " ███████ ",
    "██       ",
    "██  ████ ",
    "██    ██ ",
    " ███████ ",
]
N = [
    "███    ██",
    "████   ██",
    "██ ██  ██",
    "██  ██ ██",
    "██   ████",
]
assert all(len(r) == 9 for r in G + N)
WORDMARK = ["  ".join(parts) for parts in zip(G, N, G)]
WORD_W = len(WORDMARK[0])  # 31

# Compact: three 5x5 glyphs, 1-column gaps, 17 columns total (narrow terminals).
CG = [" ████", "█    ", "█  ██", "█   █", " ████"]
CN = ["█   █", "██  █", "█ █ █", "█  ██", "█   █"]
assert all(len(r) == 5 for r in CG + CN)
COMPACT = [" ".join(parts) for parts in zip(CG, CN, CG)]
COMPACT_W = len(COMPACT[0])  # 17

# --- Palettes: truecolor, 256-color, and plain 16-color ANSI -----------------
PALETTES = {
    "truecolor": {
        "cyan": "38;2;0;240;255",
        "magenta": "38;2;255;0;170",
        "violet": "38;2;123;97;255",
        "gray": "38;5;245",
    },
    "256": {
        "cyan": "38;5;51",
        "magenta": "38;5;199",
        "violet": "38;5;99",
        "gray": "38;5;245",
    },
    "16": {
        "cyan": "96",
        "magenta": "95",
        "violet": "94",
        "gray": "37",
    },
}

ASCII_MAP = str.maketrans({
    "█": "#", "═": "=", "║": "|", "╔": "+", "╗": "+", "╚": "+", "╝": "+",
    "─": "-", "│": "|", "┌": "+", "┐": "+", "└": "+", "┘": "+",
})

COMMANDS = [
    ("folder <name>", "create a folder here"),
    ("new <name>", "start a Python CLI project"),
    ("doctor", "check your setup"),
    ("todo", "list TODO notes in code"),
    ("clean", "remove cache folders"),
    ("--help", "list every command"),
]


# --- Environment detection --------------------------------------------------
def color_enabled(stream):
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return stream.isatty()


def color_depth():
    """'truecolor', '256' or '16', judged from COLORTERM and TERM."""
    colorterm = os.environ.get("COLORTERM", "").lower()
    if colorterm in ("truecolor", "24bit"):
        return "truecolor"
    if "256" in colorterm or "256color" in os.environ.get("TERM", "").lower():
        return "256"
    return "16"


def palette():
    return PALETTES[color_depth()]


def unicode_ok():
    if os.environ.get("GNG_ASCII"):
        return False
    enc = (getattr(sys.stdout, "encoding", None) or "").lower()
    return "utf" in enc


# --- Rendering helpers ------------------------------------------------------
def _paint(text, codes, color):
    if not color or not text.strip():
        return text
    return "\x1b[" + ";".join(codes) + "m" + text + "\x1b[0m"


def _wrap(text, width):
    return textwrap.wrap(text, max(width, 1)) or [""]


def _center(text, width, paint_fn):
    if len(text) >= width:
        return paint_fn(text)
    left = (width - len(text)) // 2
    return " " * left + paint_fn(text) + " " * (width - left - len(text))


def _frame(rows, pad, edge, ink, blank_rows):
    """Single-line frame around rows. Every returned line is the same width."""
    w = len(rows[0]) + 2 * pad
    blank = edge("│") + " " * w + edge("│")
    body = [edge("│") + " " * pad + ink(r) + " " * pad + edge("│") for r in rows]
    if blank_rows:
        body = [blank] + body + [blank]
    return [edge("┌" + "─" * w + "┐")] + body + [edge("└" + "─" * w + "┘")]


# --- Rendering --------------------------------------------------------------
def render_banner(width, color=True, tagline=None, pal=None):
    """Pick the largest banner that fits, always leaving a 2-column margin.

    >= 57 columns: wordmark in a double outer frame and a single inner frame
    >= 41 columns: wordmark in the inner frame only
    >= 23 columns: compact wordmark in a single frame
    otherwise:     plain "[ GNG ]" text
    """
    pal = pal or PALETTES["truecolor"]
    tagline = tagline or random.choice(TAGLINES)

    def paint(text, *codes):
        return _paint(text, codes, color)

    mag = lambda s: paint(s, "1", pal["magenta"])
    vio = lambda s: paint(s, pal["violet"])
    cyan = lambda s: paint(s, "1", pal["cyan"])
    bold = lambda s: paint(s, "1")

    inner_total = WORD_W + 2 * 3 + 2   # 39
    side = 7
    outer_in = inner_total + 2 * side  # 53
    compact_total = COMPACT_W + 2 + 2  # 21

    if width >= outer_in + 2 + 2:
        inner = _frame(WORDMARK, 3, vio, cyan, True)
        blank = mag("║") + " " * outer_in + mag("║")
        ver = f"[ v{VERSION} ]"
        lines = [mag("╔═[ gng ]" + "═" * (outer_in - 8) + "╗"), blank]
        lines += [mag("║") + " " * side + ln + " " * side + mag("║") for ln in inner]
        lines.append(blank)
        lines += [mag("║") + _center(t, outer_in, bold) + mag("║")
                  for t in _wrap(tagline, outer_in)]
        lines.append(blank)
        lines.append(mag("╚" + "═" * (outer_in - len(ver) - 1))
                     + paint(ver, pal["gray"]) + mag("═╝"))
    elif width >= inner_total + 2:
        lines = _frame(WORDMARK, 3, vio, cyan, True)
        lines += [_center(t, inner_total, bold) for t in _wrap(tagline, inner_total)]
    elif width >= compact_total + 2:
        lines = _frame(COMPACT, 1, vio, cyan, False)
        lines += [_center(t, compact_total, bold) for t in _wrap(tagline, compact_total)]
    else:
        lines = [mag("[ GNG ]")] + [bold(t) for t in _wrap(tagline, width)]
    return "\n".join(lines)


def render_screen(width, color=True, ascii_only=False, tagline=None, pal=None):
    pal = pal or PALETTES["truecolor"]

    def paint(text, *codes):
        return _paint(text, codes, color)

    ind = "  " if width >= 30 else ""
    avail = width - len(ind)

    name = paint("GNG", "1", pal["cyan"])
    sep = paint("//", pal["magenta"])
    if avail >= 33:
        status = (f"{name} {sep} " + paint("developer toolkit", pal["gray"])
                  + f" {sep} " + paint("ready", "1"))
    elif avail >= 12:
        status = f"{name} {sep} " + paint("ready", "1")
    else:
        status = name

    out = [render_banner(width, color, tagline, pal), "", ind + status, ""]
    out += [ind + l for l in _wrap("Welcome. Try one of these:", avail)]

    cmd_ind = ind + "  "
    table_w = len(cmd_ind) + 4 + 12 + max(len(d) for _, d in COMMANDS)
    for cmd, desc in COMMANDS:
        if width >= table_w:
            out.append(cmd_ind + paint("gng " + cmd.ljust(12), pal["cyan"]) + desc)
        else:
            out += [cmd_ind + paint(l, pal["cyan"])
                    for l in _wrap("gng " + cmd, width - len(cmd_ind))]
            out += [cmd_ind + "  " + l
                    for l in _wrap(desc, width - len(cmd_ind) - 2)]
    text = "\n".join(out)
    return text.translate(ASCII_MAP) if ascii_only else text


def show():
    """Entry point for bare `gng`."""
    if not sys.stdout.isatty():
        print(f"gng {VERSION} // developer toolkit // ready")
        return
    width = shutil.get_terminal_size((80, 24)).columns
    print(render_screen(width, color_enabled(sys.stdout), not unicode_ok(), pal=palette()))


def error(what, fix):
    """Precise, joke-free errors with a next step. Goes to stderr."""
    label = "\x1b[1;31merror\x1b[0m" if color_enabled(sys.stderr) else "error"
    print(f"{label}: {what}", file=sys.stderr)
    print(f"  next: {fix}", file=sys.stderr)


if __name__ == "__main__":
    show()
