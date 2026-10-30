#!/usr/bin/env bash
# Run zer0-CMS's LinkedIn lane (`manage.py linkedin`) over this site.
#
# The one place that knows where zer0-CMS lives and which Python runs it, so the
# linkedin-share skill, /linkedin-draft, .mcp.json and the docs call this rather
# than a path inside zer0-CMS that its next restructure moves.
#
#   scripts/linkedin.sh status
#   scripts/linkedin.sh draft tech/2026-10-29-some-post
#   scripts/linkedin.sh preview 2026-10-29-some-post
#   scripts/linkedin.sh mcp
#
# ZER0_CMS_DIR     the zer0-CMS checkout (default: ../zer0-CMS beside this repo)
# ZER0_CMS_PYTHON  a Python with its content/requirements.txt installed
#                  (default: the checkout's content/.venv)
#
# Errors go to stderr only: under `mcp`, stdout is the JSON-RPC channel.

set -euo pipefail

site="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cms="${ZER0_CMS_DIR:-$site/../zer0-CMS}"
python="${ZER0_CMS_PYTHON:-$cms/content/.venv/bin/python}"

if [ ! -f "$cms/content/manage.py" ]; then
  echo "linkedin.sh: no zer0-CMS at $cms (clone bamr87/zer0-CMS there, or set ZER0_CMS_DIR)" >&2
  exit 2
fi
if [ ! -x "$python" ]; then
  echo "linkedin.sh: no Python at $python. Create it once:" >&2
  echo "  python3 -m venv $cms/content/.venv && $cms/content/.venv/bin/pip install -r $cms/content/requirements.txt" >&2
  echo "or set ZER0_CMS_PYTHON." >&2
  exit 2
fi
if [ $# -eq 0 ]; then
  echo "usage: scripts/linkedin.sh COMMAND [args] — COMMAND as in manage.py linkedin (help: scripts/linkedin.sh help)" >&2
  exit 2
fi

command="$1"
shift
exec "$python" "$cms/content/manage.py" linkedin "$command" --site "$site" "$@"
