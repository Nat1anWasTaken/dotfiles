#!/usr/bin/env python3
"""Select or cycle even and balanced tiled layouts for the invoking window."""
from layout_common import LAYOUTS, column_layout
import subprocess
import sys

window = sys.argv[1]

def tmux(*args):
    return subprocess.check_output(["tmux", *args], text=True).strip()


try:
    current = tmux("show-options", "-wqv", "-t", window, "@cycle-layout")
    cycle = [name for _, name in LAYOUTS]
    layout = sys.argv[2] if len(sys.argv) > 2 else cycle[(cycle.index(current) + 1) % len(cycle)] if current in cycle else cycle[0]
    if layout not in cycle:
        raise ValueError(f"Unknown layout: {layout}")
    if layout.startswith("tiled-"):
        width, height = map(int, tmux("display-message", "-p", "-t", window,
                                     "#{window_width} #{window_height}").split())
        panes = [p.removeprefix("%") for p in tmux("list-panes", "-t", window,
                                                   "-F", "#{pane_id}").splitlines()]
        target = column_layout(width, height, panes, layout == "tiled-left")
    else:
        target = layout
    tmux("select-layout", "-t", window, target)
    if "--preview" not in sys.argv[3:]:
        tmux("set-option", "-w", "-t", window, "@cycle-layout", layout)
except (subprocess.CalledProcessError, ValueError) as error:
    subprocess.run(["tmux", "display-message", "-t", window, f"Layout cycle: {error}"], check=False)
    sys.exit(1)
