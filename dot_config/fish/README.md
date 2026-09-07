# my-fish-config

Minimal, portable Fish shell config for `~/.config/fish`.

## Tracked files (critical only)

- `config.fish` - core shell config (aliases, PATH, integrations)
- `fish_plugins` - Fisher plugin manifest
- `conf.d/auto_venv.fish` - auto-activate/deactivate Python virtualenv by directory
- `.gitignore`
- `README.md`

## Apply on a new machine

1. Back up your current Fish config:
   ```bash
   mv ~/.config/fish ~/.config/fish.backup-"$(date +%Y%m%d-%H%M%S)"
   ```
2. Clone this repo:
   ```bash
   git clone https://github.com/Nat1anWasTaken/my-fish-config.git ~/.config/fish
   ```
3. Install Fisher:
   ```bash
   curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher
   ```
4. Install plugins from `fish_plugins`:
   ```bash
   fisher update
   ```
5. Start a new Fish shell:
   ```bash
   exec fish
   ```

## Notes

- Plugin-generated files in `functions/`, `completions/`, and most of `conf.d/` are intentionally not tracked.
- `config.fish` contains machine-specific paths (`/Users/nathan/...`); adjust for your user on other machines.
