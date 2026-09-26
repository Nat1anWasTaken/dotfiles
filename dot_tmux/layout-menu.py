#!/usr/bin/env python3
"""Keyboard layout picker with cached geometry and native tmux previews."""
import curses
import subprocess
import sys

from layout_common import LAYOUTS, column_layout


class LayoutPicker:
    def __init__(self, window, current):
        self.window = window
        self.initial = next((i for i, (_, name) in enumerate(LAYOUTS)
                             if name == current), 0)
        self.error = ""
        self.original_layout = self.load_targets()

    def load_targets(self):
        # One snapshot supplies both geometry and pane IDs. Only opening or
        # resizing the popup needs this query; navigation uses cached targets.
        rows = subprocess.check_output(
            ["tmux", "list-panes", "-t", self.window, "-F",
             "#{window_width}\t#{window_height}\t#{pane_id}\t#{window_layout}"],
            text=True,
        ).splitlines()
        width, height, _, original = rows[0].split("\t")
        panes = [row.split("\t")[2].removeprefix("%") for row in rows]
        self.targets = []
        for _, name in LAYOUTS:
            if name.startswith("tiled-"):
                try:
                    target = column_layout(int(width), int(height), panes,
                                           name == "tiled-left")
                except ValueError:
                    target = None
            else:
                target = name
            self.targets.append(target)
        return original

    def apply(self, index, commit=False):
        target = self.targets[index]
        if target is None:
            self.error = "Window too small for this layout"
            return False
        command = ["tmux", "select-layout", "-t", self.window, target]
        if commit:
            command += [";", "set-option", "-w", "-t", self.window,
                        "@cycle-layout", LAYOUTS[index][1]]
        result = subprocess.run(command, capture_output=True, text=True)
        self.error = result.stderr.strip() if result.returncode else ""
        return result.returncode == 0

    def restore(self):
        subprocess.run(["tmux", "select-layout", "-t", self.window,
                        self.original_layout], check=False, capture_output=True)

    def choose(self, screen):
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        screen.keypad(True)
        selected = self.initial
        self.apply(selected)
        while True:
            screen.erase()
            height, width = screen.getmaxyx()

            def line(y, text, style=0):
                if y < height and width > 2:
                    screen.addnstr(y, 1, text, width - 2, style)

            for i, (label, _) in enumerate(LAYOUTS):
                marker = " *" if i == self.initial else ""
                line(i + 1, f" {i + 1}  {label}{marker}",
                     curses.A_REVERSE if i == selected else 0)
            if self.error:
                line(6, self.error)
            screen.refresh()
            key = screen.getch()
            previous = selected
            if key in (ord(" "), curses.KEY_DOWN, ord("j")):
                selected = (selected + 1) % len(LAYOUTS)
            elif key in (curses.KEY_UP, ord("k")):
                selected = (selected - 1) % len(LAYOUTS)
            elif key in (10, 13, curses.KEY_ENTER):
                if self.apply(selected, commit=True):
                    return selected
            elif ord("1") <= key <= ord("5"):
                index = key - ord("1")
                if self.apply(index, commit=True):
                    return index
            elif key in (27, ord("q")):
                return None
            elif key == curses.KEY_RESIZE:
                self.load_targets()
                self.apply(selected)
            if selected != previous and not self.apply(selected):
                selected = previous


def main():
    picker = LayoutPicker(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
    # Keep Escape responsive while recognizing arrow-key escape sequences.
    curses.set_escdelay(25)
    committed = False
    try:
        committed = curses.wrapper(picker.choose) is not None
    finally:
        if not committed:
            picker.restore()


if __name__ == "__main__":
    main()
