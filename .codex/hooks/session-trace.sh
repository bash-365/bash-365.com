#!/usr/bin/env bash
# SessionEnd hook — record what this Claude Code session touched, for the
# content loop (docs/content-loop.md). Cheap, non-blocking, never fails a
# session: it hands the hook payload on stdin to scripts/loop/trace.py, which
# appends ONE scrubbed metadata line (session id, intent, files, commits — never
# the transcript) to the local, gitignored queue .claude/loop/sessions.jsonl.
# Fold the queue into the committed trace with `python3 scripts/loop/trace.py --sync`.
root="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
command -v python3 >/dev/null 2>&1 || exit 0
python3 "$root/scripts/loop/trace.py" append 2>/dev/null || true
exit 0
