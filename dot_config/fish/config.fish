# ~/.config/fish/config.fish

set -gx PNPM_HOME "/Users/nathan/Library/pnpm"

# --- pnpm start ---
if type -q fish_add_path
    fish_add_path $PNPM_HOME
else
    if not contains $PNPM_HOME $PATH
        set -gx PATH $PNPM_HOME $PATH
    end
end
# --- pnpm end ---

if not contains "$HOME/.local/bin" $PATH
    fish_add_path "$HOME/.local/bin"
end

set -gx GPG_TTY (tty)

alias clde "claude --dangerously-skip-permissions"
alias vim "nvim"
alias tailscale="/Applications/Tailscale.app/Contents/MacOS/Tailscale"
alias gay "agy"

function commit
    codex e "\$commit" \
        -m gpt-5.6-luna \
        -c 'service_tier="fast"' \
        -c 'model_reasoning_effort="high"' \
        $argv
end

# Added by OrbStack: command-line tools and integration
# This won't be added again if you remove it.
source ~/.orbstack/shell/init2.fish 2>/dev/null || :

if type -q direnv
    direnv hook fish | source
end

if type -q fish_add_path
    fish_add_path /opt/homebrew/bin
    fish_add_path /opt/homebrew/sbin
end

# bun
set --export BUN_INSTALL "$HOME/.bun"
set --export PATH $BUN_INSTALL/bin $PATH

# Added by Antigravity
fish_add_path /Users/nathan/.antigravity/antigravity/bin

# Added by Antigravity
fish_add_path /Users/nathan/.antigravity/antigravity/bin

# Added by Antigravity IDE
fish_add_path /Users/nathan/.antigravity-ide/antigravity-ide/bin


# Added by Antigravity CLI installer
set -gx PATH "/Users/nathan/.local/bin" $PATH

# >>> grok installer >>>
fish_add_path $HOME/.grok/bin
# <<< grok installer <<<

# Added by GitButler installer
but completions fish | source

# Cloudflare CLI completions
if type -q cf
    cf complete fish | source
end
