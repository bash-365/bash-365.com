#!/usr/bin/env python3
"""The org brain: BASH Consulting's knowledge, rules and repositories, in one place
an agent (or a person) can query before it touches anything.

The vault is this repository read in place — the site's services, toolkit,
case studies and posts, the constitution and decisions, the brand and editorial
rules, the agent layer — plus hand-written notes in brain/notes/ and snapshots
of the other org repos' agent files in brain/sources/. The generated layer in
brain/generated/ (hot cache, map of content, concepts, repo cards, audit,
health) and brain/graph.json are rebuilt from those inputs, deterministically.

Standard library only. Operator's guide: docs/brain.md.

    python3 scripts/brain/brain.py hot                       # where to start
    python3 scripts/brain/brain.py query erp migration       # ranked notes
    python3 scripts/brain/brain.py note "Deterministic-first"  # a note, its links and backlinks
    python3 scripts/brain/brain.py neighbours AGENTS.md --depth 2
    python3 scripts/brain/brain.py repos                     # the org registry
    python3 scripts/brain/brain.py brief bash-365-apex --task "add a security.txt"
    python3 scripts/brain/brain.py audit                     # every member repo vs _data/org/standard.yml
    python3 scripts/brain/brain.py sync [--workspace DIR]    # refresh brain/sources/ snapshots
    python3 scripts/brain/brain.py build                     # rewrite brain/generated/ + brain/graph.json
    python3 scripts/brain/brain.py check [--strict]          # the CI gate
    python3 scripts/brain/brain.py lint                      # vault health, read-only
    python3 scripts/brain/brain.py save "Title" "Body" --tag decisions
    python3 scripts/brain/brain.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate  # noqa: E402
import org  # noqa: E402
from common import NOTES_DIR, ROOT, read_text, rel, scrub, slugify, summary  # noqa: E402
from vault import build_vault, load_config, source_repo_map  # noqa: E402


def _vault():
    reg = org.load_registry()
    return build_vault(cfg=load_config(), repo_of=source_repo_map(reg)), reg


def _print(obj, as_json: bool) -> None:
    if as_json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    elif isinstance(obj, str):
        print(obj, end="" if obj.endswith("\n") else "\n")
    else:
        print(obj)


def cmd_hot(a) -> int:
    path = ROOT / "brain/generated/hot.md"
    files, _ = generate.outputs()
    _print(files["brain/generated/hot.md"] if a.live or not path.exists() else read_text(path), False)
    return 0


def cmd_query(a) -> int:
    v, _ = _vault()
    rows = v.search(" ".join(a.terms), limit=a.limit, include_untrusted=not a.first_party)
    if a.json:
        _print(rows, True)
        return 0
    if not rows:
        print("No note matches. The brain does not say; check the repository or ask.")
        return 1
    for r in rows:
        tag = " [untrusted snapshot]" if r["trust"] != "first-party" else ""
        print(f"{r['score']:>6}  {r['path']}  ({r['kind']}){tag}\n        {r['title']}: {summary(r['description'], 110)}")
    return 0


def cmd_note(a) -> int:
    v, _ = _vault()
    path = v.lookup(a.target)
    if not path:
        print(f"No note called {a.target!r}. Try: brain.py query {a.target}", file=sys.stderr)
        return 1
    n = v.notes[path]
    data = {"path": path, "title": n.title, "kind": n.kind, "repo": n.repo, "trust": n.trust, "date": n.date,
            "tags": n.tags, "permalink": n.permalink, "description": n.description,
            "links": v.outlinks(path), "backlinks": sorted(v.backlinks.get(path, ()))}
    if a.json:
        _print(data, True)
        return 0
    print(f"# {n.title}\n{path} · {n.kind} · {n.repo} · {n.trust}" + (f" · {n.date}" if n.date else ""))
    if n.permalink:
        print(f"site: https://www.bash-365.com{n.permalink}")
    print(f"\n{n.description}\n")
    print("links →\n" + ("\n".join(f"  {p}" for p in data["links"]) or "  (none)"))
    print("← backlinks\n" + ("\n".join(f"  {p}" for p in data["backlinks"]) or "  (none)"))
    if a.body:
        print("\n" + n.body.strip())
    return 0


def cmd_neighbours(a) -> int:
    v, _ = _vault()
    path = v.lookup(a.target)
    if not path:
        print(f"No note called {a.target!r}.", file=sys.stderr)
        return 1
    rows = [{"path": p, "distance": d, "title": v.notes[p].title, "kind": v.notes[p].kind}
            for p, d in v.neighbours(path, a.depth).items()]
    if a.json:
        _print(rows, True)
    else:
        for r in rows:
            print(f"{r['distance']}  {r['path']}  ({r['kind']})  {r['title']}")
    return 0


def cmd_repos(a) -> int:
    reg = org.load_registry()
    errs = org.validate_registry(reg)
    if a.check:
        std_errs = org.validate_standard(org.load_standard())
        for e in errs + std_errs:
            print(f"error: {e}")
        print("registry OK" if not errs + std_errs else f"{len(errs + std_errs)} error(s)")
        return 1 if errs + std_errs else 0
    rows = reg.get("repos") or []
    if a.json:
        _print(rows, True)
        return 0
    for r in rows:
        print(f"{r['repo']:<28} {r['role']:<9} {r['status']:<12} {summary(r['summary'], 80)}")
    return 0


def cmd_audit(a) -> int:
    reg, std = org.load_registry(), org.load_standard()
    rows = org.audit(reg, std)
    if a.repo:
        rows = [r for r in rows if a.repo.lower() in (r["name"].lower(), r["repo"].lower())]
    if a.json:
        _print(rows, True)
        return 0
    must = 0
    for r in rows:
        if not r.get("checked"):
            print(f"{r['repo']}: not checked ({r.get('skipped')})")
            continue
        must += r["errors"]
        print(f"{r['repo']} @ {r['commit']}: {r['errors']} must · {r['warnings']} should")
        for c in r["results"]:
            if not c["pass"]:
                print(f"  {c['level']:<6} {c['id']} {c['title']}: {c['detail']}")
    return 1 if (a.strict and must) else 0


def cmd_brief(a) -> int:
    reg, std = org.load_registry(), org.load_standard()
    entry = org.repo_entry(reg, a.repo)
    if entry is None:
        print(f"{a.repo!r} is not in _data/org/repos.yml. Known: "
              + ", ".join(r["name"] for r in reg.get("repos") or []), file=sys.stderr)
        return 1
    v, _ = _vault()
    b = org.brief(reg, std, entry, task=a.task or "", vault=v)
    _print(b if a.json else org.render_brief(b), a.json)
    return 0


def cmd_sync(a) -> int:
    reg = org.load_registry()
    done = org.sync(reg, workspace=Path(a.workspace).resolve() if a.workspace else None, only=a.repo)
    print(f"{len(done)} snapshot(s) refreshed. Rebuild with: python3 scripts/brain/brain.py build")
    return 0


def cmd_build(a) -> int:
    files, status = generate.outputs()
    if status["registry_errors"] or status["standard_errors"]:
        for e in status["registry_errors"] + status["standard_errors"]:
            print(f"error: {e}", file=sys.stderr)
        return 1
    changed = generate.write(files)
    print(f"brain built: {status['notes']} notes, {status['concepts']} concepts, fingerprint {status['fingerprint']}; "
          f"{len(changed)} file(s) changed")
    for p in changed:
        print(f"  {p}")
    return 0


def cmd_check(a) -> int:
    files, status = generate.outputs()
    errors = [f"registry: {e}" for e in status["registry_errors"]] + [f"standard: {e}" for e in status["standard_errors"]]
    v, _ = _vault()
    errors += [f"{f['path']}:{f['line']}: {f['message']}" for f in v.lint() if f["severity"] == "error"]
    for p in sorted(rel(x) for x in (ROOT / "brain").rglob("*.md") if x.is_file()):
        text = read_text(ROOT / p)
        if scrub(text) != text:
            errors.append(f"{p}: holds something that looks like a credential")
    stale = generate.stale(files)
    for e in errors:
        print(f"error: {e}")
    if stale:
        level = "error" if a.strict else "warning"
        print(f"{level}: the generated brain is stale ({len(stale)} file(s)); run: python3 scripts/brain/brain.py build")
        for p in stale[:20]:
            print(f"  {p}")
    findings = status["findings"]
    print(f"brain check: {status['notes']} notes · fingerprint {status['fingerprint']} · "
          f"{len(errors)} error(s) · {'stale' if stale else 'fresh'} · lint {findings}")
    return 1 if errors or (stale and a.strict) else 0


def cmd_lint(a) -> int:
    v, _ = _vault()
    rows = v.lint()
    if a.json:
        _print(rows, True)
    else:
        for f in rows:
            if a.all or f["severity"] != "info":
                print(f"{f['severity']:<7} {f['path']}:{f['line']} ({f['check']}) {f['message']}")
        print(f"{sum(f['severity'] == 'error' for f in rows)} error(s), "
              f"{sum(f['severity'] == 'warning' for f in rows)} warning(s), {sum(f['severity'] == 'info' for f in rows)} info")
    return 1 if any(f["severity"] == "error" for f in rows) else 0


def cmd_save(a) -> int:
    """File a durable note in brain/notes/ — the only hand-written part of the vault."""
    slug = slugify(a.title) or "note"
    path = NOTES_DIR / f"{slug}.md"
    if path.exists() and not a.force:
        print(f"{rel(path)} exists; pass --force to replace it, or edit it by hand.", file=sys.stderr)
        return 1
    body = scrub(a.body.replace("\\n", "\n")).strip()
    desc = summary(body.split("\n", 1)[0], 155).rstrip(".")
    sys.path.insert(0, str(ROOT / "scripts" / "loop"))
    import _lib  # noqa: E402

    lines = ["---", f'title: "{a.title.replace(chr(34), chr(39))}"', f'description: "{desc.replace(chr(34), chr(39))}"',
             f"date: {_lib.today().isoformat()}"]
    if a.tag:
        lines.append("tags: [" + ", ".join(sorted(set(a.tag))) + "]")
    if a.source:
        lines.append("sources: [" + ", ".join(a.source) + "]")
    lines += ["---", "", f"# {a.title}", "", body, ""]
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved {rel(path)}; rebuild with: python3 scripts/brain/brain.py build")
    return 0


def self_test() -> int:
    import unittest

    suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent), pattern="test_brain.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="brain.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true", help="run the unit tests and exit")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("hot", help="the hot cache: where to start")
    p.add_argument("--live", action="store_true", help="render from the working tree, not the committed file")
    p.set_defaults(fn=cmd_hot)
    p = sub.add_parser("query", help="rank notes for some words")
    p.add_argument("terms", nargs="+")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--first-party", action="store_true", help="leave out other repos' snapshots")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_query)
    p = sub.add_parser("note", help="one note: description, links, backlinks")
    p.add_argument("target", help="a path, title, alias or file stem")
    p.add_argument("--body", action="store_true", help="also print the note's text")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_note)
    p = sub.add_parser("neighbours", aliases=["neighbors"], help="notes within N links, either direction")
    p.add_argument("target")
    p.add_argument("--depth", type=int, default=1)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_neighbours)
    p = sub.add_parser("repos", help="the org registry")
    p.add_argument("--check", action="store_true", help="validate _data/org/repos.yml and standard.yml")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_repos)
    p = sub.add_parser("audit", help="member repos against _data/org/standard.yml")
    p.add_argument("repo", nargs="?")
    p.add_argument("--strict", action="store_true", help="exit 1 on any must-level gap")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_audit)
    p = sub.add_parser("brief", help="the work order an agent reads before contributing to a repo")
    p.add_argument("repo", help="registry name, owner/name, or hub name")
    p.add_argument("--task", default="", help="what the agent is about to do; pulls in the relevant notes")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_brief)
    p = sub.add_parser("sync", help="refresh brain/sources/ from the other member repos")
    p.add_argument("--workspace", help="a directory holding local checkouts (else: shallow clone over HTTPS)")
    p.add_argument("--repo", help="only this repo")
    p.set_defaults(fn=cmd_sync)
    p = sub.add_parser("build", help="rewrite brain/generated/ and brain/graph.json")
    p.set_defaults(fn=cmd_build)
    p = sub.add_parser("check", help="the CI gate: data valid, no secrets, generated layer fresh")
    p.add_argument("--strict", action="store_true", help="a stale generated layer is an error")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("lint", help="vault health: dead links, orphans, note front matter")
    p.add_argument("--all", action="store_true", help="also print info-level findings")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("save", help="file a hand-written note in brain/notes/")
    p.add_argument("title")
    p.add_argument("body")
    p.add_argument("--tag", action="append", default=[])
    p.add_argument("--source", action="append", default=[], help="a note path the answer came from")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_save)

    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not getattr(a, "fn", None):
        ap.print_help()
        return 2
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
