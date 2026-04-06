"""
DevMind — terminal output styles
Minimal. Punchy. No deps.
"""

import sys

# ANSI codes
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

# Colors
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

# Bright variants
BGREEN  = "\033[92m"
BYELLOW = "\033[93m"
BCYAN   = "\033[96m"
BWHITE  = "\033[97m"

NO_COLOR = not sys.stdout.isatty()


def c(text, *codes):
    if NO_COLOR:
        return text
    return "".join(codes) + str(text) + RESET


def header(text):
    width = 52
    bar = "─" * width
    print()
    print(c(f"  ┌{bar}┐", CYAN, BOLD))
    pad = (width - len(text)) // 2
    print(c(f"  │{' ' * pad}{text}{' ' * (width - pad - len(text))}│", CYAN, BOLD))
    print(c(f"  └{bar}┘", CYAN, BOLD))
    print()


def section(label):
    print(c(f"\n  ╸ {label}", YELLOW, BOLD))
    print(c("  " + "·" * 40, DIM))


def row(label, value, accent=BGREEN):
    label_str = c(f"  {label:<22}", DIM)
    value_str = c(str(value), accent, BOLD)
    print(f"{label_str}{value_str}")


def info(msg):
    print(c("  ▸ ", CYAN) + msg)


def success(msg):
    print(c("  ✓ ", BGREEN) + c(msg, BGREEN))


def warn(msg):
    print(c("  ⚠ ", BYELLOW) + c(msg, BYELLOW))


def error(msg):
    print(c("  ✗ ", RED) + c(msg, RED))


def vibe_line(msg):
    print()
    print(c("  ╔" + "═" * 50 + "╗", MAGENTA, BOLD))
    # Word-wrap inside the box at 48 chars
    words = msg.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 48:
            lines.append(cur.strip())
            cur = w + " "
        else:
            cur += w + " "
    if cur.strip():
        lines.append(cur.strip())
    for line in lines:
        pad = 48 - len(line)
        print(c(f"  ║ {line}{' ' * pad} ║", MAGENTA, BOLD))
    print(c("  ╚" + "═" * 50 + "╝", MAGENTA, BOLD))
    print()


def bar_chart(label, value, max_value, width=20, color=BCYAN):
    filled = int((value / max_value) * width) if max_value else 0
    bar = "█" * filled + c("░" * (width - filled), DIM)
    label_str = c(f"  {label:<22}", DIM)
    print(f"{label_str}{c(bar, color)}  {c(str(value), BOLD)}")


def spark(values, width=30):
    """Inline sparkline from a list of floats."""
    blocks = " ▁▂▃▄▅▆▇█"
    if not values:
        return c("no data", DIM)
    mn, mx = min(values), max(values)
    rng = mx - mn or 1
    chars = [blocks[int(((v - mn) / rng) * 8)] for v in values]
    return c("".join(chars), BCYAN)
