# Fish config

Portable Fish shell config for `~/.config/fish`, managed by chezmoi from the
dotfiles repository.

## Tracked files

- `config.fish` - core shell config (PATH, aliases, integrations). It is a
  chezmoi template (`config.fish.tmpl`) that uses `.chezmoi.os` and
  `.chezmoi.arch` to pick the Homebrew prefix, the pnpm home and macOS-only
  integrations. Edit it with `chezmoi edit ~/.config/fish/config.fish`, not
  `chezmoi add`.
- `fish_plugins` - Fisher plugin manifest
- `conf.d/auto_venv.fish` - auto-activate/deactivate Python virtualenv by directory
- `.gitignore`
- `README.md`

## Plugins

`chezmoi apply` runs `.chezmoiscripts/run_onchange_after_fish-plugins.sh`
whenever `fish_plugins` changes. It installs Fisher if needed and runs
`fisher update`. It does nothing if Fish is not installed.

## Notes

- Plugin-generated files in `functions/`, `completions/`, and most of `conf.d/`
  are intentionally not tracked.
- Paths use `$HOME`; optional tools are only added to `PATH` when their
  directories exist.
