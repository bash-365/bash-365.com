#!/usr/bin/env python3
"""The vault: this repository, read in place as one linked knowledge base.

This module is the single definition of what a note is and what a link points
at. The generator, the CLI, the brief and the MCP server all resolve links
here, so every surface sees the same graph.

A note is any Markdown file a root in `_data/org/brain.yml` matches. The site
links three ways and all three resolve:

* `[[Page Title]]` wikilinks (the site's Obsidian convention, by title or alias);
* Markdown links to a relative `.md` path, to a site permalink (`/services/erp/`)
  or to the site's own absolute URL;
* Liquid `{% link path %}` tags.

External links are counted, never followed. Anything internal that does not
resolve is reported by `lint`, which observes and fixes nothing.
"""
from __future__ import annotations

import fnmatch
import posixpath
import re
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlparse

from common import (HOME_REPO, ROOT, SOURCES_DIR, as_list, frontmatter, norm, read_text,
                    read_yaml, rel, CONFIG_PATH, summary, tokens)

WIKILINK = re.compile(r"(!?)\[\[([^\[\]\n]+?)\]\]")
MD_LINK = re.compile(r"(?<!!)\[([^\[\]\n]*)\]\(\s*<?([^()\s>]+(?:\([^()\s]*\)[^()\s>]*)*)>?(?:\s+\"[^\"]*\")?\s*\)")
LIQUID_LINK = re.compile(r"\{%-?\s*link\s+([^\s%]+)\s*-?%\}")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)(?:(?!\1).)+?\1")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
LIQUID = re.compile(r"\{\{.*?\}\}|\{%.*?%\}")
DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})-")
SITE_HOSTS = {"bash-365.com", "www.bash-365.com"}
ASSET_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf", ".json", ".txt", ".xml",
             ".css", ".js", ".ico", ".mp4", ".webm", ".zip", ".csv", ".yml", ".yaml"}
GITHUB_BLOB = re.compile(r"^/bash-365/bash-365\.com/(?:blob|tree)/[^/]+/(.+)$")


@dataclass
class Link:
    raw: str
    style: str          # wiki | md | liquid
    line: int
    target: str | None = None   # resolved note path
    kind: str = "internal"      # internal | external | site | asset | repo-file | upstream-file


@dataclass
class Note:
    path: str
    kind: str
    title: str
    description: str
    tags: list[str]
    date: str
    aliases: list[str]
    permalink: str | None
    repo: str
    trust: str
    words: int
    body: str
    links: list[Link] = field(default_factory=list)

    @property
    def untrusted(self) -> bool:
        return self.trust != "first-party"


# --------------------------------------------------------------------------- #
# Reading
# --------------------------------------------------------------------------- #


def load_config() -> dict:
    cfg = read_yaml(CONFIG_PATH, default={}) or {}
    if cfg.get("schema") != "org-brain/v1":
        raise ValueError(f"{rel(CONFIG_PATH)}: schema must be org-brain/v1")
    return cfg


def _excluded(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def discover(cfg: dict, root: Path = ROOT) -> list[tuple[str, str]]:
    """(path, kind) for every note, first matching root wins, sorted by path."""
    seen: dict[str, str] = {}
    excludes = [str(p) for p in cfg.get("exclude") or []]
    for spec in cfg.get("roots") or []:
        for hit in sorted(root.glob(str(spec["glob"]))):
            if not hit.is_file():
                continue
            path = hit.relative_to(root).as_posix()
            if path in seen or _excluded(path, excludes):
                continue
            seen[path] = str(spec["kind"])
    return sorted(seen.items())


def mask_code(body: str) -> str:
    """Blank out fenced and inline code (and comments, Liquid output) but keep line numbers."""
    out, fence = [], None
    for line in body.split("\n"):
        m = FENCE.match(line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            out.append("")
            continue
        if m:
            fence = m.group(1)
            out.append("")
            continue
        out.append(INLINE_CODE.sub(lambda x: " " * len(x.group(0)), line))
    text = "\n".join(out)
    text = HTML_COMMENT.sub(lambda x: "\n" * x.group(0).count("\n"), text)
    return text


def _first_heading(body: str) -> str:
    for line in mask_code(body).split("\n"):
        if line.startswith("# "):
            return line[2:].strip().strip("#").strip()
    return ""


def _first_paragraph(body: str) -> str:
    """The opening paragraph; a leading `>` summary line (the fleet's docs convention) counts."""
    buf: list[str] = []
    for line in mask_code(body).split("\n"):
        s = line.strip()
        if not s:
            if buf:
                break
            continue
        if s.startswith(("#", "|", "<", "{%", "---", "![", "- [", "```", "[!", "**Status")):
            if buf:
                break
            continue
        buf.append(s.lstrip("> ").strip())
    text = LIQUID.sub("", " ".join(buf))
    text = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[*_`]", "", text).strip()


def _site_path(url: str) -> str:
    p = unquote(url.split("#", 1)[0].split("?", 1)[0])
    if not p.startswith("/"):
        p = "/" + p
    p = re.sub(r"/index\.html?$", "/", p)
    if not posixpath.splitext(p)[1] and not p.endswith("/"):
        p += "/"
    return p


def _permalink(path: str, kind: str, fm: dict) -> str | None:
    if fm.get("permalink"):
        return _site_path(str(fm["permalink"]))
    stem = Path(path).stem
    cats = as_list(fm.get("categories"))
    if kind == "page":
        return "/" if stem == "index" else f"/{stem}/"
    if kind == "toolkit" and cats:
        return f"/tools/{cats[0]}/{stem}/"
    if kind == "case-study":
        return f"/case-studies/{stem}/"
    if kind == "service":
        return "/services/" + "".join(f"{c}/" for c in cats) + f"{stem}/"
    return None


def _source_repo(path: str) -> str:
    """brain/sources/<name>/… belongs to the registry entry <name>."""
    parts = path.split("/")
    return parts[2] if len(parts) > 3 and parts[:2] == ["brain", "sources"] else ""


def parse_note(path: str, kind: str, text: str, repo_of: dict[str, str] | None = None) -> Note:
    fm, body, start = frontmatter(text)
    stem = Path(path).stem
    title = str(fm.get("title") or "").strip()
    aliases = as_list(fm.get("aliases"))
    if kind in ("skill", "agent") and fm.get("name"):
        aliases.append(str(fm["name"]))
        title = title or str(fm["name"])
    if kind == "command":
        title = title or f"/{stem}"
    if kind == "skill":
        stem = Path(path).parent.name
    title = title or _first_heading(body) or re.sub(r"\.(prompt|instructions)$", "", stem).replace("-", " ")
    if fm.get("slug"):
        aliases.append(str(fm["slug"]))
    desc = str(fm.get("description") or fm.get("excerpt") or "").strip() or _first_paragraph(body)
    date = str(fm.get("lastmod") or fm.get("date") or "")[:10]
    if not re.match(r"\d{4}-\d{2}-\d{2}$", date):
        m = DATE_PREFIX.match(Path(path).name)
        date = m.group(1) if m else ""
    tags = sorted({t.lower() for t in as_list(fm.get("tags")) + as_list(fm.get("categories"))})
    src = _source_repo(path) if kind == "source" else ""
    repo = (repo_of or {}).get(src, src) if src else HOME_REPO
    note = Note(
        path=path, kind=kind, title=title, description=summary(desc), tags=tags, date=date,
        aliases=sorted(set(a for a in aliases if a)), permalink=_permalink(path, kind, fm),
        repo=repo, trust="untrusted-third-party" if src else "first-party",
        words=len(re.findall(r"\w+", mask_code(body))), body=body,
    )
    note.links = extract_links(body, start)
    return note


def extract_links(body: str, start_line: int = 1) -> list[Link]:
    """Every link, in source order."""
    links: list[Link] = []
    for n, line in enumerate(mask_code(body).split("\n"), start_line):
        found: list[tuple[int, Link]] = []
        for m in WIKILINK.finditer(line):
            if m.group(1) != "!":
                found.append((m.start(), Link(raw=m.group(2).replace("\\|", "|"), style="wiki", line=n)))
        for m in MD_LINK.finditer(line):
            found.append((m.start(), Link(raw=m.group(2), style="md", line=n)))
        for m in LIQUID_LINK.finditer(line):
            found.append((m.start(), Link(raw=m.group(1), style="liquid", line=n)))
        links.extend(link for _, link in sorted(found, key=lambda x: x[0]))
    return links


# --------------------------------------------------------------------------- #
# The vault and its resolver
# --------------------------------------------------------------------------- #


class Vault:
    """Every note, the resolver, and the link graph built from them."""

    def __init__(self, notes: list[Note]):
        self.notes = {n.path: n for n in notes}
        self.by_title: dict[str, list[str]] = defaultdict(list)
        self.by_alias: dict[str, list[str]] = defaultdict(list)
        self.by_stem: dict[str, list[str]] = defaultdict(list)
        self.by_permalink: dict[str, str] = {}
        for n in notes:
            self.by_title[norm(n.title)].append(n.path)
            for a in n.aliases:
                self.by_alias[norm(a)].append(n.path)
            stem = Path(n.path).parent.name if n.path.endswith("SKILL.md") else Path(n.path).stem
            self.by_stem[norm(stem)].append(n.path)
            if n.permalink and n.trust == "first-party":
                self.by_permalink.setdefault(n.permalink, n.path)
        for n in notes:
            for link in n.links:
                self.resolve(link, n)
        self.backlinks: dict[str, set[str]] = defaultdict(set)
        for n in notes:
            for link in n.links:
                if link.target and link.target != n.path:
                    self.backlinks[link.target].add(n.path)

    # -- resolution --------------------------------------------------------- #

    def _pick(self, candidates: list[str], src: Note) -> str | None:
        if not candidates:
            return None
        same = [c for c in candidates if self.notes[c].repo == src.repo]
        pool = same or candidates
        return sorted(pool)[0]

    def _by_path(self, path: str) -> str | None:
        path = posixpath.normpath(path)
        while path.startswith("./"):
            path = path[2:]
        path = "" if path == "." else path.lstrip("/")
        for cand in (path, path + ".md", posixpath.join(path, "README.md"), posixpath.join(path, "index.md")):
            if cand in self.notes:
                return cand
        return None

    def lookup(self, target: str, src: Note | None = None) -> str | None:
        """Resolve a bare name (title, alias, path or stem) the way a wikilink does."""
        t = target.split("|", 1)[0].split("#", 1)[0].strip()
        if not t:
            return None
        hit = self._by_path(t)
        if hit:
            return hit
        key = norm(t)
        probe = src or Note("", "", "", "", [], "", [], None, HOME_REPO, "first-party", 0, "")
        for table in (self.by_title, self.by_alias, self.by_stem):
            hit = self._pick(table.get(key, []), probe)
            if hit:
                return hit
        return None

    def resolve(self, link: Link, src: Note) -> None:
        raw = link.raw.strip()
        if link.style == "wiki":
            link.target = self.lookup(raw, src)
            return
        if link.style == "liquid":
            link.target = self._by_path(raw)
            return
        parsed = urlparse(raw)
        if parsed.scheme in ("mailto", "tel", "javascript", "data"):
            link.kind = "external"
            return
        if parsed.scheme in ("http", "https"):
            host = (parsed.hostname or "").lower()
            if host in SITE_HOSTS:
                raw = parsed.path or "/"
            elif host == "github.com" and GITHUB_BLOB.match(parsed.path):
                path = GITHUB_BLOB.match(parsed.path).group(1)
                link.target = self._by_path(path)
                if link.target is None and (ROOT / path).exists():
                    link.kind = "repo-file"
                return
            else:
                link.kind = "external"
                return
        if raw.startswith("#") or not raw:
            link.kind = "external"
            return
        if raw.startswith("/"):
            site = _site_path(raw)
            if posixpath.splitext(site)[1].lower() in ASSET_EXT:
                link.kind = "asset"
                return
            link.kind = "site"
            link.target = self.by_permalink.get(site)
            return
        path = unquote(raw.split("#", 1)[0].split("?", 1)[0])
        if posixpath.splitext(path)[1].lower() in ASSET_EXT:
            link.kind = "asset"
            return
        base = posixpath.dirname(src.path)
        joined = posixpath.normpath(posixpath.join(base, path))
        if joined.startswith(".."):
            link.kind = "external"
            return
        link.target = self._by_path(joined)
        if link.target is None and src.trust == "first-party" and (ROOT / joined).exists():
            link.kind = "repo-file"   # a real file or directory that is not a vault note
        elif link.target is None and src.trust != "first-party":
            link.kind = "upstream-file"   # a path in the snapshotted repo; only part of it is copied here

    # -- graph queries ------------------------------------------------------ #

    def outlinks(self, path: str) -> list[str]:
        note = self.notes[path]
        return sorted({l.target for l in note.links if l.target and l.target != path})

    def neighbours(self, path: str, depth: int = 1) -> dict[str, int]:
        """Notes within `depth` links of `path`, either direction: {path: distance}."""
        seen = {path: 0}
        queue = deque([path])
        while queue:
            cur = queue.popleft()
            if seen[cur] >= depth:
                continue
            for nxt in set(self.outlinks(cur)) | self.backlinks.get(cur, set()):
                if nxt not in seen:
                    seen[nxt] = seen[cur] + 1
                    queue.append(nxt)
        seen.pop(path)
        return dict(sorted(seen.items(), key=lambda kv: (kv[1], kv[0])))

    def search(self, query: str, limit: int = 10, include_untrusted: bool = True) -> list[dict]:
        """Rank notes for a query: title > tags/aliases > description > body."""
        qt = tokens(query)
        if not qt:
            return []
        rows = []
        for n in self.notes.values():
            if n.untrusted and not include_untrusted:
                continue
            title_t = set(tokens(n.title)) | set(tokens(" ".join(n.aliases)))
            tag_t = set(tokens(" ".join(n.tags)))
            desc_t = set(tokens(n.description))
            body = Counter(tokens(mask_code(n.body)))
            score = 0.0
            for t in qt:
                score += 4.0 * (t in title_t) + 2.5 * (t in tag_t) + 1.5 * (t in desc_t)
                score += min(body.get(t, 0), 8) * 0.25
            if score <= 0:
                continue
            if all(t in title_t | tag_t | desc_t or body.get(t) for t in qt):
                score *= 1.5            # every term present somewhere
            if n.kind in ("governance", "rule", "note", "skill"):
                score *= 1.15           # the rules outrank the prose that follows them
            score += 0.05 * len(self.backlinks.get(n.path, ()))
            rows.append({"path": n.path, "title": n.title, "kind": n.kind, "repo": n.repo,
                         "trust": n.trust, "description": n.description, "score": round(score, 2)})
        rows.sort(key=lambda r: (-r["score"], r["path"]))
        return rows[:limit]

    # -- health -------------------------------------------------------------- #

    def lint(self) -> list[dict]:
        """Findings: unresolved internal links, orphans, notes with no description."""
        out: list[dict] = []
        for n in sorted(self.notes.values(), key=lambda x: x.path):
            third = n.untrusted
            for l in n.links:
                if l.target or l.kind in ("external", "asset", "repo-file", "upstream-file"):
                    continue
                if l.kind == "site":
                    sev = "info"        # a route a layout may generate (section indexes, feeds)
                elif l.style == "wiki":
                    sev = "info" if third else "warning"
                else:
                    sev = "info" if third else "warning"
                out.append({"severity": sev, "check": "unresolved-link", "path": n.path, "line": l.line,
                            "message": f"{l.style} link to {l.raw!r} does not resolve to a vault note"})
            if not third and not n.description and n.kind not in ("command",):
                out.append({"severity": "info", "check": "no-description", "path": n.path, "line": 1,
                            "message": "no description: add `description:` front matter or an opening paragraph"})
            if n.kind == "note":
                fm, _, _ = frontmatter(read_text(ROOT / n.path))
                for key in ("title", "description"):
                    if not fm.get(key):
                        out.append({"severity": "error", "check": "note-front-matter", "path": n.path, "line": 1,
                                    "message": f"brain note is missing `{key}:` front matter"})
        linked_kinds = {"toolkit", "service", "case-study", "rule", "skill", "note", "operations", "decision"}
        for n in sorted(self.notes.values(), key=lambda x: x.path):
            if n.kind in linked_kinds and not self.backlinks.get(n.path) and not self.outlinks(n.path):
                out.append({"severity": "info", "check": "orphan", "path": n.path, "line": 1,
                            "message": "no links in or out: nothing in the vault leads here"})
        return out


def build_vault(root: Path = ROOT, cfg: dict | None = None, repo_of: dict[str, str] | None = None) -> Vault:
    cfg = cfg or load_config()
    notes = [parse_note(path, kind, read_text(root / path), repo_of) for path, kind in discover(cfg, root)]
    return Vault(notes)


def source_repo_map(registry: dict) -> dict[str, str]:
    """Snapshot directory name → owner/name, from the registry."""
    return {str(r["name"]): str(r["repo"]) for r in (registry.get("repos") or [])}


__all__ = ["Link", "Note", "Vault", "build_vault", "discover", "extract_links", "load_config",
           "mask_code", "parse_note", "source_repo_map", "SOURCES_DIR"]
