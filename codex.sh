#!/bin/bash
# Activate mise so tools (bun, node, go, etc.) are on PATH inside Codex sessions
if command -v mise &>/dev/null; then
  eval "$(mise activate bash)"
elif [ -x "$HOME/.local/bin/mise" ]; then
  eval "$("$HOME/.local/bin/mise" activate bash)"
fi
# Auto-detect cbp from sibling seed-studio repo (ships pre-built binaries
# so this works for the whole team without needing the private bp2transformer).
_CBP_SETUP="$(cd "$(dirname "$0")/../seed-studio/tools/cbp" 2>/dev/null && pwd)/setup-env.sh"
[ -f "$_CBP_SETUP" ] && source "$_CBP_SETUP"

codex --dangerously-bypass-approvals-and-sandbox "$@"
