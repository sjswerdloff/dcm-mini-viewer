#!/usr/bin/env bash
# kindled-review post-commit wrapper — runs the canonical kindled-code-review hook.
#
# Baked in via .pre-commit-config.yaml (kindled-review hook, stages: [post-commit]).
# Every clone that runs `pre-commit install` gets this.  The canonical hook lives
# OUTSIDE any clone, in shared infrastructure; this script finds it and execs it.
#
# The canonical hook exits early on main, never blocks a commit (post-commit
# exit code is ignored by git), and runs the cross-file wall + OCR on
# gemma-4-E4B-it-mlx-mxfp8.  OCR needs the local model endpoint — CI cannot
# run it.  This hook is for developers' commits only.
#
# INVARIANT: this script must never fail silently when the canonical hook is
# missing.  A new host without it must see a loud error on every commit.
set -euo pipefail

CANONICAL="${KINDLED_REVIEW_HOOK:-$HOME/ai/kindled_projects/kindled-code-review/hooks/post-commit}"

# Per-SHA guard prevents double-run when an old .git/hooks/post-commit symlink
# is chained by pre-commit as post-commit.legacy (it execs canonical first, then
# the baked wrapper execs it again).  The canonical hook writes a log per SHA;
# if the log already exists for this SHA, the review already ran — skip.
AI="${AI_FULL_NAME:-$(whoami)}"
SHA="$(git rev-parse --short HEAD)"
REPO_NAME="$(basename "$(git rev-parse --show-toplevel)")"
REVIEW_LOG="$HOME/ai/ClaudeInstanceHomeOffices/$AI/kindled-review-runs/$REPO_NAME/$SHA.log"

# Atomic per-SHA lock: two overlapping post-commit invocations for the same SHA
# could both see the log as absent and both run the review (#12).  mkdir is
# atomic — if it succeeds we own the lock; if it fails, another run is in flight.
LOCKDIR="$(git rev-parse --git-dir)/kindled-review-lock-$SHA"
if ! mkdir "$LOCKDIR" 2>/dev/null; then
    echo "kindled-review: review already running for $SHA — skipping" >&2
    exit 0
fi
trap 'rmdir "$LOCKDIR" 2>/dev/null' EXIT

if [[ -f "$REVIEW_LOG" ]]; then
    echo "kindled-review: already reviewed $SHA — skipping duplicate" >&2
    exit 0
fi

if [[ ! -f "$CANONICAL" ]]; then
    cat >&2 <<EOF
==========================================================================
kindled-review: CANONICAL HOOK NOT FOUND — review did NOT run.

  Expected: $CANONICAL
  Fix:      kindled-code-review is not deployed at ~/ai/kindled_projects
            on this host.  Ask Stuart to deploy it.

  This message prints on every commit until the hook is installed.
==========================================================================
EOF
    exit 1
fi

exec "$CANONICAL"
