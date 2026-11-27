#!/usr/bin/env python3
"""The organization: its registry, its agent-readiness standard, the audit, the
snapshots of other org repos, and the brief an agent reads before contributing.

Read-only toward every repository except this one: `sync` clones (or reads a
local checkout of) each member repo and copies its agent-facing docs into
`brain/sources/<name>/`, redacted and stripped of hidden characters. Nothing
here pushes, opens a pull request, or writes outside `brain/`.
"""
from __future__ import annotations

import json
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from common import (HOME_REPO, NOTES_DIR, REPOS_PATH, ROOT, SOURCES_DIR, STANDARD_PATH, YamlError,
                    fence_untrusted, read_text, read_yaml, rel, scrub, strip_hidden, summary)

ROLES = {"member", "upstream"}
STATUSES = {"active", "maintenance", "archived", "experiment"}
LEVELS = {"must", "should"}
REQUIRED_REPO_KEYS = ("name", "repo", "role", "branch", "status", "kind", "summary", "agent_file")
SIX_HEADINGS = ("what this repo is", "stack & commands", "layout", "conventions", "fleet context",
                "standard deviations")
# Files a check reads or tests for; `sync` records their presence for every member.
CHECK_FILES = ("AGENTS.md", "CLAUDE.md", "README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md",
               "docs/constitution.md", "features/features.yml", ".github/workflows/ci.yml")
COPY_TEXT = ("AGENTS.md", "CLAUDE.md")
STANDARD_CI = "bamr87/bamr87/.github/workflows/standard-ci.yml@"
MANIFEST = "_manifest.json"
BRAIN_URL = "github.com/bash-365/bash-365.com/tree/main/brain"


# --------------------------------------------------------------------------- #
# Registry + standard
# --------------------------------------------------------------------------- #


def load_registry(path: Path = REPOS_PATH) -> dict:
    data = read_yaml(path, default=None)
    if not isinstance(data, dict):
        raise ValueError(f"{rel(path)}: missing or not a map")
    return data


def validate_registry(reg: dict) -> list[str]:
    errs: list[str] = []
    if reg.get("schema") != "org-repos/v1":
        errs.append("schema must be org-repos/v1")
    names: set[str] = set()
    for i, r in enumerate(reg.get("repos") or []):
        where = f"repos[{i}] ({r.get('name', '?')})"
        for k in REQUIRED_REPO_KEYS:
            if not r.get(k):
                errs.append(f"{where}: missing `{k}`")
        if r.get("role") not in ROLES:
            errs.append(f"{where}: role must be one of {sorted(ROLES)}")
        if r.get("status") not in STATUSES:
            errs.append(f"{where}: status must be one of {sorted(STATUSES)}")
        if not re.match(r"^[\w.-]+/[\w.-]+$", str(r.get("repo", ""))):
            errs.append(f"{where}: repo must be owner/name")
        if r.get("role") == "member" and not str(r.get("repo", "")).startswith(f"{reg.get('org')}/"):
            errs.append(f"{where}: a member must live in the {reg.get('org')} organization")
        if r.get("role") == "upstream" and not r.get("change_here"):
            errs.append(f"{where}: an upstream needs `change_here`")
        if r.get("name") in names:
            errs.append(f"{where}: duplicate name")
        names.add(str(r.get("name")))
    if not any(r.get("repo") == reg.get("brain_home") for r in reg.get("repos") or []):
        errs.append("brain_home must name a registered repo")
    return errs


def load_standard(path: Path = STANDARD_PATH) -> dict:
    data = read_yaml(path, default=None)
    if not isinstance(data, dict):
        raise ValueError(f"{rel(path)}: missing or not a map")
    return data


def validate_standard(std: dict) -> list[str]:
    errs: list[str] = []
    if std.get("schema") != "org-standard/v1":
        errs.append("schema must be org-standard/v1")
    ids: set[str] = set()
    for c in std.get("checks") or []:
        cid = c.get("id", "?")
        if cid in ids:
            errs.append(f"{cid}: duplicate id")
        ids.add(cid)
        if c.get("level") not in LEVELS:
            errs.append(f"{cid}: level must be must|should")
        if c.get("test") not in TESTS:
            errs.append(f"{cid}: unknown test {c.get('test')!r}")
        if c.get("test") == "exists" and not c.get("paths"):
            errs.append(f"{cid}: an exists test needs `paths`")
        for k in ("title", "fix"):
            if not c.get(k):
                errs.append(f"{cid}: missing `{k}`")
    return errs


def repo_entry(reg: dict, name: str) -> dict | None:
    key = name.strip().lower()
    for r in reg.get("repos") or []:
        if key in (str(r["name"]).lower(), str(r["repo"]).lower(), str(r.get("hub_name", "")).lower()):
            return r
    return None


# --------------------------------------------------------------------------- #
# A repository as the checks see it: a live checkout or a committed snapshot
# --------------------------------------------------------------------------- #


@dataclass
class RepoView:
    name: str
    repo: str
    root: Path | None           # a checkout (this repo, or --workspace)
    snapshot: Path | None       # brain/sources/<name>/
    manifest: dict

    def exists(self, path: str) -> bool:
        if self.root is not None:
            return (self.root / path).exists()
        return bool((self.manifest.get("files") or {}).get(path))

    def read(self, path: str) -> str:
        base = self.root if self.root is not None else self.snapshot
        return read_text(base / path) if base is not None else ""

    @property
    def commit(self) -> str:
        return str(self.manifest.get("commit") or "")

    @property
    def available(self) -> bool:
        return self.root is not None or bool(self.manifest)


def view_for(entry: dict, home_root: Path = ROOT, sources: Path = SOURCES_DIR) -> RepoView:
    if entry["repo"] == HOME_REPO:
        return RepoView(entry["name"], entry["repo"], home_root, None, {"commit": "working tree"})
    snap = sources / entry["name"]
    manifest = {}
    if (snap / MANIFEST).exists():
        try:
            manifest = json.loads(read_text(snap / MANIFEST))
        except json.JSONDecodeError:
            manifest = {}
    return RepoView(entry["name"], entry["repo"], None, snap, manifest)


# --------------------------------------------------------------------------- #
# The checks (named by `test:` in _data/org/standard.yml)
# --------------------------------------------------------------------------- #


def _headings(text: str) -> list[str]:
    return [m.group(1).strip().lower() for m in re.finditer(r"^##\s+(.+?)\s*#*\s*$", text, re.M)]


def _agent_text(v: RepoView) -> str:
    return v.read("AGENTS.md") if v.exists("AGENTS.md") else v.read("CLAUDE.md")


def t_agents_file(v: RepoView, c: dict) -> tuple[bool, str]:
    return (True, "") if v.exists("AGENTS.md") else (False, "no root AGENTS.md")


def t_agents_headings(v: RepoView, c: dict) -> tuple[bool, str]:
    if not v.exists("AGENTS.md"):
        return False, "no AGENTS.md to read"
    have = set(_headings(v.read("AGENTS.md")))
    missing = [h for h in SIX_HEADINGS if h not in have]
    return (not missing, "missing: " + ", ".join(missing) if missing else "")


def t_claude_pointer(v: RepoView, c: dict) -> tuple[bool, str]:
    if not v.exists("CLAUDE.md"):
        return False, "no CLAUDE.md"
    text = v.read("CLAUDE.md")
    lines = [l for l in text.splitlines() if l.strip()]
    problems = []
    if not re.search(r"^@AGENTS\.md\s*$", text, re.M):
        problems.append("no @AGENTS.md import")
    if any(h in SIX_HEADINGS for h in _headings(text)):
        problems.append("carries AGENTS.md headings")
    if len(lines) > 20:
        problems.append(f"{len(lines)} non-blank lines (max 20)")
    return (not problems, "; ".join(problems))


def t_no_scaffold(v: RepoView, c: dict) -> tuple[bool, str]:
    hits = []
    for f in ("AGENTS.md", "CLAUDE.md"):
        if v.exists(f):
            n = len(re.findall(r"<!--\s*TODO:", v.read(f)))
            if n:
                hits.append(f"{f}: {n} TODO marker(s)")
    return (not hits, "; ".join(hits))


def t_agents_donts(v: RepoView, c: dict) -> tuple[bool, str]:
    text = _agent_text(v).lower()
    if not text:
        return False, "no agent file"
    wants = {
        "never push to main": r"(never|don't|do not)\b[^.\n]{0,40}push[^.\n]{0,40}(main|default branch)|pull requests only",
        "no secrets": r"secret",
        "no hand-edited generated files": r"generated",
    }
    missing = [k for k, pat in wants.items() if not re.search(pat, text)]
    return (not missing, "not stated: " + ", ".join(missing) if missing else "")


def t_agents_budget(v: RepoView, c: dict) -> tuple[bool, str]:
    if not v.exists("AGENTS.md"):
        return True, ""
    words = len(re.findall(r"\S+", v.read("AGENTS.md")))
    return (words <= 2000, f"{words} words" if words > 2000 else "")


def t_exists(v: RepoView, c: dict) -> tuple[bool, str]:
    missing = [p for p in c.get("paths") or [] if not v.exists(p)]
    return (not missing, "missing: " + ", ".join(missing) if missing else "")


def t_ci_caller(v: RepoView, c: dict) -> tuple[bool, str]:
    if not v.exists(".github/workflows/ci.yml"):
        return False, "no .github/workflows/ci.yml"
    if v.root is None:   # a snapshot records the fact, not the workflow file (no nested .github/workflows/ here)
        ok = bool((v.manifest.get("facts") or {}).get("ci_calls_standard_ci"))
    else:
        ok = STANDARD_CI in v.read(".github/workflows/ci.yml")
    return (ok, "" if ok else "ci.yml does not call the hub's standard-ci.yml")


def t_links_brain(v: RepoView, c: dict) -> tuple[bool, str]:
    text = _agent_text(v)
    if v.repo == HOME_REPO:
        return ("brain/" in text, "" if "brain/" in text else "AGENTS.md does not name brain/")
    ok = "bash-365/bash-365.com" in text and "brain" in text.lower()
    return (ok, "" if ok else "the agent file does not point at the org brain")


TESTS = {
    "agents_file": t_agents_file, "agents_headings": t_agents_headings, "claude_pointer": t_claude_pointer,
    "no_scaffold": t_no_scaffold, "agents_donts": t_agents_donts, "agents_budget": t_agents_budget,
    "exists": t_exists, "ci_caller": t_ci_caller, "links_brain": t_links_brain,
}


def audit_repo(entry: dict, std: dict, view: RepoView | None = None) -> dict:
    view = view or view_for(entry)
    result = {"name": entry["name"], "repo": entry["repo"], "status": entry["status"],
              "commit": view.commit, "checked": view.available, "results": []}
    if entry.get("role") != "member" or entry.get("status") == "archived":
        result["checked"] = False
        result["skipped"] = "upstream: the hub's conformance gate owns it" if entry.get("role") != "member" \
            else "archived"
        return result
    if not view.available:
        result["skipped"] = "no snapshot yet: run `python3 scripts/brain/brain.py sync`"
        return result
    for c in std.get("checks") or []:
        ok, detail = TESTS[c["test"]](view, c)
        hub = entry.get("hub_name") or entry["name"]
        result["results"].append({
            "id": c["id"], "ups": c.get("ups"), "level": c["level"], "title": c["title"], "pass": ok,
            "detail": detail, "fix": c["fix"],
            "remediate": str(c["remediate"]).replace("<hub_name>", hub) if c.get("remediate") else None,
        })
    fails = [r for r in result["results"] if not r["pass"]]
    result["errors"] = sum(1 for r in fails if r["level"] == "must")
    result["warnings"] = sum(1 for r in fails if r["level"] == "should")
    return result


def audit(reg: dict, std: dict) -> list[dict]:
    return [audit_repo(e, std) for e in reg.get("repos") or [] if e.get("role") == "member"]


# --------------------------------------------------------------------------- #
# Snapshots of other org repos
# --------------------------------------------------------------------------- #


def _git(*args: str, cwd: Path | None = None) -> str:
    try:
        return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
                              timeout=300).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def find_checkout(entry: dict, workspace: Path) -> Path | None:
    """A local checkout of `entry` under `workspace`, confirmed by its remote URL."""
    owner, name = entry["repo"].split("/", 1)
    for cand in (workspace / name, workspace / owner / name, workspace / "projects" / name):
        if (cand / ".git").exists():
            url = _git("config", "--get", "remote.origin.url", cwd=cand).lower().removesuffix(".git")
            if url.endswith(entry["repo"].lower()):
                return cand
    return None


def snapshot(entry: dict, checkout: Path, dest_root: Path = SOURCES_DIR) -> dict:
    """Copy a member repo's agent-facing docs into brain/sources/<name>/; return the manifest."""
    dest = dest_root / entry["name"]
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    redactions = 0
    copied = []
    for path in sorted(set(list(entry.get("sources") or []) + list(COPY_TEXT))):
        src = checkout / path
        if not src.is_file():
            continue
        text = strip_hidden(read_text(src))
        clean = scrub(text)
        redactions += sum(1 for a, b in zip(text.splitlines(), clean.splitlines()) if a != b)
        out = dest / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(clean.rstrip() + "\n", encoding="utf-8")
        copied.append(path)
    md = [str(dest / p) for p in copied if p.endswith(".md")]
    if md:   # this repo's prose gate (one paragraph per line) applies to every tracked Markdown file
        subprocess.run([sys.executable, str(ROOT / "tools" / "unwrap-prose.py"), "--write", *md],
                       capture_output=True, text=True, check=False)
    manifest = {
        "repo": entry["repo"], "branch": entry["branch"],
        "commit": _git("rev-parse", "HEAD", cwd=checkout)[:12],
        "files": {p: (checkout / p).exists() for p in CHECK_FILES},
        "facts": {"ci_calls_standard_ci": STANDARD_CI in read_text(checkout / ".github/workflows/ci.yml")},
        "copied": copied, "redacted_lines": redactions,
    }
    (dest / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def sync(reg: dict, workspace: Path | None = None, only: str | None = None, log=print) -> list[dict]:
    """Refresh every member snapshot (not this repo, which the brain reads live)."""
    done = []
    for entry in reg.get("repos") or []:
        if entry.get("role") != "member" or entry["repo"] == HOME_REPO:
            continue
        if only and only.lower() not in (entry["name"].lower(), entry["repo"].lower()):
            continue
        checkout = find_checkout(entry, workspace) if workspace else None
        tmp = None
        if checkout is None:
            tmp = Path(tempfile.mkdtemp(prefix="brain-sync-"))
            url = f"https://github.com/{entry['repo']}.git"
            _git("clone", "--quiet", "--depth", "1", "--branch", entry["branch"], url, str(tmp / "repo"))
            checkout = tmp / "repo" if (tmp / "repo" / ".git").exists() else None
        if checkout is None:
            log(f"skip {entry['repo']}: no checkout and the clone failed (offline, or private without a token)")
            if tmp:
                shutil.rmtree(tmp, ignore_errors=True)
            continue
        manifest = snapshot(entry, checkout)
        log(f"synced {entry['repo']}@{manifest['commit']}: {len(manifest['copied'])} files"
            + (f", {manifest['redacted_lines']} line(s) redacted" if manifest["redacted_lines"] else ""))
        done.append(manifest)
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    return done


# --------------------------------------------------------------------------- #
# Reading another repo's agent file: the parts a brief needs
# --------------------------------------------------------------------------- #


def section(text: str, *names: str) -> str:
    """The body of the first `##` section whose heading matches one of `names`."""
    wanted = {n.lower() for n in names}
    lines = text.splitlines()
    out: list[str] = []
    grab = False
    fence = False
    for line in lines:
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
        if not fence and re.match(r"^##\s", line):
            if grab:
                break
            grab = line[2:].strip().strip("#").strip().lower() in wanted
            continue
        if grab:
            out.append(line)
    return "\n".join(out).strip()


def commands(text: str) -> str:
    """The first fenced block under the commands heading, else the first bash block anywhere."""
    for body in (section(text, "stack & commands", "essential commands", "commands", "development"), text):
        m = re.search(r"```(?:bash|sh|shell|console)?\n(.*?)```", body, re.S)
        if m:
            return m.group(1).rstrip()
    return ""


def operating_rules() -> str:
    """The org's hand-written operating rules note, body only."""
    from common import frontmatter

    path = NOTES_DIR / "org-operating-rules.md"
    text = read_text(path)
    if not text:
        return ""
    body = re.sub(r"\A\s*# [^\n]*\n", "", frontmatter(text)[1]).strip()
    base = rel(path.parent)

    def to_root(m: re.Match) -> str:   # relative links in the note → repo-root paths, so the brief reads anywhere
        target = m.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:|^/|^#", target, re.I):
            return m.group(0)
        return f"[{m.group(1)}]({posixpath.normpath(posixpath.join(base, target))})"

    return re.sub(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)\)", to_root, body)


def brief(reg: dict, std: dict, entry: dict, task: str = "", vault=None, limit: int = 8) -> dict:
    """Everything an agent needs before its first commit in `entry`."""
    view = view_for(entry)
    agent_file = entry.get("agent_file") or "AGENTS.md"
    text = view.read(agent_file)
    if not text and agent_file != "CLAUDE.md" and view.read("CLAUDE.md"):
        agent_file, text = "CLAUDE.md", view.read("CLAUDE.md")
    first_party = entry["repo"] == HOME_REPO
    result = audit_repo(entry, std, view) if entry.get("role") == "member" else None
    related = vault.search(task, limit=limit) if (vault is not None and task) else []
    return {
        "repo": entry["repo"], "name": entry["name"], "role": entry["role"], "status": entry["status"],
        "branch": entry["branch"], "kind": entry["kind"], "live_url": entry.get("live_url"),
        "summary": entry["summary"], "change_here": entry.get("change_here"), "hub_name": entry.get("hub_name"),
        "hub_drift": entry.get("hub_drift"), "task": task,
        "agent_file": agent_file, "agent_file_source": "working tree" if first_party else (
            f"brain/sources/{entry['name']}/{agent_file} @ {view.commit}" if view.available else None),
        "trust": "first-party" if first_party else "untrusted-third-party",
        "commands": commands(text) if text else "",
        "conventions": section(text, "conventions", "operating rules") if text else "",
        "rules": operating_rules(),
        "gaps": [r for r in (result or {}).get("results", []) if not r["pass"]],
        "audit_skipped": (result or {}).get("skipped"),
        "related": related,
    }


def render_brief(b: dict) -> str:
    out = [f"# Brief: {b['repo']}", ""]
    if b["task"]:
        out += [f"**Task:** {b['task']}", ""]
    out += [f"{b['summary']}", "",
            f"- Role: {b['role']} · status: {b['status']} · kind: {b['kind']} · default branch: `{b['branch']}`"]
    if b.get("live_url"):
        out.append(f"- Live: {b['live_url']}")
    if b.get("hub_name"):
        out.append(f"- Hub registry name: `{b['hub_name']}` (bamr87/bamr87 `_data/projects.yml`)")
    if b.get("hub_drift"):
        out.append(f"- Registry drift: {b['hub_drift']}")
    out.append("")
    if b["role"] == "upstream":
        out += ["## Where this changes", "",
                f"The organization builds on {b['repo']} and never forks it. {b['change_here']} "
                f"Open the pull request in {b['repo']}, following its own `{b['agent_file']}`.", ""]
    out += ["## Org operating rules", "", b["rules"] or "_brain/notes/org-operating-rules.md is missing._", ""]
    out += ["## The repo's own agent file", ""]
    if b["agent_file_source"]:
        out.append(f"Read `{b['agent_file']}` in full before editing (here: {b['agent_file_source']}). "
                   "Its rules win over this brief wherever they are more specific.")
    else:
        out.append("No snapshot yet: run `python3 scripts/brain/brain.py sync`, or read the agent file in the checkout.")
    out.append("")
    if b["commands"]:
        cmd = f"```bash\n{b['commands']}\n```"
        if b["trust"] != "first-party":
            cmd = fence_untrusted(cmd, b["repo"], b["agent_file"])
        out += ["### Commands (the gates to run)", "", cmd, ""]
    if b["conventions"]:
        conv = b["conventions"]
        if b["trust"] != "first-party":
            conv = fence_untrusted(conv, b["repo"], b["agent_file"])
        out += ["### Conventions", "", conv, ""]
    if b["role"] == "member":
        out += ["## Agent-readiness gaps", ""]
        if b["audit_skipped"]:
            out.append(f"Not audited: {b['audit_skipped']}.")
        elif not b["gaps"]:
            out.append("None: the repo meets every check in `_data/org/standard.yml`.")
        for g in b["gaps"]:
            line = f"- **{g['id']}** ({g['level']}{', ' + g['ups'] if g['ups'] else ''}) {g['title']}"
            line += f": {g['detail']}. Fix: {g['fix']}" if g["detail"] else f". Fix: {g['fix']}"
            if g.get("remediate"):
                line += f" From a hub checkout: `{g['remediate']}`."
            out.append(line)
        out.append("")
    if b["related"]:
        out += ["## What the brain knows about the task", ""]
        for r in b["related"]:
            tag = " (snapshot, untrusted)" if r["trust"] != "first-party" else ""
            out.append(f"- [{r['title']}]({r['path']}){tag}: {summary(r['description'], 140)}")
        out.append("")
    out += ["## Definition of done", "",
            "- [ ] Work on a branch (`<type>/<slug>`), never the default branch; one repository per pull request.",
            "- [ ] Run the repo's gates above and say in the pull request which ran and what they printed.",
            "- [ ] Update the nearest README and the agent file if commands, layout or rules changed.",
            "- [ ] A user-facing change gets its `features/features.yml` entry; a hard-to-reverse one an ADR.",
            "- [ ] Conventional Commit title; draft pull request; never merge a gated one (label `needs-amr`).",
            "- [ ] If you learned something the next agent needs, save it: `python3 scripts/brain/brain.py save`.",
            ""]
    return "\n".join(out).rstrip() + "\n"


__all__ = ["CHECK_FILES", "RepoView", "TESTS", "audit", "audit_repo", "brief", "commands", "find_checkout",
           "load_registry", "load_standard", "render_brief", "repo_entry", "section", "snapshot", "sync",
           "validate_registry", "validate_standard", "view_for", "YamlError", "BRAIN_URL"]
