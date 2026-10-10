#!/usr/bin/env bash
# PostToolUse (Bash) hook.
# When the just-run command created or readied a PR (`gh pr create` / `gh pr ready`),
# inject a mandatory instruction for Claude to review that PR's comments before finishing.
# Reads the PostToolUse payload JSON on stdin; emits a hookSpecificOutput.additionalContext
# JSON object on match, otherwise stays silent and exits 0.

set -euo pipefail

# Fail open when jq is unavailable — the hook is advisory and must never block the tool call.
command -v jq >/dev/null 2>&1 || exit 0

payload="$(cat)"
cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // ""')"

# Match `gh pr create` / `gh pr ready` as an actual subcommand invocation,
# tolerating extra whitespace and compound commands (e.g. `git push && gh pr create`).
if printf '%s' "$cmd" | grep -Eq '(^|[^[:alnum:]_-])gh[[:space:]]+pr[[:space:]]+(create|ready)([[:space:]]|$)'; then
  read -r -d '' context <<'EOF' || true
A pull request was just created or marked ready via `gh pr`. Per this project's policy you MUST review the PR's comments before considering the task complete:
1. Run `gh pr view --comments` for the issue-level comments and review summaries.
2. Run `gh api repos/{owner}/{repo}/pulls/{number}/comments` to fetch inline review threads (replace owner/repo/number, e.g. via `gh pr view --json url,number`).
3. Evaluate every comment, including automated reviewers such as Copilot and CI bots. For each one, either address it (make the fix) or explicitly justify why it does not apply.
4. If no review comments have appeared yet, note that automated reviewers (Copilot/CI) often post within a minute or two — wait briefly and re-check before declaring the task done.
EOF
  jq -n --arg ctx "$context" \
    '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'
fi

exit 0
