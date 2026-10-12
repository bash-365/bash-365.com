#!/usr/bin/env python3
"""Doctrine check — the deterministic half of practicing what we preach.

The site sells a doctrine: **deterministic foundations first, AI as an overlay.**
This script is where that doctrine turns on itself. Every check here is a rule the
"preacher" (`.claude/agents/preacher.md`) would otherwise have to enforce with AI
judgment every week. Once a rule can be mechanized, it moves here — cheaper, faster,
and impossible to skip — so the model is spent only on what genuinely needs judgment.

The design goal is *growth*: this is a registry of checks. When the preacher finds
the repo clean, its job is to convert one more recurring AI-review burden into a new
`@check(...)` function below. Over time the deterministic floor rises and the weekly
AI pass shrinks.

Companion to `scripts/content_lint.py` (editorial contract). This file covers
*structural* doctrine — DRY, single-source-of-truth, and the like — across the repo.

Usage:
    python3 scripts/doctrine_check.py              # run all checks; exit 1 on any error
    python3 scripts/doctrine_check.py --warn-only  # report but always exit 0
    python3 scripts/doctrine_check.py --list       # list the registered checks
    python3 scripts/doctrine_check.py --only DRY-CONTACT
    python3 scripts/doctrine_check.py --self-test  # run inline fixtures
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# --------------------------------------------------------------------------- #
# Findings + the check registry
# --------------------------------------------------------------------------- #


@dataclass
class Finding:
    check: str
    severity: str  # "error" | "warning"
    path: str
    line: int
    message: str
    fix: str = ""


# (id, description, fn) — fn(root: Path) -> list[Finding]
CHECKS: list[tuple[str, str, Callable[[Path], list]]] = []


def check(check_id: str, description: str):
    """Register a doctrine check. The whole point of this file is to grow this list."""

    def decorator(fn: Callable[[Path], list]):
        CHECKS.append((check_id, description, fn))
        return fn

    return decorator


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #

# Customer-facing content that gets rendered — the place a stray hardcoded value
# is a real duplication. Config, data, includes, layouts, docs, tooling, and the
# machine-readable indexes are the *homes* of these values and are never scanned.
CONTENT_GLOBS = ["pages/**/*.md"]
ROOT_CONTENT = ["index.md", "about.md", "contact.md", "tools.md", "ai-operations.md"]

# Directories/paths whose files legitimately hold or reference the canonical
# values (or aren't customer content) — never flagged.
ALLOW_PREFIXES = (
    "_config", "_data/", "_includes/", "_layouts/", "_sass/", "_plugins/",
    ".github/", ".claude/", "docs/", "scripts/", "api/", "extension/", "_site/",
    "vendor/", "drafts/", "node_modules/",
)
ALLOW_FILES = {"CHANGELOG.md", "README.md", "llms.txt", "search.json"}


def content_files(root: Path) -> list[Path]:
    """The set of customer-facing content files a DRY check should police."""
    found: list[Path] = []
    for pattern in CONTENT_GLOBS:
        found.extend(sorted(root.glob(pattern)))
    for name in ROOT_CONTENT:
        p = root / name
        if p.exists():
            found.append(p)
    out = []
    for p in found:
        rel = p.relative_to(root).as_posix()
        if rel in ALLOW_FILES or rel.startswith(ALLOW_PREFIXES):
            continue
        out.append(p)
    return out


def _lineno(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.S)


def strip_frontmatter(text: str) -> str:
    """Blank out YAML frontmatter, preserving line numbers.

    Only the Liquid-processed body can reference the SSOT (`{{ site... }}`);
    values in frontmatter data (FAQ answers, `email:` fields) can't, so scanning
    them would flag things that cannot be fixed. Keep the newlines so reported
    line numbers still line up with the source file.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return text
    return "\n" * m.group(0).count("\n") + text[m.end():]


# --------------------------------------------------------------------------- #
# Checks (grow this section — that is the preacher's standing job)
# --------------------------------------------------------------------------- #

# Contact values with a single source of truth. Keyed pattern -> where the value
# actually lives, so the finding tells the author what to use instead.
_CONTACT_PATTERNS = [
    (re.compile(r"info@(?:bash-365|bashconsultants)\.com"),
     'site.data.entity.info["contact-email"] (or {% include contact-methods.html %})'),
    (re.compile(r"amr@(?:bash-365|bashconsultants)\.com"),
     "site.email"),
    (re.compile(r"\(720\)\s*352-4641|720[.\-]352[.\-]4641|\+1?7203524641"),
     'site.data.entity.info["contact-phone"] (tel via | remove: \'-\')'),
]


@check(
    "DRY-CONTACT",
    "Hardcoded contact values (email/phone) in content that should read from the "
    "single source of truth — _data/entity/info.yml / _config.yml.",
)
def dry_contact(root: Path) -> list[Finding]:
    """DRY / configuration-over-duplication for contact details.

    This is the exact class of redundancy that had the same email + phone
    copy-pasted at the foot of all eight service pages. A Liquid reference like
    `{{ site.data.entity.info["contact-email"] }}` contains no literal address,
    so only genuine hardcoded values are flagged.
    """
    findings: list[Finding] = []
    for path in content_files(root):
        rel = path.relative_to(root).as_posix()
        text = strip_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        for pattern, source in _CONTACT_PATTERNS:
            for m in pattern.finditer(text):
                findings.append(Finding(
                    check="DRY-CONTACT",
                    severity="error",
                    path=rel,
                    line=_lineno(text, m.start()),
                    message=f'hardcoded contact value "{m.group(0)}" — one source of truth only',
                    fix=f"reference {source}",
                ))
    return findings


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #


def run(root: Path, only: str | None, warn_only: bool) -> int:
    selected = [c for c in CHECKS if only is None or c[0] == only]
    if only and not selected:
        print(f"doctrine_check: unknown check '{only}'. Use --list.", file=sys.stderr)
        return 2

    all_findings: list[Finding] = []
    for check_id, _desc, fn in selected:
        all_findings.extend(fn(root))

    n_files = len(content_files(root))
    print(f"doctrine_check: {len(selected)} check(s) over {n_files} content file(s)\n")

    errors = [f for f in all_findings if f.severity == "error"]
    warnings = [f for f in all_findings if f.severity == "warning"]

    by_path: dict[str, list[Finding]] = {}
    for f in all_findings:
        by_path.setdefault(f.path, []).append(f)

    for path in sorted(by_path):
        print(path)
        for f in sorted(by_path[path], key=lambda x: x.line):
            tag = "[ERROR]" if f.severity == "error" else "[WARN]"
            print(f"  {tag} {f.check}: {f.message}:{f.line}")
            if f.fix:
                print(f"          → {f.fix}")
        print()

    print(f"doctrine_check: {len(errors)} error(s), {len(warnings)} warning(s)")
    if errors and not warn_only:
        print("doctrine_check: FAIL")
        return 1
    print("doctrine_check: PASS")
    return 0


# --------------------------------------------------------------------------- #
# Self-test
# --------------------------------------------------------------------------- #

_FIXTURE_BAD = "Email us at info@bash-365.com or call (720) 352-4641 today."
_FIXTURE_GOOD = 'Email us at {{ site.data.entity.info["contact-email"] }} or call {{ site.data.entity.info["contact-phone"] }}.'


def run_self_test() -> int:
    import tempfile

    failures = []
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "pages").mkdir()
        (root / "pages" / "bad.md").write_text(_FIXTURE_BAD, encoding="utf-8")
        (root / "pages" / "good.md").write_text(_FIXTURE_GOOD, encoding="utf-8")
        findings = dry_contact(root)
        bad = [f for f in findings if f.path.endswith("bad.md")]
        good = [f for f in findings if f.path.endswith("good.md")]
        if len(bad) < 2:
            failures.append(f"DRY-CONTACT should flag email+phone in bad.md, got {len(bad)}")
        if good:
            failures.append(f"DRY-CONTACT false-positive on Liquid references: {good}")

    if failures:
        for msg in failures:
            print(f"SELF-TEST FAIL: {msg}", file=sys.stderr)
        return 1
    print(f"doctrine_check: self-test PASS ({len(CHECKS)} check(s) registered)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic doctrine checks for bash-365.com.")
    parser.add_argument("--warn-only", action="store_true", help="report findings but always exit 0")
    parser.add_argument("--list", action="store_true", help="list the registered checks and exit")
    parser.add_argument("--only", metavar="CHECK_ID", help="run only one check by id")
    parser.add_argument("--self-test", action="store_true", help="run inline fixtures instead of the repo")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="repo root to check (default: parent of scripts/)")
    args = parser.parse_args()

    if args.list:
        print("Registered doctrine checks:\n")
        for check_id, desc, _fn in CHECKS:
            print(f"  {check_id}\n      {desc}\n")
        return 0
    if args.self_test:
        return run_self_test()
    return run(args.root, args.only, args.warn_only)


if __name__ == "__main__":
    raise SystemExit(main())
