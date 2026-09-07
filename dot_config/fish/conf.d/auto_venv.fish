if not status is-interactive
    exit
end

function __auto_venv_find_activate
    set -l dir (pwd -P)
    while true
        for name in .venv venv .env env
            set -l activate_script "$dir/$name/bin/activate.fish"
            if test -f "$activate_script"
                echo "$activate_script"
                return 0
            end
        end

        if test "$dir" = /
            return 1
        end

        set dir (path dirname "$dir")
    end
end

function __auto_venv_refresh --on-variable PWD
    set -l activate_script (__auto_venv_find_activate)

    if test -n "$activate_script"
        set -l next_env (path dirname (path dirname "$activate_script"))

        if test "$VIRTUAL_ENV" != "$next_env"
            functions -q deactivate; and deactivate >/dev/null 2>&1
            source "$activate_script" >/dev/null 2>&1
        end

        set -g __auto_venv_active "$next_env"
        return
    end

    if set -q __auto_venv_active
        if test "$VIRTUAL_ENV" = "$__auto_venv_active"
            functions -q deactivate; and deactivate >/dev/null 2>&1
        end
        set -e __auto_venv_active
    end
end

__auto_venv_refresh
