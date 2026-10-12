#!/usr/bin/env python3
"""Content lint for bash-365.com.

Mechanically enforces the editorial contract defined in
.github/instructions/content-style.instructions.md and posts.instructions.md
across reader-facing Markdown:

  - pages/**/*.md (posts, services, case studies, about collection)
  - index.md, about.md, contact.md at the repo root

Checks (errors fail the build unless --warn-only):
  * posts: required frontmatter fields
    (title, description, author, date, lastmod, categories, tags, preview)
  * description length 120-155 chars (156-160 downgraded to a warning)
  * banned marketing phrases (case-insensitive, word-boundaried;
    fenced/inline code, HTML comments, and Liquid comments are exempt)
  * any truthy `draft:` value (drafts must never ship from main)
  * posts: filename date prefix must equal the frontmatter `date:`
  * posts: categories/tags must be flow-style YAML lists (categories: [a, b])
  * exclamation marks in titles and descriptions

Usage:
  python3 scripts/content_lint.py             # lint the repo, exit 1 on errors
  python3 scripts/content_lint.py --warn-only # report but always exit 0
  python3 scripts/content_lint.py --self-test # run inline fixtures
  python3 scripts/content_lint.py --root PATH # lint a different checkout
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Banned / suspect phrase patterns
# ---------------------------------------------------------------------------

# Hard bans -> errors. (name, compiled regex)
BANNED_PATTERNS = [
    ("cutting-edge", re.compile(r"\bcutting[- ]edge\b", re.I)),
    ("next-generation", re.compile(r"\bnext[- ]generation\b", re.I)),
    ("disruptive", re.compile(r"\bdisruptive\b", re.I)),
    ("revolutionary", re.compile(r"\brevolutionar(?:y|ies)\b", re.I)),
    (
        "in today's ... world/age/era",
        re.compile(
            r"\bin\s+today[’']s\s+[^.\n]{0,40}?\b(world|age|era|landscape|climate|environment)\b",
            re.I,
        ),
    ),
    ("leverage synergies", re.compile(r"\bleverag\w*\s+synerg\w*", re.I)),
    ("unlock value", re.compile(r"\bunlock(?:ing|s)?\s+value\b", re.I)),
    ("best-of-breed", re.compile(r"\bbest[- ]of[- ]breed\b", re.I)),
    ("world-class", re.compile(r"\bworld[- ]class\b", re.I)),
    ("solutioning", re.compile(r"\bsolutioning\b", re.I)),
    ("ideate", re.compile(r"\bideat(?:e|es|ed|ing|ion)\b", re.I)),
    ("circle back", re.compile(r"\bcircl(?:e|ing)\s+back\b", re.I)),
    ("low-hanging fruit", re.compile(r"\blow[- ]hanging\s+fruit\b", re.I)),
]

# Conditional words -> warnings (allowed only with a number/example or a
# named who+what; that judgment can't be automated, so flag for review).
SUSPECT_PATTERNS = [
    ("robust (needs a number or example)", re.compile(r"\brobust(?:ly|ness)?\b", re.I)),
    ("seamless (needs a number or example)", re.compile(r"\bseamless(?:ly)?\b", re.I)),
    ("scalable (needs a number or example)", re.compile(r"\bscalab(?:le|ility)\b", re.I)),
    ("empower (must name who + to do what)", re.compile(r"\bempower(?:s|ed|ing|ment)?\b", re.I)),
]

POST_REQUIRED_FIELDS = [
    "title",
    "description",
    "author",
    "date",
    "lastmod",
    "categories",
    "tags",
    "preview",
]

DESC_MIN = 120
DESC_MAX = 155
DESC_WARN_MAX = 160  # 156-160 chars: warn instead of error

FILENAME_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")


# ---------------------------------------------------------------------------
# Minimal frontmatter reader (no external dependencies)
# ---------------------------------------------------------------------------

def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def split_frontmatter(text: str):
    """Return (frontmatter_text, body_text, body_start_line) or (None, text, 1)."""
    if not text.startswith("---"):
        return None, text, 1
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None, text, 1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            fm = "\n".join(lines[1:idx])
            body = "\n".join(lines[idx + 1:])
            return fm, body, idx + 2
    return None, text, 1


def parse_frontmatter(fm_text: str):
    """Parse the top-level scalar keys and lists this linter cares about.

    Returns (data, key_lines) where key_lines maps key -> 1-based line in the
    frontmatter block. Nested maps are recorded as empty strings.
    """
    data: dict = {}
    key_lines: dict = {}
    lines = fm_text.split("\n")
    i, n = 0, len(lines)
    key_re = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$")
    while i < n:
        m = key_re.match(lines[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2)
        key_lines[key] = i + 1
        # Trailing YAML comment on an unquoted scalar
        if val and not val.startswith(("'", '"', "[")) and " #" in val:
            val = val.split(" #", 1)[0].strip()
        if val in (">", ">-", ">+", "|", "|-", "|+"):
            # Folded / literal block scalar: join indented continuation lines.
            buf = []
            i += 1
            while i < n and (lines[i].startswith((" ", "\t")) or lines[i].strip() == ""):
                if lines[i].strip() == "" and (i + 1 >= n or not lines[i + 1].startswith((" ", "\t"))):
                    break
                if lines[i].strip():
                    buf.append(lines[i].strip())
                i += 1
            data[key] = " ".join(buf)
            continue
        if val == "":
            # Possible block-style list directly under this key.
            items = []
            j = i + 1
            item_re = re.compile(r"^\s+-\s+(.*?)\s*$")
            while j < n:
                im = item_re.match(lines[j])
                if im:
                    items.append(_strip_quotes(im.group(1)))
                    j += 1
                else:
                    break
            if items:
                data[key] = items
                data[key + "__style"] = "block"
                i = j
                continue
            data[key] = ""  # empty value or nested map
            i += 1
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = [_strip_quotes(p) for p in inner.split(",") if p.strip()] if inner else []
            data[key] = items
            data[key + "__style"] = "flow"
            i += 1
            continue
        data[key] = _strip_quotes(val)
        i += 1
    return data, key_lines


# ---------------------------------------------------------------------------
# Body preparation: drop non-reader-facing spans before phrase scanning
# ---------------------------------------------------------------------------

FENCED_CODE_RE = re.compile(r"^(```|~~~).*?^\1\s*$", re.M | re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
LIQUID_COMMENT_RE = re.compile(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", re.S)


def _blank_preserving_lines(match: re.Match) -> str:
    """Replace matched span with whitespace, keeping newlines so line numbers hold."""
    return re.sub(r"[^\n]", " ", match.group(0))


def prepare_body(body: str) -> str:
    body = FENCED_CODE_RE.sub(_blank_preserving_lines, body)
    body = LIQUID_COMMENT_RE.sub(_blank_preserving_lines, body)
    body = HTML_COMMENT_RE.sub(_blank_preserving_lines, body)
    body = INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), body)
    return body


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

class Finding:
    def __init__(self, path, level, code, message, line=None):
        self.path = path
        self.level = level  # "error" | "warning"
        self.code = code
        self.message = message
        self.line = line

    def __str__(self):
        loc = f":{self.line}" if self.line else ""
        return f"  [{self.level.upper():7s}] {self.code}: {self.message}{loc}"


def scan_phrases(path, text, where, findings, base_line=0, errors_only=False):
    """Scan a text span for banned and suspect phrases."""
    for name, pattern in BANNED_PATTERNS:
        for m in pattern.finditer(text):
            line = base_line + text.count("\n", 0, m.start()) + 1 if base_line else None
            findings.append(Finding(
                path, "error", "BANNED_PHRASE",
                f'banned phrase "{m.group(0)}" ({name}) in {where}', line))
    if errors_only:
        return
    for name, pattern in SUSPECT_PATTERNS:
        for m in pattern.finditer(text):
            line = base_line + text.count("\n", 0, m.start()) + 1 if base_line else None
            findings.append(Finding(
                path, "warning", "SUSPECT_PHRASE",
                f'"{m.group(0)}" in {where} — {name}', line))


# ---------------------------------------------------------------------------
# Per-file checks
# ---------------------------------------------------------------------------

def classify(rel_path: str, data: dict) -> str:
    """Return 'post', 'service', 'section-index', or 'page'."""
    parts = rel_path.replace("\\", "/")
    name = parts.rsplit("/", 1)[-1]
    if parts.startswith("pages/_posts/"):
        if name.endswith("-index.md") or str(data.get("index", "")).lower() == "true":
            return "section-index"
        if FILENAME_DATE_RE.match(name):
            return "post"
        return "section-index"
    if parts.startswith("pages/_services/"):
        return "service"
    return "page"


def check_file(root: Path, path: Path) -> list:
    findings = []
    rel = str(path.relative_to(root))
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        findings.append(Finding(rel, "error", "UNREADABLE", f"cannot read file: {exc}"))
        return findings

    fm_text, body, body_start = split_frontmatter(text)
    if fm_text is None:
        findings.append(Finding(rel, "error", "NO_FRONTMATTER", "file has no YAML frontmatter block"))
        scan_phrases(rel, prepare_body(text), "body", findings)
        return findings

    data, key_lines = parse_frontmatter(fm_text)
    kind = classify(rel, data)
    strict = kind in ("post", "service")

    def fm_line(key):
        return key_lines.get(key, None) and key_lines[key] + 1  # +1: fm starts on line 2

    # --- draft blocker (all files) ---
    if "draft" in data:
        draft_val = str(data.get("draft", "")).strip().lower()
        if draft_val in ("true", "yes", "draft", "wip", "pending"):
            findings.append(Finding(
                rel, "error", "DRAFT_TRUE",
                f'draft is "{data.get("draft")}" — drafts must not ship from main '
                f"(set draft: false or move to drafts/)", fm_line("draft")))
        elif draft_val not in ("false", ""):
            findings.append(Finding(
                rel, "warning", "DRAFT_VALUE",
                f'non-standard draft value "{data.get("draft")}" (house style: draft: false)',
                fm_line("draft")))

    title = data.get("title", "") if isinstance(data.get("title"), str) else ""
    description = data.get("description", "") if isinstance(data.get("description"), str) else ""

    # --- exclamation marks in title / description ---
    for field, value in (("title", title), ("description", description)):
        if "!" in value:
            findings.append(Finding(
                rel, "error", "EXCLAMATION",
                f"exclamation mark in {field} (house style: none)", fm_line(field)))

    # --- description length ---
    if description:
        length = len(description)
        if length > DESC_WARN_MAX:
            findings.append(Finding(
                rel, "error" if strict else "warning", "DESC_LONG",
                f"description is {length} chars (must be {DESC_MIN}-{DESC_MAX})",
                fm_line("description")))
        elif length > DESC_MAX:
            findings.append(Finding(
                rel, "warning", "DESC_LONG",
                f"description is {length} chars (target {DESC_MIN}-{DESC_MAX})",
                fm_line("description")))
        elif length < DESC_MIN:
            findings.append(Finding(
                rel, "error" if strict else "warning", "DESC_SHORT",
                f"description is {length} chars (must be {DESC_MIN}-{DESC_MAX})",
                fm_line("description")))
        if description.rstrip().endswith("."):
            findings.append(Finding(
                rel, "warning", "DESC_PERIOD",
                "description ends with a period (house style: no trailing period)",
                fm_line("description")))
    elif strict:
        # Covered again for posts by MISSING_FIELD; services need it too.
        if kind == "service":
            findings.append(Finding(rel, "error", "MISSING_FIELD", "missing description"))
    else:
        findings.append(Finding(rel, "warning", "MISSING_FIELD", "missing description"))

    # --- post frontmatter contract ---
    if kind == "post":
        for field in POST_REQUIRED_FIELDS:
            value = data.get(field)
            if value is None or value == "" or value == []:
                findings.append(Finding(
                    rel, "error", "MISSING_FIELD", f"missing required post field: {field}"))

        # filename date must equal frontmatter date
        name = path.name
        fname_match = FILENAME_DATE_RE.match(name)
        date_val = str(data.get("date", ""))
        if fname_match and date_val:
            if date_val[:10] != fname_match.group(1):
                findings.append(Finding(
                    rel, "error", "DATE_MISMATCH",
                    f"filename date {fname_match.group(1)} != frontmatter date {date_val[:10]}",
                    fm_line("date")))
        for field in ("date", "lastmod"):
            value = str(data.get(field, ""))
            if value and not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$", value):
                findings.append(Finding(
                    rel, "warning", "DATE_FORMAT",
                    f"{field} should be ISO-8601 with milliseconds "
                    f"(YYYY-MM-DDTHH:MM:SS.000Z), got: {value}", fm_line(field)))

        # flow-style lists: categories: [a, b]
        for field in ("categories", "tags"):
            if field in data and data.get(field + "__style") == "block":
                findings.append(Finding(
                    rel, "error", "LIST_STYLE",
                    f"{field} must be a flow-style YAML list, e.g. {field}: [tech, ai]",
                    fm_line(field)))

        preview = str(data.get("preview", ""))
        if preview and not preview.startswith("/images/previews/"):
            findings.append(Finding(
                rel, "warning", "PREVIEW_PATH",
                f"post preview should live under /images/previews/, got: {preview}",
                fm_line("preview")))

        layout = str(data.get("layout", ""))
        if layout and layout not in ("article", "news"):
            findings.append(Finding(
                rel, "warning", "LAYOUT",
                f'post layout is "{layout}" (expected article or news)', fm_line("layout")))

    # --- banned phrases: frontmatter reader-facing strings, then body ---
    for field in ("title", "description", "sub-title", "subtitle", "snippet", "excerpt"):
        value = data.get(field)
        if isinstance(value, str) and value:
            scan_phrases(rel, value, f"frontmatter {field}", findings)
    scan_phrases(rel, prepare_body(body), "body", findings, base_line=body_start - 1)

    return findings


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def collect_files(root: Path) -> list:
    files = sorted(root.glob("pages/**/*.md"))
    for extra in ("index.md", "about.md", "contact.md", "privacy.md"):
        candidate = root / extra
        if candidate.exists():
            files.append(candidate)
    return files


def run_lint(root: Path, warn_only: bool) -> int:
    files = collect_files(root)
    if not files:
        print(f"content_lint: no content files found under {root}", file=sys.stderr)
        return 1

    all_findings = []
    for path in files:
        all_findings.extend(check_file(root, path))

    errors = [f for f in all_findings if f.level == "error"]
    warnings = [f for f in all_findings if f.level == "warning"]

    by_file: dict = {}
    for finding in all_findings:
        by_file.setdefault(finding.path, []).append(finding)

    print(f"content_lint: checked {len(files)} files")
    for file_path in sorted(by_file):
        print(f"\n{file_path}")
        for finding in sorted(by_file[file_path], key=lambda f: (f.line or 0, f.code)):
            print(finding)

    print(f"\ncontent_lint: {len(errors)} error(s), {len(warnings)} warning(s)")
    if errors and not warn_only:
        print("content_lint: FAIL (use --warn-only to report without failing)")
        return 1
    print("content_lint: PASS" + (" (warn-only mode)" if warn_only and errors else ""))
    return 0


# ---------------------------------------------------------------------------
# Self-test fixtures
# ---------------------------------------------------------------------------

GOOD_POST = '''---
title: "A quickbooks migration playbook for denver distributors"
description: "How a Denver distributor moves from QuickBooks to a mid-market ERP in phases, what it typically costs, and where projects go wrong"
author: "Amr Abdel-Motaleb"
layout: article
date: 2026-07-06T12:00:00.000Z
lastmod: 2026-07-06T12:00:00.000Z
draft: false
categories: [erp, migration]
tags: [quickbooks, erp, smb]
preview: /images/previews/a-quickbooks-migration-playbook-for-denver-distri.png
---

## Why this matters

Plain, useful content. Code is exempt from phrase checks:

```bash
echo "this cutting-edge script is fine inside a fence"
```

And `inline world-class code` is exempt too. Next step: [talk to us](/contact/).
'''

BAD_POST = '''---
title: "Our revolutionary new offering!"
description: "Too short and world-class"
author: "Amr Abdel-Motaleb"
layout: article
date: 2026-07-05T12:00:00.000Z
lastmod: 2026-07-05T12:00:00.000Z
draft: true
categories:
  - erp
tags: [erp]
---

In today's fast-paced world we leverage synergies and circle back on
low-hanging fruit with our robust platform.
'''

SELF_TEST_CASES = [
    # (relative path, content, expected error codes, forbidden error codes)
    (
        "pages/_posts/erp/2026-07-06-a-quickbooks-migration-playbook.md",
        GOOD_POST,
        set(),
        {"BANNED_PHRASE", "MISSING_FIELD", "DRAFT_TRUE", "DATE_MISMATCH",
         "LIST_STYLE", "EXCLAMATION", "DESC_SHORT", "DESC_LONG"},
    ),
    (
        "pages/_posts/erp/2026-07-06-bad-post.md",
        BAD_POST,
        {"BANNED_PHRASE", "MISSING_FIELD", "DRAFT_TRUE", "DATE_MISMATCH",
         "LIST_STYLE", "EXCLAMATION", "DESC_SHORT"},
        set(),
    ),
]


def run_self_test() -> int:
    import tempfile

    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel, content, expected, forbidden in SELF_TEST_CASES:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            findings = check_file(root, target)
            got_errors = {f.code for f in findings if f.level == "error"}
            missing = expected - got_errors
            unexpected = got_errors & forbidden
            if missing:
                failures.append(f"{rel}: expected error codes not raised: {sorted(missing)}")
            if unexpected:
                failures.append(f"{rel}: unexpected error codes raised: {sorted(unexpected)}")

        # Focused assertions on the bad fixture
        bad = root / SELF_TEST_CASES[1][0]
        findings = check_file(root, bad)
        errors = [f for f in findings if f.level == "error"]
        banned_hits = {f.message for f in errors if f.code == "BANNED_PHRASE"}
        for needle in ("revolutionary", "world-class", "leverage synergies",
                       "circle back", "low-hanging fruit", "in today's"):
            if not any(needle in msg for msg in banned_hits):
                failures.append(f"bad fixture: banned phrase not detected: {needle}")
        if not any(f.code == "MISSING_FIELD" and "preview" in f.message for f in errors):
            failures.append("bad fixture: missing preview not detected")
        if not any(f.code == "SUSPECT_PHRASE" and "robust" in f.message
                   for f in findings if f.level == "warning"):
            failures.append("bad fixture: suspect word 'robust' not warned")

        # Good fixture must stay clean of errors
        good = root / SELF_TEST_CASES[0][0]
        good_errors = [f for f in check_file(root, good) if f.level == "error"]
        if good_errors:
            failures.append(f"good fixture raised errors: {[str(f) for f in good_errors]}")

    if failures:
        print("content_lint --self-test: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("content_lint --self-test: PASS "
          f"({len(SELF_TEST_CASES)} fixtures, banned-phrase + contract checks)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Editorial lint for bash-365.com content")
    parser.add_argument("--warn-only", action="store_true",
                        help="report findings but always exit 0")
    parser.add_argument("--self-test", action="store_true",
                        help="run inline fixtures instead of linting the repo")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="repo root to lint (default: parent of scripts/)")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_lint(args.root.resolve(), args.warn_only)


if __name__ == "__main__":
    sys.exit(main())
