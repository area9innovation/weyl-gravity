#!/bin/bash
# Activate mise so tools (bun, node, go, etc.) are on PATH inside Claude Code sessions
if command -v mise &>/dev/null; then
  eval "$(mise activate bash)"
elif [ -x "$HOME/.local/bin/mise" ]; then
  eval "$("$HOME/.local/bin/mise" activate bash)"
fi

# Use THIS repo's cbp — not the seed-studio-distributed copy — so
# local changes in tools/code-bp/ take effect immediately without a
# rebuild-and-ship roundtrip. setup-env.sh prefers target/release/cbp
# (fresh cargo build) and falls back to bin/cbp-<os>-<arch> for
# users who haven't run cargo.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
_CBP_SETUP="$SCRIPT_DIR/tools/code-bp/setup-env.sh"
[ -f "$_CBP_SETUP" ] && source "$_CBP_SETUP"

printf '\033]0;Claude Code\007'

# Build the claude invocation: add the cbp system-prompt hint when
# available, and the PostToolUse hook settings when available. Both
# are silently skipped if cbp isn't present.
_CLAUDE_EXTRA=()
[ -n "$CODE_BP_PROMPT" ] && _CLAUDE_EXTRA+=(--append-system-prompt "$CODE_BP_PROMPT")
[ -n "$CODE_BP_SETTINGS" ] && _CLAUDE_EXTRA+=(--settings "$CODE_BP_SETTINGS")

claude --dangerously-skip-permissions "${_CLAUDE_EXTRA[@]}" "$@"
