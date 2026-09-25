#!/usr/bin/env python3
"""Select or cycle even and balanced tiled layouts for the invoking window."""
import math
import subprocess
import sys

window = sys.argv[1]

def tmux(*args):
    return subprocess.check_output(["tmux", *args], text=True).strip()

def sizes(total, count):
    base, extra = divmod(total - count + 1, count)
    return [base + (i < extra) for i in range(count)]

def column_layout(width, height, panes, large_left):
    rows = math.isqrt(len(panes) - 1) + 1
    columns = (len(panes) + rows - 1) // rows
    counts = [rows] * (columns - 1) + [len(panes) - rows * (columns - 1)]
    if large_left:
        counts.reverse()
    widths = sizes(width, columns)
    if min(widths) < 2 or min(sizes(height, max(counts))) < 2:
        raise ValueError("Window is too small for this tiled layout")
    cells = []
    x = index = 0
    for w, count in zip(widths, counts):
        leaves = []
        y = 0
        for h in sizes(height, count):
            leaves.append(f"{w}x{h},{x},{y},{panes[index]}")
            y += h + 1
            index += 1
        cells.append(leaves[0] if count == 1 else
                     f"{w}x{height},{x},0[" + ",".join(leaves) + "]")
        x += w + 1
    body = cells[0] if columns == 1 else f"{width}x{height},0,0{{" + ",".join(cells) + "}"
    checksum = 0
    for byte in body.encode():
        checksum = ((checksum >> 1) | ((checksum & 1) << 15)) + byte
        checksum &= 0xffff
    return f"{checksum:04x},{body}"

try:
    current = tmux("show-options", "-wqv", "-t", window, "@cycle-layout")
    cycle = ["even-horizontal", "even-vertical", "tiled", "tiled-left", "tiled-right"]
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
    tmux("set-option", "-w", "-t", window, "@cycle-layout", layout)
except (subprocess.CalledProcessError, ValueError) as error:
    subprocess.run(["tmux", "display-message", "-t", window, f"Layout cycle: {error}"], check=False)
    sys.exit(1)
