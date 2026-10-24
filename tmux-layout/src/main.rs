//! Keyboard layout picker with cached geometry and native tmux previews.
//!
//! Usage: tmux-layout WINDOW_ID [CURRENT_LAYOUT]

mod layout;

use std::io::{self, Write};
use std::process::{Command, ExitCode};

use crossterm::event::{self, Event, KeyCode, KeyEventKind, KeyModifiers};
use crossterm::style::{Attribute, Print, SetAttribute};
use crossterm::{cursor, queue, terminal};

use layout::{LAYOUTS, column_layout};

fn tmux(args: &[&str]) -> Result<String, String> {
    let output = Command::new("tmux")
        .args(args)
        .output()
        .map_err(|e| e.to_string())?;
    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).into_owned())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).trim().to_owned())
    }
}

struct Picker {
    window: String,
    initial: usize,
    /// `None` marks a layout that does not fit the window.
    targets: Vec<Option<String>>,
    original: String,
    error: String,
}

impl Picker {
    /// One snapshot supplies both geometry and pane IDs. Only opening or
    /// resizing the popup needs this query; navigation uses cached targets.
    fn load_targets(&mut self) -> Result<(), String> {
        let out = tmux(&[
            "list-panes",
            "-t",
            &self.window,
            "-F",
            "#{window_width}\t#{window_height}\t#{pane_id}\t#{window_layout}",
        ])?;
        let rows: Vec<Vec<&str>> = out.lines().map(|row| row.split('\t').collect()).collect();
        let first = rows
            .first()
            .filter(|r| r.len() == 4)
            .ok_or("unexpected tmux output")?;
        let width = first[0].parse().map_err(|_| "bad window width")?;
        let height = first[1].parse().map_err(|_| "bad window height")?;
        let panes: Vec<String> = rows
            .iter()
            .map(|r| r[2].trim_start_matches('%').to_owned())
            .collect();
        self.targets = LAYOUTS
            .iter()
            .map(|&(_, name)| match name {
                "tiled-left" | "tiled-right" => {
                    column_layout(width, height, &panes, name == "tiled-left")
                }
                _ => Some(name.to_owned()),
            })
            .collect();
        self.original = first[3].to_owned();
        Ok(())
    }

    fn apply(&mut self, index: usize, commit: bool) -> bool {
        let Some(target) = &self.targets[index] else {
            self.error = "Window too small for this layout".to_owned();
            return false;
        };
        let mut args = vec!["select-layout", "-t", &self.window, target];
        if commit {
            args.extend([
                ";",
                "set-option",
                "-w",
                "-t",
                &self.window,
                "@cycle-layout",
                LAYOUTS[index].1,
            ]);
        }
        let result = tmux(&args);
        self.error = result.as_ref().err().cloned().unwrap_or_default();
        result.is_ok()
    }

    fn restore(&self) {
        let _ = tmux(&["select-layout", "-t", &self.window, &self.original]);
    }

    fn draw(&self, out: &mut impl Write, selected: usize) -> io::Result<()> {
        let (width, height) = terminal::size().unwrap_or((80, 24));
        queue!(out, terminal::Clear(terminal::ClearType::All))?;
        let mut line = |y: u16, text: &str, reverse: bool| -> io::Result<()> {
            if y >= height || width <= 2 {
                return Ok(());
            }
            let text: String = text.chars().take(usize::from(width - 2)).collect();
            queue!(out, cursor::MoveTo(1, y))?;
            if reverse {
                queue!(
                    out,
                    SetAttribute(Attribute::Reverse),
                    Print(text),
                    SetAttribute(Attribute::Reset)
                )
            } else {
                queue!(out, Print(text))
            }
        };
        for (i, (label, _)) in LAYOUTS.iter().enumerate() {
            let marker = if i == self.initial { " *" } else { "" };
            line(
                i as u16 + 1,
                &format!(" {}  {label}{marker}", i + 1),
                i == selected,
            )?;
        }
        if !self.error.is_empty() {
            line(6, &self.error.clone(), false)?;
        }
        out.flush()
    }

    /// Runs the picker loop and reports whether a layout was committed.
    fn choose(&mut self, out: &mut impl Write) -> io::Result<bool> {
        let count = LAYOUTS.len();
        let mut selected = self.initial;
        self.apply(selected, false);
        loop {
            self.draw(out, selected)?;
            let previous = selected;
            match event::read()? {
                Event::Key(key) if key.kind != KeyEventKind::Release => match key.code {
                    KeyCode::Char(' ' | 'j') | KeyCode::Down => selected = (selected + 1) % count,
                    KeyCode::Char('k') | KeyCode::Up => selected = (selected + count - 1) % count,
                    KeyCode::Enter => {
                        if self.apply(selected, true) {
                            return Ok(true);
                        }
                    }
                    KeyCode::Char(c @ '1'..='5') => {
                        if self.apply(c as usize - '1' as usize, true) {
                            return Ok(true);
                        }
                    }
                    KeyCode::Char('c') if key.modifiers.contains(KeyModifiers::CONTROL) => {
                        return Ok(false);
                    }
                    KeyCode::Esc | KeyCode::Char('q') => return Ok(false),
                    _ => {}
                },
                Event::Resize(..)
                    if self.load_targets().is_ok() => {
                        self.apply(selected, false);
                    }
                _ => {}
            }
            if selected != previous && !self.apply(selected, false) {
                selected = previous;
            }
        }
    }
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().collect();
    let Some(window) = args.get(1) else {
        eprintln!("usage: tmux-layout WINDOW_ID [CURRENT_LAYOUT]");
        return ExitCode::from(2);
    };
    let current = args.get(2).map(String::as_str).unwrap_or("");
    let mut picker = Picker {
        window: window.clone(),
        initial: LAYOUTS
            .iter()
            .position(|&(_, name)| name == current)
            .unwrap_or(0),
        targets: Vec::new(),
        original: String::new(),
        error: String::new(),
    };
    if let Err(e) = picker.load_targets() {
        eprintln!("tmux-layout: {e}");
        return ExitCode::FAILURE;
    }

    let mut out = io::stdout();
    let committed = terminal::enable_raw_mode()
        .and_then(|()| queue!(out, cursor::Hide))
        .and_then(|()| picker.choose(&mut out));
    let _ = queue!(out, terminal::Clear(terminal::ClearType::All), cursor::Show);
    let _ = out.flush();
    let _ = terminal::disable_raw_mode();
    match committed {
        Ok(true) => ExitCode::SUCCESS,
        Ok(false) => {
            picker.restore();
            ExitCode::SUCCESS
        }
        Err(e) => {
            picker.restore();
            eprintln!("tmux-layout: {e}");
            ExitCode::FAILURE
        }
    }
}

#[cfg(test)]
mod tests;
