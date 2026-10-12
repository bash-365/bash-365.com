#!/usr/bin/env python3
"""Shared helpers for the content loop scripts (`scripts/loop/`).

Standard library only, like every other script in this repo: the loop must run
on a bare GitHub runner *and* on a laptop with nothing installed, and it must
behave identically in both places.

What lives here:

  * a strict YAML **subset** reader/writer — enough for `_data/loop/*.yml` (plain
    `key: value`, nested maps, block and flow lists, quoted strings, numbers,
    booleans, comments). It refuses block scalars, anchors, and flow maps on
    purpose: the loop's data files stay simple enough that a human can read
    them and a 200-line parser can trust them;
  * a `git` wrapper that returns "" instead of raising;
  * `scrub()`, which masks anything that looks like a credential before a line
    of text is written to a file that will be committed;
  * the house slug rule (docs/preview-images.md) and small date helpers.

    python3 scripts/loop/_lib.py --self-test
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOOP_DATA = ROOT / "_data" / "loop"
RUNS_DIR = LOOP_DATA / "runs"
CONFIG_PATH = LOOP_DATA / "config.yml"
SOURCES_PATH = LOOP_DATA / "sources.yml"
SESSIONS_PATH = LOOP_DATA / "sessions.jsonl"
LOCAL_QUEUE = ROOT / ".claude" / "loop" / "sessions.jsonl"
WORK_DIR = ROOT / ".loop"

# The four post sections (pages/_posts/<section>/), in _data/taxonomy.yml order.
SECTIONS = ("corp", "erp", "muses", "tech")


class YamlError(ValueError):
    """Raised for anything outside the supported YAML subset."""


# --------------------------------------------------------------------------- #
# YAML subset — reader
# --------------------------------------------------------------------------- #

_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
_INLINE_PAIR_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*):(?:\s+(.*))?$")
_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$")


def _tokenize(text: str) -> list[tuple[int, str, int]]:
    """(indent, content, line_no) for every meaningful line.

    A `- key: value` list item is split into a `-` token and a `key: value`
    token two columns deeper, which is exactly how YAML defines it — so a list
    of maps parses with the same code path as any other map.
    """
    out: list[tuple[int, str, int]] = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lead = line[: len(line) - len(line.lstrip())]
        if "\t" in lead:
            raise YamlError(f"line {n}: tabs are not allowed in indentation")
        indent = len(lead)
        if stripped.startswith("- ") and not stripped[2:].lstrip().startswith(("'", '"', "[", "{")):
            body = stripped[2:].strip()
            if _INLINE_PAIR_RE.match(body):
                out.append((indent, "-", n))
                out.append((indent + 2, body, n))
                continue
            if body.startswith("- "):
                raise YamlError(f"line {n}: nested inline lists (`- - x`) are not supported")
        out.append((indent, stripped, n))
    return out


def _split_comment(rest: str, n: int) -> str:
    """Drop a trailing ` # comment` from a scalar without touching quoted text."""
    if not rest:
        return rest
    if rest[0] in "\"'":
        q = rest[0]
        i = 1
        while i < len(rest):
            if rest[i] == "\\" and q == '"':
                i += 2
                continue
            if rest[i] == q:
                if q == "'" and i + 1 < len(rest) and rest[i + 1] == "'":
                    i += 2
                    continue
                break
            i += 1
        if i >= len(rest):
            raise YamlError(f"line {n}: unterminated quoted string")
        tail = rest[i + 1:].strip()
        if tail and not tail.startswith("#"):
            raise YamlError(f"line {n}: unexpected text after a quoted string: {tail!r}")
        return rest[: i + 1]
    if rest[0] == "[":
        depth = 0
        in_q = ""
        for i, ch in enumerate(rest):
            if in_q:
                if ch == in_q:
                    in_q = ""
                continue
            if ch in "\"'":
                in_q = ch
            elif ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    tail = rest[i + 1:].strip()
                    if tail and not tail.startswith("#"):
                        raise YamlError(f"line {n}: unexpected text after a flow list: {tail!r}")
                    return rest[: i + 1]
        raise YamlError(f"line {n}: unterminated flow list")
    m = re.search(r"\s#", rest)
    return rest[: m.start()].rstrip() if m else rest


def _split_flow_items(inner: str) -> list[str]:
    items: list[str] = []
    buf = ""
    in_q = ""
    for ch in inner:
        if in_q:
            buf += ch
            if ch == in_q:
                in_q = ""
            continue
        if ch in "\"'":
            in_q = ch
            buf += ch
        elif ch == ",":
            items.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        items.append(buf.strip())
    return items


def _parse_scalar(s: str, n: int):
    s = s.strip()
    if s == "":
        return None
    if s[0] == '"':
        try:
            return json.loads(s)
        except json.JSONDecodeError as exc:
            raise YamlError(f"line {n}: bad double-quoted string ({exc.msg})") from None
    if s[0] == "'":
        if len(s) < 2 or s[-1] != "'":
            raise YamlError(f"line {n}: bad single-quoted string")
        return s[1:-1].replace("''", "'")
    if s[0] == "[":
        if s[-1] != "]":
            raise YamlError(f"line {n}: bad flow list")
        inner = s[1:-1].strip()
        return [] if not inner else [_parse_scalar(it, n) for it in _split_flow_items(inner)]
    if s == "{}":
        return {}
    if s[0] == "{":
        raise YamlError(f"line {n}: flow maps are not supported — use nested keys")
    if s[0] in "|>":
        raise YamlError(f"line {n}: block scalars are not supported — use a quoted string")
    if s[0] in "&*!":
        raise YamlError(f"line {n}: anchors, aliases, and tags are not supported")
    low = s.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if low in ("null", "~"):
        return None
    if _INT_RE.match(s):
        return int(s)
    if _FLOAT_RE.match(s):
        return float(s)
    return s


def _parse_block(toks, i, indent):
    ind, s, n = toks[i]
    if ind != indent:
        raise YamlError(f"line {n}: unexpected indent")
    if s == "-" or s.startswith("- "):
        return _parse_list(toks, i, indent)
    return _parse_map(toks, i, indent)


def _parse_map(toks, i, indent):
    obj: dict = {}
    while i < len(toks):
        ind, s, n = toks[i]
        if ind < indent:
            break
        if ind > indent:
            raise YamlError(f"line {n}: unexpected indent")
        if s == "-" or s.startswith("- "):
            break
        key, sep, rest = s.partition(":")
        key = key.strip()
        if not sep or not _KEY_RE.match(key) or (rest and not rest.startswith(" ")):
            raise YamlError(f"line {n}: expected `key: value`, got {s!r}")
        if key in obj:
            raise YamlError(f"line {n}: duplicate key {key!r}")
        rest = _split_comment(rest.strip(), n)
        if rest == "":
            nxt = toks[i + 1] if i + 1 < len(toks) else None
            if nxt and nxt[0] > indent:
                val, i = _parse_block(toks, i + 1, nxt[0])
            elif nxt and nxt[0] == indent and (nxt[1] == "-" or nxt[1].startswith("- ")):
                val, i = _parse_list(toks, i + 1, indent)
            else:
                val, i = None, i + 1
        else:
            val, i = _parse_scalar(rest, n), i + 1
        obj[key] = val
    return obj, i


def _parse_list(toks, i, indent):
    items: list = []
    while i < len(toks):
        ind, s, n = toks[i]
        if ind < indent:
            break
        if ind > indent:
            raise YamlError(f"line {n}: unexpected indent inside a list")
        if not (s == "-" or s.startswith("- ")):
            break
        body = s[1:].strip()
        if body == "":
            nxt = toks[i + 1] if i + 1 < len(toks) else None
            if nxt and nxt[0] > indent:
                val, i = _parse_block(toks, i + 1, nxt[0])
            else:
                val, i = None, i + 1
        else:
            val, i = _parse_scalar(_split_comment(body, n), n), i + 1
        items.append(val)
    return items, i


def load_yaml(text: str):
    """Parse the supported YAML subset. Empty input -> None."""
    toks = _tokenize(text)
    if not toks:
        return None
    val, i = _parse_block(toks, 0, toks[0][0])
    if i < len(toks):
        raise YamlError(f"line {toks[i][2]}: trailing content at an unexpected indent")
    return val


def read_yaml(path: Path, default=None):
    if not path.exists():
        return default
    val = load_yaml(path.read_text(encoding="utf-8"))
    return default if val is None else val


# --------------------------------------------------------------------------- #
# YAML subset — writer (maps, lists of scalars, lists of flat maps)
# --------------------------------------------------------------------------- #

def _scalar_out(v) -> str:
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return repr(v)
    return json.dumps(str(v), ensure_ascii=False)


def _dump(obj, indent: int, lines: list[str]) -> None:
    pad = " " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not _KEY_RE.match(str(k)):
                raise YamlError(f"cannot write key {k!r}")
            if isinstance(v, dict):
                if not v:
                    lines.append(f"{pad}{k}: {{}}")
                else:
                    lines.append(f"{pad}{k}:")
                    _dump(v, indent + 2, lines)
            elif isinstance(v, (list, tuple)):
                if not v:
                    lines.append(f"{pad}{k}: []")
                else:
                    lines.append(f"{pad}{k}:")
                    _dump(list(v), indent + 2, lines)
            else:
                lines.append(f"{pad}{k}: {_scalar_out(v)}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                if not item:
                    lines.append(f"{pad}- {{}}")
                    continue
                first = True
                for k, v in item.items():
                    if isinstance(v, (dict, list, tuple)):
                        raise YamlError("lists of maps may only hold scalar values")
                    lead = f"{pad}- " if first else f"{pad}  "
                    lines.append(f"{lead}{k}: {_scalar_out(v)}")
                    first = False
            elif isinstance(item, (list, tuple)):
                raise YamlError("nested lists are not supported")
            else:
                lines.append(f"{pad}- {_scalar_out(item)}")
    else:
        lines.append(f"{pad}{_scalar_out(obj)}")


def dump_yaml(obj, header: str = "") -> str:
    """Serialize to the subset `load_yaml` reads back byte-for-byte."""
    lines: list[str] = []
    _dump(obj, 0, lines)
    body = "\n".join(lines) + "\n"
    return (header.rstrip("\n") + "\n" + body) if header else body


# --------------------------------------------------------------------------- #
# git, dates, slugs, scrubbing
# --------------------------------------------------------------------------- #

def git(*args: str, cwd: Path | None = None, default: str = "") -> str:
    """Run git and return stdout, or `default` when git is missing or fails."""
    try:
        res = subprocess.run(["git", *args], cwd=str(cwd or ROOT), capture_output=True,
                             text=True, encoding="utf-8", errors="replace", check=False)
    except (OSError, ValueError):
        return default
    return res.stdout if res.returncode == 0 else default


def repo_slug() -> str:
    """`owner/repo` of the checkout, from origin or GITHUB_REPOSITORY."""
    env = os.environ.get("GITHUB_REPOSITORY", "").strip()
    url = git("remote", "get-url", "origin").strip()
    m = re.search(r"[:/]([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else env


def today() -> _dt.date:
    """Today in UTC; `LOOP_TODAY=YYYY-MM-DD` pins it for reproducible runs and tests."""
    pinned = os.environ.get("LOOP_TODAY", "").strip()
    if pinned:
        return _dt.date.fromisoformat(pinned)
    return _dt.datetime.now(_dt.timezone.utc).date()


def parse_date(value) -> _dt.date | None:
    """YYYY-MM-DD (or any ISO-8601 stamp starting with one) -> date, else None."""
    if isinstance(value, _dt.date):
        return value
    s = str(value or "").strip()
    try:
        return _dt.date.fromisoformat(s[:10])
    except ValueError:
        return None


def slugify(title: str, limit: int = 50) -> str:
    """The house slug: lowercase, non-alphanumeric runs -> `-`, edges stripped,
    truncated to 50 (a trailing `-` left by truncation is kept — docs/preview-images.md)."""
    s = re.sub(r"[^a-z0-9]+", "-", str(title).lower()).strip("-")
    return s[:limit]


_SECRET_PATTERNS = [
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}"), "sk-ant-***"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"), "sk-***"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "gh*_***"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "github_pat_***"),
    (re.compile(r"\bAKIA[0-9A-Z]{12,}"), "AKIA***"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), "xox*-***"),
    (re.compile(r"\bphx_[A-Za-z0-9]{10,}"), "phx_***"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "eyJ***"),
    (re.compile(r"(?i)\b(bearer\s+)[A-Za-z0-9._~+/=-]{16,}"), r"\1***"),
    (re.compile(r"(?i)\b((?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|token|secret|password)"
                r"[\"']?\s*[:=]\s*[\"']?)([^\s\"',;]{8,})"), r"\1***"),
]


def scrub(text: str) -> str:
    """Mask anything that looks like a credential. Cheap, conservative, and
    applied to every string the loop writes into a committed file."""
    out = str(text or "")
    for pat, repl in _SECRET_PATTERNS:
        out = pat.sub(repl, out)
    return out


def one_line(text: str, limit: int = 240) -> str:
    """Collapse whitespace and cap length — for intents, summaries, PR excerpts."""
    s = re.sub(r"\s+", " ", str(text or "")).strip()
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


# --------------------------------------------------------------------------- #
# self-test
# --------------------------------------------------------------------------- #

_FIXTURE = '''
# a comment
cadence:
  new_every_days: 2   # trailing comment
  ratio: 1.5
sections:
  ring: [tech, corp, "erp", 'muses']
empty_list: []
empty_map: {}
nothing:
flag: true
off_flag: no
name: "quoted: with # hash"
single: 'it''s'
plain: plain text with: colon inside
repos:
  - slug: bash-365/bash-365.com
    via: git
    weight: 1.0
  - slug: bamr87/lifehacker.dev
    via: github
    weight: 0.6
same_indent_list:
- a
- b
nested:
  deeper:
    deepest: 3
'''


def self_test() -> int:
    failures: list[str] = []

    def check(name: str, got, want) -> None:
        if got != want:
            failures.append(f"{name}: got {got!r}, want {want!r}")

    data = load_yaml(_FIXTURE)
    check("nested int", data["cadence"]["new_every_days"], 2)
    check("float", data["cadence"]["ratio"], 1.5)
    check("flow list", data["sections"]["ring"], ["tech", "corp", "erp", "muses"])
    check("empty list", data["empty_list"], [])
    check("empty map", data["empty_map"], {})
    check("null", data["nothing"], None)
    check("bool", data["flag"], True)
    check("no -> False", data["off_flag"], False)
    check("double-quoted", data["name"], "quoted: with # hash")
    check("single-quoted", data["single"], "it's")
    check("plain with colon", data["plain"], "plain text with: colon inside")
    check("list of maps", data["repos"][1], {"slug": "bamr87/lifehacker.dev", "via": "github", "weight": 0.6})
    check("list at key indent", data["same_indent_list"], ["a", "b"])
    check("deep map", data["nested"]["deeper"]["deepest"], 3)

    for bad, why in [("k: |\n  x\n", "block scalar"), ("k: {a: 1}\n", "flow map"),
                     ("k: &a 1\n", "anchor"), ("k: 1\nk: 2\n", "duplicate key"),
                     ("k:\n\t- a\n", "tab indent"), ("- - a\n", "nested inline list")]:
        try:
            load_yaml(bad)
            failures.append(f"accepted unsupported input ({why})")
        except YamlError:
            pass

    rec = {"id": "2026-09-05-new-x", "date": "2026-09-05", "mode": "new", "n": 3, "ok": True,
           "none": None, "signals": ["session:abc", "pr:38"], "empty": [],
           "nested": {"a": 1, "b": ["x"]}, "rows": [{"k": "v", "n": 1}, {"k": "w", "n": 2}],
           "title": 'He said "hi" — naïve: yes'}
    text = dump_yaml(rec, header="# header")
    check("dump header", text.startswith("# header\n"), True)
    check("round-trip", load_yaml(text), rec)
    check("round-trip twice", dump_yaml(load_yaml(text), header="# header"), text)

    check("slug: bashos", slugify("bashos: the new command-line operating system"),
          "bashos-the-new-command-line-operating-system")
    check("slug: 50 chars kept", slugify("Your best programmer thinks they're just good at Excel"),
          "your-best-programmer-thinks-they-re-just-good-at-e")
    check("slug: quickbooks", slugify("When the numbers say it's time to leave QuickBooks"),
          "when-the-numbers-say-it-s-time-to-leave-quickbooks")

    scrubbed = scrub("key sk-ant-api03-abcdefghijklmnop and ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234 "
                     "and github_pat_11AAAAAAA0bbbbbbbbbbbbbbbbb and AKIAIOSFODNN7EXAMPLE "
                     "and Bearer abcdefghijklmnopqrstuvwxyz and password=hunter2hunter2 "
                     "and xoxb-1234567890-abcdefghij and phx_abcdefghijklmnop and plain words")
    for leak in ("api03-abcdefghijklmnop", "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234", "11AAAAAAA0bbbb",
                 "IOSFODNN7EXAMPLE", "abcdefghijklmnopqrstuvwxyz", "hunter2hunter2",
                 "1234567890-abcdefghij", "phx_abcdefghijklmnop"):
        if leak in scrubbed:
            failures.append(f"scrub leaked {leak!r}")
    check("scrub keeps prose", "plain words" in scrubbed, True)
    check("one_line", one_line("  a \n b   c  ", limit=4), "a b…")
    check("one_line fits", one_line("  a \n b   c  ", limit=5), "a b c")
    check("parse_date", parse_date("2026-09-05T12:00:00.000Z"), _dt.date(2026, 9, 5))
    check("parse_date bad", parse_date("nope"), None)

    if failures:
        print("_lib --self-test: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("_lib --self-test: PASS (yaml subset round-trip, slug rule, scrubber, dates)")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    print(__doc__)
