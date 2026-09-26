"""Shared layout names and pure geometry calculations for the tmux picker."""
import math

LAYOUTS = [
    ("Side by side", "even-horizontal"),
    ("Stacked", "even-vertical"),
    ("Tiled", "tiled"),
    ("Tiled - big left", "tiled-left"),
    ("Tiled - big right", "tiled-right"),
]


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

