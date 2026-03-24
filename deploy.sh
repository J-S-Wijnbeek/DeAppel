#!/usr/bin/env bash
# deploy.sh
#
# Push the current project to one or more remote repositories.
# Supported targets:
#   github   – pushes to the 'origin' remote (GitHub)
#   devops   – pushes to the 'devops' remote (Azure DevOps)
#   all      – pushes to both remotes (default)
#
# Usage:
#   ./deploy.sh [--target github|devops|all] [--branch <branch>] [--message <msg>]
#
# The script assumes SSH keys are already loaded (via ssh-agent or ~/.ssh/config).
# See the README for SSH configuration instructions.

set -euo pipefail

# ---------------------------------------------------------------------------
# Default values
# ---------------------------------------------------------------------------
TARGET="all"
BRANCH=""
COMMIT_MESSAGE=""

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --target)
            TARGET="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --message|-m)
            COMMIT_MESSAGE="$2"
            shift 2
            ;;
        --help|-h)
            sed -n '/^# deploy.sh/,/^[^#]/p' "$0" | grep '^#' | sed 's/^# \?//'
            exit 0
            ;;
        *)
            echo "[ERROR] Onbekend argument: $1" >&2
            exit 1
            ;;
    esac
done

# Validate --target value
case "$TARGET" in
    github|devops|all) ;;
    *)
        echo "[ERROR] Ongeldige waarde voor --target: '$TARGET'. Kies uit: github, devops, all." >&2
        exit 1
        ;;
esac

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
log()  { echo "[INFO]  $*"; }
warn() { echo "[WARN]  $*" >&2; }
err()  { echo "[ERROR] $*" >&2; exit 1; }

remote_exists() {
    git remote get-url "$1" &>/dev/null
}

push_to_remote() {
    local remote="$1"
    local branch="$2"

    if ! remote_exists "$remote"; then
        warn "Remote '$remote' bestaat niet – sla push over."
        return 0
    fi

    log "Push naar remote '$remote' (branch: $branch) ..."
    git push "$remote" "$branch"
    log "Push naar '$remote' geslaagd."
}

# ---------------------------------------------------------------------------
# Determine active branch
# ---------------------------------------------------------------------------
if [[ -z "$BRANCH" ]]; then
    BRANCH="$(git rev-parse --abbrev-ref HEAD)"
fi
log "Actieve branch: $BRANCH"

# ---------------------------------------------------------------------------
# Stage & commit if there are changes and a message was provided
# ---------------------------------------------------------------------------
if [[ -n "$COMMIT_MESSAGE" ]]; then
    if [[ -n "$(git status --porcelain)" ]]; then
        log "Wijzigingen gevonden – commit aanmaken..."
        git add .
        git commit -m "$COMMIT_MESSAGE"
        log "Commit aangemaakt: $COMMIT_MESSAGE"
    else
        log "Geen openstaande wijzigingen – geen commit nodig."
    fi
fi

# ---------------------------------------------------------------------------
# Push to the requested remote(s)
# ---------------------------------------------------------------------------
case "$TARGET" in
    github)
        push_to_remote "origin" "$BRANCH"
        ;;
    devops)
        push_to_remote "devops" "$BRANCH"
        ;;
    all)
        push_to_remote "origin" "$BRANCH"
        push_to_remote "devops" "$BRANCH"
        ;;
esac

log "Deploy klaar."
