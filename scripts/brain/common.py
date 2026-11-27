#!/usr/bin/env python3
"""Shared plumbing for the org brain (`scripts/brain/`).

Standard library only, like every script in this repo. Nothing here is new
parsing: data files go through the content loop's YAML-subset reader
(`scripts/loop/_lib.py`), front matter through the content linter's parser
(`scripts/content_lint.py`), and credential masking through the loop's
`scrub()`. One parser per format keeps every tool in the repo agreeing on what
a file says.
"""
from __future__ import annotations

import hashlib
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "_data" / "org"
REPOS_PATH = DATA_DIR / "repos.yml"
STANDARD_PATH = DATA_DIR / "standard.yml"
CONFIG_PATH = DATA_DIR / "brain.yml"
BRAIN_DIR = ROOT / "brain"
NOTES_DIR = BRAIN_DIR / "notes"
SOURCES_DIR = BRAIN_DIR / "sources"
GENERATED_DIR = BRAIN_DIR / "generated"
GRAPH_PATH = BRAIN_DIR / "graph.json"

for _p in (ROOT / "scripts" / "loop", ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _lib as looplib  # noqa: E402  (scripts/loop/_lib.py)
import content_lint  # noqa: E402  (scripts/content_lint.py)

YamlError = looplib.YamlError
load_yaml = looplib.load_yaml
dump_yaml = looplib.dump_yaml
scrub = looplib.scrub
slugify = looplib.slugify
one_line = looplib.one_line

HOME_REPO = "bash-365/bash-365.com"
SUMMARY_LIMIT = 180

# Zero-width and bidi control characters: invisible in a rendered page, but an
# agent reading the raw text sees whatever they hide. Stripped from every
# snapshot of another repository before it is committed.
HIDDEN_CHARS = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff]")


def read_yaml(path: Path, default=None):
    """Read a data file with the loop's subset reader; a missing file is `default`."""
    if not path.exists():
        return default
    return load_yaml(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def rel(path: Path) -> str:
    """Repository-relative POSIX path."""
    return path.resolve().relative_to(ROOT).as_posix()


def norm(text: str) -> str:
    """Fold a title for lookup: case, punctuation and spacing don't count."""
    text = unicodedata.normalize("NFKC", str(text)).casefold()
    text = re.sub(r"[^\w\s-]", " ", text)
    return " ".join(text.replace("_", " ").replace("-", " ").split())


def tokens(text: str) -> list[str]:
    return [t for t in norm(text).split() if len(t) > 1]


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def strip_hidden(text: str) -> str:
    return HIDDEN_CHARS.sub("", text)


def frontmatter(text: str) -> tuple[dict, str, int]:
    """(data, body, body_start_line) using the content linter's parser."""
    fm, body, start = content_lint.split_frontmatter(text)
    if fm is None:
        return {}, text, 1
    data, _ = content_lint.parse_frontmatter(fm)
    return {k: v for k, v in data.items() if not k.endswith("__style")}, body, start


def as_list(value) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [p.strip() for p in str(value).split(",") if p.strip()]


def summary(text: str, limit: int = SUMMARY_LIMIT) -> str:
    """One line, cut on a word boundary."""
    s = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(s) <= limit:
        return s
    cut = s[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:.")
    return cut + "…"


def md_escape_cell(text: str) -> str:
    """Make text safe inside a Markdown table cell."""
    return str(text or "").replace("|", "\\|").replace("\n", " ")


def relpath(target: str, start_dir: str) -> str:
    """A POSIX relative link from one repo-relative directory to a repo-relative path."""
    import posixpath

    return posixpath.relpath(target, start_dir or ".")


def fence_untrusted(text: str, repo: str, path: str) -> str:
    """Wrap another repository's text so a reader (or a model) knows it is data.

    A fence tag inside the text has its `<` escaped, so the text cannot close the
    fence early and read as the brain's own words (the README engine's rule).
    """
    safe = re.sub(r"<(\s*/?\s*untrusted-doc)", r"&lt;\1", text, flags=re.I)
    return f'<untrusted-doc repo="{repo}" path="{path}">\n{safe.rstrip()}\n</untrusted-doc>'
