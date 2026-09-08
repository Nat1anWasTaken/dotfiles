# Dotfiles

This is a [chezmoi](https://www.chezmoi.io/) repository for managing personal dotfiles across machines. chezmoi stores configuration in this source directory and applies it to your home directory.

| Source | Destination | Configuration |
| --- | --- | --- |
| `dot_config/fish/` | `~/.config/fish/` | Fish shell |
| `dot_config/ghostty/` | `~/.config/ghostty/` | Ghostty terminal |
| `dot_config/nvim/` | `~/.config/nvim/` | Neovim |
| `dot_tmux.conf` | `~/.tmux.conf` | tmux |

The `dot_` prefix is chezmoi's naming convention for files and directories that start with a dot.

## Install chezmoi

Use the command for your operating system and package manager:

| System | Package manager | Command |
| --- | --- | --- |
| macOS | Homebrew | `brew install chezmoi` |
| macOS | MacPorts | `sudo port install chezmoi` |
| Debian (where packaged) | APT | `sudo apt-get install chezmoi` |
| Fedora | DNF | `sudo dnf install chezmoi` |
| Arch Linux | Pacman | `sudo pacman -S chezmoi` |
| Alpine Linux | APK | `sudo apk add chezmoi` |
| openSUSE Tumbleweed | Zypper | `sudo zypper install chezmoi` |
| Windows | WinGet | `winget install twpayne.chezmoi` |
| Windows | Scoop | `scoop install chezmoi` |
| Windows | Chocolatey | `choco install chezmoi` |
| FreeBSD | pkg | `sudo pkg install chezmoi` |

On Linux or macOS, including distributions without a chezmoi package, you can also run the official installer from a POSIX shell such as `sh`, Bash, or Zsh:

```sh
sh -c "$(curl -fsLS https://get.chezmoi.io)" -- -b "$HOME/.local/bin"
```

Ensure `~/.local/bin` is on your `PATH`, then verify the installation:

```sh
chezmoi --version
```

See the [official installation guide](https://www.chezmoi.io/install/) for additional platforms, package availability, and binary downloads.

## Set up these dotfiles

Install Git and chezmoi first. Install Fish, Neovim, and tmux separately to use their configurations.

Replace `REPOSITORY_URL` with this repository's Git clone URL:

```sh
chezmoi init REPOSITORY_URL
chezmoi diff
chezmoi apply
```

Review the diff before applying: `chezmoi apply` updates the managed files in your home directory. The default source directory is `~/.local/share/chezmoi`.

If this repository is already checked out in that default source directory, skip `chezmoi init` and run `chezmoi diff` followed by `chezmoi apply`.

## Everyday use

```sh
# Preview and apply local source changes.
chezmoi diff
chezmoi apply

# Capture changes made directly to a managed file.
chezmoi add ~/.tmux.conf

# Open a shell in the source repository to commit and push changes with Git.
chezmoi cd

# Pull remote changes and apply them to this machine.
chezmoi update
```

## Official documentation

- [Quick start](https://www.chezmoi.io/quick-start/)
- [User guide and command overview](https://www.chezmoi.io/user-guide/command-overview/)
- [Daily operations](https://www.chezmoi.io/user-guide/daily-operations/)
- [Reference](https://www.chezmoi.io/reference/)
- [Source code](https://github.com/twpayne/chezmoi)
