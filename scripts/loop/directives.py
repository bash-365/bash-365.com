#!/usr/bin/env python3
"""Editorial directives — the hub's approved topics, read from this repository's issues.

The bamr87 hub's content atlas (bamr87/bamr87 `.github/scripts/dash-gen/content_atlas.py`,
`docs/CONTENT-ATLAS.md`) declares a topic once and files each approved one as an issue
in this repository labelled `editorial:directive`. The issue is the message and this
script is its only reader here. Three consumers call it:

  * the planner (scripts/loop/plan.py): an unclaimed `write` directive goes ahead of a
    new article — the `directive` mode;
  * the weekly gardener (.github/workflows/content-gardener.yml): the first `write`
    directive is the topic when the dispatch input gave none;
  * the review lane (.github/workflows/content-review.yml): a `refresh` or `fix`
    directive with a `Document:` path is the focus when the dispatch input gave none.

The contract consumed, exactly as `content_atlas.issue_body` writes it:

  title   [editorial] <title>
  body    <!-- editorial-directive key=<key> site=<site> -->          (line 1, hidden)
          **Editorial directive** · kind `<kind>` · priority `<P>` [· pillar `<pillar>`]
          <the brief, one paragraph>
          [Document: `<path>`]
          [### The narrative this serves   +   a `> ` quoted paragraph]
          ---  and a footer sentence

Kinds are write, refresh, fix, hold, pillar and cadence. Only the kinds in
`_data/loop/config.yml` `directives.kinds` (write, refresh) are topics; the rest are
instructions for people or other lanes and are listed as skipped, never acted on.

A directive is *claimed* when an open pull request references its URL or `#<n>` (or
lists it among its closing references) and *spent* when a ledger run record carries
it (`scripts/loop/ledger.py --record … --directive <url>`); either drops it. The rest
are ranked by priority (P0 first) then age (oldest first) and capped at
`directives.max_per_run`, because every run opens ONE pull request.

Deterministic, stdlib only, no model calls. No `gh`, no token, or an API refusal gives
an empty list and a note — never a failure — so a lane that finds nothing falls back
to its own pick. One listing of open pull requests, filtered here, stands in for a
search round trip per directive: GitHub's search tokenizes `#38` and URLs loosely,
and the local match is exact.

Usage:
  python3 scripts/loop/directives.py [--kind write,refresh] [--max N] [--require-path]
                                     [--include-claimed] [--label L] [--json]
  python3 scripts/loop/directives.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lib  # noqa: E402
import ledger  # noqa: E402

KINDS = ("write", "refresh", "fix", "hold", "pillar", "cadence")
DEFAULT_LABEL = "editorial:directive"
DEFAULT_KINDS = ["write", "refresh"]
DEFAULT_MAX = 1
PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
TITLE_PREFIX = "[editorial]"

MARKER_RE = re.compile(r"<!--\s*editorial-directive\s+key=(?P<key>\S+)\s+site=(?P<site>\S+)\s*-->")
HEAD_RE = re.compile(r"^\*\*Editorial directive\*\*(?P<rest>.*)$", re.M)
FIELD_RE = re.compile(r"\b(kind|priority|pillar)\s+`([^`]*)`")
DOC_RE = re.compile(r"^Document:\s*`([^`]+)`\s*$", re.M)
NARRATIVE_RE = re.compile(r"^### The narrative this serves\s*\n+((?:>.*(?:\n|$))+)", re.M)


# --------------------------------------------------------------------------- #
# Parsing — one issue -> one directive (or None when it is not one)
# --------------------------------------------------------------------------- #

def parse_directive(issue: dict) -> dict | None:
    """Read the atlas's contract out of an issue. None when the marker is missing —
    a labelled issue a person wrote by hand is not a directive."""
    body = str(issue.get("body") or "")
    m = MARKER_RE.search(body)
    if not m:
        return None
    fields: dict[str, str] = {}
    head = HEAD_RE.search(body)
    if head:
        for name, value in FIELD_RE.findall(head.group("rest")):
            fields[name] = value.strip()
    brief = ""
    after = body[head.end():] if head else body[m.end():]
    for para in re.split(r"\n\s*\n", after):
        text = para.strip()
        if not text or text.startswith(("Document:", "#", ">", "---", "_Filed", "<!--")):
            continue
        brief = _lib.one_line(text, limit=2000)
        break
    doc = DOC_RE.search(body)
    narrative = ""
    n = NARRATIVE_RE.search(body)
    if n:
        narrative = _lib.one_line(" ".join(line.lstrip("> ").strip() for line in n.group(1).splitlines()), limit=2000)
    title = str(issue.get("title") or "").strip()
    if title.startswith(TITLE_PREFIX):
        title = title[len(TITLE_PREFIX):].strip()
    try:
        number = int(issue.get("number") or 0)
    except (TypeError, ValueError):
        number = 0
    kind = fields.get("kind", "").lower()
    return {
        "number": number,
        "url": str(issue.get("url") or "").strip(),
        "title": _lib.one_line(_lib.scrub(title), limit=200),
        "slug": _lib.slugify(title),
        "key": m.group("key"),
        "site": m.group("site"),
        "kind": kind if kind in KINDS else (kind or "unknown"),
        "priority": fields.get("priority", "").upper() or "P2",
        "pillar": fields.get("pillar") or None,
        "brief": _lib.scrub(brief),
        "path": doc.group(1).strip() if doc else None,
        "narrative": _lib.scrub(narrative),
        "created_at": str(issue.get("createdAt") or ""),
    }


def claimed_by(directive: dict, prs: list[dict]) -> str:
    """The URL of the open pull request that already references this directive, or ""."""
    n = directive.get("number") or 0
    url = directive.get("url") or ""
    ref = re.compile(rf"(?<!\d)#{n}(?!\d)") if n else None
    for pr in prs:
        body = str(pr.get("body") or "")
        closing = pr.get("closingIssuesReferences") or []
        if (url and url in body) or (ref and ref.search(body)) \
                or any(str(c.get("number")) == str(n) for c in closing if isinstance(c, dict)):
            return str(pr.get("url") or "")
    return ""


# --------------------------------------------------------------------------- #
# Observation — gh, best-effort
# --------------------------------------------------------------------------- #

def _run(cmd: list[str], timeout: int = 60) -> tuple[int, str]:
    """(returncode, stdout-or-stderr). 127 when gh is missing or cannot run."""
    if not shutil.which(cmd[0]):
        return 127, f"{cmd[0]}: not found"
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)
    return res.returncode, res.stdout if res.returncode == 0 else (res.stderr or res.stdout)


def _json_list(rc: int, out: str) -> list | None:
    if rc != 0:
        return None
    try:
        data = json.loads(out or "[]")
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, list) else None


def list_issues(label: str = DEFAULT_LABEL, run=_run, limit: int = 100) -> tuple[list[dict], str]:
    """Open issues under the label, or ([], note) when gh cannot tell."""
    rc, out = run(["gh", "issue", "list", "--label", label, "--state", "open", "--limit", str(limit),
                   "--json", "number,title,body,url,createdAt"])
    issues = _json_list(rc, out)
    if issues is None:
        return [], f"directives: could not list `{label}` issues (no gh, no token, or the API refused: {_lib.one_line(out, 120) or 'no output'}) — none offered"
    return issues, ""


def list_open_prs(run=_run, limit: int = 100) -> tuple[list[dict], str]:
    rc, out = run(["gh", "pr", "list", "--state", "open", "--limit", str(limit),
                   "--json", "number,url,body,closingIssuesReferences"])
    prs = _json_list(rc, out)
    if prs is None:
        return [], f"directives: could not list open pull requests ({_lib.one_line(out, 120) or 'no output'}) — claims unknown, assuming none"
    return prs, ""


# --------------------------------------------------------------------------- #
# The pure part — filter, drop the claimed and the spent, rank, cap
# --------------------------------------------------------------------------- #

def rank(directives: list[dict], *, kinds: list[str], max_per_run: int, prs: list[dict],
         spent: set[str], require_path: bool = False, include_claimed: bool = False) -> dict:
    """{"directives": offered (best first), "skipped": [{number, title, kind, reason}]}."""
    offered: list[dict] = []
    skipped: list[dict] = []
    for d in directives:
        why = ""
        if d.get("kind") not in kinds:
            why = f"kind `{d.get('kind')}` is not a topic for this lane"
        elif require_path and not d.get("path"):
            why = "no Document: path"
        elif d.get("url") and d["url"] in spent:
            why = "spent — a ledger run already carries it"
        else:
            holder = "" if include_claimed else claimed_by(d, prs)
            if holder:
                why = f"claimed by {holder}"
        if why:
            skipped.append({"number": d.get("number"), "title": d.get("title"), "kind": d.get("kind"), "reason": why})
        else:
            offered.append(d)
    offered.sort(key=lambda d: (PRIORITY_RANK.get(str(d.get("priority")), 9), str(d.get("created_at") or "9999"), int(d.get("number") or 0)))
    return {"directives": offered[:max(0, int(max_per_run))], "skipped": skipped, "seen": len(directives)}


def gather(config: dict, runs: list[dict] | None = None, *, kinds: list[str] | None = None,
           max_per_run: int | None = None, require_path: bool = False, include_claimed: bool = False,
           label: str | None = None, run=_run) -> dict:
    """Observe with gh, then rank. Never raises for a missing gh or token."""
    cfg = config.get("directives") or {}
    label = label or str(cfg.get("label") or DEFAULT_LABEL)
    kinds = [str(k).lower() for k in (kinds if kinds is not None else (cfg.get("kinds") or DEFAULT_KINDS))]
    cap = int(max_per_run if max_per_run is not None else (cfg.get("max_per_run") or DEFAULT_MAX))
    notes: list[str] = []
    issues, note = list_issues(label, run=run)
    if note:
        notes.append(note)
        return {"directives": [], "skipped": [], "seen": 0, "label": label, "notes": notes}
    directives = [d for d in (parse_directive(i) for i in issues) if d]
    if len(directives) < len(issues):
        notes.append(f"directives: {len(issues) - len(directives)} `{label}` issue(s) carry no editorial-directive marker — ignored")
    prs: list[dict] = []
    if directives and not include_claimed:
        prs, note = list_open_prs(run=run)
        if note:
            notes.append(note)
    spent = ledger.spent_directives(runs or [])
    out = rank(directives, kinds=kinds, max_per_run=cap, prs=prs, spent=spent,
               require_path=require_path, include_claimed=include_claimed)
    if directives and not out["directives"]:
        skipped = out["skipped"]
        why = []
        other = sorted({str(s["kind"]) for s in skipped if "is not a topic" in str(s["reason"])})
        if other:
            why.append(f"kind {', '.join(other)} — not topics for this lane")
        for tag, text in (("claimed", "claimed by an open pull request"), ("spent", "spent by a ledger run"), ("no Document", "without a Document: path")):
            n = sum(1 for s in skipped if str(s["reason"]).startswith(tag))
            if n:
                why.append(f"{n} {text}")
        notes.append(f"directives: {len(directives)} `{label}` issue(s) open, none offered ({'; '.join(why)})")
    out["label"] = label
    out["notes"] = notes
    return out


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def render_table(found: dict) -> str:
    lines = [f"directives: {len(found['directives'])} offered of {found.get('seen', 0)} open `{found.get('label', DEFAULT_LABEL)}` issue(s)"]
    for d in found["directives"]:
        extra = f" · pillar {d['pillar']}" if d.get("pillar") else ""
        extra += f" · {d['path']}" if d.get("path") else ""
        lines.append(f"  #{d['number']:<4} {d['priority']:<3} {d['kind']:<8} {d['title']}{extra}")
        lines.append(f"        {d['url']}")
    for s in found.get("skipped", []):
        lines.append(f"  -#{s['number']:<4} {s['kind']:<8} {_lib.one_line(str(s['title']), 60)} — {s['reason']}")
    for n in found.get("notes", []):
        lines.append(f"  note: {n}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Self-test — in-file fixtures, no network
# --------------------------------------------------------------------------- #

_NARRATIVE = ("BASH Consulting runs on governed AI: rules in files, reusable playbooks, agents that draft, humans who "
              "approve. The site shows a small or mid-size business what that looks like across cloud, ERP and "
              "financial systems, data and BI, and custom development — describing categories of work and what the "
              "frameworks require, never inventing clients or claims.")
_FOOTER = ("---\n_Filed by the hub's content atlas from an approved entry in `bamr87/bamr87` `_data/editorial.yml`. "
           "Close it when the work ships; the atlas marks the directive done on its next `file` pass._")

# Issues #38 and #41 of bash-365/bash-365.com, verbatim (filed 2026-10-02 by the hub's atlas).
_ISSUE_38 = {
    "number": 38, "url": "https://github.com/bash-365/bash-365.com/issues/38", "createdAt": "2026-10-02T04:36:26Z",
    "title": "[editorial] Map the orphan topics",
    "body": ("<!-- editorial-directive key=unmapped site=bash-365.com -->\n\n"
             "**Editorial directive** · kind `pillar` · priority `P2`\n\n"
             "34% of documents match no pillar. Their top tags: toolkit, partners, migration, cloud-services, aws, "
             "azure, gcp, infrastructure. Either extend a pillar's match or declare a new one.\n\n"
             "### The narrative this serves\n\n> " + _NARRATIVE + "\n\n" + _FOOTER),
}
_ISSUE_41 = {
    "number": 41, "url": "https://github.com/bash-365/bash-365.com/issues/41", "createdAt": "2026-10-02T04:36:29Z",
    "title": "[editorial] Rest “SMB strategy” for a cycle",
    "body": ("<!-- editorial-directive key=pillar-over:smb-strategy site=bash-365.com -->\n\n"
             "**Editorial directive** · kind `hold` · priority `P3` · pillar `smb-strategy`\n\n"
             "53% of recent work against a 15% target — the mix is drifting toward this pillar at the others' expense.\n\n"
             "### The narrative this serves\n\n> " + _NARRATIVE + "\n\n" + _FOOTER),
}


def _fixture(number: int, kind: str, priority: str, title: str, created: str, *, pillar: str = "",
             path: str = "", brief: str = "Write it for the owner who signs the checks.") -> dict:
    head = f"**Editorial directive** · kind `{kind}` · priority `{priority}`" + (f" · pillar `{pillar}`" if pillar else "")
    body = [f"<!-- editorial-directive key=test:{number} site=bash-365.com -->", "", head, "", brief, ""]
    if path:
        body += [f"Document: `{path}`", ""]
    body += ["### The narrative this serves", "", "> " + _NARRATIVE, "", _FOOTER]
    return {"number": number, "url": f"https://github.com/bash-365/bash-365.com/issues/{number}",
            "createdAt": created, "title": f"[editorial] {title}", "body": "\n".join(body)}


def self_test() -> int:
    failures: list[str] = []

    def check(name, got, want):
        if got != want:
            failures.append(f"{name}: got {got!r}, want {want!r}")

    d38 = parse_directive(_ISSUE_38)
    check("38 key", d38["key"], "unmapped")
    check("38 site", d38["site"], "bash-365.com")
    check("38 kind", d38["kind"], "pillar")
    check("38 priority", d38["priority"], "P2")
    check("38 no pillar", d38["pillar"], None)
    check("38 title stripped", d38["title"], "Map the orphan topics")
    check("38 slug", d38["slug"], "map-the-orphan-topics")
    check("38 brief", d38["brief"].startswith("34% of documents match no pillar"), True)
    check("38 brief is one paragraph", d38["brief"].endswith("declare a new one."), True)
    check("38 no path", d38["path"], None)
    check("38 narrative", d38["narrative"].startswith("BASH Consulting runs on governed AI"), True)
    check("38 narrative ends", d38["narrative"].endswith("never inventing clients or claims."), True)
    d41 = parse_directive(_ISSUE_41)
    check("41 kind", d41["kind"], "hold")
    check("41 priority", d41["priority"], "P3")
    check("41 pillar", d41["pillar"], "smb-strategy")
    check("41 key with colon", d41["key"], "pillar-over:smb-strategy")
    check("41 unicode title", d41["title"], "Rest “SMB strategy” for a cycle")
    check("no marker -> not a directive", parse_directive({"number": 1, "title": "[editorial] by hand", "body": "**Editorial directive** · kind `write`"}), None)
    check("empty body", parse_directive({"number": 2, "title": "x", "body": None}), None)

    w70 = _fixture(70, "write", "P1", "Making progress: the essay", "2026-10-10T00:00:00Z", pillar="ai-operations")
    w71 = _fixture(71, "write", "P2", "An older, lower-priority topic", "2026-10-01T00:00:00Z")
    r72 = _fixture(72, "refresh", "P1", "Refresh the AI-native practice doc", "2026-10-15T00:00:00Z",
                   path="pages/_toolkit/ai-native-practice.md", brief="The loop section is stale.")
    w74 = _fixture(74, "write", "P0", "Already being drafted", "2026-10-20T00:00:00Z")
    w76 = _fixture(76, "write", "P0", "Already written up", "2026-10-21T00:00:00Z")
    f77 = _fixture(77, "fix", "P3", "Fix one description", "2026-10-22T00:00:00Z", path="pages/_services/cloud.md")
    hand = {"number": 78, "url": "https://github.com/bash-365/bash-365.com/issues/78", "createdAt": "2026-10-23T00:00:00Z",
            "title": "a labelled issue someone typed", "body": "no marker here"}
    issues = [_ISSUE_38, _ISSUE_41, w70, w71, r72, w74, w76, f77, hand]
    prs = [{"number": 80, "url": "https://github.com/bash-365/bash-365.com/pull/80", "body": "Drafts the essay.\n\nCloses #74\n", "closingIssuesReferences": []},
           {"number": 81, "url": "https://github.com/bash-365/bash-365.com/pull/81", "body": "unrelated — see #740 and #7", "closingIssuesReferences": []}]
    runs = [{"id": "r", "date": "2026-10-22", "mode": "new", "section": "muses", "path": "p", "signals": [],
             "directive": "https://github.com/bash-365/bash-365.com/issues/76"}]
    check("72 path", parse_directive(r72)["path"], "pages/_toolkit/ai-native-practice.md")
    check("72 brief", parse_directive(r72)["brief"], "The loop section is stale.")

    calls: list[list[str]] = []

    def gh_ok(cmd, timeout=60):
        calls.append(cmd)
        if cmd[:3] == ["gh", "issue", "list"]:
            return 0, json.dumps(issues)
        if cmd[:3] == ["gh", "pr", "list"]:
            return 0, json.dumps(prs)
        return 1, "unexpected"

    cfg = {"directives": {"label": "editorial:directive", "max_per_run": 1, "kinds": ["write", "refresh"]}}
    found = gather(cfg, runs, run=gh_ok)
    check("issue list command", calls[0][:6], ["gh", "issue", "list", "--label", "editorial:directive", "--state"])
    check("cap at max_per_run", [d["number"] for d in found["directives"]], [70])
    check("seen", found["seen"], 8)
    check("hand-written issue noted", any("no editorial-directive marker" in n for n in found["notes"]), True)
    reasons = {s["number"]: s["reason"] for s in found["skipped"]}
    check("pillar kind skipped", "kind `pillar`" in reasons.get(38, ""), True)
    check("hold kind skipped", "kind `hold`" in reasons.get(41, ""), True)
    check("fix kind skipped by default", "kind `fix`" in reasons.get(77, ""), True)
    check("claimed skipped", reasons.get(74, ""), "claimed by https://github.com/bash-365/bash-365.com/pull/80")
    check("spent skipped", "spent" in reasons.get(76, ""), True)
    check("#7 / #740 are not #70 or #71", 70 in reasons or 71 in reasons, False)
    wide = gather(cfg, runs, run=gh_ok, max_per_run=5)
    check("rank: priority then age", [d["number"] for d in wide["directives"]], [70, 72, 71])
    review = gather(cfg, runs, run=gh_ok, kinds=["refresh", "fix"], require_path=True, max_per_run=5)
    check("review lane: refresh/fix with a path", [d["number"] for d in review["directives"]], [72, 77])
    check("review lane: write skipped", "kind `write`" in {s["number"]: s["reason"] for s in review["skipped"]}.get(70, ""), True)
    included = gather(cfg, runs, run=gh_ok, include_claimed=True, max_per_run=5)
    check("include claimed", [d["number"] for d in included["directives"]], [74, 70, 72, 71])
    check("include claimed: one gh call", sum(1 for c in calls if c[:3] == ["gh", "pr", "list"]), 3)

    def gh_missing(cmd, timeout=60):
        return 127, "gh: not found"

    none = gather(cfg, runs, run=gh_missing)
    check("no gh -> empty", none["directives"], [])
    check("no gh -> note", any("could not list" in n and "none offered" in n for n in none["notes"]), True)

    def gh_no_prs(cmd, timeout=60):
        if cmd[:3] == ["gh", "issue", "list"]:
            return 0, json.dumps([w70])
        return 1, "HTTP 403"

    nop = gather(cfg, [], run=gh_no_prs)
    check("pr list refused -> still offered", [d["number"] for d in nop["directives"]], [70])
    only_hold = gather(cfg, [], run=lambda cmd, timeout=60: (0, json.dumps([_ISSUE_38, _ISSUE_41])))
    check("open but none a topic -> empty", only_hold["directives"], [])
    check("open but none a topic -> note", any("2 `editorial:directive` issue(s) open, none offered (kind hold, pillar — not topics for this lane)" in n for n in only_hold["notes"]), True)
    all_claimed = gather(cfg, [], run=lambda cmd, timeout=60: (0, json.dumps([w74] if cmd[1] == "issue" else prs)))
    check("all claimed -> note", any("none offered (1 claimed by an open pull request)" in n for n in all_claimed["notes"]), True)
    check("pr list refused -> note", any("claims unknown" in n for n in nop["notes"]), True)
    check("defaults without a config block", gather({}, [], run=gh_no_prs)["label"], DEFAULT_LABEL)
    table = render_table(wide)
    check("table head", table.startswith("directives: 3 offered of 8 open"), True)
    check("table row", "#70   P1  write    Making progress: the essay · pillar ai-operations" in table, True)
    check("claimed_by url form", claimed_by({"number": 5, "url": "https://x/issues/5"}, [{"url": "https://x/pull/9", "body": "see https://x/issues/5"}]), "https://x/pull/9")
    check("claimed_by closing refs", claimed_by({"number": 5, "url": ""}, [{"url": "https://x/pull/9", "body": "", "closingIssuesReferences": [{"number": 5}]}]), "https://x/pull/9")

    if failures:
        print("directives --self-test: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("directives --self-test: PASS (marker + fields + brief + path + narrative, kind filter, claimed and spent skipped, rank, cap, no gh)")
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser(description="List the hub's open editorial directives this lane may act on.")
    ap.add_argument("--kind", help="comma-separated kinds to offer (default: config directives.kinds)")
    ap.add_argument("--max", type=int, help="cap (default: config directives.max_per_run)")
    ap.add_argument("--label", help="issue label (default: config directives.label)")
    ap.add_argument("--require-path", action="store_true", help="offer only directives that name a Document: path")
    ap.add_argument("--include-claimed", action="store_true", help="do not drop directives an open pull request references")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    config = _lib.read_yaml(_lib.CONFIG_PATH, default={}) or {}
    kinds = [k.strip().lower() for k in args.kind.split(",") if k.strip()] if args.kind else None
    found = gather(config, ledger.load_runs(), kinds=kinds, max_per_run=args.max, require_path=args.require_path,
                   include_claimed=args.include_claimed, label=args.label)
    if args.json:
        print(json.dumps(found, indent=2, ensure_ascii=False))
    else:
        print(render_table(found))
    return 0


if __name__ == "__main__":
    sys.exit(main())
