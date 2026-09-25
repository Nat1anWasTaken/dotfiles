#!/usr/bin/env python3
"""Keyboard layout picker hosted in a tmux popup."""
import curses
from pathlib import Path
import subprocess
import sys

LAYOUTS = [
    ("Side by side", "even-horizontal"),
    ("Stacked", "even-vertical"),
    ("Tiled", "tiled"),
    ("Tiled - big left", "tiled-left"),
    ("Tiled - big right", "tiled-right"),
]
window = sys.argv[1]
current = sys.argv[2] if len(sys.argv) > 2 else ""
initial = next((i for i, (_, layout) in enumerate(LAYOUTS) if layout == current), 0)


def choose(screen):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    screen.keypad(True)
    selected = initial
    while True:
        screen.erase()
        height, width = screen.getmaxyx()
        def line(y, text, style=0):
            if y < height and width > 2:
                screen.addnstr(y, 1, text, width - 2, style)
        for i, (label, _) in enumerate(LAYOUTS):
            marker = " *" if i == initial else ""
            line(i + 1, f" {i + 1}  {label}{marker}",
                 curses.A_REVERSE if i == selected else 0)
        screen.refresh()
        key = screen.getch()
        if key in (ord(" "), curses.KEY_DOWN, ord("j")):
            selected = (selected + 1) % len(LAYOUTS)
        elif key in (curses.KEY_UP, ord("k")):
            selected = (selected - 1) % len(LAYOUTS)
        elif key in (10, 13, curses.KEY_ENTER):
            return selected
        elif ord("1") <= key <= ord("5"):
            return key - ord("1")
        elif key in (27, ord("q")):
            return None


# Keep Escape responsive while still recognizing arrow-key escape sequences.
curses.set_escdelay(25)
selection = curses.wrapper(choose)
if selection is not None:
    subprocess.run([sys.executable, str(Path(__file__).with_name("layout-cycle.py")),
                    window, LAYOUTS[selection][1]], check=True)
